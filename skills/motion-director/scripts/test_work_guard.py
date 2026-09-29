#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("work_guard.py")


def child(*parts: str) -> list[str]:
    return [sys.executable, "-u", *parts]


def run_guard(run_root: Path, guard_args: list[str], command: list[str], timeout: float = 8.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "run", "--run-root", str(run_root), *guard_args, "--", *command],
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def load_summary(run_root: Path) -> dict:
    runs = [path for path in run_root.iterdir() if path.is_dir()]
    if len(runs) != 1:
        raise AssertionError(f"expected one run directory, found {runs}")
    return json.loads((runs[0] / "summary.json").read_text(encoding="utf-8"))


def process_is_running(pid: int) -> bool:
    proc_stat = Path(f"/proc/{pid}/stat")
    if proc_stat.exists():
        try:
            state = proc_stat.read_text(encoding="utf-8").split()[2]
            return state != "Z"
        except (OSError, IndexError):
            pass
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


class WorkGuardTests(unittest.TestCase):
    def test_success_streams_output_and_records_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runs"
            result = run_guard(root, ["--hard-timeout", "2"], child("-c", "print('hello-guard')"))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("hello-guard", result.stdout)
            summary = load_summary(root)
            self.assertEqual(summary["classification"], "success")
            self.assertEqual(len(summary["attempts"]), 1)
            self.assertEqual(summary["attempts"][0]["exit_code"], 0)

    def test_nonzero_child_exit_propagates_without_retry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runs"
            result = run_guard(root, ["--hard-timeout", "2"], child("-c", "import sys; sys.exit(7)"))
            self.assertEqual(result.returncode, 7)
            summary = load_summary(root)
            self.assertEqual(summary["classification"], "child-exit")
            self.assertEqual(len(summary["attempts"]), 1)
            self.assertEqual(summary["attempts"][0]["exit_code"], 7)

    def test_silent_stall_is_contained(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runs"
            started = time.monotonic()
            result = run_guard(
                root,
                ["--stall-timeout", "0.25", "--kill-grace", "0.1"],
                child("-c", "import time; time.sleep(5)"),
            )
            self.assertEqual(result.returncode, 124, result.stderr)
            self.assertLess(time.monotonic() - started, 3)
            summary = load_summary(root)
            self.assertEqual(summary["classification"], "stall-timeout")
            self.assertEqual(len(summary["attempts"]), 1)

    def test_noisy_process_still_hits_hard_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runs"
            code = "import time\nwhile True:\n print('tick', flush=True); time.sleep(0.05)"
            result = run_guard(
                root,
                ["--stall-timeout", "0.2", "--hard-timeout", "0.45", "--kill-grace", "0.1"],
                child("-c", code),
            )
            self.assertEqual(result.returncode, 124, result.stderr)
            self.assertIn("tick", result.stdout)
            self.assertEqual(load_summary(root)["classification"], "hard-timeout")

    def test_active_heartbeat_prevents_false_stall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "runs"
            heartbeat = tmp_path / "heartbeat"
            code = (
                "from pathlib import Path\nimport sys,time\n"
                "p=Path(sys.argv[1])\n"
                "for i in range(6): p.write_text(str(i)); time.sleep(0.1)"
            )
            result = run_guard(
                root,
                ["--stall-timeout", "0.25", "--hard-timeout", "2", "--heartbeat", str(heartbeat)],
                child("-c", code, str(heartbeat)),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(load_summary(root)["classification"], "success")

    def test_stale_heartbeat_allows_stall_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "runs"
            heartbeat = tmp_path / "heartbeat"
            code = (
                "from pathlib import Path\nimport sys,time\n"
                "Path(sys.argv[1]).write_text('once')\ntime.sleep(5)"
            )
            result = run_guard(
                root,
                ["--stall-timeout", "0.25", "--kill-grace", "0.1", "--heartbeat", str(heartbeat)],
                child("-c", code, str(heartbeat)),
            )
            self.assertEqual(result.returncode, 124, result.stderr)
            self.assertEqual(load_summary(root)["classification"], "stall-timeout")

    def test_safe_retry_can_recover_on_second_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "runs"
            state = tmp_path / "state"
            code = (
                "from pathlib import Path\nimport sys,time\n"
                "p=Path(sys.argv[1])\n"
                "if not p.exists(): p.write_text('first'); time.sleep(5)\n"
                "else: print('recovered', flush=True)"
            )
            result = run_guard(
                root,
                ["--stall-timeout", "0.25", "--kill-grace", "0.1", "--retry-safe", "1"],
                child("-c", code, str(state)),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("recovered", result.stdout)
            summary = load_summary(root)
            self.assertEqual(summary["classification"], "success")
            self.assertEqual([a["classification"] for a in summary["attempts"]], ["stall-timeout", "success"])

    def test_timeout_does_not_retry_without_explicit_safe_retry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "runs"
            state = tmp_path / "state"
            code = (
                "from pathlib import Path\nimport sys,time\n"
                "p=Path(sys.argv[1]); p.write_text(p.read_text()+'x' if p.exists() else 'x'); time.sleep(5)"
            )
            result = run_guard(
                root,
                ["--stall-timeout", "0.25", "--kill-grace", "0.1"],
                child("-c", code, str(state)),
            )
            self.assertEqual(result.returncode, 124, result.stderr)
            self.assertEqual(state.read_text(encoding="utf-8"), "x")
            self.assertEqual(len(load_summary(root)["attempts"]), 1)

    def test_probe_and_heal_hooks_are_logged_before_safe_retry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "runs"
            state = tmp_path / "state"
            healed = tmp_path / "healed"
            child_code = (
                "from pathlib import Path\nimport sys,time\n"
                "p=Path(sys.argv[1])\n"
                "if not p.exists(): p.write_text('first'); time.sleep(5)\n"
                "else: print('ok', flush=True)"
            )
            probe = shlex.join(child("-c", "print('probe-evidence')"))
            heal = shlex.join(child("-c", "from pathlib import Path; import sys; Path(sys.argv[1]).write_text('healed')", str(healed)))
            result = run_guard(
                root,
                [
                    "--stall-timeout", "0.25",
                    "--kill-grace", "0.1",
                    "--retry-safe", "1",
                    "--probe-command", probe,
                    "--heal-command", heal,
                    "--hook-timeout", "1",
                ],
                child("-c", child_code, str(state)),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(healed.read_text(encoding="utf-8"), "healed")
            run_dir = next(path for path in root.iterdir() if path.is_dir())
            self.assertIn("probe-evidence", (run_dir / "attempt-1.probe.log").read_text(encoding="utf-8"))
            self.assertTrue((run_dir / "attempt-1.heal.log").exists())

    @unittest.skipUnless(os.name == "posix" and Path("/proc").exists(), "requires POSIX /proc")
    def test_timeout_kills_owned_child_process_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "runs"
            pid_file = tmp_path / "grandchild.pid"
            code = (
                "import subprocess,sys,time\n"
                "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'])\n"
                "open(sys.argv[1],'w').write(str(p.pid))\n"
                "time.sleep(30)"
            )
            result = run_guard(
                root,
                ["--stall-timeout", "0.35", "--kill-grace", "0.1"],
                child("-c", code, str(pid_file)),
            )
            self.assertEqual(result.returncode, 124, result.stderr)
            pid = int(pid_file.read_text(encoding="utf-8"))
            deadline = time.monotonic() + 2
            while process_is_running(pid) and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertFalse(process_is_running(pid), f"grandchild {pid} survived containment")

    @unittest.skipUnless(os.name == "posix" and Path("/proc").exists(), "requires POSIX /proc")
    def test_ctrl_c_during_probe_contains_main_child_and_probe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "runs"
            child_pid_file = tmp_path / "child.pid"
            probe_pid_file = tmp_path / "probe.pid"
            child_code = (
                "import os,sys,time\n"
                "open(sys.argv[1],'w').write(str(os.getpid()))\n"
                "time.sleep(30)"
            )
            probe_code = (
                "import os,sys,time\n"
                "open(sys.argv[1],'w').write(str(os.getpid()))\n"
                "time.sleep(30)"
            )
            probe = shlex.join(child("-c", probe_code, str(probe_pid_file)))
            proc = subprocess.Popen(
                [
                    sys.executable,
                    str(SCRIPT),
                    "run",
                    "--run-root",
                    str(root),
                    "--stall-timeout",
                    "0.15",
                    "--hook-timeout",
                    "30",
                    "--kill-grace",
                    "0.1",
                    "--probe-command",
                    probe,
                    "--",
                    *child("-c", child_code, str(child_pid_file)),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            child_pid = None
            probe_pid = None
            try:
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    if child_pid_file.exists():
                        child_pid = int(child_pid_file.read_text(encoding="utf-8"))
                    if probe_pid_file.exists():
                        probe_pid = int(probe_pid_file.read_text(encoding="utf-8"))
                    if child_pid and probe_pid:
                        break
                    time.sleep(0.02)
                self.assertIsNotNone(child_pid, "main child did not start")
                self.assertIsNotNone(probe_pid, "probe did not start")
                proc.send_signal(signal.SIGINT)
                stdout, stderr = proc.communicate(timeout=4)
                self.assertEqual(proc.returncode, 130, stdout + stderr)

                for pid in (child_pid, probe_pid):
                    deadline = time.monotonic() + 2
                    while process_is_running(pid) and time.monotonic() < deadline:
                        time.sleep(0.05)
                    self.assertFalse(process_is_running(pid), f"process {pid} survived Ctrl+C containment")
                self.assertEqual(load_summary(root)["classification"], "interrupted")
            finally:
                for pid in (child_pid, probe_pid):
                    if pid and process_is_running(pid):
                        try:
                            os.kill(pid, signal.SIGKILL)
                        except OSError:
                            pass
                if proc.poll() is None:
                    proc.kill()
                    proc.wait(timeout=2)

    @unittest.skipUnless(os.name == "posix", "signal test requires POSIX")
    def test_ctrl_c_contains_child_and_exits_130(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runs"
            proc = subprocess.Popen(
                [
                    sys.executable,
                    str(SCRIPT),
                    "run",
                    "--run-root",
                    str(root),
                    "--kill-grace",
                    "0.1",
                    "--",
                    *child("-c", "import time; time.sleep(30)"),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            time.sleep(0.35)
            proc.send_signal(signal.SIGINT)
            stdout, stderr = proc.communicate(timeout=4)
            self.assertEqual(proc.returncode, 130, stdout + stderr)
            self.assertEqual(load_summary(root)["classification"], "interrupted")


if __name__ == "__main__":
    unittest.main()

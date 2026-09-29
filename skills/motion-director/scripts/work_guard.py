#!/usr/bin/env python3
"""Contain hangs around long-running motion-production commands.

The guard supervises one owned process group per attempt, preserves output and
metadata, and retries only when the caller explicitly marks the command safe.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import IO

TIMEOUT_EXIT = 124
INTERRUPT_EXIT = 130
LAUNCH_EXIT = 127


class Activity:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last = time.monotonic()

    def touch(self) -> None:
        with self._lock:
            self._last = time.monotonic()

    def age(self) -> float:
        with self._lock:
            return time.monotonic() - self._last


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def heartbeat_signature(path: Path | None) -> tuple[int, int] | None:
    if path is None:
        return None
    try:
        stat = path.stat()
    except OSError:
        return None
    return stat.st_mtime_ns, stat.st_size


def stream_pipe(
    source: IO[bytes],
    log: IO[bytes],
    target: IO[bytes],
    activity: Activity,
) -> None:
    try:
        while True:
            chunk = os.read(source.fileno(), 4096)
            if not chunk:
                break
            log.write(chunk)
            log.flush()
            target.write(chunk)
            target.flush()
            activity.touch()
    finally:
        try:
            source.close()
        except OSError:
            pass


def process_group_kwargs() -> dict:
    if os.name == "posix":
        return {"start_new_session": True}
    flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    return {"creationflags": flags} if flags else {}


def signal_process_group(proc: subprocess.Popen[bytes], sig: int) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(proc.pid, sig)
        elif sig == signal.SIGTERM:
            proc.terminate()
        else:
            proc.kill()
    except (ProcessLookupError, PermissionError, OSError):
        pass


def terminate_process_group(proc: subprocess.Popen[bytes], grace: float) -> None:
    if proc.poll() is not None:
        return
    signal_process_group(proc, signal.SIGTERM)
    try:
        proc.wait(timeout=max(0.0, grace))
        return
    except subprocess.TimeoutExpired:
        pass
    kill_signal = getattr(signal, "SIGKILL", signal.SIGTERM)
    signal_process_group(proc, kill_signal)
    try:
        proc.wait(timeout=max(0.1, grace))
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass


def run_hook(command: str, log_path: Path, timeout: float) -> dict:
    result = {
        "command": [],
        "started_at": utc_now(),
        "timed_out": False,
        "exit_code": None,
    }
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        result["exit_code"] = 2
        result["error"] = str(exc)
        log_path.write_text(f"parse error: {exc}\n", encoding="utf-8")
        return result
    result["command"] = argv
    if not argv:
        result["exit_code"] = 2
        log_path.write_text("empty hook command\n", encoding="utf-8")
        return result

    if timeout <= 0:
        raise ValueError("hook timeout must be > 0")

    started = time.monotonic()
    try:
        proc = subprocess.Popen(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            **process_group_kwargs(),
        )
    except OSError as exc:
        result["exit_code"] = LAUNCH_EXIT
        log_path.write_text(f"launch error: {exc}\n", encoding="utf-8")
        result["duration_seconds"] = round(time.monotonic() - started, 3)
        return result

    try:
        output, _ = proc.communicate(timeout=timeout)
        result["exit_code"] = proc.returncode
    except subprocess.TimeoutExpired:
        result["timed_out"] = True
        terminate_process_group(proc, 0.25)
        output, _ = proc.communicate()
        result["exit_code"] = TIMEOUT_EXIT
    except KeyboardInterrupt:
        terminate_process_group(proc, 0.25)
        output, _ = proc.communicate()
        log_path.write_bytes(output or b"")
        raise

    log_path.write_bytes(output or b"")
    result["duration_seconds"] = round(time.monotonic() - started, 3)
    return result


def make_run_dir(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    candidate = root / f"{stamp}-{os.getpid()}"
    suffix = 1
    while candidate.exists():
        candidate = root / f"{stamp}-{os.getpid()}-{suffix}"
        suffix += 1
    candidate.mkdir(parents=True)
    return candidate


def attempt_command(
    command: list[str],
    attempt: int,
    run_dir: Path,
    stall_timeout: float,
    hard_timeout: float,
    heartbeat: Path | None,
    probe_command: str | None,
    hook_timeout: float,
    kill_grace: float,
) -> dict:
    stdout_path = run_dir / f"attempt-{attempt}.stdout.log"
    stderr_path = run_dir / f"attempt-{attempt}.stderr.log"
    record = {
        "attempt": attempt,
        "started_at": utc_now(),
        "classification": None,
        "exit_code": None,
    }
    started = time.monotonic()
    activity = Activity()
    previous_heartbeat = heartbeat_signature(heartbeat)

    with stdout_path.open("wb") as stdout_log, stderr_path.open("wb") as stderr_log:
        try:
            proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                **process_group_kwargs(),
            )
        except OSError as exc:
            record.update(
                classification="launch-error",
                exit_code=LAUNCH_EXIT,
                error=str(exc),
                duration_seconds=round(time.monotonic() - started, 3),
                finished_at=utc_now(),
            )
            write_json(run_dir / f"attempt-{attempt}.json", record)
            return record

        assert proc.stdout is not None
        assert proc.stderr is not None
        out_thread = threading.Thread(
            target=stream_pipe,
            args=(proc.stdout, stdout_log, getattr(sys.stdout, "buffer"), activity),
            daemon=True,
        )
        err_thread = threading.Thread(
            target=stream_pipe,
            args=(proc.stderr, stderr_log, getattr(sys.stderr, "buffer"), activity),
            daemon=True,
        )
        out_thread.start()
        err_thread.start()

        classification: str | None = None
        try:
            while proc.poll() is None:
                current_heartbeat = heartbeat_signature(heartbeat)
                if current_heartbeat is not None and current_heartbeat != previous_heartbeat:
                    previous_heartbeat = current_heartbeat
                    activity.touch()

                elapsed = time.monotonic() - started
                if hard_timeout > 0 and elapsed >= hard_timeout:
                    classification = "hard-timeout"
                    break
                if stall_timeout > 0 and activity.age() >= stall_timeout:
                    classification = "stall-timeout"
                    break
                time.sleep(0.02)
        except KeyboardInterrupt:
            classification = "interrupted"

        if classification in {"stall-timeout", "hard-timeout"} and probe_command:
            try:
                record["probe"] = run_hook(
                    probe_command,
                    run_dir / f"attempt-{attempt}.probe.log",
                    hook_timeout,
                )
            except KeyboardInterrupt:
                classification = "interrupted"

        if classification is not None:
            terminate_process_group(proc, kill_grace)
        else:
            proc.wait()

        out_thread.join(timeout=1)
        err_thread.join(timeout=1)

        child_code = proc.returncode
        if classification == "interrupted":
            exit_code = INTERRUPT_EXIT
        elif classification in {"stall-timeout", "hard-timeout"}:
            exit_code = TIMEOUT_EXIT
        elif child_code == 0:
            classification = "success"
            exit_code = 0
        else:
            classification = "child-exit"
            exit_code = int(child_code if child_code is not None else LAUNCH_EXIT)

        record.update(
            classification=classification,
            exit_code=exit_code,
            child_exit_code=child_code,
            duration_seconds=round(time.monotonic() - started, 3),
            finished_at=utc_now(),
        )
        write_json(run_dir / f"attempt-{attempt}.json", record)
        return record


def run_guard(args: argparse.Namespace) -> int:
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise ValueError("a command is required after --")
    if args.retry_safe < 0:
        raise ValueError("--retry-safe must be >= 0")
    for name in ("stall_timeout", "hard_timeout", "kill_grace"):
        if getattr(args, name) < 0:
            raise ValueError(f"--{name.replace('_', '-')} must be >= 0")
    if args.hook_timeout <= 0:
        raise ValueError("--hook-timeout must be > 0")

    run_dir = make_run_dir(Path(args.run_root))
    heartbeat = Path(args.heartbeat) if args.heartbeat else None
    write_json(
        run_dir / "command.json",
        {
            "command": command,
            "created_at": utc_now(),
            "stall_timeout": args.stall_timeout,
            "hard_timeout": args.hard_timeout,
            "retry_safe": args.retry_safe,
            "heartbeat": str(heartbeat) if heartbeat else None,
            "probe_command": args.probe_command,
            "heal_command": args.heal_command,
        },
    )

    attempts = []
    final_code = LAUNCH_EXIT
    final_class = "launch-error"
    try:
        for attempt in range(1, args.retry_safe + 2):
            record = attempt_command(
                command=command,
                attempt=attempt,
                run_dir=run_dir,
                stall_timeout=args.stall_timeout,
                hard_timeout=args.hard_timeout,
                heartbeat=heartbeat,
                probe_command=args.probe_command,
                hook_timeout=args.hook_timeout,
                kill_grace=args.kill_grace,
            )
            attempts.append(record)
            final_code = int(record["exit_code"])
            final_class = str(record["classification"])

            if final_class == "interrupted":
                break
            if final_class not in {"stall-timeout", "hard-timeout"}:
                break
            if attempt > args.retry_safe:
                break

            if args.heal_command:
                heal = run_hook(
                    args.heal_command,
                    run_dir / f"attempt-{attempt}.heal.log",
                    args.hook_timeout,
                )
                record["heal"] = heal
                write_json(run_dir / f"attempt-{attempt}.json", record)
                if heal["exit_code"] != 0:
                    break
    except KeyboardInterrupt:
        final_code = INTERRUPT_EXIT
        final_class = "interrupted"

    write_json(
        run_dir / "summary.json",
        {
            "classification": final_class,
            "exit_code": final_code,
            "attempt_count": len(attempts),
            "attempts": attempts,
            "finished_at": utc_now(),
        },
    )
    return final_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Contain hangs around long-running motion commands.")
    sub = parser.add_subparsers(dest="subcommand", required=True)

    run = sub.add_parser("run", help="run one command under the guard")
    run.add_argument("--stall-timeout", type=float, default=0.0, help="seconds without output/heartbeat before containment; 0 disables")
    run.add_argument("--hard-timeout", type=float, default=0.0, help="absolute seconds per attempt; 0 disables")
    run.add_argument("--heartbeat", help="file whose mtime/size changes count as progress")
    run.add_argument("--probe-command", help="diagnostic command to run on timeout before containment")
    run.add_argument("--heal-command", help="recovery command to run after containment and before a safe retry")
    run.add_argument("--hook-timeout", type=float, default=15.0, help="maximum seconds for probe/heal hooks; must be > 0")
    run.add_argument("--kill-grace", type=float, default=2.0, help="seconds between TERM and KILL")
    run.add_argument("--retry-safe", nargs="?", const=1, type=int, default=0, help="explicitly declare the command safe and allow N retries; bare flag means one retry")
    run.add_argument("--run-root", default=".motion-guard/runs", help="directory that receives run evidence")
    run.add_argument("command", nargs=argparse.REMAINDER)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.subcommand != "run":
        parser.error("unsupported subcommand")
    try:
        return run_guard(args)
    except ValueError as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

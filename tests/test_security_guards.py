"""Unit and regression tests for security guards and script resilience."""
import unittest
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SecurityGuardsTests(unittest.TestCase):
    def test_lufs_check_nonexistent_file_exits_one(self):
        script = ROOT / "tools/scripts/lufs-check.py"
        res = subprocess.run(
            [sys.executable, str(script), "nonexistent_file.mp4"],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 1)
        self.assertIn("does not exist", res.stderr)

    def test_seek_assets_downloader_rejects_unsafe_scheme(self):
        sys.path.insert(0, str(ROOT / "skills/assetseeker/scripts"))
        from seek_assets import _download_file
        # Test file scheme rejection (SSRF / local disclosure prevention)
        self.assertFalse(_download_file("file:///etc/passwd", "/tmp/passwd_leak"))
        # Test metadata IP rejection
        self.assertFalse(_download_file("http://169.254.169.254/latest/meta-data/", "/tmp/meta"))
        self.assertFalse(_download_file("http://metadata.google.internal/computeMetadata/v1/", "/tmp/gcp_meta"))

    def test_openreview_config_invariants(self):
        config_path = ROOT / "openreview.config.json"
        self.assertTrue(config_path.exists(), "openreview.config.json must exist")
        import json
        data = json.loads(config_path.read_text())
        self.assertLessEqual(data["llm"]["max_steps"], 50)
        self.assertLessEqual(data["llm"]["max_tokens"], 500000)
        self.assertIn(data["sandbox"]["driver"], ["local", "docker"])

    def test_validate_assets_hook_syntax(self):
        hook = ROOT / ".claude/hooks/validate-assets.sh"
        res = subprocess.run(["bash", "-n", str(hook)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, hook)

    def test_validate_commit_hook_syntax(self):
        hook = ROOT / ".claude/hooks/validate-commit.sh"
        res = subprocess.run(["bash", "-n", str(hook)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, hook)

if __name__ == "__main__":
    unittest.main()

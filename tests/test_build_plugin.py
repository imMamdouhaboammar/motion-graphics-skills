"""Check the archive boundary and repeatable package identity."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from tools import build_plugin


class PluginBuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "source"
        for directory in [".codex-plugin", "skills/demo", "assets/plugin", "docs/plugin", "projects", ".git"]:
            (self.root / directory).mkdir(parents=True)
        for path, text in {
            "plugin.json": json.dumps({"version": "1.0.0"}),
            ".codex-plugin/plugin.json": "{}",
            "LICENSE": "test license",
            "skills/demo/SKILL.md": "---\nname: demo\ndescription: Use when testing\n---\nTest",
            "projects/private-video.mp4": "private",
            ".git/config": "private",
        }.items():
            (self.root / path).write_text(text)
        self.override = patch.object(build_plugin, "ROOT", self.root)
        self.override.start()
        self.addCleanup(self.override.stop)

    def test_identity_is_repeatable_and_excludes_project_and_git_files(self):
        first = build_plugin.build(self.base / "first.zip")
        second = build_plugin.build(self.base / "second.zip")
        self.assertEqual(first["sha256"], second["sha256"])
        with ZipFile(first["archive"]) as archive:
            self.assertEqual(sorted(archive.namelist()), [
                ".codex-plugin/plugin.json", "LICENSE", "plugin.json", "skills/demo/SKILL.md"])

    def test_existing_output_is_preserved(self):
        output = self.base / "existing.zip"
        output.write_bytes(b"existing user data")
        with self.assertRaises(ValueError):
            build_plugin.build(output)
        self.assertEqual(output.read_bytes(), b"existing user data")

    def test_symlink_rejected_before_an_archive_is_created(self):
        (self.root / "skills/demo/escape").symlink_to(self.root / "LICENSE")
        output = self.base / "symlink.zip"
        with self.assertRaises(ValueError):
            build_plugin.build(output)
        self.assertFalse(output.exists())

    def test_output_inside_packaged_sources_is_rejected(self):
        output = self.root / "skills/demo/self.zip"
        with self.assertRaises(ValueError):
            build_plugin.build(output)
        self.assertFalse(output.exists())

    def test_secret_shaped_file_is_rejected(self):
        (self.root / "skills/demo/.env").write_text("secret fixture")
        output = self.base / "secret.zip"
        with self.assertRaises(ValueError):
            build_plugin.build(output)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()

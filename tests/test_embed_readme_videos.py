"""Regression tests for real GitHub attachment embeds in README."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.embed_readme_videos import render, validate_manifest

EXAMPLE = """<!-- readme-video:arabic:start -->
  <a href="projects/mgs-promo/renders/mgs-promo-final.mp4"><img src="poster.png"></a>
  <!-- readme-video:arabic:end -->"""

URL = "https://github.com/user-attachments/assets/95f6dc55-5fce-4661-b5df-8043f32cb359"


class ReadmeVideoTests(unittest.TestCase):
    def test_accepts_only_real_github_attachment_hosts(self):
        self.assertEqual(validate_manifest({"arabic": URL}), {"arabic": URL})
        with self.assertRaises(ValueError):
            validate_manifest({"arabic": "https://raw.githubusercontent.com/user/repo/main/film.mp4"})
        with self.assertRaises(ValueError):
            validate_manifest({"arabic": "https://github.com.evil.test/user-attachments/assets/95f6dc55-5fce-4661-b5df-8043f32cb359"})

    def test_rejects_markup_injection_and_unknown_ids(self):
        with self.assertRaises(ValueError):
            validate_manifest({"arabic": URL + "' onload='alert(1)"})
        with self.assertRaises(ValueError):
            validate_manifest({"not-a-film": URL})

    def test_replaces_thumbnail_with_full_length_embedded_player(self):
        output = render(EXAMPLE, {"arabic": URL})
        self.assertIn('<video src="' + URL + '"', output)
        self.assertIn('controls', output)
        self.assertIn('preload="metadata"', output)
        self.assertIn('width="300"', output)
        self.assertNotIn('src="poster.png"', output)
        self.assertIn('readme-video:arabic:start', output)

    def test_idempotent(self):
        once = render(EXAMPLE, {"arabic": URL})
        self.assertEqual(render(once, {"arabic": URL}), once)

    def test_refuses_missing_or_duplicated_slots(self):
        with self.assertRaises(ValueError):
            render("README has no slots", {"arabic": URL})
        with self.assertRaises(ValueError):
            render(EXAMPLE + "\n" + EXAMPLE, {"arabic": URL})

    def test_all_six_final_files_are_listed(self):
        readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
        for film in ("arabic", "curve", "countdown", "teola", "four-steps", "jedar"):
            self.assertEqual(readme.count(f"<!-- readme-video:{film}:start -->"), 1)
            self.assertEqual(readme.count(f"<!-- readme-video:{film}:end -->"), 1)


if __name__ == "__main__":
    unittest.main()

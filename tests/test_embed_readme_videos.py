"""Regression tests for real GitHub attachment embeds in README."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.embed_readme_videos import render, validate_manifest
from tools.publish_readme_videos import FILMS, parse_comment, locate_uploaded_comment, validate_delivery_probe

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
        self.assertIn("\n\n" + URL + "\n\n", output)
        self.assertNotIn("<video", output)
        self.assertNotIn("![", output)
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

    def test_parse_full_video_uploads_preserves_film_identity(self):
        marker = "README_VIDEO_BATCH_test"
        body = "Full-length README promo assets: " + marker + "\n\n"
        for index, film in enumerate(FILMS):
            body += (
                f"### {film}\n\n"
                f"https://github.com/user-attachments/assets/"
                f"00000000-0000-0000-0000-{index+1:012x}\n\n"
            )
        result = parse_comment(body, marker)
        self.assertEqual(len(result), 6)
        self.assertTrue(result["arabic"].endswith("000000000001"))
        self.assertTrue(result["jedar"].endswith("000000000006"))

    def test_parser_rejects_unmatched_upload_comment(self):
        with self.assertRaises(ValueError):
            parse_comment("### arabic\n\nhttps://github.com/user-attachments/assets/"
                          "95f6dc55-5fce-4661-b5df-8043f32cb359", "missing-marker")

    def test_find_upload_marker_in_paginated_comments(self):
        marker = "README_VIDEO_BATCH_unique"
        first_page = [
            {"body": "unrelated bot comment " + str(index)}
            for index in range(100)
        ]
        later = [{"body": "six uploaded videos " + marker}]
        ndjson = "\n".join(__import__("json").dumps(comment) for comment in first_page + later)
        match = locate_uploaded_comment(ndjson, marker)
        self.assertIn(marker, match)

    def test_accepts_cli_quoted_json_comment_format(self):
        marker = "README_VIDEO_BATCH_quoted"
        item = {"body": "upload found " + marker}
        quoted = json.dumps(json.dumps(item))
        self.assertIn(marker, locate_uploaded_comment(quoted, marker))

    def test_missing_or_duplicated_upload_marker_fails_closed(self):
        marker = "README_VIDEO_BATCH_unique"
        with self.assertRaises(ValueError):
            locate_uploaded_comment('{"body": "not our upload"}', marker)
        with self.assertRaises(ValueError):
            locate_uploaded_comment('{"body": "' + marker + '"}\n{"body": "' + marker + '"}', marker)

    def test_rejects_truncated_delivery_after_video_encoding(self):
        source = {"format": {"duration": "52.0"}, "streams": [{"codec_type": "video"}, {"codec_type": "audio"}]}
        delivery = {"format": {"duration": "31.0"}, "streams": [{"codec_type": "video"}, {"codec_type": "audio"}]}
        with self.assertRaisesRegex(ValueError, "duration"):
            validate_delivery_probe(source, delivery, "countdown")

    def test_rejects_delivery_that_loses_original_audio(self):
        source = {"format": {"duration": "26.6"}, "streams": [{"codec_type": "video"}, {"codec_type": "audio"}]}
        delivery = {"format": {"duration": "26.6"}, "streams": [{"codec_type": "video"}]}
        with self.assertRaisesRegex(ValueError, "audio"):
            validate_delivery_probe(source, delivery, "arabic")

    def test_accepts_full_length_delivery_with_preserved_audio(self):
        source = {"format": {"duration": "59.0"}, "streams": [{"codec_type": "video"}, {"codec_type": "audio"}]}
        delivery = {"format": {"duration": "58.94"}, "streams": [{"codec_type": "video"}, {"codec_type": "audio"}]}
        validate_delivery_probe(source, delivery, "jedar")

    def test_rejects_delivery_that_has_no_video(self):
        source = {"format": {"duration": "30"}, "streams": [{"codec_type": "video"}, {"codec_type": "audio"}]}
        delivery = {"format": {"duration": "30"}, "streams": [{"codec_type": "audio"}]}
        with self.assertRaisesRegex(ValueError, "video"):
            validate_delivery_probe(source, delivery, "curve")

    def test_all_six_final_files_are_listed(self):
        readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
        for film in ("arabic", "curve", "countdown", "teola", "four-steps", "jedar"):
            self.assertEqual(readme.count(f"<!-- readme-video:{film}:start -->"), 1)
            self.assertEqual(readme.count(f"<!-- readme-video:{film}:end -->"), 1)
        showcase = readme.split("## Watch the work", 1)[1].split("## Install", 1)[0]
        self.assertNotIn("<table>", showcase)
        self.assertEqual(showcase.count("<!-- readme-video:"), 12)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("review_video.py")


def load_module():
    spec = importlib.util.spec_from_file_location("review_video", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load review_video")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VideoReviewTests(unittest.TestCase):
    def test_probe_analysis_catches_delivery_mismatches_and_av_drift(self) -> None:
        review = load_module()
        probe = {
            "format": {"duration": "10.000"},
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1080,
                    "height": 1920,
                    "avg_frame_rate": "25/1",
                    "r_frame_rate": "25/1",
                    "pix_fmt": "yuv420p",
                    "duration": "10.000",
                },
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "duration": "9.650",
                    "sample_rate": "48000",
                    "channels": 2,
                },
            ],
        }
        findings, technical = review.analyze_probe(
            probe,
            {
                "width": 1080,
                "height": 1920,
                "fps": 30.0,
                "duration": 10.0,
                "duration_tolerance": 0.1,
                "expect_audio": True,
            },
        )
        codes = {item["code"]: item["severity"] for item in findings}
        self.assertEqual(codes["frame-rate-mismatch"], "hard")
        self.assertEqual(codes["audio-video-duration-drift"], "hard")
        self.assertEqual(technical["video"]["width"], 1080)
        self.assertEqual(technical["audio"]["codec"], "aac")

    def test_probe_analysis_catches_missing_expected_audio(self) -> None:
        review = load_module()
        probe = {
            "format": {"duration": "4.0"},
            "streams": [
                {
                    "codec_type": "video",
                    "width": 720,
                    "height": 1280,
                    "avg_frame_rate": "25/1",
                    "r_frame_rate": "25/1",
                }
            ],
        }
        findings, _ = review.analyze_probe(probe, {"expect_audio": True})
        self.assertIn(
            ("audio-missing", "hard"),
            {(item["code"], item["severity"]) for item in findings},
        )

    def test_parse_blackdetect(self) -> None:
        review = load_module()
        intervals = review.parse_blackdetect(
            "x\n[blackdetect @ a] black_start:0 black_end:0.12 black_duration:0.12\n"
            "[blackdetect @ a] black_start:5.5 black_end:6.1 black_duration:0.6\n"
        )
        self.assertEqual(intervals, [
            {"start": 0.0, "end": 0.12, "duration": 0.12},
            {"start": 5.5, "end": 6.1, "duration": 0.6},
        ])

    def test_parse_freezedetect_pairs_start_duration_and_end(self) -> None:
        review = load_module()
        intervals = review.parse_freezedetect(
            "[freezedetect @ x] lavfi.freezedetect.freeze_start: 8.7\n"
            "[freezedetect @ x] lavfi.freezedetect.freeze_duration: 1.3\n"
            "[freezedetect @ x] lavfi.freezedetect.freeze_end: 10.0\n"
        )
        self.assertEqual(intervals, [{"start": 8.7, "end": 10.0, "duration": 1.3}])

    def test_parse_silencedetect(self) -> None:
        review = load_module()
        intervals = review.parse_silencedetect(
            "[silencedetect @ x] silence_start: 2.0\n"
            "[silencedetect @ x] silence_end: 3.25 | silence_duration: 1.25\n"
        )
        self.assertEqual(intervals, [{"start": 2.0, "end": 3.25, "duration": 1.25}])

    def test_parse_max_volume_flags_clipping_risk(self) -> None:
        review = load_module()
        self.assertEqual(review.parse_max_volume("[volumedetect @ x] max_volume: -0.0 dB"), 0.0)
        finding = review.volume_finding(0.0)
        self.assertEqual(finding["code"], "audio-clipping-risk")
        self.assertEqual(finding["severity"], "warning")

    def test_expected_end_hold_requires_tail_freeze_evidence(self) -> None:
        review = load_module()
        ok = review.end_hold_finding(
            freezes=[{"start": 8.7, "end": 10.0, "duration": 1.3}],
            video_duration=10.0,
            expected_hold=1.0,
        )
        self.assertIsNone(ok)

        missing = review.end_hold_finding(
            freezes=[],
            video_duration=10.0,
            expected_hold=1.0,
        )
        self.assertEqual(missing["severity"], "hard")
        self.assertEqual(missing["code"], "end-hold-not-proven")

    def test_gpu_gate_blocks_implicit_cpu_fallback(self) -> None:
        review = load_module()
        code, result = review.gpu_gate(
            {
                "os": "Linux",
                "ffmpeg_hwaccels": [],
                "nvidia_smi": False,
                "vaapi_devices": [],
            },
            allow_cpu=False,
        )
        self.assertEqual(code, 3)
        self.assertEqual(result["decision"], "blocked")

    def test_gpu_gate_allows_cpu_only_when_explicit(self) -> None:
        review = load_module()
        code, result = review.gpu_gate(
            {
                "os": "Linux",
                "ffmpeg_hwaccels": [],
                "nvidia_smi": False,
                "vaapi_devices": [],
            },
            allow_cpu=True,
        )
        self.assertEqual(code, 0)
        self.assertEqual(result["decision"], "cpu-fallback-explicit")

    def test_review_paths_are_private_round_artifacts(self) -> None:
        review = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / ".motion-review" / "rounds"
            paths = review.create_round_paths(root, Path("/tmp/My Film.mp4"))
            self.assertTrue(paths["round_dir"].is_dir())
            self.assertTrue(paths["evidence_dir"].is_dir())
            self.assertTrue((root.parent / ".gitignore").exists())
            self.assertEqual(
                (root.parent / ".gitignore").read_text(encoding="utf-8"),
                "*\n!.gitignore\n",
            )

    def test_reference_contract_produces_review_checklist(self) -> None:
        review = load_module()
        contract = {
            "mode": "structural-fidelity",
            "difficulty_mode": "preserve",
            "must_preserve": [
                {
                    "id": "world-flips",
                    "mechanism": "hard light and dark world resets on major cuts",
                    "evidence": "major cut frames",
                },
                {
                    "id": "object-scale",
                    "mechanism": "oversized intentionally cropped focal object per shot",
                    "evidence": "contact sheet",
                },
            ],
        }
        items = review.reference_checklist(contract)
        self.assertEqual([item["id"] for item in items], ["world-flips", "object-scale"])
        self.assertTrue(all(item["required"] for item in items))

    def test_reference_comparison_times_are_normalized(self) -> None:
        review = load_module()
        self.assertEqual(
            review.normalized_sample_times(10.0, 5),
            [0.0, 2.5, 5.0, 7.5, 9.96],
        )
        self.assertEqual(review.normalized_sample_times(None, 5), [])

    def test_malformed_detector_logs_do_not_crash(self) -> None:
        review = load_module()
        self.assertEqual(review.parse_blackdetect("garbage"), [])
        self.assertEqual(review.parse_freezedetect("garbage"), [])
        self.assertEqual(review.parse_silencedetect("garbage"), [])
        self.assertIsNone(review.parse_max_volume("garbage"))


    def test_parse_freezedetect_flushes_open_tail_freeze_at_video_end(self) -> None:
        review = load_module()
        intervals = review.parse_freezedetect(
            "[freezedetect @ x] lavfi.freezedetect.freeze_start: 8.7\n"
            "[freezedetect @ x] lavfi.freezedetect.freeze_duration: 1.3\n",
            video_duration=10.0,
        )
        self.assertEqual(intervals, [{"start": 8.7, "end": 10.0, "duration": 1.3}])
        self.assertIsNone(
            review.end_hold_finding(
                freezes=intervals,
                video_duration=10.0,
                expected_hold=1.0,
            )
        )

    def test_custom_round_root_does_not_write_blanket_ignore_to_parent(self) -> None:
        review = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            root = project / "reviews"
            review.create_round_paths(root, Path("/tmp/My Film.mp4"))

            parent_gitignore = project / ".gitignore"
            self.assertFalse(parent_gitignore.exists())

            local_gitignore = root / ".gitignore"
            self.assertTrue(local_gitignore.exists())
            self.assertEqual(
                local_gitignore.read_text(encoding="utf-8"),
                "*\n!.gitignore\n",
            )

    def test_custom_round_root_appends_rules_to_existing_gitignore(self) -> None:
        review = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            root = project / "reviews"
            root.mkdir(parents=True)
            local_gitignore = root / ".gitignore"
            local_gitignore.write_text("*.notes\n", encoding="utf-8")

            paths = review.create_round_paths(root, Path("/tmp/My Film.mp4"))
            self.assertTrue(paths["round_dir"].is_dir())

            content = local_gitignore.read_text(encoding="utf-8")
            self.assertIn("*.notes", content)
            self.assertIn("[0-9]*T*Z-*", content)
            self.assertIn("*.log", content)
            self.assertIn("manifest.json", content)


    def test_video_analysis_failure_is_a_hard_blocker(self) -> None:
        review = load_module()
        finding = review.video_analysis_failure_finding()
        self.assertEqual(finding["code"], "video-analysis-pass-failed")
        self.assertEqual(finding["severity"], "hard")

    def test_run_command_timeout_returns_failed_process_and_writes_log(self) -> None:
        review = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            log_file = Path(tmp) / "timed_out.log"
            res = review.run_command(["sleep", "1"], timeout=0.01, log_path=log_file)
            self.assertEqual(res.returncode, 124)
            self.assertIn("Command timed out", log_file.read_text(encoding="utf-8"))

    def test_reference_contract_requires_reference_video(self) -> None:
        review = load_module()
        with self.assertRaises(review.ReviewError):
            review.validate_reference_inputs(
                reference=None,
                reference_contract=Path("/tmp/reference-contract.json"),
            )


    def test_reference_contract_must_bind_to_actual_reference_video(self) -> None:
        review = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract_path = root / "reference-contract.json"
            reference_a = root / "reference-a.mp4"
            reference_b = root / "reference-b.mp4"
            reference_a.write_bytes(b"a")
            reference_b.write_bytes(b"b")
            contract = {
                "reference": {
                    "source": "reference-a.mp4"
                }
            }
            review.validate_reference_contract_binding(
                reference_a,
                contract_path,
                contract,
            )
            with self.assertRaises(review.ReviewError):
                review.validate_reference_contract_binding(
                    reference_b,
                    contract_path,
                    contract,
                )


    def test_audio_analysis_failure_is_hard_when_expect_audio_set(self) -> None:
        review = load_module()
        # analyze_probe must flag missing audio as hard when expect_audio=True
        probe_no_audio = {
            "format": {"duration": "10.000"},
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                    "avg_frame_rate": "25/1",
                    "r_frame_rate": "25/1",
                    "duration": "10.000",
                }
            ],
        }
        findings, _ = review.analyze_probe(probe_no_audio, {"expect_audio": True})
        codes = [f["code"] for f in findings]
        self.assertIn("audio-missing", codes)
        hard = [f for f in findings if f["code"] == "audio-missing"]
        self.assertEqual(hard[0]["severity"], "hard")

    def test_reference_with_no_video_stream_emits_reference_unusable(self) -> None:
        review = load_module()
        # analyze_probe on a reference that has no video stream returns video-stream-missing (hard)
        probe_no_video = {
            "format": {"duration": "5.000"},
            "streams": [
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "duration": "5.000",
                    "sample_rate": "48000",
                    "channels": 2,
                }
            ],
        }
        ref_findings, _ = review.analyze_probe(probe_no_video, {})
        ref_hard = [f for f in ref_findings if f.get("severity") == "hard"]
        self.assertTrue(len(ref_hard) >= 1)
        codes = {f["code"] for f in ref_hard}
        self.assertIn("video-stream-missing", codes)


if __name__ == "__main__":
    unittest.main()

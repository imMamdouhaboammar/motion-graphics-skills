#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("strict_video_signals.py")


def load_module():
    spec = importlib.util.spec_from_file_location("strict_video_signals", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load strict_video_signals")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StrictVideoSignalTests(unittest.TestCase):
    def test_parse_signalstats_groups_metadata_by_frame(self) -> None:
        mod = load_module()
        frames = mod.parse_signalstats(
            "frame:0 pts:0 pts_time:0.000\n"
            "lavfi.signalstats.YAVG=42\n"
            "lavfi.signalstats.SATAVG=12\n"
            "frame:1 pts:1 pts_time:0.040\n"
            "lavfi.signalstats.YAVG=80\n"
        )
        self.assertEqual(frames[0]["frame"], 0)
        self.assertEqual(frames[0]["YAVG"], 42.0)
        self.assertEqual(frames[1]["time"], 0.04)

    def test_detects_single_frame_flash_that_returns_to_neighbor_level(self) -> None:
        mod = load_module()
        frames = [
            {"frame": 0, "time": 0.0, "YAVG": 40.0},
            {"frame": 1, "time": 0.04, "YAVG": 78.0},
            {"frame": 2, "time": 0.08, "YAVG": 43.0},
        ]
        findings = mod.detect_one_frame_flashes(frames)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["code"], "one-frame-luma-flash")

    def test_does_not_call_sustained_scene_change_a_one_frame_flash(self) -> None:
        mod = load_module()
        frames = [
            {"frame": 0, "time": 0.0, "YAVG": 40.0},
            {"frame": 1, "time": 0.04, "YAVG": 78.0},
            {"frame": 2, "time": 0.08, "YAVG": 80.0},
        ]
        self.assertEqual(mod.detect_one_frame_flashes(frames), [])

    def test_flags_extreme_frame_to_frame_luma_changes_for_review(self) -> None:
        mod = load_module()
        frames = [
            {"frame": 0, "time": 0.0, "YAVG": 20.0},
            {"frame": 1, "time": 0.04, "YAVG": 80.0},
        ]
        findings = mod.detect_extreme_luma_changes(frames)
        self.assertEqual(findings[0]["severity"], "review")


    def test_signalstats_command_places_gpu_input_args_before_input(self) -> None:
        mod = load_module()
        argv = mod.signalstats_argv(
            Path("/tmp/final.mp4"),
            "ffmpeg",
            ["-hwaccel", "videotoolbox"],
        )
        input_index = argv.index("-i")
        self.assertLess(argv.index("-hwaccel"), input_index)
        self.assertEqual(argv[input_index + 1], "/tmp/final.mp4")
        self.assertIn("signalstats,metadata=print", argv)

    def test_signalstats_command_supports_explicit_cpu_path(self) -> None:
        mod = load_module()
        argv = mod.signalstats_argv(Path("/tmp/final.mp4"), "ffmpeg", [])
        self.assertEqual(argv[:3], ["ffmpeg", "-hide_banner", "-i"])

    def test_run_audit_retries_on_cpu_when_hardware_decode_fails_and_allow_cpu_is_true(self) -> None:
        from unittest.mock import patch
        mod = load_module()
        gpu_decision = {
            "decision": "gpu",
            "backend": "videotoolbox",
            "gpu": {
                "ffmpeg_input_args": ["-hwaccel", "videotoolbox"],
                "verification": "unverified",
            },
        }

        call_args_list = []

        def fake_analyze(video, ffmpeg_bin, input_args=None):
            call_args_list.append(input_args)
            if input_args:
                raise RuntimeError("Hardware decode failed for codec")
            return {
                "status": "pass",
                "findings": [],
                "frames_analyzed": 10,
                "source": str(video),
            }

        with patch.object(mod, "resolve_gpu", return_value=(gpu_decision, ["-hwaccel", "videotoolbox"])):
            with patch.object(mod, "analyze", side_effect=fake_analyze):
                result = mod.run_audit(Path("/tmp/test.mp4"), allow_cpu=True)
                self.assertEqual(len(call_args_list), 2)
                self.assertEqual(call_args_list[0], ["-hwaccel", "videotoolbox"])
                self.assertIsNone(call_args_list[1])
                self.assertEqual(result["gpu"]["decision"], "cpu-fallback-explicit")
                self.assertEqual(
                    result["gpu"]["reason"],
                    "gpu-backend-detected-but-media-decode-failed",
                )
                self.assertEqual(result["gpu"]["gpu"]["verification"], "media-decode-failed")

    def test_run_audit_does_not_retry_when_allow_cpu_is_false(self) -> None:
        from unittest.mock import patch
        mod = load_module()
        gpu_decision = {
            "decision": "gpu",
            "backend": "videotoolbox",
            "gpu": {"ffmpeg_input_args": ["-hwaccel", "videotoolbox"]},
        }

        def fake_analyze(video, ffmpeg_bin, input_args=None):
            raise RuntimeError("Hardware decode failed")

        with patch.object(mod, "resolve_gpu", return_value=(gpu_decision, ["-hwaccel", "videotoolbox"])):
            with patch.object(mod, "analyze", side_effect=fake_analyze):
                with self.assertRaises(RuntimeError):
                    mod.run_audit(Path("/tmp/test.mp4"), allow_cpu=False)


if __name__ == "__main__":
    unittest.main()

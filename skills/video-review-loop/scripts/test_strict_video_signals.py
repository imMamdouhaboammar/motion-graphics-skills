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


if __name__ == "__main__":
    unittest.main()

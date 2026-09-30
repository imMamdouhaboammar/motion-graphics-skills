#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from speaker_layer import (
    calculate_pip_layout,
    generate_depth_stack_filter,
    build_speaker_windows,
)


def test_calculate_pip_layout():
    layout = calculate_pip_layout(1080, 1920, scale=0.6, anchor_x=0.5, anchor_y=0.9)
    assert layout["width"] == 648
    assert layout["height"] == 1152
    assert layout["x"] == 216
    assert layout["y"] == 691


def test_generate_depth_stack_filter():
    cmd = generate_depth_stack_filter(
        "bg.png",
        "chart.mov",
        "person_alpha.mov",
        output_w=1080,
        output_h=1920,
        speaker_scale=0.8,
        speaker_x=100,
        speaker_y=200
    )
    assert "[0:v]scale=1080:1920" in cmd
    assert "[base][spk]overlay=100:200" in cmd


def test_build_speaker_windows():
    events = [
        {"start": 0.0, "end": 4.5, "mode": "full", "bg": "original"},
        {"start": 4.5, "end": 9.0, "mode": "pip", "scale": 0.65, "bg": "brand"}
    ]
    windows = build_speaker_windows(events, 9.0)
    assert len(windows) == 2
    assert windows[0]["duration"] == 4.5
    assert windows[1]["scale"] == 0.65

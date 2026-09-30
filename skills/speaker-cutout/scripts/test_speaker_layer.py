#!/usr/bin/env python3
from pathlib import Path
import json
import math
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import speaker_layer
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


@pytest.mark.parametrize(
    "event",
    [
        {"start": -0.1, "end": 1.0},
        {"start": 2.0, "end": 2.0},
        {"start": 4.0, "end": 3.0},
        {"start": 0.0, "end": 10.1},
        {"start": math.nan, "end": 2.0},
        {"start": 0.0, "end": math.inf},
    ],
)
def test_build_speaker_windows_rejects_invalid_intervals(event):
    with pytest.raises(ValueError, match="start|end|interval"):
        build_speaker_windows([event], 10.0)


def test_full_mode_ignores_pip_scale_and_anchors(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "speaker_layer.py",
            "--mode",
            "full",
            "--scale",
            "0.4",
            "--anchor-x",
            "1.0",
            "--anchor-y",
            "1.0",
        ],
    )

    assert speaker_layer.main() == 0
    layout = json.loads(capsys.readouterr().out)
    assert layout == {"width": 1080, "height": 1920, "x": 0, "y": 0}

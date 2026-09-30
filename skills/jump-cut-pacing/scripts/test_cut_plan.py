#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from cut_plan import (
    parse_silence_log,
    invert_silences_to_speech,
    generate_jump_cut_plan,
    build_cut_summary,
)


def test_parse_silence_log():
    log_text = """
[silencedetect @ 0x7fa] silence_start: 1.200
[silencedetect @ 0x7fa] silence_end: 2.100 | silence_duration: 0.900
[silencedetect @ 0x7fa] silence_start: 5.400
[silencedetect @ 0x7fa] silence_end: 5.600 | silence_duration: 0.200
"""
    silences = parse_silence_log(log_text, min_duration=0.3)
    assert len(silences) == 1
    assert silences[0] == (1.2, 2.1)


def test_invert_silences():
    silences = [(2.0, 3.0), (6.0, 7.0)]
    speech = invert_silences_to_speech(silences, total_duration=10.0, pad_start=0.05, pad_end=0.05)
    assert len(speech) == 3
    assert speech[0][0] == 0.0
    assert speech[0][1] == 2.05


def test_jump_cut_alternation():
    speech = [(0.0, 2.0), (2.0, 5.0), (5.0, 8.0)]
    plan = generate_jump_cut_plan(speech, base_zoom=1.0, push_zoom=1.15, zoom_anchor_y=0.12)
    assert len(plan) == 3
    assert plan[0]["zoom"] == 1.0
    assert plan[1]["zoom"] == 1.15
    assert plan[2]["zoom"] == 1.0
    assert plan[0]["zoom_anchor_y"] == 0.12


def test_build_cut_summary():
    speech = [(0.0, 2.0), (2.5, 4.5)]
    plan = generate_jump_cut_plan(speech)
    summary = build_cut_summary(plan, total_input_duration=5.0)
    assert summary["input_duration"] == 5.0
    assert summary["output_duration"] == 4.0
    assert summary["cut_duration"] == 1.0
    assert summary["reduction_percentage"] == 20.0

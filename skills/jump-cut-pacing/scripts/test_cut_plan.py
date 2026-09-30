#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import cut_plan
from cut_plan import (
    parse_silence_log,
    invert_silences_to_speech,
    generate_jump_cut_plan,
    build_cut_summary,
    run_silence_detect,
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


def test_invert_uses_start_padding_before_speech_and_end_padding_after_speech():
    silences = [(2.0, 3.0)]
    speech = invert_silences_to_speech(
        silences,
        total_duration=5.0,
        pad_start=0.06,
        pad_end=0.08,
    )
    assert speech == [(0.0, 2.08), (2.94, 5.0)]


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


def test_run_silence_detect_requires_successful_ffmpeg(monkeypatch):
    def fake_run(cmd, capture_output, text, check):
        assert check is True
        raise subprocess.CalledProcessError(1, cmd, stderr="ffmpeg failed")

    monkeypatch.setattr(cut_plan.subprocess, "run", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        run_silence_detect("missing.mov")


def test_main_discovers_duration_when_not_supplied(monkeypatch, tmp_path):
    calls = {"duration": 0}

    def fake_probe(_video_path):
        calls["duration"] += 1
        return 10.0

    monkeypatch.setattr(cut_plan, "probe_media_duration", fake_probe, raising=False)
    monkeypatch.setattr(cut_plan, "run_silence_detect", lambda *_args, **_kwargs: "")
    output = tmp_path / "plan.json"
    monkeypatch.setattr(sys, "argv", ["cut_plan.py", "source.mov", "-o", str(output)])

    assert cut_plan.main() == 0
    assert calls["duration"] == 1
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["input_duration"] == 10.0
    assert payload["segments"][0]["source_end"] == 10.0


def test_main_does_not_write_plan_when_ffmpeg_fails(monkeypatch, tmp_path, capsys):
    error = subprocess.CalledProcessError(
        1,
        ["ffmpeg"],
        stderr="decoder exploded",
    )
    monkeypatch.setattr(cut_plan, "probe_media_duration", lambda _video_path: 10.0, raising=False)
    monkeypatch.setattr(cut_plan, "run_silence_detect", lambda *_args, **_kwargs: (_ for _ in ()).throw(error))
    output = tmp_path / "plan.json"
    monkeypatch.setattr(sys, "argv", ["cut_plan.py", "source.mov", "-o", str(output)])

    assert cut_plan.main() != 0
    assert not output.exists()
    assert "decoder exploded" in capsys.readouterr().err

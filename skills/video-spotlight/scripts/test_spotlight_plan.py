#!/usr/bin/env python3
from pathlib import Path
import json
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import spotlight_plan
from spotlight_plan import (
    build_spotlight_filter,
    validate_spotlight_window,
)


def test_validate_spotlight_window():
    win = validate_spotlight_window(2.0, 5.0, target="person", area={"x": 0.4, "y": 0.3, "rx": 0.15, "ry": 0.2})
    assert win["start"] == 2.0
    assert win["end"] == 5.0
    assert win["duration"] == 3.0
    assert win["target"] == "person"


def test_invalid_spotlight_timing():
    with pytest.raises(ValueError):
        validate_spotlight_window(5.0, 3.0)


def test_invalid_spotlight_bounds():
    with pytest.raises(ValueError):
        validate_spotlight_window(1.0, 2.0, area={"x": 1.5, "y": 0.5, "rx": 0.1, "ry": 0.1})


def test_build_spotlight_filter_uses_lighting_strength_and_spatial_mask():
    weaker = build_spotlight_filter(
        200,
        300,
        80,
        dim_factor=0.8,
        desat_factor=0.2,
        enable_expr="between(t,1,3)",
    )
    stronger = build_spotlight_filter(
        200,
        300,
        80,
        dim_factor=0.4,
        desat_factor=0.6,
        enable_expr="between(t,1,3)",
    )

    assert weaker != stronger
    assert "geq=" in stronger
    assert "200" in stronger
    assert "300" in stronger
    assert "80" in stronger
    assert "[base][effect]overlay=0:0:enable='between(t,1,3)'" in stronger


def test_spotlight_plan_preserves_cli_lighting_settings(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "spotlight_plan.py",
            "--start",
            "1.0",
            "--end",
            "3.0",
            "--dim",
            "0.45",
            "--desat",
            "0.60",
        ],
    )

    assert spotlight_plan.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["lighting"] == {"dim": 0.45, "desat": 0.6}

#!/usr/bin/env python3
from pathlib import Path
import pytest
import sys

sys.path.insert(0, str(Path(__file__).parent))

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


def test_build_spotlight_filter():
    filt = build_spotlight_filter(200, 300, 80, dim_factor=0.4, desat_factor=0.6, enable_expr="between(t,1,3)")
    assert "brightness=-0.15" in filt
    assert "between(t,1,3)" in filt

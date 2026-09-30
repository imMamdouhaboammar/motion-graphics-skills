#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from paper_builder import (
    quantize_time_12fps,
    build_paper_piece,
    generate_paper_html,
)


def test_quantize_time_12fps():
    assert quantize_time_12fps(0.0) == 0.0
    assert quantize_time_12fps(0.08) == 0.0
    assert quantize_time_12fps(0.09) == 0.0833
    assert quantize_time_12fps(0.5) == 0.5


def test_build_paper_piece():
    p = build_paper_piece("CLAIM 1", 150, 300, 3.2, bg_color="#FFF9EE", text_color="#111")
    assert p["text"] == "CLAIM 1"
    assert p["x"] == 150
    assert p["rotation"] == 3.2
    assert p["bg_color"] == "#FFF9EE"


def test_generate_paper_html():
    p1 = build_paper_piece("TITLE", 100, 100, 0.0)
    html = generate_paper_html([p1], width=1080, height=1920)
    assert "<!DOCTYPE html>" in html
    assert "TITLE" in html
    assert "window.seek" in html
    assert "width: 1080px" in html

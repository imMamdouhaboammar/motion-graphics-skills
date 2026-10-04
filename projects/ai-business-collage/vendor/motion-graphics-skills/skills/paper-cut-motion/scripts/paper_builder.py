#!/usr/bin/env python3
"""
paper_builder.py - Helper for generating 12fps stop-motion paper-cut templates and time quantization.
"""

import argparse
import json
import math
import sys
from typing import Dict, List, Optional


def quantize_time_12fps(t: float) -> float:
    """
    Quantize continuous time in seconds to 12 frames-per-second steps.
    This creates authentic physical stop-motion animation.
    """
    return round(math.floor(t * 12.0) / 12.0, 4)


def build_paper_piece(
    text: str,
    x: int,
    y: int,
    rotation_deg: float,
    bg_color: str = "#FAF8F5",
    text_color: str = "#1A1A1A",
    enter_at: Optional[float] = None,
) -> Dict:
    """
    Build metadata for a single paper cut cutout piece.
    """
    piece = {
        "text": text,
        "x": x,
        "y": y,
        "rotation": round(rotation_deg, 1),
        "bg_color": bg_color,
        "text_color": text_color,
        "shadow": "2px 4px 6px rgba(0,0,0,0.18)",
    }
    if enter_at is not None:
        if not math.isfinite(enter_at) or enter_at < 0:
            raise ValueError("enter_at must be a non-negative finite number")
        piece["enter_at"] = round(enter_at, 4)
    return piece


def generate_paper_html(pieces: List[Dict], width: int = 1080, height: int = 1920) -> str:
    """
    Generate minimal standalone HTML file with deterministic window.seek(seconds) support.
    """
    if width <= 0 or height <= 0:
        raise ValueError("Canvas dimensions must be positive")

    pieces_json = json.dumps(pieces).replace("<", "\\u003c")
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ margin: 0; background: #EFECE6; overflow: hidden; font-family: sans-serif; }}
  #stage {{ position: relative; width: {width}px; height: {height}px; background: #E8E4DC; }}
  .paper-piece {{
    position: absolute;
    padding: 16px 28px;
    border-radius: 2px;
    box-shadow: 3px 5px 8px rgba(0,0,0,0.22);
    font-weight: bold;
    transform-origin: center center;
    border: 1px dashed rgba(0,0,0,0.06);
    will-change: transform, opacity;
  }}
</style>
</head>
<body>
<div id="stage"></div>
<script>
const pieces = {pieces_json};
const stage = document.getElementById("stage");

pieces.forEach((p, i) => {{
  const el = document.createElement("div");
  el.className = "paper-piece";
  el.id = "p-" + i;
  el.textContent = p.text;
  el.style.backgroundColor = p.bg_color;
  el.style.color = p.text_color;
  el.style.left = p.x + "px";
  el.style.top = p.y + "px";
  stage.appendChild(el);
}});

function renderFrame(stepT) {{
  pieces.forEach((p, i) => {{
    const el = document.getElementById("p-" + i);
    const enterAt = Number.isFinite(p.enter_at) ? p.enter_at : i * 0.35;
    const enterDuration = 0.25;
    const progress = Math.max(0, Math.min(1, (stepT - enterAt) / enterDuration));
    const dropY = (1 - progress) * 80;

    el.style.visibility = stepT < enterAt ? "hidden" : "visible";
    el.style.opacity = String(progress);
    el.style.transform = `translateY(${{dropY}}px) rotate(${{p.rotation}}deg)`;
  }});
}}

window.seek = function(seconds) {{
  const safeSeconds = Math.max(0, Number(seconds) || 0);
  const stepT = Math.floor(safeSeconds * 12) / 12;
  renderFrame(stepT);
  return stepT;
}};

renderFrame(0);
</script>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Build paper cut stop-motion metadata.")
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    parser.add_argument("--output", "-o", help="Output HTML file path")

    args = parser.parse_args()

    if args.test:
        t1 = quantize_time_12fps(0.09)
        assert t1 == 0.0833
        t2 = quantize_time_12fps(1.0)
        assert t2 == 1.0

        piece = build_paper_piece("EVIDENCE", 100, 200, -3.5)
        assert piece["rotation"] == -3.5
        assert piece["text"] == "EVIDENCE"

        html = generate_paper_html([piece])
        assert "window.seek" in html
        assert "renderFrame(stepT)" in html
        assert "EVIDENCE" in html
        print("Self-test passed successfully.")
        return 0

    pieces = [
        build_paper_piece("THE BRIEF", 180, 420, -2.5, enter_at=0.0),
        build_paper_piece("EXHIBIT A", 220, 680, 4.0, enter_at=0.35),
        build_paper_piece("RESULT: 10X", 260, 940, -1.2, enter_at=0.70),
    ]
    html = generate_paper_html(pieces)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated {args.output}")
    else:
        print(html)
    return 0


if __name__ == "__main__":
    sys.exit(main())

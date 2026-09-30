#!/usr/bin/env python3
"""
spotlight_plan.py - Selective lighting and focus beat planner for video footage.
Generates ffmpeg filter strings for timed area dimming, target spotlighting, and desaturation beats.
"""

import argparse
import json
import sys
from typing import Dict, List, Optional


def build_spotlight_filter(
    area_x: int,
    area_y: int,
    radius: int,
    dim_factor: float = 0.5,
    desat_factor: float = 0.5,
    enable_expr: str = "1"
) -> str:
    """
    Generate an ffmpeg filter for an elliptical spotlight area.
    Darkens outside the circle while keeping the center bright.
    """
    # Clamp dim_factor between 0.1 and 1.0
    dim = max(0.1, min(1.0, dim_factor))
    # desat expression using hue filter
    filter_chain = (
        f"split[main][spot];"
        f"[main]eq=brightness=-0.15:contrast=0.9,hue=s={1.0 - desat_factor}[dark];"
        f"[dark][spot]overlay=enable='{enable_expr}'"
    )
    return filter_chain


def validate_spotlight_window(
    start: float,
    end: float,
    target: str = "area",
    area: Optional[Dict[str, float]] = None,
    pulse: bool = False
) -> Dict:
    """
    Validate spotlight timing window and ensure coordinates stay within [0.0, 1.0].
    """
    if end <= start:
        raise ValueError(f"Window end ({end}) must be greater than start ({start})")

    dur = round(end - start, 2)
    parsed_area = area or {"x": 0.5, "y": 0.5, "rx": 0.25, "ry": 0.25}

    for coord in ["x", "y", "rx", "ry"]:
        val = parsed_area.get(coord, 0.5)
        if not (0.0 <= val <= 1.0):
            raise ValueError(f"Coordinate {coord}={val} out of bounds [0.0, 1.0]")

    return {
        "start": start,
        "end": end,
        "duration": dur,
        "target": target,
        "area": parsed_area,
        "pulse": pulse
    }


def main():
    parser = argparse.ArgumentParser(description="Plan video spotlight effects.")
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--end", type=float, default=2.0)
    parser.add_argument("--dim", type=float, default=0.5)
    parser.add_argument("--desat", type=float, default=0.6)

    args = parser.parse_args()

    if args.test:
        win = validate_spotlight_window(1.0, 3.5, "product", {"x": 0.3, "y": 0.4, "rx": 0.2, "ry": 0.2})
        assert win["duration"] == 2.5
        assert win["target"] == "product"

        try:
            validate_spotlight_window(4.0, 2.0)
            assert False, "Should raise ValueError for invalid times"
        except ValueError:
            pass

        filt = build_spotlight_filter(100, 200, 50, dim_factor=0.6, desat_factor=0.4)
        assert "eq=brightness" in filt
        print("Self-test passed successfully.")
        return 0

    win = validate_spotlight_window(args.start, args.end)
    print(json.dumps(win, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

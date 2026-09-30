#!/usr/bin/env python3
"""
spotlight_plan.py - Selective lighting and focus beat planner for video footage.
Generates ffmpeg filter strings for timed area dimming, target spotlighting, and desaturation beats.
"""

import argparse
import json
import math
import sys
from typing import Dict, Optional


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def build_spotlight_filter(
    area_x: int,
    area_y: int,
    radius: int,
    dim_factor: float = 0.5,
    desat_factor: float = 0.5,
    enable_expr: str = "1",
    radius_y: Optional[int] = None,
) -> str:
    """
    Generate an ffmpeg filter for an elliptical spotlight area.
    Pixels inside the mask keep the original image while the surroundings dim.
    """
    rx = int(radius)
    ry = int(radius_y if radius_y is not None else radius)
    if rx <= 0 or ry <= 0:
        raise ValueError("Spotlight radii must be positive")

    dim = _clamp(float(dim_factor), 0.1, 1.0)
    desat = _clamp(float(desat_factor), 0.0, 1.0)

    brightness = round(-0.30 * (1.0 - dim), 3)
    contrast = round(0.82 + (0.18 * dim), 3)
    saturation = round(1.0 - desat, 3)

    mask_expr = (
        "if(lte("
        f"((X-{int(area_x)})*(X-{int(area_x)}))/({rx}*{rx})+"
        f"((Y-{int(area_y)})*(Y-{int(area_y)}))/({ry}*{ry})"
        "\\,1)\\,255\\,0)"
    )

    return (
        "split=4[base][spot][dimsrc][masksrc];"
        f"[dimsrc]eq=brightness={brightness}:contrast={contrast},hue=s={saturation}[dark];"
        f"[masksrc]format=gray,geq=lum='{mask_expr}'[mask];"
        "[dark][spot][mask]maskedmerge[effect];"
        f"[base][effect]overlay=0:0:enable='{enable_expr}':eof_action=pass[out]"
    )


def validate_spotlight_window(
    start: float,
    end: float,
    target: str = "area",
    area: Optional[Dict[str, float]] = None,
    pulse: bool = False,
) -> Dict:
    """
    Validate spotlight timing window and normalized target coordinates.
    """
    if not math.isfinite(start) or not math.isfinite(end) or start < 0 or end <= start:
        raise ValueError(f"Expected finite 0 <= start < end, got start={start}, end={end}")

    dur = round(end - start, 2)
    parsed_area = dict(area or {"x": 0.5, "y": 0.5, "rx": 0.25, "ry": 0.25})

    for coord in ["x", "y", "rx", "ry"]:
        val = float(parsed_area.get(coord, 0.5))
        if not math.isfinite(val):
            raise ValueError(f"Coordinate {coord} must be finite")
        if coord in {"rx", "ry"}:
            if not 0.0 < val <= 1.0:
                raise ValueError(f"Radius {coord}={val} out of bounds (0.0, 1.0]")
        elif not 0.0 <= val <= 1.0:
            raise ValueError(f"Coordinate {coord}={val} out of bounds [0.0, 1.0]")
        parsed_area[coord] = val

    return {
        "start": start,
        "end": end,
        "duration": dur,
        "target": target,
        "area": parsed_area,
        "pulse": pulse,
    }


def validate_lighting_settings(dim: float, desat: float) -> Dict[str, float]:
    if not math.isfinite(dim) or not 0.1 <= dim <= 1.0:
        raise ValueError("dim must be within [0.1, 1.0]")
    if not math.isfinite(desat) or not 0.0 <= desat <= 1.0:
        raise ValueError("desat must be within [0.0, 1.0]")
    return {"dim": round(dim, 3), "desat": round(desat, 3)}


def main():
    parser = argparse.ArgumentParser(description="Plan video spotlight effects.")
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--end", type=float, default=2.0)
    parser.add_argument("--target", default="area")
    parser.add_argument("--x", type=float, default=0.5)
    parser.add_argument("--y", type=float, default=0.5)
    parser.add_argument("--rx", type=float, default=0.25)
    parser.add_argument("--ry", type=float, default=0.25)
    parser.add_argument("--dim", type=float, default=0.5)
    parser.add_argument("--desat", type=float, default=0.6)
    parser.add_argument("--pulse", action="store_true")
    parser.add_argument("--frame-width", type=int, default=1080)
    parser.add_argument("--frame-height", type=int, default=1920)

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
        assert "geq=" in filt
        assert "maskedmerge" in filt
        print("Self-test passed successfully.")
        return 0

    if args.frame_width <= 0 or args.frame_height <= 0:
        print("Frame dimensions must be positive", file=sys.stderr)
        return 2

    try:
        win = validate_spotlight_window(
            args.start,
            args.end,
            target=args.target,
            area={"x": args.x, "y": args.y, "rx": args.rx, "ry": args.ry},
            pulse=args.pulse,
        )
        lighting = validate_lighting_settings(args.dim, args.desat)
    except ValueError as exc:
        print(f"Invalid spotlight plan: {exc}", file=sys.stderr)
        return 2

    area = win["area"]
    area_x = int(round(area["x"] * args.frame_width))
    area_y = int(round(area["y"] * args.frame_height))
    radius_x = max(1, int(round(area["rx"] * args.frame_width)))
    radius_y = max(1, int(round(area["ry"] * args.frame_height)))
    enable_expr = f"between(t,{win['start']},{win['end']})"

    win["lighting"] = lighting
    win["frame"] = {"width": args.frame_width, "height": args.frame_height}
    win["ffmpeg_filter"] = build_spotlight_filter(
        area_x,
        area_y,
        radius_x,
        dim_factor=lighting["dim"],
        desat_factor=lighting["desat"],
        enable_expr=enable_expr,
        radius_y=radius_y,
    )

    print(json.dumps(win, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

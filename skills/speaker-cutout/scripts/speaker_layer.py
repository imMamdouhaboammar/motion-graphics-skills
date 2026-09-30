#!/usr/bin/env python3
"""
speaker_layer.py - Layout and compositing planner for presenter cutouts and depth stacking.
Computes bounding boxes, picture-in-picture transitions, and ffmpeg overlay commands.
"""

import argparse
import json
import math
import sys
from typing import Dict, List


def _validate_layout_inputs(
    frame_w: int,
    frame_h: int,
    scale: float,
    anchor_x: float,
    anchor_y: float,
) -> None:
    if frame_w <= 0 or frame_h <= 0:
        raise ValueError("Frame dimensions must be positive")
    if not math.isfinite(scale) or not 0 < scale <= 1.0:
        raise ValueError("scale must be finite and within (0, 1]")
    for name, value in (("anchor_x", anchor_x), ("anchor_y", anchor_y)):
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be finite and within [0, 1]")


def calculate_pip_layout(
    frame_w: int = 1080,
    frame_h: int = 1920,
    scale: float = 0.65,
    anchor_x: float = 0.5,
    anchor_y: float = 0.85,
) -> Dict[str, int]:
    """
    Calculate target dimensions and pixel positions for shrinking speaker into PiP card.
    """
    _validate_layout_inputs(frame_w, frame_h, scale, anchor_x, anchor_y)

    target_w = int(round(frame_w * scale))
    if target_w % 2 != 0:
        target_w += 1
    target_h = int(round(frame_h * scale))
    if target_h % 2 != 0:
        target_h += 1

    pos_x = int(round((frame_w - target_w) * anchor_x))
    pos_y = int(round((frame_h - target_h) * anchor_y))

    return {
        "width": target_w,
        "height": target_h,
        "x": pos_x,
        "y": pos_y,
    }


def calculate_speaker_layout(
    mode: str,
    frame_w: int = 1080,
    frame_h: int = 1920,
    scale: float = 0.65,
    anchor_x: float = 0.5,
    anchor_y: float = 0.85,
) -> Dict[str, int]:
    """Resolve a full-frame or PiP layout using one explicit mode."""
    if mode == "full":
        if frame_w <= 0 or frame_h <= 0:
            raise ValueError("Frame dimensions must be positive")
        return {"width": frame_w, "height": frame_h, "x": 0, "y": 0}
    if mode == "pip":
        return calculate_pip_layout(frame_w, frame_h, scale, anchor_x, anchor_y)
    raise ValueError(f"Unsupported speaker mode: {mode!r}")


def generate_depth_stack_filter(
    bg_source: str,
    graphics_source: str,
    speaker_cutout: str,
    output_w: int = 1080,
    output_h: int = 1920,
    speaker_scale: float = 1.0,
    speaker_x: int = 0,
    speaker_y: int = 0,
) -> str:
    """
    Generate ffmpeg complex filtergraph for depth stacking:
    Layer 0: Background
    Layer 1: Behind-person motion graphics
    Layer 2: Presenter cutout (foreground)
    """
    if not math.isfinite(speaker_scale) or speaker_scale <= 0:
        raise ValueError("speaker_scale must be positive and finite")

    filtergraph = (
        f"[0:v]scale={output_w}:{output_h},setsar=1[bg];"
        f"[1:v]scale={output_w}:{output_h},setsar=1[gfx];"
        f"[bg][gfx]overlay=0:0:shortest=1[base];"
        f"[2:v]scale={int(output_w * speaker_scale)}:-2[spk];"
        f"[base][spk]overlay={speaker_x}:{speaker_y}:shortest=1,format=yuv420p[out]"
    )
    return filtergraph


def build_speaker_windows(
    events: List[Dict],
    total_duration: float,
) -> List[Dict]:
    """
    Validate and build timeline states for speaker position.
    """
    if not math.isfinite(total_duration) or total_duration <= 0:
        raise ValueError("total_duration must be positive and finite")

    windows = []
    for index, ev in enumerate(events):
        start = float(ev.get("start", 0.0))
        end = float(ev.get("end", total_duration))

        if (
            not math.isfinite(start)
            or not math.isfinite(end)
            or start < 0
            or end <= start
            or end > total_duration
        ):
            raise ValueError(
                f"Invalid interval at event {index}: expected 0 <= start < end <= "
                f"{total_duration}, got start={start}, end={end}"
            )

        mode = ev.get("mode", "full")
        if mode not in {"full", "pip"}:
            raise ValueError(f"Invalid mode at event {index}: {mode!r}")

        if mode == "full":
            scale = 1.0
        else:
            scale = float(ev.get("scale", 0.65))
            if not math.isfinite(scale) or not 0 < scale <= 1.0:
                raise ValueError(f"Invalid PiP scale at event {index}: {scale!r}")

        windows.append({
            "start": round(start, 2),
            "end": round(end, 2),
            "duration": round(end - start, 2),
            "mode": mode,
            "scale": scale,
            "bg": ev.get("bg", "original"),
            "transition": ev.get("transition", "cut"),
        })
    return windows


def main():
    parser = argparse.ArgumentParser(description="Plan speaker cutout and depth layers.")
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    parser.add_argument("--mode", choices=["full", "pip"], default="pip")
    parser.add_argument("--scale", type=float, default=0.65)
    parser.add_argument("--anchor-x", type=float, default=0.5)
    parser.add_argument("--anchor-y", type=float, default=0.85)

    args = parser.parse_args()

    if args.test:
        pip = calculate_pip_layout(1080, 1920, scale=0.5, anchor_x=0.5, anchor_y=1.0)
        assert pip["width"] == 540
        assert pip["height"] == 960
        assert pip["x"] == 270
        assert pip["y"] == 960

        full = calculate_speaker_layout("full", 1080, 1920, scale=0.5, anchor_x=1.0, anchor_y=1.0)
        assert full == {"width": 1080, "height": 1920, "x": 0, "y": 0}

        filt = generate_depth_stack_filter("bg.mp4", "gfx.mp4", "spk.mov", 1080, 1920)
        assert "[bg][gfx]overlay" in filt
        assert "[base][spk]overlay" in filt

        events = [{"start": 0, "end": 5, "mode": "full"}, {"start": 5, "end": 10, "mode": "pip"}]
        wins = build_speaker_windows(events, 10.0)
        assert len(wins) == 2
        assert wins[1]["mode"] == "pip"
        print("Self-test passed successfully.")
        return 0

    layout = calculate_speaker_layout(
        args.mode,
        1080,
        1920,
        args.scale,
        args.anchor_x,
        args.anchor_y,
    )
    print(json.dumps(layout, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

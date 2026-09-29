#!/usr/bin/env python3
"""Detect frame-level temporal anomalies in a rendered video.

The detector uses FFmpeg signalstats metadata. It does not decide whether a cut
is aesthetically wrong; it surfaces one-frame flashes and extreme luma jumps
that deserve frame-by-frame visual inspection.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any


FRAME_RE = re.compile(r"frame:\s*(?P<frame>\d+).*?pts_time:(?P<time>[-+0-9.]+)")
META_RE = re.compile(r"lavfi\.signalstats\.(?P<key>[A-Z0-9]+)=(?P<value>[-+0-9.eE]+)")


def parse_float(value: str) -> float | None:
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def parse_signalstats(text: str) -> list[dict[str, Any]]:
    frames: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw in text.splitlines():
        frame_match = FRAME_RE.search(raw)
        if frame_match:
            if current is not None:
                frames.append(current)
            current = {
                "frame": int(frame_match.group("frame")),
                "time": float(frame_match.group("time")),
            }
            continue

        meta_match = META_RE.search(raw)
        if meta_match and current is not None:
            value = parse_float(meta_match.group("value"))
            if value is not None:
                current[meta_match.group("key")] = value

    if current is not None:
        frames.append(current)
    return frames


def detect_one_frame_flashes(
    frames: list[dict[str, Any]],
    *,
    luma_delta: float = 24.0,
    neighbor_tolerance: float = 8.0,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for index in range(1, len(frames) - 1):
        prev_frame = frames[index - 1]
        current = frames[index]
        next_frame = frames[index + 1]
        if not all("YAVG" in item for item in (prev_frame, current, next_frame)):
            continue

        prev_y = float(prev_frame["YAVG"])
        cur_y = float(current["YAVG"])
        next_y = float(next_frame["YAVG"])
        returns_to_neighbor = abs(prev_y - next_y) <= neighbor_tolerance
        spike = (
            abs(cur_y - prev_y) >= luma_delta
            and abs(cur_y - next_y) >= luma_delta
        )
        if spike and returns_to_neighbor:
            findings.append({
                "code": "one-frame-luma-flash",
                "severity": "warning",
                "frame": current["frame"],
                "time": current["time"],
                "previous_yavg": round(prev_y, 3),
                "yavg": round(cur_y, 3),
                "next_yavg": round(next_y, 3),
                "message": "Single-frame luma spike returns immediately to the neighboring visual level; inspect this frame for an accidental flash",
            })
    return findings


def detect_extreme_luma_changes(
    frames: list[dict[str, Any]],
    *,
    delta: float = 52.0,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for previous, current in zip(frames, frames[1:]):
        if "YAVG" not in previous or "YAVG" not in current:
            continue
        change = abs(float(current["YAVG"]) - float(previous["YAVG"]))
        if change >= delta:
            findings.append({
                "code": "extreme-luma-change",
                "severity": "review",
                "frame": current["frame"],
                "time": current["time"],
                "delta_yavg": round(change, 3),
                "message": "Large frame-to-frame luma change detected; confirm that the cut or transition is intentional",
            })
    return findings


def run_signalstats(video: Path, ffmpeg_bin: str) -> str:
    result = subprocess.run(
        [
            ffmpeg_bin,
            "-hide_banner",
            "-i",
            str(video),
            "-vf",
            "signalstats,metadata=print",
            "-an",
            "-f",
            "null",
            "-",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    output = (result.stdout or "") + "\n" + (result.stderr or "")
    if result.returncode != 0:
        raise RuntimeError(output.strip() or "FFmpeg signalstats pass failed")
    return output


def analyze(video: Path, ffmpeg_bin: str) -> dict[str, Any]:
    frames = parse_signalstats(run_signalstats(video, ffmpeg_bin))
    flashes = detect_one_frame_flashes(frames)
    luma_changes = detect_extreme_luma_changes(frames)
    return {
        "source": str(video.resolve()),
        "frames_analyzed": len(frames),
        "findings": flashes + luma_changes,
        "counts": {
            "one_frame_flashes": len(flashes),
            "extreme_luma_changes": len(luma_changes),
        },
        "note": "Temporal signal findings are review candidates, not automatic creative failures",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect frame-level motion anomalies")
    parser.add_argument("video", type=Path)
    parser.add_argument("--ffmpeg-bin", default="ffmpeg")
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.video.is_file():
        print(json.dumps({"status": "blocked", "error": f"Video not found: {args.video}"}, indent=2))
        return 2

    try:
        result = analyze(args.video, args.ffmpeg_bin)
    except (OSError, RuntimeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

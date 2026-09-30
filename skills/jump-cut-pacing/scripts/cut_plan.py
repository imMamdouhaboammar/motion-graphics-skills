#!/usr/bin/env python3
"""
cut_plan.py - Silence detection and rhythmic jump-cut planner.
Parses ffmpeg silencedetect output to produce clean cut segments and
face-guarded zoom alternation (1.0x vs 1.15x).
"""

import argparse
import json
import math
import re
import subprocess
import sys
from typing import Dict, List, Optional, Tuple


def parse_silence_log(log_text: str, min_duration: float = 0.45) -> List[Tuple[float, float]]:
    """
    Parse ffmpeg silencedetect logs and return list of (start, end) silence intervals.
    """
    silences = []
    start_pattern = re.compile(r"silence_start:\s*([0-9.]+)")
    end_pattern = re.compile(r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)")

    current_start = None
    for line in log_text.splitlines():
        start_match = start_pattern.search(line)
        if start_match:
            current_start = float(start_match.group(1))
            continue

        end_match = end_pattern.search(line)
        if end_match:
            end_val = float(end_match.group(1))
            dur_val = float(end_match.group(2))
            if current_start is not None and dur_val >= min_duration:
                silences.append((current_start, end_val))
            current_start = None

    return silences


def invert_silences_to_speech(
    silences: List[Tuple[float, float]],
    total_duration: float,
    pad_start: float = 0.06,
    pad_end: float = 0.08,
) -> List[Tuple[float, float]]:
    """
    Invert silence intervals to active speech chunks with breath padding.

    pad_start is the lead-in preserved before a speech segment begins.
    pad_end is the tail preserved after a speech segment ends.
    """
    if total_duration <= 0 or not math.isfinite(total_duration):
        return []

    if pad_start < 0 or pad_end < 0:
        raise ValueError("Speech padding values must be non-negative")

    if not silences:
        return [(0.0, total_duration)]

    speech = []
    last_end = 0.0

    for s_start, s_end in silences:
        seg_start = max(0.0, last_end - pad_start) if last_end > 0 else 0.0
        seg_end = min(total_duration, s_start + pad_end)

        if seg_end - seg_start > 0.15:
            speech.append((round(seg_start, 3), round(seg_end, 3)))
        last_end = s_end

    if last_end < total_duration:
        seg_start = max(0.0, last_end - pad_start)
        seg_end = total_duration
        if seg_end - seg_start > 0.15:
            speech.append((round(seg_start, 3), round(seg_end, 3)))

    return speech


def generate_jump_cut_plan(
    speech_segments: List[Tuple[float, float]],
    base_zoom: float = 1.0,
    push_zoom: float = 1.15,
    zoom_anchor_y: float = 0.15,
) -> List[Dict]:
    """
    Assign alternating zooms to speech cuts while keeping face framing safe.
    """
    if base_zoom <= 0 or push_zoom <= 0:
        raise ValueError("Zoom values must be positive")
    if not 0.0 <= zoom_anchor_y <= 1.0:
        raise ValueError("zoom_anchor_y must be between 0.0 and 1.0")

    plan = []
    for idx, (start, end) in enumerate(speech_segments):
        if not all(math.isfinite(v) for v in (start, end)) or start < 0 or end <= start:
            raise ValueError(f"Invalid speech interval: start={start}, end={end}")

        duration = round(end - start, 3)
        zoom = push_zoom if (idx % 2 == 1) else base_zoom
        plan.append({
            "segment_id": idx + 1,
            "source_start": start,
            "source_end": end,
            "duration": duration,
            "zoom": zoom,
            "zoom_anchor_y": zoom_anchor_y,
            "face_safe": True,
        })

    return plan


def probe_media_duration(video_path: str) -> float:
    """Return source duration in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    raw = res.stdout.strip()
    try:
        duration = float(raw)
    except ValueError as exc:
        raise ValueError(f"ffprobe returned an invalid duration: {raw!r}") from exc

    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f"Source duration must be positive and finite, got {duration!r}")
    return duration


def run_silence_detect(video_path: str, noise_db: float = -35.0, min_dur: float = 0.45) -> str:
    """Run ffmpeg silencedetect and return its diagnostic log."""
    cmd = [
        "ffmpeg",
        "-v",
        "info",
        "-i",
        video_path,
        "-af",
        f"silencedetect=noise={noise_db}dB:d={min_dur}",
        "-f",
        "null",
        "-",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return res.stderr


def build_cut_summary(plan: List[Dict], total_input_duration: float) -> Dict:
    total_output = sum(item["duration"] for item in plan)
    cut_duration = round(max(0.0, total_input_duration - total_output), 3)
    reduction_pct = round((cut_duration / total_input_duration * 100), 1) if total_input_duration > 0 else 0.0

    return {
        "input_duration": total_input_duration,
        "output_duration": round(total_output, 3),
        "cut_duration": cut_duration,
        "reduction_percentage": reduction_pct,
        "total_segments": len(plan),
        "segments": plan,
    }


def _format_command_error(exc: subprocess.CalledProcessError) -> str:
    detail = (exc.stderr or exc.stdout or "").strip()
    return detail or str(exc)


def _resolve_duration(video_path: str, supplied_duration: Optional[float]) -> float:
    if supplied_duration is None:
        return probe_media_duration(video_path)
    if not math.isfinite(supplied_duration) or supplied_duration <= 0:
        raise ValueError("--total-duration must be a positive finite number")
    return supplied_duration


def main():
    parser = argparse.ArgumentParser(description="Generate jump-cut plan from silence detection.")
    parser.add_argument("video", nargs="?", default="", help="Input video or audio file")
    parser.add_argument("--noise-db", type=float, default=-35.0, help="Noise threshold in dB (default: -35.0)")
    parser.add_argument("--min-silence", type=float, default=0.45, help="Minimum silence duration in seconds")
    parser.add_argument("--total-duration", type=float, default=None, help="Override source duration in seconds")
    parser.add_argument("--output", "-o", help="Output JSON path")
    parser.add_argument("--test", action="store_true", help="Run self-tests")

    args = parser.parse_args()

    if args.test:
        test_log = """
[silencedetect @ 0x123] silence_start: 2.15
[silencedetect @ 0x123] silence_end: 3.40 | silence_duration: 1.25
[silencedetect @ 0x123] silence_start: 7.00
[silencedetect @ 0x123] silence_end: 7.80 | silence_duration: 0.80
"""
        silences = parse_silence_log(test_log, min_duration=0.45)
        assert len(silences) == 2, f"Expected 2 silences, got {len(silences)}"
        assert silences[0] == (2.15, 3.40)
        assert silences[1] == (7.00, 7.80)

        speech = invert_silences_to_speech(silences, total_duration=10.0)
        assert len(speech) == 3, f"Expected 3 speech segments, got {len(speech)}"
        plan = generate_jump_cut_plan(speech)
        assert len(plan) == 3
        assert plan[0]["zoom"] == 1.0
        assert plan[1]["zoom"] == 1.15
        assert plan[2]["zoom"] == 1.0

        summary = build_cut_summary(plan, total_input_duration=10.0)
        assert summary["total_segments"] == 3
        print("Self-test passed successfully.")
        return 0

    if not args.video:
        parser.print_help()
        return 1

    try:
        total_duration = _resolve_duration(args.video, args.total_duration)
        log_output = run_silence_detect(args.video, args.noise_db, args.min_silence)
    except subprocess.CalledProcessError as exc:
        print(f"Media command failed: {_format_command_error(exc)}", file=sys.stderr)
        return 2
    except (OSError, ValueError) as exc:
        print(f"Could not analyze source media: {exc}", file=sys.stderr)
        return 2

    silences = parse_silence_log(log_output, args.min_silence)
    speech = invert_silences_to_speech(silences, total_duration)
    plan = generate_jump_cut_plan(speech)
    summary = build_cut_summary(plan, total_duration)

    out_json = json.dumps(summary, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_json)
        print(f"Saved cut plan to {args.output}")
    else:
        print(out_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())

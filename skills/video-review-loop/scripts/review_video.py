#!/usr/bin/env python3
"""Build evidence-based review rounds for rendered motion videos."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
GPU_POLICY_PATH = (
    Path(__file__).resolve().parents[2]
    / "motion-director"
    / "scripts"
    / "gpu_policy.py"
)
REFERENCE_FIDELITY_PATH = (
    Path(__file__).resolve().parents[2]
    / "motion-director"
    / "scripts"
    / "reference_fidelity.py"
)


class ReviewError(RuntimeError):
    pass


def load_gpu_policy():
    spec = importlib.util.spec_from_file_location("motion_gpu_policy", GPU_POLICY_PATH)
    if spec is None or spec.loader is None:
        raise ReviewError(f"GPU policy is unavailable at {GPU_POLICY_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gpu_gate(signals: dict[str, Any], allow_cpu: bool) -> tuple[int, dict[str, Any]]:
    gpu = load_gpu_policy()
    return gpu.evaluate(signals, require=True, allow_cpu=allow_cpu)


def load_reference_fidelity():
    spec = importlib.util.spec_from_file_location(
        "motion_reference_fidelity",
        REFERENCE_FIDELITY_PATH,
    )
    if spec is None or spec.loader is None:
        raise ReviewError(
            f"Reference fidelity tool is unavailable at {REFERENCE_FIDELITY_PATH}"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reference_checklist(contract: dict[str, Any]) -> list[dict[str, Any]]:
    items = contract.get("must_preserve", [])
    if not isinstance(items, list):
        return []
    checklist: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        contract_id = str(item.get("id", "")).strip()
        mechanism = str(item.get("mechanism", "")).strip()
        if not contract_id or not mechanism:
            continue
        checklist.append({
            "id": contract_id,
            "mechanism": mechanism,
            "evidence": str(item.get("evidence", "")).strip(),
            "required": True,
        })
    return checklist


def normalized_sample_times(
    duration: float | None,
    count: int = 12,
) -> list[float]:
    if duration is None or duration <= 0 or count < 2:
        return []
    times = [
        round(duration * index / (count - 1), 6)
        for index in range(count)
    ]
    times[-1] = round(max(0.0, duration - 0.04), 6)
    return times


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def parse_fraction(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if "/" not in text:
        return parse_float(text)
    numerator, denominator = text.split("/", 1)
    top = parse_float(numerator)
    bottom = parse_float(denominator)
    if top is None or bottom in {None, 0.0}:
        return None
    return top / bottom


def make_finding(
    code: str,
    severity: str,
    message: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "evidence": evidence or {},
    }


def first_stream(probe: dict[str, Any], kind: str) -> dict[str, Any] | None:
    for stream in probe.get("streams", []):
        if isinstance(stream, dict) and stream.get("codec_type") == kind:
            return stream
    return None


def stream_duration(stream: dict[str, Any] | None, fallback: float | None) -> float | None:
    if not stream:
        return None
    value = parse_float(stream.get("duration"))
    return fallback if value is None else value


def analyze_probe(
    probe: dict[str, Any],
    expectations: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    format_info = probe.get("format", {}) if isinstance(probe.get("format"), dict) else {}
    format_duration = parse_float(format_info.get("duration"))
    video = first_stream(probe, "video")
    audio = first_stream(probe, "audio")

    technical: dict[str, Any] = {
        "format_duration": format_duration,
        "format_name": format_info.get("format_name"),
        "video": None,
        "audio": None,
    }

    if video is None:
        findings.append(make_finding(
            "video-stream-missing",
            "hard",
            "No video stream was reported by FFprobe",
        ))
        return findings, technical

    avg_fps = parse_fraction(video.get("avg_frame_rate"))
    nominal_fps = parse_fraction(video.get("r_frame_rate"))
    video_duration = stream_duration(video, format_duration)
    width = int(video.get("width") or 0)
    height = int(video.get("height") or 0)

    technical["video"] = {
        "codec": video.get("codec_name"),
        "width": width,
        "height": height,
        "avg_fps": avg_fps,
        "nominal_fps": nominal_fps,
        "pix_fmt": video.get("pix_fmt"),
        "duration": video_duration,
        "color_space": video.get("color_space"),
        "color_primaries": video.get("color_primaries"),
        "color_transfer": video.get("color_transfer"),
        "color_range": video.get("color_range"),
        "bit_rate": parse_float(video.get("bit_rate")),
    }

    expected_width = expectations.get("width")
    if expected_width is not None and width != int(expected_width):
        findings.append(make_finding(
            "width-mismatch",
            "hard",
            f"Expected width {int(expected_width)}, got {width}",
            {"expected": int(expected_width), "actual": width},
        ))

    expected_height = expectations.get("height")
    if expected_height is not None and height != int(expected_height):
        findings.append(make_finding(
            "height-mismatch",
            "hard",
            f"Expected height {int(expected_height)}, got {height}",
            {"expected": int(expected_height), "actual": height},
        ))

    expected_fps = parse_float(expectations.get("fps"))
    if expected_fps is not None and (
        avg_fps is None or abs(avg_fps - expected_fps) > 0.02
    ):
        findings.append(make_finding(
            "frame-rate-mismatch",
            "hard",
            f"Expected {expected_fps:g} fps, got {avg_fps if avg_fps is not None else 'unknown'}",
            {"expected": expected_fps, "actual": avg_fps},
        ))

    if avg_fps is not None and nominal_fps is not None and abs(avg_fps - nominal_fps) > 0.02:
        findings.append(make_finding(
            "variable-frame-rate-signal",
            "warning",
            "Average and nominal frame rates differ",
            {"average": avg_fps, "nominal": nominal_fps},
        ))

    expected_duration = parse_float(expectations.get("duration"))
    tolerance = parse_float(expectations.get("duration_tolerance"))
    if tolerance is None:
        tolerance = 0.08
    if expected_duration is not None and (
        video_duration is None or abs(video_duration - expected_duration) > tolerance
    ):
        findings.append(make_finding(
            "duration-mismatch",
            "hard",
            "Video duration is outside the explicit tolerance",
            {
                "expected": expected_duration,
                "actual": video_duration,
                "tolerance": tolerance,
            },
        ))

    if audio is None:
        if bool(expectations.get("expect_audio", False)):
            findings.append(make_finding(
                "audio-missing",
                "hard",
                "Audio was required but no audio stream was reported",
            ))
    else:
        audio_duration = stream_duration(audio, format_duration)
        technical["audio"] = {
            "codec": audio.get("codec_name"),
            "duration": audio_duration,
            "sample_rate": int(audio.get("sample_rate") or 0),
            "channels": int(audio.get("channels") or 0),
            "bit_rate": parse_float(audio.get("bit_rate")),
        }
        if video_duration is not None and audio_duration is not None:
            drift = abs(video_duration - audio_duration)
            if drift > 0.25:
                findings.append(make_finding(
                    "audio-video-duration-drift",
                    "hard",
                    "Audio and video durations differ by more than 250 ms",
                    {"drift_seconds": round(drift, 6)},
                ))
            elif drift > 0.08:
                findings.append(make_finding(
                    "audio-video-duration-drift",
                    "warning",
                    "Audio and video durations differ by more than 80 ms",
                    {"drift_seconds": round(drift, 6)},
                ))

    return findings, technical


def parse_blackdetect(text: str) -> list[dict[str, float]]:
    pattern = re.compile(
        rf"black_start:(?P<start>{NUMBER})\s+"
        rf"black_end:(?P<end>{NUMBER})\s+"
        rf"black_duration:(?P<duration>{NUMBER})"
    )
    return [
        {
            "start": float(match.group("start")),
            "end": float(match.group("end")),
            "duration": float(match.group("duration")),
        }
        for match in pattern.finditer(text)
    ]


def parse_freezedetect(
    text: str,
    video_duration: float | None = None,
) -> list[dict[str, float]]:
    start_re = re.compile(rf"freeze_start:\s*(?P<value>{NUMBER})")
    duration_re = re.compile(rf"freeze_duration:\s*(?P<value>{NUMBER})")
    end_re = re.compile(rf"freeze_end:\s*(?P<value>{NUMBER})")
    result: list[dict[str, float]] = []
    current: dict[str, float] = {}

    for line in text.splitlines():
        start = start_re.search(line)
        if start:
            current = {"start": float(start.group("value"))}
            continue
        duration = duration_re.search(line)
        if duration and current:
            current["duration"] = float(duration.group("value"))
            continue
        end = end_re.search(line)
        if end and current:
            current["end"] = float(end.group("value"))
            if "duration" not in current:
                current["duration"] = max(0.0, current["end"] - current["start"])
            result.append({
                "start": current["start"],
                "end": current["end"],
                "duration": current["duration"],
            })
            current = {}

    if current and "start" in current and video_duration is not None:
        end = max(float(video_duration), current["start"])
        result.append({
            "start": current["start"],
            "end": end,
            "duration": round(max(0.0, end - current["start"]), 6),
        })

    return result


def parse_silencedetect(text: str) -> list[dict[str, float]]:
    start_re = re.compile(rf"silence_start:\s*(?P<value>{NUMBER})")
    end_re = re.compile(
        rf"silence_end:\s*(?P<end>{NUMBER})\s*\|\s*"
        rf"silence_duration:\s*(?P<duration>{NUMBER})"
    )
    result: list[dict[str, float]] = []
    start_value: float | None = None
    for line in text.splitlines():
        start = start_re.search(line)
        if start:
            start_value = float(start.group("value"))
            continue
        end = end_re.search(line)
        if end and start_value is not None:
            result.append({
                "start": start_value,
                "end": float(end.group("end")),
                "duration": float(end.group("duration")),
            })
            start_value = None
    return result


def parse_max_volume(text: str) -> float | None:
    match = re.search(rf"max_volume:\s*(?P<value>{NUMBER})\s*dB", text)
    if not match:
        return None
    return float(match.group("value"))


def volume_finding(max_volume: float | None) -> dict[str, Any] | None:
    if max_volume is None:
        return None
    if max_volume >= -0.1:
        return make_finding(
            "audio-clipping-risk",
            "warning",
            "Peak audio level is at or above -0.1 dBFS",
            {"max_volume_db": max_volume},
        )
    return None


def video_analysis_failure_finding() -> dict[str, Any]:
    return make_finding(
        "video-analysis-pass-failed",
        "hard",
        "FFmpeg could not complete the primary video analysis pass",
        {"log": "video-analysis.log"},
    )


def validate_reference_inputs(
    reference: Path | None,
    reference_contract: Path | None,
) -> None:
    if reference_contract is not None and reference is None:
        raise ReviewError(
            "--reference-contract requires --reference so structural fidelity "
            "is checked against the actual benchmark video"
        )


def end_hold_finding(
    freezes: list[dict[str, float]],
    video_duration: float | None,
    expected_hold: float,
) -> dict[str, Any] | None:
    if expected_hold <= 0:
        return None
    if video_duration is not None:
        for interval in freezes:
            if (
                abs(interval["end"] - video_duration) <= 0.12
                and interval["duration"] + 0.04 >= expected_hold
            ):
                return None
    return make_finding(
        "end-hold-not-proven",
        "hard",
        "The required clean end hold was not proven by tail freeze evidence",
        {"expected_hold_seconds": expected_hold, "video_duration": video_duration},
    )


def safe_stem(path: Path) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", path.stem).strip("-._")
    return cleaned[:48] or "video"


def create_round_paths(root: Path, video: Path) -> dict[str, Path]:
    root.mkdir(parents=True, exist_ok=True)

    if root.name == "rounds" and root.parent.name == ".motion-review":
        ignore_dir = root.parent
    else:
        ignore_dir = root

    gitignore = ignore_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!.gitignore\n", encoding="utf-8")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    round_dir = root / f"{stamp}-{safe_stem(video)}"
    suffix = 1
    while round_dir.exists():
        round_dir = root / f"{stamp}-{safe_stem(video)}-{suffix}"
        suffix += 1
    evidence_dir = round_dir / "evidence"
    evidence_dir.mkdir(parents=True)
    return {
        "round_dir": round_dir,
        "evidence_dir": evidence_dir,
    }


def run_command(
    argv: list[str],
    *,
    timeout: float = 120.0,
    log_path: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            argv,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise ReviewError(f"Required executable not found: {argv[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ReviewError(f"Command timed out: {argv[0]}") from exc

    if log_path is not None:
        log_path.write_text(
            (result.stdout or "") + (result.stderr or ""),
            encoding="utf-8",
        )
    return result


def probe_video(video: Path, ffprobe_bin: str) -> dict[str, Any]:
    result = run_command([
        ffprobe_bin,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(video),
    ])
    if result.returncode != 0:
        raise ReviewError(result.stderr.strip() or "FFprobe failed")
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ReviewError("FFprobe returned invalid JSON") from exc
    if not isinstance(data, dict):
        raise ReviewError("FFprobe returned an unexpected payload")
    return data


def verify_gpu_decode(
    video: Path,
    ffmpeg_bin: str,
    gpu_result: dict[str, Any],
    *,
    allow_cpu: bool,
    log_path: Path,
) -> dict[str, Any]:
    if gpu_result["decision"] != "gpu":
        return gpu_result

    input_args = list(gpu_result["gpu"].get("ffmpeg_input_args", []))
    result = run_command([
        ffmpeg_bin,
        "-hide_banner",
        "-v",
        "error",
        *input_args,
        "-ss",
        "0",
        "-t",
        "1",
        "-i",
        str(video),
        "-an",
        "-f",
        "null",
        "-",
    ], timeout=30, log_path=log_path)

    if result.returncode == 0:
        verified = dict(gpu_result)
        verified["gpu"] = dict(gpu_result["gpu"])
        verified["gpu"]["verification"] = "media-decode-verified"
        return verified

    if allow_cpu:
        fallback = dict(gpu_result)
        fallback["decision"] = "cpu-fallback-explicit"
        fallback["reason"] = "gpu-backend-detected-but-media-decode-failed"
        fallback["gpu"] = dict(gpu_result["gpu"])
        fallback["gpu"]["verification"] = "media-decode-failed"
        return fallback

    raise ReviewError(
        "GPU backend was detected but failed the media decode verification. "
        "CPU fallback was not explicitly allowed"
    )


def ffmpeg_input_args(gpu_result: dict[str, Any]) -> list[str]:
    if gpu_result.get("decision") != "gpu":
        return []
    return list(gpu_result.get("gpu", {}).get("ffmpeg_input_args", []))


def run_video_analysis(
    video: Path,
    ffmpeg_bin: str,
    gpu_result: dict[str, Any],
    log_path: Path,
) -> tuple[int, str]:
    result = run_command([
        ffmpeg_bin,
        "-hide_banner",
        *ffmpeg_input_args(gpu_result),
        "-i",
        str(video),
        "-vf",
        "blackdetect=d=0.04:pix_th=0.10,freezedetect=n=-50dB:d=0.12",
        "-an",
        "-f",
        "null",
        "-",
    ], timeout=180, log_path=log_path)
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def run_audio_analysis(
    video: Path,
    ffmpeg_bin: str,
    log_path: Path,
) -> tuple[int, str]:
    result = run_command([
        ffmpeg_bin,
        "-hide_banner",
        "-i",
        str(video),
        "-af",
        "silencedetect=n=-45dB:d=0.25,volumedetect",
        "-vn",
        "-f",
        "null",
        "-",
    ], timeout=180, log_path=log_path)
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def build_contact_sheet(
    video: Path,
    ffmpeg_bin: str,
    gpu_result: dict[str, Any],
    duration: float | None,
    output: Path,
    log_path: Path,
) -> bool:
    interval = max((duration or 12.0) / 12.0, 0.25)
    result = run_command([
        ffmpeg_bin,
        "-y",
        "-hide_banner",
        *ffmpeg_input_args(gpu_result),
        "-i",
        str(video),
        "-vf",
        f"fps=1/{interval:.6f},scale=360:-2,tile=4x3:padding=8:margin=8",
        "-frames:v",
        "1",
        str(output),
    ], timeout=180, log_path=log_path)
    return result.returncode == 0 and output.exists()


def build_sample_frames(
    video: Path,
    ffmpeg_bin: str,
    gpu_result: dict[str, Any],
    duration: float | None,
    evidence_dir: Path,
    log_path: Path,
) -> bool:
    interval = max((duration or 8.0) / 8.0, 0.20)
    output = evidence_dir / "sample-%03d.jpg"
    result = run_command([
        ffmpeg_bin,
        "-y",
        "-hide_banner",
        *ffmpeg_input_args(gpu_result),
        "-i",
        str(video),
        "-vf",
        f"fps=1/{interval:.6f},scale=720:-2",
        "-frames:v",
        "8",
        str(output),
    ], timeout=180, log_path=log_path)
    return result.returncode == 0


def build_edge_frames(
    video: Path,
    ffmpeg_bin: str,
    gpu_result: dict[str, Any],
    duration: float | None,
    evidence_dir: Path,
) -> list[str]:
    outputs: list[str] = []
    times = [("first-frame.jpg", 0.0)]
    if duration is not None and duration > 0.05:
        times.append(("last-frame.jpg", max(0.0, duration - 0.04)))

    for name, timestamp in times:
        path = evidence_dir / name
        result = run_command([
            ffmpeg_bin,
            "-y",
            "-hide_banner",
            *ffmpeg_input_args(gpu_result),
            "-ss",
            f"{timestamp:.6f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            str(path),
        ], timeout=60)
        if result.returncode == 0 and path.exists():
            outputs.append(name)
    return outputs


def build_reference_comparison(
    reference_sheet: Path,
    output_sheet: Path,
    ffmpeg_bin: str,
    destination: Path,
    log_path: Path,
) -> bool:
    result = run_command([
        ffmpeg_bin,
        "-y",
        "-hide_banner",
        "-i",
        str(reference_sheet),
        "-i",
        str(output_sheet),
        "-filter_complex",
        "[0:v]scale=-2:1080[r];[1:v]scale=-2:1080[o];[r][o]hstack=inputs=2",
        "-frames:v",
        "1",
        str(destination),
    ], timeout=120, log_path=log_path)
    return result.returncode == 0 and destination.exists()


def build_waveform(
    video: Path,
    ffmpeg_bin: str,
    output: Path,
    log_path: Path,
) -> bool:
    result = run_command([
        ffmpeg_bin,
        "-y",
        "-hide_banner",
        "-i",
        str(video),
        "-filter_complex",
        "showwavespic=s=1280x240:colors=white",
        "-frames:v",
        "1",
        str(output),
    ], timeout=120, log_path=log_path)
    return result.returncode == 0 and output.exists()


def detector_findings(
    black: list[dict[str, float]],
    freezes: list[dict[str, float]],
    silence: list[dict[str, float]],
    max_volume: float | None,
    video_duration: float | None,
    expected_hold: float,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    for interval in black:
        if interval["duration"] >= 0.04:
            findings.append(make_finding(
                "black-interval",
                "warning",
                "Black interval detected. Confirm that it is intentional",
                interval,
            ))

    for interval in freezes:
        tail = (
            video_duration is not None
            and abs(interval["end"] - video_duration) <= 0.12
        )
        if interval["duration"] >= 0.30 and not tail:
            findings.append(make_finding(
                "mid-film-freeze",
                "warning",
                "Frozen interval detected away from the video end",
                interval,
            ))

    for interval in silence:
        if interval["duration"] >= 1.0:
            findings.append(make_finding(
                "long-silence",
                "warning",
                "Silence interval longer than one second detected",
                interval,
            ))

    volume = volume_finding(max_volume)
    if volume:
        findings.append(volume)

    hold = end_hold_finding(freezes, video_duration, expected_hold)
    if hold:
        findings.append(hold)
    return findings


def source_manifest(video: Path) -> dict[str, Any]:
    stat = video.stat()
    return {
        "path": str(video.resolve()),
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def write_json(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_review_markdown(
    path: Path,
    source: Path,
    findings: list[dict[str, Any]],
    reference_items: list[dict[str, Any]] | None = None,
) -> None:
    lines = [
        "# Video Review Round",
        "",
        f"Source: {source}",
        "",
        "## Machine findings",
        "",
    ]
    if findings:
        for item in findings:
            lines.append(
                f"- [{item['severity']}] {item['code']}: {item['message']}"
            )
    else:
        lines.append("- No machine hard failures or warnings were produced.")
    if reference_items:
        lines.extend([
            "",
            "## Reference fidelity gate",
            "",
            "Compare the actual reference and output videos, not only isolated frames.",
            "The paired contact sheet is orientation evidence, not final proof.",
            "",
        ])
        for item in reference_items:
            evidence = (
                f" Evidence: {item['evidence']}."
                if item.get("evidence")
                else ""
            )
            lines.append(
                f"- [ ] {item['id']}: {item['mechanism']}.{evidence}"
            )

    lines.extend([
        "",
        "## Required visual review",
        "",
        "- [ ] Watch the full video with audio at normal speed",
        "- [ ] Watch the full video muted",
        "- [ ] Inspect the first second densely",
        "- [ ] Inspect every important transition",
        "- [ ] Inspect each machine finding at its timestamp",
        "- [ ] Inspect CTA and ending",
        "- [ ] Inspect the contact sheet at phone scale",
        "",
        "## Timecoded visual findings",
        "",
        "Add one line per confirmed visual defect:",
        "",
        "00:00.000  severity  observable defect  ->  proposed fix",
        "",
        "## Signoff",
        "",
        "Status: agent-review-required",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def review_video(args: argparse.Namespace) -> int:
    video = args.video
    if not video.is_file():
        raise ReviewError(f"Video not found: {video}")

    validate_reference_inputs(args.reference, args.reference_contract)

    gpu = load_gpu_policy()
    signals = gpu.probe_signals(args.ffmpeg_bin)
    gate_code, gpu_result = gpu_gate(signals, allow_cpu=args.allow_cpu)
    if gate_code != 0:
        print(json.dumps(gpu_result, ensure_ascii=False, indent=2))
        return gate_code

    paths = create_round_paths(args.round_root, video)
    round_dir = paths["round_dir"]
    evidence_dir = paths["evidence_dir"]

    reference_contract = None
    reference_items: list[dict[str, Any]] = []
    if args.reference_contract is not None:
        try:
            reference_contract = json.loads(
                args.reference_contract.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise ReviewError(f"Reference contract cannot be read: {exc}") from exc
        if not isinstance(reference_contract, dict):
            raise ReviewError("Reference contract must contain a JSON object")
        fidelity = load_reference_fidelity()
        contract_result = fidelity.validate_contract(reference_contract)
        if contract_result["status"] != "pass":
            raise ReviewError(
                "Reference contract failed validation before final video review"
            )
        reference_items = reference_checklist(reference_contract)

    gpu_result = verify_gpu_decode(
        video,
        args.ffmpeg_bin,
        gpu_result,
        allow_cpu=args.allow_cpu,
        log_path=round_dir / "gpu-decode.log",
    )

    probe = probe_video(video, args.ffprobe_bin)
    expectations = {
        "width": args.expect_width,
        "height": args.expect_height,
        "fps": args.expect_fps,
        "duration": args.expect_duration,
        "duration_tolerance": args.duration_tolerance,
        "expect_audio": args.expect_audio,
    }
    findings, technical = analyze_probe(probe, expectations)
    write_json(round_dir / "technical.json", technical)

    video_duration = (
        technical.get("video", {}).get("duration")
        if isinstance(technical.get("video"), dict)
        else technical.get("format_duration")
    )

    video_code, video_log = run_video_analysis(
        video,
        args.ffmpeg_bin,
        gpu_result,
        round_dir / "video-analysis.log",
    )
    if video_code != 0:
        findings.append(video_analysis_failure_finding())

    black = parse_blackdetect(video_log)
    freezes = parse_freezedetect(video_log, video_duration=video_duration)

    audio_stream = technical.get("audio")
    silence: list[dict[str, float]] = []
    max_volume: float | None = None
    if isinstance(audio_stream, dict):
        audio_code, audio_log = run_audio_analysis(
            video,
            args.ffmpeg_bin,
            round_dir / "audio-analysis.log",
        )
        if audio_code != 0:
            findings.append(make_finding(
                "audio-analysis-pass-failed",
                "warning",
                "FFmpeg audio detector pass failed. Review the saved log",
                {"log": "audio-analysis.log"},
            ))
        silence = parse_silencedetect(audio_log)
        max_volume = parse_max_volume(audio_log)

    findings.extend(detector_findings(
        black,
        freezes,
        silence,
        max_volume,
        video_duration,
        args.expect_end_hold,
    ))

    contact_ok = build_contact_sheet(
        video,
        args.ffmpeg_bin,
        gpu_result,
        video_duration,
        evidence_dir / "contact-sheet.jpg",
        round_dir / "contact-sheet.log",
    )
    if not contact_ok:
        findings.append(make_finding(
            "contact-sheet-generation-failed",
            "warning",
            "Contact sheet could not be generated",
            {"log": "contact-sheet.log"},
        ))

    reference_comparison_ok = False
    reference_manifest = None
    if args.reference is not None:
        if not args.reference.is_file():
            raise ReviewError(f"Reference video not found: {args.reference}")
        reference_probe = probe_video(args.reference, args.ffprobe_bin)
        _, reference_technical = analyze_probe(reference_probe, {})
        write_json(round_dir / "reference-technical.json", reference_technical)
        reference_duration = (
            reference_technical.get("video", {}).get("duration")
            if isinstance(reference_technical.get("video"), dict)
            else reference_technical.get("format_duration")
        )
        reference_sheet = evidence_dir / "reference-contact-sheet.jpg"
        reference_sheet_ok = build_contact_sheet(
            args.reference,
            args.ffmpeg_bin,
            gpu_result,
            reference_duration,
            reference_sheet,
            round_dir / "reference-contact-sheet.log",
        )
        if reference_sheet_ok and contact_ok:
            reference_comparison_ok = build_reference_comparison(
                reference_sheet,
                evidence_dir / "contact-sheet.jpg",
                args.ffmpeg_bin,
                evidence_dir / "reference-vs-output.jpg",
                round_dir / "reference-vs-output.log",
            )
        if not reference_comparison_ok:
            findings.append(make_finding(
                "reference-comparison-generation-failed",
                "warning",
                "Reference versus output comparison evidence could not be generated",
                {"log": "reference-vs-output.log"},
            ))
        reference_manifest = source_manifest(args.reference)

    samples_ok = build_sample_frames(
        video,
        args.ffmpeg_bin,
        gpu_result,
        video_duration,
        evidence_dir,
        round_dir / "sample-frames.log",
    )
    if not samples_ok:
        findings.append(make_finding(
            "sample-frame-generation-failed",
            "warning",
            "Sample frame evidence could not be generated",
            {"log": "sample-frames.log"},
        ))

    edge_frames = build_edge_frames(
        video,
        args.ffmpeg_bin,
        gpu_result,
        video_duration,
        evidence_dir,
    )

    waveform_ok = False
    if isinstance(audio_stream, dict):
        waveform_ok = build_waveform(
            video,
            args.ffmpeg_bin,
            evidence_dir / "waveform.png",
            round_dir / "waveform.log",
        )
        if not waveform_ok:
            findings.append(make_finding(
                "waveform-generation-failed",
                "warning",
                "Audio waveform evidence could not be generated",
                {"log": "waveform.log"},
            ))

    write_json(round_dir / "findings.json", findings)
    write_review_markdown(
        round_dir / "review.md",
        video,
        findings,
        reference_items=reference_items,
    )

    hard_count = sum(item["severity"] == "hard" for item in findings)
    warning_count = sum(item["severity"] == "warning" for item in findings)

    manifest = {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": (
            "machine-hard-fail-agent-review-required"
            if hard_count
            else "agent-review-required"
        ),
        "source": source_manifest(video),
        "reference": reference_manifest,
        "reference_contract": (
            str(args.reference_contract.resolve())
            if args.reference_contract is not None
            else None
        ),
        "gpu": gpu_result,
        "expectations": expectations | {
            "expect_end_hold": args.expect_end_hold,
        },
        "evidence": {
            "contact_sheet": contact_ok,
            "reference_comparison": reference_comparison_ok,
            "sample_frames": samples_ok,
            "edge_frames": edge_frames,
            "waveform": waveform_ok,
        },
        "finding_counts": {
            "hard": hard_count,
            "warning": warning_count,
        },
    }
    write_json(round_dir / "manifest.json", manifest)

    result = {
        "round_dir": str(round_dir),
        "status": manifest["status"],
        "hard_findings": hard_count,
        "warnings": warning_count,
        "gpu_decision": gpu_result.get("decision"),
        "next": "Review the actual video and write timecoded visual findings into review.md",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if hard_count else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create evidence-based review rounds for motion videos",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    review = sub.add_parser("review", help="review one rendered video")
    review.add_argument("video", type=Path)
    review.add_argument(
        "--round-root",
        type=Path,
        default=Path(".motion-review/rounds"),
    )
    review.add_argument("--expect-width", type=int)
    review.add_argument("--expect-height", type=int)
    review.add_argument("--expect-fps", type=float)
    review.add_argument("--expect-duration", type=float)
    review.add_argument("--duration-tolerance", type=float, default=0.08)
    review.add_argument("--expect-audio", action="store_true")
    review.add_argument("--expect-end-hold", type=float, default=0.0)
    review.add_argument("--reference", type=Path)
    review.add_argument("--reference-contract", type=Path)
    review.add_argument("--allow-cpu", action="store_true")
    review.add_argument("--ffmpeg-bin", default="ffmpeg")
    review.add_argument("--ffprobe-bin", default="ffprobe")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "review":
            return review_video(args)
    except ReviewError as exc:
        print(json.dumps({
            "status": "blocked",
            "error": str(exc),
        }, ensure_ascii=False, indent=2))
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

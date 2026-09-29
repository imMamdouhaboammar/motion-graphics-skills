#!/usr/bin/env python3
"""Select and enforce a GPU-first execution policy for motion work."""

from __future__ import annotations

import argparse
import glob
import json
import platform
import shutil
import subprocess
from typing import Any


def browser_args_for(os_name: str) -> list[str]:
    if os_name == "Darwin":
        return [
            "--enable-gpu",
            "--ignore-gpu-blocklist",
            "--use-angle=metal",
        ]
    if os_name == "Windows":
        return [
            "--enable-gpu",
            "--ignore-gpu-blocklist",
            "--use-angle=d3d11",
        ]
    return [
        "--enable-gpu",
        "--ignore-gpu-blocklist",
        "--use-gl=angle",
    ]


def select_backend(signals: dict[str, Any]) -> dict[str, Any]:
    os_name = str(signals.get("os", ""))
    hwaccels = {
        str(item).strip().lower()
        for item in signals.get("ffmpeg_hwaccels", [])
        if str(item).strip()
    }
    nvidia = bool(signals.get("nvidia_smi", False))
    vaapi_devices = [
        str(item)
        for item in signals.get("vaapi_devices", [])
        if str(item)
    ]

    backend: str | None = None
    ffmpeg_input_args: list[str] = []

    if nvidia and "cuda" in hwaccels:
        backend = "cuda"
        ffmpeg_input_args = ["-hwaccel", "cuda"]
    elif os_name == "Darwin" and "videotoolbox" in hwaccels:
        backend = "videotoolbox"
        ffmpeg_input_args = ["-hwaccel", "videotoolbox"]
    elif os_name == "Linux" and "vaapi" in hwaccels and vaapi_devices:
        backend = "vaapi"
        ffmpeg_input_args = [
            "-hwaccel",
            "vaapi",
            "-hwaccel_device",
            vaapi_devices[0],
        ]
    elif os_name == "Windows" and "d3d11va" in hwaccels:
        backend = "d3d11va"
        ffmpeg_input_args = ["-hwaccel", "d3d11va"]
    elif "qsv" in hwaccels:
        backend = "qsv"
        ffmpeg_input_args = ["-hwaccel", "qsv"]

    return {
        "gpu_available": backend is not None,
        "backend": backend,
        "ffmpeg_input_args": ffmpeg_input_args,
        "browser_args": browser_args_for(os_name),
        "signals": {
            "os": os_name,
            "ffmpeg_hwaccels": sorted(hwaccels),
            "nvidia_smi": nvidia,
            "vaapi_devices": vaapi_devices,
        },
        "verification": (
            "candidate-backend-detected"
            if backend
            else "no-supported-backend-detected"
        ),
        "note": (
            "Runtime or media decode verification is still required before claiming actual GPU acceleration"
        ),
    }


def command_output(argv: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(
            argv,
            text=True,
            capture_output=True,
            check=False,
            timeout=8,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 127, ""
    return result.returncode, (result.stdout or "") + "\n" + (result.stderr or "")


def parse_hwaccels(output: str) -> list[str]:
    result: list[str] = []
    started = False
    for raw in output.splitlines():
        line = raw.strip()
        if line.lower().startswith("hardware acceleration methods"):
            started = True
            continue
        if not started or not line:
            continue
        token = line.split()[0].strip().lower()
        if token.replace("_", "").replace("-", "").isalnum():
            result.append(token)
    return sorted(set(result))


def probe_signals(ffmpeg_bin: str = "ffmpeg") -> dict[str, Any]:
    code, ffmpeg_output = command_output([ffmpeg_bin, "-hide_banner", "-hwaccels"])
    hwaccels = parse_hwaccels(ffmpeg_output) if code == 0 else []

    nvidia_smi = False
    nvidia_path = shutil.which("nvidia-smi")
    if nvidia_path:
        nvidia_code, _ = command_output([nvidia_path, "-L"])
        nvidia_smi = nvidia_code == 0

    vaapi_devices = sorted(glob.glob("/dev/dri/renderD*"))

    return {
        "os": platform.system(),
        "ffmpeg_present": code == 0,
        "ffmpeg_hwaccels": hwaccels,
        "nvidia_smi": nvidia_smi,
        "vaapi_devices": vaapi_devices,
    }


def evaluate(
    signals: dict[str, Any],
    *,
    require: bool,
    allow_cpu: bool,
) -> tuple[int, dict[str, Any]]:
    gpu = select_backend(signals)
    if gpu["gpu_available"]:
        return 0, {
            "decision": "gpu",
            "reason": "supported-gpu-backend-detected",
            "gpu": gpu,
        }

    if require and not allow_cpu:
        return 3, {
            "decision": "blocked",
            "reason": "gpu-required-but-unavailable",
            "gpu": gpu,
        }

    if allow_cpu:
        return 0, {
            "decision": "cpu-fallback-explicit",
            "reason": "caller-explicitly-allowed-cpu",
            "gpu": gpu,
        }

    return 0, {
        "decision": "cpu",
        "reason": "gpu-not-required-for-this-operation",
        "gpu": gpu,
    }


def parse_signals_json(value: str) -> dict[str, Any]:
    data = json.loads(value)
    if not isinstance(data, dict):
        raise ValueError("--signals-json must contain a JSON object")
    return data


def add_policy_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--require",
        action="store_true",
        help="fail closed when no supported GPU backend is detected",
    )
    parser.add_argument(
        "--allow-cpu",
        action="store_true",
        help="explicitly permit CPU fallback",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect and enforce GPU-first motion execution",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    probe = sub.add_parser("probe", help="probe the current environment")
    add_policy_args(probe)
    probe.add_argument("--ffmpeg-bin", default="ffmpeg")

    evaluate_parser = sub.add_parser(
        "evaluate",
        help="evaluate supplied capability signals",
    )
    add_policy_args(evaluate_parser)
    evaluate_parser.add_argument("--signals-json", required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "probe":
            signals = probe_signals(args.ffmpeg_bin)
        else:
            signals = parse_signals_json(args.signals_json)
    except (json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
        return 2

    code, result = evaluate(
        signals,
        require=bool(args.require),
        allow_cpu=bool(args.allow_cpu),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

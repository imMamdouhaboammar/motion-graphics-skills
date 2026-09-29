#!/usr/bin/env python3
"""Select and enforce GPU-first execution for motion work.

The policy distinguishes three different acceleration claims:
- browser rasterization / WebGL: verified by browser_gpu_probe.cjs
- media decode: selected here and verified against the actual input video
- final encode: selected only when a hardware encoder is actually exposed by FFmpeg

Seeing a GPU device is not enough evidence for any of those claims.
"""

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
        return ["--enable-gpu", "--ignore-gpu-blocklist", "--use-angle=metal"]
    if os_name == "Windows":
        return ["--enable-gpu", "--ignore-gpu-blocklist", "--use-angle=d3d11"]
    return ["--enable-gpu", "--ignore-gpu-blocklist", "--use-gl=angle"]


def choose_encoder(
    os_name: str,
    backend: str | None,
    encoders: set[str],
) -> tuple[str | None, list[str]]:
    candidates: list[tuple[str, list[str]]] = []

    if backend == "cuda":
        candidates.append(("h264_nvenc", ["-c:v", "h264_nvenc"]))
        candidates.append(("hevc_nvenc", ["-c:v", "hevc_nvenc"]))
    elif backend == "videotoolbox" or os_name == "Darwin":
        candidates.append(("h264_videotoolbox", ["-c:v", "h264_videotoolbox"]))
        candidates.append(("hevc_videotoolbox", ["-c:v", "hevc_videotoolbox"]))
    elif backend == "vaapi":
        candidates.append(("h264_vaapi", ["-c:v", "h264_vaapi"]))
        candidates.append(("hevc_vaapi", ["-c:v", "hevc_vaapi"]))
    elif backend == "qsv":
        candidates.append(("h264_qsv", ["-c:v", "h264_qsv"]))
        candidates.append(("hevc_qsv", ["-c:v", "hevc_qsv"]))

    # QSV can be present even when another decoder backend was selected first.
    if "h264_qsv" in encoders:
        candidates.append(("h264_qsv", ["-c:v", "h264_qsv"]))

    for name, args in candidates:
        if name in encoders:
            return name, args
    return None, []


def select_backend(signals: dict[str, Any]) -> dict[str, Any]:
    os_name = str(signals.get("os", ""))
    hwaccels = {
        str(item).strip().lower()
        for item in signals.get("ffmpeg_hwaccels", [])
        if str(item).strip()
    }
    encoders = {
        str(item).strip().lower()
        for item in signals.get("ffmpeg_encoders", [])
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
    elif "qsv" in hwaccels:
        backend = "qsv"
        ffmpeg_input_args = ["-hwaccel", "qsv"]
    elif os_name == "Windows" and "d3d11va" in hwaccels:
        backend = "d3d11va"
        ffmpeg_input_args = ["-hwaccel", "d3d11va"]

    video_encoder, encoder_args = choose_encoder(os_name, backend, encoders)

    return {
        "gpu_available": backend is not None,
        "backend": backend,
        "ffmpeg_input_args": ffmpeg_input_args,
        "video_encoder": video_encoder,
        "encoder_args": encoder_args,
        "encode_accelerated": video_encoder is not None,
        "browser_args": browser_args_for(os_name),
        "signals": {
            "os": os_name,
            "ffmpeg_hwaccels": sorted(hwaccels),
            "ffmpeg_encoders": sorted(encoders),
            "nvidia_smi": nvidia,
            "vaapi_devices": vaapi_devices,
        },
        "verification": (
            "candidate-backend-detected"
            if backend
            else "no-supported-backend-detected"
        ),
        "encode_verification": (
            "candidate-hardware-encoder-detected"
            if video_encoder
            else "no-hardware-encoder-detected"
        ),
        "note": (
            "Browser GPU, media decode, and hardware encode are separate claims and each must be verified on the actual workload"
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


def parse_encoders(output: str) -> list[str]:
    result: list[str] = []
    for raw in output.splitlines():
        line = raw.strip()
        if not line or line.startswith("--") or line.startswith("Encoders:"):
            continue
        # FFmpeg encoder rows look like: V....D h264_nvenc ...
        parts = line.split()
        if len(parts) < 2:
            continue
        flags, name = parts[0], parts[1].lower()
        if "V" not in flags[:2] and not flags.startswith("V"):
            continue
        if name.startswith("="):
            continue
        result.append(name)
    return sorted(set(result))


def probe_signals(ffmpeg_bin: str = "ffmpeg") -> dict[str, Any]:
    hw_code, hw_output = command_output([ffmpeg_bin, "-hide_banner", "-hwaccels"])
    enc_code, enc_output = command_output([ffmpeg_bin, "-hide_banner", "-encoders"])

    hwaccels = parse_hwaccels(hw_output) if hw_code == 0 else []
    encoders = parse_encoders(enc_output) if enc_code == 0 else []

    nvidia_smi = False
    nvidia_path = shutil.which("nvidia-smi")
    if nvidia_path:
        nvidia_code, _ = command_output([nvidia_path, "-L"])
        nvidia_smi = nvidia_code == 0

    vaapi_devices = sorted(glob.glob("/dev/dri/renderD*"))

    return {
        "os": platform.system(),
        "ffmpeg_present": hw_code == 0 or enc_code == 0,
        "ffmpeg_hwaccels": hwaccels,
        "ffmpeg_encoders": encoders,
        "nvidia_smi": nvidia_smi,
        "vaapi_devices": vaapi_devices,
    }


def evaluate(
    signals: dict[str, Any],
    *,
    require: bool,
    allow_cpu: bool,
    require_encode: bool = False,
) -> tuple[int, dict[str, Any]]:
    gpu = select_backend(signals)

    if require_encode and not gpu["encode_accelerated"]:
        if allow_cpu:
            return 0, {
                "decision": "cpu-fallback-explicit",
                "reason": "hardware-encoder-required-but-caller-explicitly-allowed-cpu",
                "gpu": gpu,
            }
        return 4, {
            "decision": "blocked",
            "reason": "hardware-encoder-required-but-unavailable",
            "gpu": gpu,
        }

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
        "--require-encode",
        action="store_true",
        help="fail closed when no supported hardware video encoder is detected",
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
        require_encode=bool(args.require_encode),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

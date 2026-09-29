#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("gpu_policy.py")


def load_module():
    spec = importlib.util.spec_from_file_location("gpu_policy", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load gpu_policy")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GPUPolicyTests(unittest.TestCase):
    def test_prefers_cuda_when_nvidia_and_ffmpeg_cuda_are_available(self) -> None:
        gpu = load_module()
        result = gpu.select_backend({
            "os": "Linux",
            "ffmpeg_hwaccels": ["cuda", "vaapi"],
            "nvidia_smi": True,
            "vaapi_devices": ["/dev/dri/renderD128"],
        })
        self.assertEqual(result["backend"], "cuda")
        self.assertEqual(result["ffmpeg_input_args"], ["-hwaccel", "cuda"])

    def test_uses_videotoolbox_on_macos(self) -> None:
        gpu = load_module()
        result = gpu.select_backend({
            "os": "Darwin",
            "ffmpeg_hwaccels": ["videotoolbox"],
            "nvidia_smi": False,
            "vaapi_devices": [],
        })
        self.assertEqual(result["backend"], "videotoolbox")
        self.assertIn("metal", " ".join(result["browser_args"]))

    def test_uses_vaapi_with_real_render_device(self) -> None:
        gpu = load_module()
        result = gpu.select_backend({
            "os": "Linux",
            "ffmpeg_hwaccels": ["vaapi"],
            "nvidia_smi": False,
            "vaapi_devices": ["/dev/dri/renderD129"],
        })
        self.assertEqual(result["backend"], "vaapi")
        self.assertEqual(
            result["ffmpeg_input_args"],
            ["-hwaccel", "vaapi", "-hwaccel_device", "/dev/dri/renderD129"],
        )

    def test_does_not_invent_backend_from_os_alone(self) -> None:
        gpu = load_module()
        result = gpu.select_backend({
            "os": "Darwin",
            "ffmpeg_hwaccels": [],
            "nvidia_smi": False,
            "vaapi_devices": [],
        })
        self.assertIsNone(result["backend"])
        self.assertFalse(result["gpu_available"])

    def test_require_mode_rejects_software_only_environment(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "evaluate", "--require", "--signals-json", json.dumps({
                "os": "Linux",
                "ffmpeg_hwaccels": [],
                "nvidia_smi": False,
                "vaapi_devices": [],
            })],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 3)
        data = json.loads(result.stdout)
        self.assertEqual(data["decision"], "blocked")
        self.assertEqual(data["reason"], "gpu-required-but-unavailable")

    def test_explicit_cpu_fallback_is_visible(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "evaluate", "--require", "--allow-cpu", "--signals-json", json.dumps({
                "os": "Linux",
                "ffmpeg_hwaccels": [],
                "nvidia_smi": False,
                "vaapi_devices": [],
            })],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["decision"], "cpu-fallback-explicit")
        self.assertFalse(data["gpu"]["gpu_available"])

    def test_gpu_backend_is_allowed_in_require_mode(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "evaluate", "--require", "--signals-json", json.dumps({
                "os": "Linux",
                "ffmpeg_hwaccels": ["cuda"],
                "nvidia_smi": True,
                "vaapi_devices": [],
            })],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["decision"], "gpu")
        self.assertEqual(data["gpu"]["backend"], "cuda")


if __name__ == "__main__":
    unittest.main()

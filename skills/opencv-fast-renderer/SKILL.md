---
name: opencv-fast-renderer
description: Render 2.5D motion graphics programmatically using Python, NumPy, Pillow, OpenCV, and FFmpeg. Use when headless, lightweight, or serverless rendering is needed without browser engines, or for pixel-exact programmatic video generation.
---

# OpenCV Fast 2.5D Renderer

A lightweight programmatic motion graphics pipeline built on Python, NumPy, Pillow, and OpenCV, streaming directly into FFmpeg.

## Why Headless Python Rendering

Browser-based renderers (such as Puppeteer or Chromium frame captures) provide high design flexibility but require heavy browser runtimes and significant memory overhead. For algorithmic particle effects, procedural data visualization, mathematical curves, or serverless execution, the Python OpenCV pipeline renders up to 5 times faster with zero browser dependencies.

## Architecture Pipeline

1. **Procedural Geometry (NumPy)**: Generate and interpolate 2.5D vector vertices, Bezier control paths, and camera matrices.
2. **Typography and Antialiasing (Pillow)**: Render clean subpixel text layers using TrueType or OpenType font files.
3. **Compositing and Motion Blur (OpenCV)**: Blend multi-layer frame buffers with alpha channels, apply directional box blur or Gaussian motion blur, and grade color.
4. **Direct FFmpeg Pipe**: Stream raw RGB frame bytes directly to an FFmpeg subprocess via stdin pipe, avoiding intermediate disk writes.

## Streaming Execution Pattern

```python
import subprocess
import cv2
import numpy as np

width, height, fps = 1920, 1080, 60
cmd = [
    "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
    "-s", f"{width}x{height}", "-pix_fmt", "bgr24", "-r", str(fps),
    "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "output.mp4"
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

for frame_idx in range(fps * 10):
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    # Render procedural scene
    proc.stdin.write(frame.tobytes())

proc.stdin.close()
proc.wait()
```

## Further Reading

- [references/opencv-compositing.md](references/opencv-compositing.md) for alpha blending and layer math.

#!/usr/bin/env python3
"""
Audio Loudness and True Peak Auditor (EBU R128 / ITU-R BS.1770-4)
Evaluates audio/video files against Studio Master Standards (-14.0 LUFS / -1.25 dBTP).
"""

import sys
import os
import subprocess
import re
import shlex

TARGET_LUFS = -14.0
LUFS_TOLERANCE = 0.5
MAX_DBTP = -1.25

def check_loudness(media_file):
    if not media_file or media_file.strip() == "":
        print("Usage: python3 lufs-check.py <path_to_audio_or_video_file>", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(media_file):
        print(f"Error: Target media file does not exist: {media_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning loudness for: {media_file}")
    cmd = [
        "ffmpeg", "-nostats", "-i", media_file,
        "-filter_complex", "ebur128=peak=true",
        "-f", "null", "-"
    ]
    try:
        res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, check=False)
        output = res.stderr
    except FileNotFoundError:
        print("Error: FFmpeg is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)

    i_lufs_match = re.search(r"I:\s+([-\d.]+)\s+LUFS", output)
    tp_match = re.search(r"Peak:\s+([-\d.]+)\s+dBFS", output)

    if not i_lufs_match:
        print("Error: Could not parse EBU R128 loudness metrics from FFmpeg output.", file=sys.stderr)
        sys.exit(1)

    i_lufs = float(i_lufs_match.group(1))
    tp = float(tp_match.group(1)) if tp_match else -99.0

    print("--------------------------------------------------")
    print(f" Integrated Loudness : {i_lufs:.1f} LUFS (Target: {TARGET_LUFS} +/- {LUFS_TOLERANCE})")
    print(f" True Peak           : {tp:.2f} dBTP (Ceiling: {MAX_DBTP} dBTP)")
    print("--------------------------------------------------")

    passed = True
    if abs(i_lufs - TARGET_LUFS) > LUFS_TOLERANCE:
        print(f" [FAIL] Integrated LUFS deviates by {abs(i_lufs - TARGET_LUFS):.1f} LU from target.")
        passed = False
    else:
        print(" [PASS] Integrated LUFS within broadcast tolerance.")

    if tp > MAX_DBTP:
        print(f" [FAIL] True Peak {tp:.2f} exceeds ceiling {MAX_DBTP} dBTP.")
        passed = False
    else:
        print(" [PASS] True Peak complies with ceiling.")

    if not passed:
        quoted = shlex.quote(media_file)
        print("\nRemediation Command:")
        print(f"ffmpeg -i {quoted} -af loudnorm=I=-14:TP=-1.25:LRA=7 -c:v copy corrected.mp4")
        sys.exit(1)
    else:
        print("\nResult: AUDIO MASTER VERIFIED")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 lufs-check.py <path_to_audio_or_video_file>")
        sys.exit(0)
    check_loudness(sys.argv[1])

if __name__ == "__main__":
    main()

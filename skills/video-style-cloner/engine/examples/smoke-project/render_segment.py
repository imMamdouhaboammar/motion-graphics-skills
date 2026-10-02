"""Technical smoke renderer. Produces a test card, not a style-cloned film."""
import argparse
import json
import subprocess
from pathlib import Path

p = argparse.ArgumentParser()
for name in ("project", "plan", "segment", "engine", "shot-ids", "frames"):
    p.add_argument("--" + name, required=True)
p.add_argument("--fixes")
a = p.parse_args()
plan = json.loads(Path(a.plan).read_text())
ids = {int(x) for x in a.shot_ids.split(",")}
# The smoke plan's 24 beats are 24 frames at its explicitly chosen one beat/frame.
frames = sum(s["beats"] for s in plan["shots"] if s["id"] in ids)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "testsrc2=size=160x90:rate=24", "-frames:v", str(frames),
                "-threads", "1", str(Path(a.frames) / "frame_%06d.png")], check=True)

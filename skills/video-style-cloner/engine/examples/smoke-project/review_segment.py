"""Independent technical smoke QA. Does not assess visual style or creative quality."""
import argparse
import json
import subprocess
from pathlib import Path

p = argparse.ArgumentParser()
for name in ("project", "plan", "segment", "frames"):
    p.add_argument("--" + name, required=True)
a = p.parse_args()
frames = sorted(Path(a.frames).glob("frame_*.png"))
expected = sum(s["beats"] for s in json.loads(Path(a.plan).read_text())["shots"])
passed = bool(frames) and len(frames) == expected
r = subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i",
                    str(Path(a.frames) / "frame_%06d.png"), "-f", "null", "-"], capture_output=True)
passed = passed and r.returncode == 0
print(json.dumps({"passed": passed, "score": 5 if passed else 0,
                  "failures": [] if passed else [{"category": "technical", "item": "Missing, corrupt or unexpected frame count", "severity": "Critical"}]}))

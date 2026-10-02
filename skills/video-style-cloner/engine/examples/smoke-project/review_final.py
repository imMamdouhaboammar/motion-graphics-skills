"""Technical final smoke QA. Production adapters must additionally review creative quality."""
import argparse
import json
import subprocess

p = argparse.ArgumentParser()
for name in ("project", "plan", "video"):
    p.add_argument("--" + name, required=True)
a = p.parse_args()
r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                    "stream=nb_frames,width,height,r_frame_rate", "-of", "json", a.video], capture_output=True, text=True)
stream = json.loads(r.stdout).get("streams", [{}])[0] if r.returncode == 0 else {}
passed = stream.get("nb_frames") == "24" and stream.get("width") == 1920 and stream.get("height") == 1080 and stream.get("r_frame_rate") == "24/1"
print(json.dumps({"passed": passed, "score": 5 if passed else 0,
                  "failures": [] if passed else [{"category": "technical", "item": "Final video has unexpected dimensions, FPS or duration", "severity": "Critical"}]}))

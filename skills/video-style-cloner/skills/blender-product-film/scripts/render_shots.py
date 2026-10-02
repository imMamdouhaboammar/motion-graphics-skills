#!/usr/bin/env python3
"""render_shots.py — render every shot spec in <build>/shots/*.json with Blender, then make a review sheet per shot.

    python render_shots.py <build_dir> --quality preview|final|cycles [--only S1,S4] [--stills auto|0.5,1.5] [--sheet-every 0.5] [--cut]
    --cut: cut the rendered frames with build/edit.json into out/<quality>_cut.mp4 and run compare.py against the reference

Frames go to <build>/renders/<quality>/<id>/f####.png; review sheets to <build>/../out/check/<id>_<quality>.jpg
(one tile every --sheet-every seconds, timestamped). --stills renders just those times per shot (fast look-dev).
"""
import argparse, glob, json, os, subprocess, sys, time, shutil
from PIL import Image, ImageDraw

BLENDER = os.environ.get("BLENDER") or shutil.which("blender") or "blender"
HERE = os.path.dirname(os.path.abspath(__file__))


def sheet(frames, fps, every, out, label):
    picks = frames[::max(1, round(every * fps))][:12]
    if not picks: return
    ims = [Image.open(f).convert("RGB") for f in picks]; w = 480; h = round(ims[0].height * w / ims[0].width)
    cols = min(6, len(ims)); rows = -(-len(ims) // cols)
    S = Image.new("RGB", (cols * w, rows * h + 30), (20, 20, 20)); d = ImageDraw.Draw(S)
    d.text((8, 6), label, fill=(230, 230, 230))
    for i, (im, f) in enumerate(zip(ims, picks)):
        x, y = (i % cols) * w, 30 + (i // cols) * h; S.paste(im.resize((w, h)), (x, y))
        idx = frames.index(f); d.rectangle([x, y, x + 64, y + 18], fill=(0, 0, 0)); d.text((x + 4, y + 3), f"{idx / fps:.2f}s", fill=(255, 255, 255))
    S.save(out, quality=90)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("build"); ap.add_argument("--quality", default="preview")
    ap.add_argument("--only"); ap.add_argument("--stills"); ap.add_argument("--sheet-every", type=float, default=0.5)
    ap.add_argument("--cut", action="store_true", help="after rendering, cut these frames with build/edit.json and run video-clone compare.py")
    a = ap.parse_args()
    shots = sorted(glob.glob(os.path.join(a.build, "shots", "*.json")))
    if a.only: shots = [s for s in shots if os.path.splitext(os.path.basename(s))[0] in a.only.split(",")]
    check = os.path.join(a.build, "..", "out", "check"); os.makedirs(check, exist_ok=True)
    for sp in shots:
        sid = os.path.splitext(os.path.basename(sp))[0]; spec = json.load(open(sp, encoding="utf-8")); fps = spec.get("fps", 30)
        out = os.path.join(a.build, "renders", "stills" if a.stills else a.quality, sid)
        if not a.stills and os.path.isdir(out): shutil.rmtree(out)
        cmd = [BLENDER, "-b", "--factory-startup", "-P", os.path.join(HERE, "pfilm.py"), "--", "--shot", sp, "--out", out, "--quality", a.quality]
        if a.stills:   # "auto" = start / middle / end of THIS shot (shots have different lengths)
            d = spec.get("duration", 3.0)
            st = f"{min(0.15, d * 0.1):.2f},{d / 2:.2f},{max(0, d - 0.15):.2f}" if a.stills == "auto" else a.stills
            cmd += ["--stills", st]
        t0 = time.time(); r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if "PFILM_DONE" not in r.stdout:
            print(f"{sid}: FAILED\n" + "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "Error" in l or "Traceback" in l or "line " in l)[-2000:]); continue
        for l in r.stdout.splitlines():
            if l.startswith("PFILM_WARN"): print("  ⚠", l[11:])
        frames = sorted(glob.glob(os.path.join(out, "*.png")))
        el = time.time() - t0
        if a.stills:
            sheet(frames, 1, 1, os.path.join(check, f"{sid}_stills.jpg"), f"{sid} stills {a.stills}")
        else:
            sheet(frames, fps, a.sheet_every, os.path.join(check, f"{sid}_{a.quality}.jpg"), f"{sid} · {a.quality} · {len(frames)} frames")
        print(f"{sid}: {len(frames)} images in {el:.0f}s ({el / max(1, len(frames)):.2f}s each)")
    if a.cut and not a.stills:
        ed_path = os.path.join(a.build, "edit.json")
        if not os.path.exists(ed_path): print("--cut: no build/edit.json yet"); return
        ed = json.load(open(ed_path, encoding="utf-8"))
        for sh in ed["shots"]:
            if sh.get("frames"): sh["frames"] = f"renders/{a.quality}/{sh['id']}"
        ed["out"] = f"../out/{a.quality}_cut.mp4"
        if a.quality == "preview": ed["size"] = [960, 540]
        tmp = os.path.join(a.build, f"edit_{a.quality}.json"); json.dump(ed, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        subprocess.run([sys.executable, os.path.join(HERE, "finish.py"), tmp], check=True)
        cmp = os.path.join(HERE, "..", "..", "video-clone", "scripts", "compare.py")
        proj = os.path.abspath(os.path.join(a.build, ".."))
        subprocess.run([sys.executable, cmp, proj, "--video", f"out/{a.quality}_cut.mp4"])


if __name__ == "__main__":
    main()

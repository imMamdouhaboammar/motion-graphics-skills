#!/usr/bin/env python3
"""finish.py — edit the rendered shots into the film: transitions, 2D titles, music + SFX, grade. System python (Pillow, numpy).

    python finish.py edit.json            (paths inside edit.json are relative to the edit.json folder)

edit.json:
{
  "fps": 30, "size": [1920, 1080], "out": "out/video.mp4",
  "shots": [
    { "id": "S1", "frames": "renders/S1", "trim": [0, 4.0],                 # seconds of that shot to use (optional)
      "in": { "type": "fade_black", "dur": 0.5 },                           # cut · fade_black · crossfade · flash_white · dip_white
      "text": [ { "segments": [["天然", "#7A7A7A"], ["鹼性離子水", "#FFFFFF"]], "at": [0.8, 3.6],
                  "x": 0.5, "y": 0.82, "size": 0.045, "weight": "medium", "align": "center",
                  "reveal": "rise", "stagger": 0.12, "tracking": 0.06 } ] }
  ],
  "music": { "file": "assets/music.mp3", "start": 0, "gain_db": -2, "fade_in": 0.3, "fade_out": 2.0 },
  "sfx": [ { "file": "assets/whoosh.mp3", "at": 3.9, "gain_db": -6 } ],
  "grade": { "vignette": 0.25, "grain": 3 }
}
Title cards need no render: give the shot "card": { "duration", "bg", "glow", "glow_strength", "zoom": [from, to] } instead of "frames".
Title positions are fractions of the frame (x, y = anchor point; y is the text's vertical centre). size = glyph height / frame height.
reveal: rise (fade + lift, per segment) · light_up (segments start grey, light up one by one) · wipe (left→right) · fade.
Titles are drawn crisp in 2D after rendering, never inside the 3D scene (depth of field would blur them).
"""
import json, os, subprocess, sys, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FFMPEG_FALLBACK = os.environ.get("FFMPEG_DIR", "")   # folder with ffmpeg/ffprobe when they are not on PATH
if not shutil.which("ffmpeg") and FFMPEG_FALLBACK and os.path.isdir(FFMPEG_FALLBACK): os.environ["PATH"] += os.pathsep + FFMPEG_FALLBACK
VF = "C:/Windows/Fonts/NotoSansTC-VF.ttf"
WEIGHTS = {"thin": 200, "light": 300, "regular": 400, "medium": 500, "bold": 700, "black": 900}
_font_cache = {}


def font(px, weight="medium"):
    key = (px, weight)
    if key in _font_cache: return _font_cache[key]
    try:
        f = ImageFont.truetype(VF, px)
        try: f.set_variation_by_axes([WEIGHTS.get(weight, 500)])
        except Exception: pass
    except Exception:
        f = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", px)
    _font_cache[key] = f; return f


ease = lambda x: (lambda t: t * t * (3 - 2 * t))(min(1, max(0, x)))
def hexrgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def draw_titles(frame, items, t, W, H):
    """Composite the titles active at shot time t onto frame (PIL RGB)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for it in items:
        t0, t1 = it.get("at", [0, 999])
        if t < t0 - 0.01 or t > t1: continue
        px = max(8, round(it.get("size", 0.045) * H / 0.72)); f = font(px, it.get("weight", "medium"))
        track = it.get("tracking", 0.04) * px
        segs = it.get("segments") or [[it.get("content", ""), it.get("color", "#FFFFFF")]]
        widths = [d.textlength(s, font=f) + track * max(0, len(s) - 1) for s, _ in segs]
        gap = px * 0.18; total = sum(widths) + gap * (len(segs) - 1)
        ax = it.get("x", 0.5) * W; al = it.get("align", "center")
        x = ax - total / 2 if al == "center" else ax if al == "left" else ax - total
        yc = it.get("y", 0.82) * H
        out_k = 1 - ease((t - (t1 - 0.4)) / 0.4) if t1 < 900 else 1
        rv = it.get("reveal", "rise"); st = it.get("stagger", 0.12)
        for i, ((txt, col), w) in enumerate(zip(segs, widths)):
            k = ease((t - t0 - i * st) / 0.55)
            a = k * out_k; dy = (1 - k) * px * 0.4 if rv == "rise" else 0
            c = hexrgb(col)
            if rv == "light_up":   # grey first, then this segment lights up to its colour in turn
                a = min(1, ease((t - t0) / 0.4)) * out_k; kk = ease((t - t0 - 0.3 - i * max(st, 0.25)) / 0.35)
                g = (90, 90, 90); c = tuple(round(g[j] + (c[j] - g[j]) * kk) for j in range(3))
            if rv == "wipe": a = out_k
            cx = x
            for ch in txt:   # per-glyph so tracking applies
                d.text((cx, yc + dy), ch, font=f, fill=(*c, round(255 * a)), anchor="lm")
                cx += d.textlength(ch, font=f) + track
            if rv == "wipe":
                p = ease((t - t0 - i * st) / 0.7); cut = round(x + w * p)
                if cut < x + w: ImageDraw.Draw(layer).rectangle([cut, yc - px, x + w + 2, yc + px], fill=(0, 0, 0, 0))
            x += w + gap
    return Image.alpha_composite(frame.convert("RGBA"), layer).convert("RGB")


def card_frames(sh, fps, W, H):
    """A title card with no render: black (or a soft coloured glow frame) + the shot's titles, with a slow zoom.
    card: { "duration": 1.5, "bg": "#000000", "glow": "#2AA8D8", "glow_strength": 0.6, "zoom": [1.06, 1.0] }"""
    c = sh["card"]; n = max(1, round(c.get("duration", 1.5) * fps)); z0, z1 = c.get("zoom", [1.04, 1.0])
    bg = Image.new("RGB", (W, H), hexrgb(c.get("bg", "#000000")))
    if c.get("glow"):   # a glow around the frame edges, dark in the middle
        yy, xx = np.mgrid[0:H, 0:W]   # rounded-rectangle distance (superellipse): no diagonal seams in the corners
        d = ((np.abs(xx - W / 2) / (W / 2)) ** 5 + (np.abs(yy - H / 2) / (H / 2)) ** 5) ** 0.2
        k = (np.clip((d - 0.55) / 0.45, 0, 1) ** 2 * c.get("glow_strength", 0.6))[..., None]
        bg = Image.fromarray((np.asarray(bg).astype(np.float32) * (1 - k) + np.array(hexrgb(c["glow"])) * k).clip(0, 255).astype(np.uint8))
    return [("card", i, n, z0 + (z1 - z0) * ease(i / max(1, n - 1)), bg) for i in range(n)]


def render_card_frame(entry, sh, W, H, fps):
    _, i, n, z, bg = entry
    layer = draw_titles(Image.new("RGB", (W, H), (0, 0, 0)), sh.get("text", []), i / fps, W, H)
    if abs(z - 1) > 1e-3:
        big = layer.resize((round(W * z), round(H * z)), Image.LANCZOS)
        if z > 1:
            x, y = (big.width - W) // 2, (big.height - H) // 2; layer = big.crop((x, y, x + W, y + H))
        else:
            canvas = Image.new("RGB", (W, H)); canvas.paste(big, ((W - big.width) // 2, (H - big.height) // 2)); layer = canvas
    return Image.fromarray(np.maximum(np.asarray(bg), np.asarray(layer)))


def shot_frames(sh, base, fps):
    if sh.get("card"): return None
    fr = sorted(f for f in os.listdir(os.path.join(base, sh["frames"])) if f.lower().endswith(".png"))
    if "trim" in sh:
        a, b = sh["trim"]; fr = fr[round(a * fps):round(b * fps)]
    return [os.path.join(base, sh["frames"], f) for f in fr]


def main():
    ed_path = sys.argv[1]; base = os.path.dirname(os.path.abspath(ed_path)); ed = json.load(open(ed_path, encoding="utf-8"))
    fps = ed.get("fps", 30); W, H = ed.get("size", [1920, 1080]); out = os.path.join(base, ed.get("out", "out/video.mp4"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out + ".video.mp4"
    g = ed.get("grade", {})
    vf = []
    if g.get("vignette", 0.25): vf.append(f"vignette=angle={0.25 + g.get('vignette', 0.25):.2f}")
    if g.get("grain", 3): vf.append(f"noise=alls={g.get('grain', 3)}:allf=t")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                            *(["-vf", ",".join(vf)] if vf else []), "-c:v", "libx264", "-crf", "15", "-preset", "slow", "-pix_fmt", "yuv420p", tmp],
                           stdin=subprocess.PIPE)
    load = lambda p: Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS) if Image.open(p).size != (W, H) else Image.open(p).convert("RGB")
    prev_tail = []; total = 0
    shots = ed["shots"]
    for si, sh in enumerate(shots):
        files = shot_frames(sh, base, fps); tr = sh.get("in", {"type": "cut"}); n_in = round(tr.get("dur", 0.4) * fps)
        if files is None: files = card_frames(sh, fps, W, H)
        # crossfade: hold back the next shot's overlap from the previous one
        nxt = shots[si + 1].get("in", {}) if si + 1 < len(shots) else {}
        hold = round(nxt.get("dur", 0.4) * fps) if nxt.get("type") == "crossfade" else 0
        body = files[: len(files) - hold] if hold else files
        for i, fpath in enumerate(body):
            t = i / fps
            img = render_card_frame(fpath, sh, W, H, fps) if isinstance(fpath, tuple) else draw_titles(load(fpath), sh.get("text", []), t, W, H)
            arr = np.asarray(img).astype(np.float32)
            typ = tr.get("type", "cut")
            if si == 0 and typ == "cut": typ = "fade_black"   # never start on a hard frame
            if typ == "fade_black" and i < n_in: arr *= ease(i / n_in)
            if typ in ("flash_white", "dip_white") and i < n_in: arr = arr + (255 - arr) * (1 - ease(i / n_in))
            if typ == "crossfade" and prev_tail and i < len(prev_tail):
                k = ease((i + 1) / (len(prev_tail) + 1)); arr = np.asarray(prev_tail[i]).astype(np.float32) * (1 - k) + arr * k
            # fade to black at the end of the film, and before a fade_black / dip into the next shot
            n_out = round(nxt.get("dur", 0.4) * fps) if nxt.get("type") in ("fade_black", "dip_white") else 0
            if si == len(shots) - 1: n_out = round(ed.get("end_fade", 0.8) * fps)
            rem = len(body) - 1 - i
            if n_out and rem < n_out:
                k = ease(rem / n_out)
                arr = arr * k if (nxt.get("type") != "dip_white" or si == len(shots) - 1) else arr + (255 - arr) * (1 - k)
            enc.stdin.write(arr.clip(0, 255).astype(np.uint8).tobytes()); total += 1
        prev_tail = [(render_card_frame(f, sh, W, H, fps) if isinstance(f, tuple) else draw_titles(load(f), sh.get("text", []), (len(body) + j) / fps, W, H)) for j, f in enumerate(files[len(body):])] if hold else []
    enc.stdin.close(); enc.wait()
    dur = total / fps
    # audio: music (trimmed, faded) + SFX at their times, normalised
    m = ed.get("music"); sfx = ed.get("sfx", [])
    if m or sfx:
        ins, flt, labels = [], [], []
        if m:
            ins += ["-ss", str(m.get("start", 0)), "-t", f"{dur:.3f}", "-i", os.path.join(base, m["file"])]
            flt.append(f"[1:a]volume={m.get('gain_db', 0)}dB,afade=t=in:d={m.get('fade_in', 0.3)},afade=t=out:st={max(0, dur - m.get('fade_out', 2)):.3f}:d={m.get('fade_out', 2)}[m]"); labels.append("[m]")
        base_i = 2 if m else 1   # input 0 is the video
        for k, s_ in enumerate(sfx):
            ins += ["-i", os.path.join(base, s_["file"])]
            ms = int(s_["at"] * 1000); flt.append(f"[{base_i + k}:a]adelay={ms}|{ms},volume={s_.get('gain_db', -6)}dB[s{k}]"); labels.append(f"[s{k}]")
        flt.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=longest,apad,atrim=0:{dur:.3f},loudnorm=I=-14:TP=-1.5[a]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, *ins, "-filter_complex", ";".join(flt), "-map", "0:v", "-map", "[a]",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-t", f"{dur:.3f}", out], check=True)
        os.remove(tmp)
    else:
        os.replace(tmp, out)
    print(f"wrote {out}  {dur:.2f}s  {total} frames")


if __name__ == "__main__":
    main()

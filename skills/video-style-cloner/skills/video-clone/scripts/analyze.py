#!/usr/bin/env python3
"""analyze.py — take a reference video (local file or URL) apart for style cloning.

    python analyze.py <file-or-url> --out <project>/analysis

Writes into --out:
    source.mp4        the input (downloaded with yt-dlp if a URL was given)
    proxy.mp4         the video cropped to the real picture (phone UI / letterbox removed) when a crop was needed
    audio.wav         mono audio, phase-safe and loudness-normalised (only if the input has sound)
    sheet_1fps.jpg    one frame per second, tiled — look at this first
    sheet_scenes.jpg  the middle frame of every detected shot
    report.json       everything measured: size, crop, shots, pacing, tempo, beats, audio health, best 30 s windows

Lessons baked in (each one broke a real run):
    - phone screen recordings: the video is a strip in the middle of a UI → cropdetect, then analyse the proxy
    - stereo recordings with inverted phase cancel to silence when summed to mono → measure L, R and L+R separately
    - loudness: normalise the chosen channel so beat tracking sees the music, not the noise floor
"""
import argparse, json, os, re, shutil, subprocess, sys, collections

FFMPEG_FALLBACK = os.environ.get("FFMPEG_DIR", "")   # folder with ffmpeg/ffprobe when they are not on PATH
if not shutil.which("ffmpeg") and FFMPEG_FALLBACK and os.path.isdir(FFMPEG_FALLBACK):
    os.environ["PATH"] += os.pathsep + FFMPEG_FALLBACK


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate,channels",
             "-of", "json", path])
    j = json.loads(r.stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    fps = None
    if v and v.get("r_frame_rate") and v["r_frame_rate"] != "0/0":
        n, d = v["r_frame_rate"].split("/"); fps = round(float(n) / float(d), 3)
    return {"duration": float(j["format"]["duration"]), "width": v and v["width"], "height": v and v["height"], "fps": fps,
            "has_audio": a is not None, "channels": a and a.get("channels")}


def fetch(src, out):
    if os.path.isfile(src):
        dst = os.path.join(out, "source" + os.path.splitext(src)[1].lower())
        shutil.copyfile(src, dst); return dst
    # a URL: yt-dlp (the user is responsible for having the right to use the material)
    tmpl = os.path.join(out, "source.%(ext)s")
    r = run([sys.executable, "-m", "yt_dlp", "-f", "bv*[height<=720]+ba/b[height<=720]/b", "--merge-output-format", "mp4",
             "-o", tmpl, "--no-playlist", src])
    if r.returncode:
        sys.exit("download failed:\n" + r.stderr[-2000:])
    for f in os.listdir(out):
        if f.startswith("source."): return os.path.join(out, f)
    sys.exit("download produced no file")


def detect_crop(path, dur, w, h):
    """Most common cropdetect box over the whole video; None if the picture already fills the frame."""
    r = run(["ffmpeg", "-hide_banner", "-i", path, "-t", str(min(dur, 60)), "-vf", "fps=2,cropdetect=limit=24:round=2:reset=1",
             "-f", "null", "-"])
    boxes = collections.Counter(re.findall(r"crop=(\d+:\d+:\d+:\d+)", r.stderr))
    if not boxes: return None
    cw, ch, cx, cy = map(int, boxes.most_common(1)[0][0].split(":"))
    if cw * ch > .85 * w * h: return None
    return {"w": cw, "h": ch, "x": cx, "y": cy, "note": "picture is a strip inside a larger frame (screen recording / letterbox)"}


def ui_strip_crop(path, dur, w, h):
    """Phone screen recordings put the video between two busy UI bands that cropdetect can't see through (they aren't
    black). Find the band of rows whose content changes most over time: that's the playing video."""
    try:
        import numpy as np, cv2
    except ImportError:
        return None
    cap = cv2.VideoCapture(path); frames = []
    for k in range(12):
        cap.set(cv2.CAP_PROP_POS_MSEC, (k + .5) / 12 * dur * 1000)
        ok, f = cap.read()
        if ok: frames.append(cv2.cvtColor(cv2.resize(f, (w // 4, h // 4)), cv2.COLOR_BGR2GRAY).astype("float32"))
    cap.release()
    if len(frames) < 4: return None
    var = np.stack(frames).std(axis=0).mean(axis=1)            # temporal change per row
    rows = np.where(var > max(6.0, var.max() * .35))[0]
    if not len(rows): return None
    # the longest run of consecutive active rows
    runs, start = [], rows[0]
    for a, b in zip(rows, rows[1:]):
        if b != a + 1: runs.append((start, a)); start = b
    runs.append((start, rows[-1]))
    y0, y1 = max(runs, key=lambda r: r[1] - r[0])
    y0, y1 = int(y0 * 4), int((y1 + 1) * 4)
    if (y1 - y0) > .85 * h or (y1 - y0) < .15 * h: return None
    return {"w": w, "h": (y1 - y0) // 2 * 2, "x": 0, "y": y0, "note": "moving picture band between static UI (phone screen recording)"}


def make_proxy(path, crop, out):
    """Analysis copy: cropped to the picture (if needed) and with a keyframe every 12 frames, so the hundreds of random
    seeks in shot_details() decode a few frames instead of up to 8 s of video each (same pixels, ~2x faster analysis)."""
    dst = os.path.join(out, "proxy.mp4")
    vf = ["-vf", f"crop={crop['w']}:{crop['h']}:{crop['x']}:{crop['y']}"] if crop else []
    run(["ffmpeg", "-v", "error", "-y", "-i", path, *vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-g", "12", "-an", dst])
    return dst


def shots(path):
    try:
        from scenedetect import detect, ContentDetector
    except ImportError:
        return []
    lst = detect(path, ContentDetector(threshold=22))
    sec = lambda x: x.seconds if hasattr(type(x), "seconds") else x.get_seconds()
    return [[round(sec(a), 3), round(sec(b), 3)] for a, b in lst]


def sheets(path, dur, cuts, out):
    n = int(min(dur, 64)); cols = 8; rows = max(1, -(-n // cols))
    run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", f"fps={n / dur:.5f},scale=300:-2,tile={cols}x{rows}", "-frames:v", "1",
         os.path.join(out, "sheet_1fps.jpg")])
    if cuts:
        try:
            import cv2, numpy as np
        except ImportError:
            return
        step = max(1, len(cuts) // 48); mids = [(a + b) / 2 for a, b in cuts][::step][:48]
        cap = cv2.VideoCapture(path); tiles = []
        for m in mids:
            cap.set(cv2.CAP_PROP_POS_MSEC, m * 1000); ok, f = cap.read()
            if ok:
                f = cv2.resize(f, (300, round(300 * f.shape[0] / f.shape[1])))
                cv2.putText(f, f"{m:.1f}s", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3); cv2.putText(f, f"{m:.1f}s", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
                tiles.append(f)
        cap.release()
        if tiles:
            h = tiles[0].shape[0]; tiles = [t if t.shape[0] == h else cv2.resize(t, (300, h)) for t in tiles]
            while len(tiles) % 8: tiles.append(np.zeros_like(tiles[0]))
            grid = np.vstack([np.hstack(tiles[r:r + 8]) for r in range(0, len(tiles), 8)])
            cv2.imwrite(os.path.join(out, "sheet_scenes.jpg"), grid, [cv2.IMWRITE_JPEG_QUALITY, 85])


def shot_details(path, cuts, dur):
    """Same as _shot_details_part over all shots, split across processes (seeking a long video is the slow part)."""
    spans = cuts or [[0.0, dur]]
    n = min(8, max(1, (os.cpu_count() or 2) - 1), max(1, len(spans) // 12))
    if n <= 1: return _shot_details_part(path, spans, 0)
    from concurrent.futures import ProcessPoolExecutor
    size = -(-len(spans) // n); parts = [(path, spans[k:k + size], k) for k in range(0, len(spans), size)]
    with ProcessPoolExecutor(len(parts)) as ex:
        res = list(ex.map(_shot_details_star, parts))
    return [x for part in res for x in part]


def _shot_details_star(args): return _shot_details_part(*args)


def _shot_details_part(path, spans, offset):
    """Per shot: camera motion (optical flow → push/pull/pan/tilt/rotate/static + speed) and look (brightness, contrast,
    dark ratio, colourfulness, dominant colours). These numbers let the plan and the review match the reference shot by shot."""
    try:
        import numpy as np, cv2
    except ImportError:
        return []
    cap = cv2.VideoCapture(path); out = []
    for i, (a, b) in enumerate(spans, offset):
        n = max(3, min(10, int((b - a) * 5))); ts = [a + (b - a) * (k + .5) / n for k in range(n)]
        grays, looks = [], []
        for t in ts:
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, f = cap.read()
            if not ok: continue
            sm = cv2.resize(f, (320, round(320 * f.shape[0] / f.shape[1])))
            grays.append(cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY)); looks.append(sm)
        if len(grays) < 2: continue
        H_, W_ = grays[0].shape; yy, xx = np.mgrid[0:H_, 0:W_]; xc, yc = xx - W_ / 2, yy - H_ / 2
        tx = ty = zoom = rot = 0.0
        for g0, g1 in zip(grays, grays[1:]):
            fl = cv2.calcOpticalFlowFarneback(g0, g1, None, .5, 3, 21, 3, 5, 1.2, 0)
            u, v = fl[..., 0], fl[..., 1]
            # only textured pixels carry motion information (black stages and static UI bars would pull the median to 0)
            gx = cv2.Sobel(g0, cv2.CV_32F, 1, 0); gy = cv2.Sobel(g0, cv2.CV_32F, 0, 1)
            tex = np.hypot(gx, gy) > 40
            tex[: max(1, H_ // 25)] = False   # ignore a thin top strip (browser tab bars in screen recordings)
            if tex.sum() < 200: continue
            uu, vv, xx_, yy_ = u[tex], v[tex], xc[tex], yc[tex]
            tx += float(np.median(uu)); ty += float(np.median(vv))
            r2 = xx_ ** 2 + yy_ ** 2 + 1e-6
            zoom += float(np.median((uu * xx_ + vv * yy_) / r2)); rot += float(np.median((vv * xx_ - uu * yy_) / r2))
        span = ts[-1] - ts[0] or 1
        mv = {"pan_x": round(tx / W_ / span, 4), "tilt_y": round(ty / H_ / span, 4), "zoom": round(zoom / span, 4), "rotate": round(rot / span, 4)}
        kind = []
        if abs(mv["zoom"]) > 0.006: kind.append("push_in" if mv["zoom"] > 0 else "pull_out")
        if abs(mv["pan_x"]) > 0.008: kind.append("move_left" if mv["pan_x"] > 0 else "move_right")   # content moves right → camera moves left
        if abs(mv["tilt_y"]) > 0.008: kind.append("move_up" if mv["tilt_y"] > 0 else "move_down")
        if abs(mv["rotate"]) > 0.01: kind.append("roll/orbit")
        mv["kind"] = kind or ["static"]
        mv["speed"] = round(max(abs(mv["pan_x"]), abs(mv["tilt_y"]), abs(mv["zoom"]), abs(mv["rotate"])), 3)
        mv["pace"] = "still" if mv["speed"] < 0.006 else "slow" if mv["speed"] < 0.04 else "medium" if mv["speed"] < 0.12 else "fast"
        px = np.concatenate([l.reshape(-1, 3) for l in looks]).astype(np.float32)
        lum = (0.114 * px[:, 0] + 0.587 * px[:, 1] + 0.299 * px[:, 2]) / 255
        rg = px[:, 2] - px[:, 1]; yb = 0.5 * (px[:, 2] + px[:, 1]) - px[:, 0]
        colorful = float(np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2)) / 255
        sample = px[:: max(1, len(px) // 4000)]
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, lab, cen = cv2.kmeans(sample, 4, None, crit, 2, cv2.KMEANS_PP_CENTERS)
        order = np.argsort(-np.bincount(lab.ravel(), minlength=4))
        dom = ["#%02X%02X%02X" % (int(cen[k][2]), int(cen[k][1]), int(cen[k][0])) for k in order]
        out.append({"shot": i + 1, "start": round(a, 2), "end": round(b, 2), "camera": mv,
                    "look": {"brightness": round(float(lum.mean()), 3), "contrast": round(float(lum.std()), 3),
                             "dark_ratio": round(float((lum < 0.08).mean()), 3), "colourfulness": round(colorful, 3), "dominant": dom}})
    cap.release()
    return out


def audio(path, info, out):
    """Pick a phase-safe channel mix, normalise, then measure tempo, beats and the densest 30 s windows."""
    if not info["has_audio"]: return {"present": False}
    import numpy as np, librosa
    raw = os.path.join(out, "_stereo.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "2", "-ar", "22050", raw])
    y, sr = librosa.load(raw, sr=22050, mono=False)
    if y.ndim == 1: y = np.stack([y, y])
    db = lambda x: float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12))
    L, R, M = db(y[0]), db(y[1]), db((y[0] + y[1]) / 2)
    phase_inverted = M < max(L, R) - 10
    mix = "pan=mono|c0=c0" if phase_inverted else "pan=mono|c0=0.5*c0+0.5*c1"
    wav = os.path.join(out, "audio.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-af", f"{mix},loudnorm=I=-14:TP=-1.5", "-ar", "44100", wav])
    os.remove(raw)
    y, sr = librosa.load(wav, sr=22050, mono=True)
    level = db(y)
    if level < -45:
        return {"present": True, "silent": True, "levels_db": {"L": L, "R": R, "mono": M}, "phase_inverted": phase_inverted,
                "note": "no usable sound: ask the user to re-record with system audio on, or to supply the audio file"}
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
    tempo = float(np.atleast_1d(tempo)[0])
    ibi = np.diff(beats); bpm = float(60 / np.median(ibi)) if len(ibi) else tempo
    on = librosa.onset.onset_strength(y=y, sr=sr); ot = librosa.times_like(on, sr=sr)
    win, dur = 30.0, len(y) / sr
    cands = []
    for i in range(0, len(beats), 4):
        s = beats[i]
        if s + win > dur: break
        cands.append((float(on[(ot >= s) & (ot < s + win)].mean()), float(s)))
    cands.sort(reverse=True)
    # noise floor: the quietest 10th percentile of 0.5 s windows
    hop = sr // 2; w = [db(y[i:i + hop]) for i in range(0, len(y) - hop, hop)]
    return {"present": True, "silent": False, "levels_db": {"L": round(L, 1), "R": round(R, 1), "mono": round(M, 1)},
            "phase_inverted": bool(phase_inverted), "noise_floor_db": round(float(np.percentile(w, 10)), 1) if w else None,
            "bpm": round(bpm, 2), "beat_seconds": round(60 / bpm, 4), "first_beat": round(float(beats[0]), 3) if len(beats) else None,
            "beats": [round(float(b), 3) for b in beats],
            "best_30s_starts": [{"start": round(s, 2), "density": round(m, 3)} for m, s in cands[:5]],
            "quality_warning": ("mono only (phase-inverted stereo)" if phase_inverted else None)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    src = fetch(a.src, a.out)
    info = probe(src)
    crop = None
    if info["width"]:
        crop = detect_crop(src, info["duration"], info["width"], info["height"]) or ui_strip_crop(src, info["duration"], info["width"], info["height"])
    vid = make_proxy(src, crop, a.out) if crop or info["duration"] > 120 else src
    from concurrent.futures import ThreadPoolExecutor
    pool = ThreadPoolExecutor(1); aud = pool.submit(audio, src, info, a.out)   # audio (librosa) in parallel with the video work
    cuts = shots(vid) if info["width"] else []
    lens = [b - a_ for a_, b in cuts]
    if info["width"]: sheets(vid, info["duration"], cuts, a.out)
    rep = {"source": os.path.basename(src), "input": a.src, "video": info, "crop": crop, "analysed": os.path.basename(vid),
           "shots": cuts, "pacing": {"count": len(cuts), "mean_shot_s": round(sum(lens) / len(lens), 2) if lens else None,
                                     "shortest_s": round(min(lens), 2) if lens else None, "longest_s": round(max(lens), 2) if lens else None},
           "audio": aud.result(),
           "shot_details": shot_details(vid, cuts, info["duration"]) if info["width"] else []}
    sd = rep["shot_details"]
    if sd:
        dark = sum(1 for x in sd if x["look"]["dark_ratio"] > 0.5) / len(sd)
        moving = sum(1 for x in sd if x["camera"]["kind"] != ["static"]) / len(sd)
        rep["look_summary"] = {"low_key_shots": round(dark, 2), "moving_camera_shots": round(moving, 2),
                               "mean_brightness": round(sum(x["look"]["brightness"] for x in sd) / len(sd), 3),
                               "camera_kinds": sorted({k for x in sd for k in x["camera"]["kind"]})}
    if rep["audio"].get("bpm") and lens:
        rep["pacing"]["mean_shot_beats"] = round(rep["pacing"]["mean_shot_s"] / rep["audio"]["beat_seconds"], 1)
    with open(os.path.join(a.out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    au = rep["audio"]
    print(f"video   {info['width']}x{info['height']} {info['fps']}fps {info['duration']:.1f}s" + (f"  crop → {crop['w']}x{crop['h']} ({crop['note']})" if crop else ""))
    print(f"shots   {rep['pacing']}")
    if rep.get("look_summary"): print(f"look    {rep['look_summary']}")
    if au.get("present") and not au.get("silent"):
        print(f"audio   {au['bpm']} bpm, first beat {au['first_beat']}s, noise floor {au['noise_floor_db']} dB, phase_inverted={au['phase_inverted']}")
        print(f"best 30s windows: {[c['start'] for c in au['best_30s_starts']]}")
    elif au.get("silent"): print("audio   SILENT —", au["note"])
    else: print("audio   none")
    print("wrote", os.path.join(a.out, "report.json"))


if __name__ == "__main__":
    main()

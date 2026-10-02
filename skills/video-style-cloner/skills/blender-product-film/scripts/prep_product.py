#!/usr/bin/env python3
"""prep_product.py — turn a front product photo (bottle / can / jar on a plain background) into what pfilm.py needs.
Runs with the SYSTEM python (Pillow + numpy), not Blender's.

    python prep_product.py <photo> --out <dir> [--height 0.235] [--bg auto]

Writes into --out:
    product.json    { "type": "photo", "height", "profile": [[r, z], …], "cap_z", "neck_z", "tex": "print.png", "img_w_m", "cx_m" }
    print.png       RGBA: the photo, alpha = where there is ink / label / cap (opaque), 0 where the bottle is clear
    cutout.png      the photo with the background removed (for review, and for 2D compositing if ever needed)
    check.png       silhouette + profile overlay, to eyeball the fit

The silhouette's half-width per row becomes a lathe profile (so the 3D bottle has the real shape); the photo is projected
from the front onto that shape. Works for round products (bottles, cans, jars, tubes). Height is the real product height
in metres (a 600 ml PET bottle ≈ 0.23–0.24 m).
"""
import argparse, json, os, shutil, subprocess
import numpy as np
from PIL import Image, ImageFilter


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("photo"); ap.add_argument("--out", required=True)
    ap.add_argument("--height", type=float, default=0.235); ap.add_argument("--bg_tol", type=float, default=38)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    src = a.photo
    esr = os.environ.get("REALESRGAN", shutil.which("realesrgan-ncnn-vulkan") or "realesrgan-ncnn-vulkan")
    if max(Image.open(src).size) < 1200 and os.path.exists(esr):   # small web images: AI 4x upscale keeps label text crisp
        up = os.path.join(a.out, "upscaled.png")
        subprocess.run([esr, "-i", src, "-o", up, "-n", "realesrgan-x4plus", "-s", "4"], capture_output=True)
        if os.path.exists(up): src = up; print("upscaled 4x with Real-ESRGAN")
    im = Image.open(src).convert("RGB")
    if max(im.size) < 1400:   # still small: plain resize
        k = 1400 / max(im.size); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    A = np.asarray(im).astype(np.float32); h, w, _ = A.shape
    # background = the colour of the border pixels (usually white)
    border = np.concatenate([A[0], A[-1], A[:, 0], A[:, -1]]); bg = np.median(border, axis=0)
    dist = np.sqrt(((A - bg) ** 2).sum(-1))
    fg = dist > a.bg_tol
    # clean: keep the biggest vertical span of rows, fill each row between its outermost foreground pixels
    rows = np.where(fg.sum(1) > 3)[0]; top, bot = rows.min(), rows.max()
    L = np.full(h, -1); R = np.full(h, -1)
    for y in range(top, bot + 1):
        xs = np.where(fg[y])[0]
        if len(xs) > 3: L[y], R[y] = xs.min(), xs.max()
    # smooth the edges (median over 5 rows) and fill gaps
    for arr in (L, R):
        valid = np.where(arr >= 0)[0]; arr[:] = np.interp(np.arange(h), valid, arr[valid]).astype(int)
        med = arr.copy()
        for y in range(top + 2, bot - 2): med[y] = int(np.median(arr[y - 2:y + 3]))
        arr[:] = med
    mask = np.zeros((h, w), bool)
    for y in range(top, bot + 1): mask[y, L[y]:R[y] + 1] = True
    px_h = bot - top + 1; m_per_px = a.height / px_h
    cx = np.median((L[top:bot + 1] + R[top:bot + 1]) / 2)
    # profile: radius per height, bottom → top, ~140 samples
    ys = np.linspace(bot, top, 140).astype(int)
    prof = []
    for y in ys:
        r = (R[y] - L[y]) / 2 * m_per_px; z = (bot - y) * m_per_px
        prof.append([round(float(r), 5), round(float(z), 5)])
    prof[0][0] *= 0.35   # close the base a little (a flat bottom ring)
    # cap: the topmost block whose colour is saturated and opaque (above the narrowest neck point)
    widths = (R - L)[top:bot + 1]; upper = widths[: int(px_h * 0.35)]
    neck_row = top + int(np.argmin(upper[int(len(upper) * 0.25):]) + len(upper) * 0.25)
    rgb = A / 255; mx, mn = rgb.max(-1), rgb.min(-1); sat = (mx - mn) / (mx + 1e-6); lum = rgb.mean(-1)
    cap_rows = [y for y in range(top, neck_row) if (sat[y, L[y]:R[y] + 1] > 0.35).mean() > 0.6]
    cap_bottom = (max(cap_rows) if cap_rows else top + int(px_h * 0.08))
    # print mask: inside the bottle, pixels that differ from the clear-bottle tint of their row
    base = np.zeros((h, 3), np.float32)
    for y in range(top, bot + 1):
        seg = A[y, L[y]:R[y] + 1]; base[y] = np.median(seg, axis=0) if len(seg) else bg
    # hue of every pixel; the clear body takes the hue of the bottle/water tint (the median hue inside the silhouette)
    r_, g_, b_ = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hue = (np.degrees(np.arctan2(np.sqrt(3) * (g_ - b_), 2 * r_ - g_ - b_)) + 360) % 360
    body_hue = float(np.median(hue[mask & (sat > 0.08)])) if (mask & (sat > 0.08)).any() else 190.0
    hue_off = np.minimum(np.abs(hue - body_hue), 360 - np.abs(hue - body_hue))
    coloured_print = (sat > 0.28) & (hue_off > 28)          # swooshes, badges, stripes in other colours
    dark_print = lum < 0.42                                    # dark text / outlines
    ink = (coloured_print | dark_print) & mask
    # fine print (thin or light-coloured text): darker than its local surroundings, inside the label band only
    gray = Image.fromarray((lum * 255).astype(np.uint8))
    local = np.asarray(gray.filter(ImageFilter.MedianFilter(15))).astype(np.float32) / 255
    fine = (local - lum > 0.09) & mask & (lum < 0.8)
    rows_p = np.where(coloured_print[neck_row:].any(1))[0] + neck_row
    if len(rows_p):
        y0, y1 = rows_p.min(), rows_p.max(); pad = int((y1 - y0) * 0.25)
        band = np.zeros_like(mask); band[max(neck_row, y0 - pad):y1 + pad] = True
        ink |= fine & band
    ink_img = Image.fromarray((ink * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
    alpha = np.asarray(ink_img).astype(np.float32)
    # near-white print (outlines around dark text) is thin white ink: keep it semi-opaque so it doesn't swallow the text
    whiteish = (lum > 0.82) & (sat < 0.18)
    # big white blobs are the photo's baked specular highlights, thin white is outline ink: open (erode→dilate) to separate them
    wimg = Image.fromarray((whiteish * 255).astype(np.uint8))
    thick = np.asarray(wimg.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(11))) > 0
    # ...but white INSIDE printed shapes is print (the white field of a seal, a logo plate): baked highlights sit on the
    # bottle's open glass, never enclosed by ink. Regions enclosed by ink stay; big enclosed regions become opaque print
    # (small ones are glyph counters and keep their soft alpha). Cutting them out left black discs where the dark water shows.
    from scipy import ndimage
    ink_bin = alpha > 128
    # printed rings are rarely perfectly closed (an arrow tail, a gap in a seal): bridge small gaps before filling
    rad = max(2, int(0.005 * w)); yy_, xx_ = np.ogrid[-rad:rad + 1, -rad:rad + 1]; disk = xx_ ** 2 + yy_ ** 2 <= rad ** 2
    closed = ndimage.binary_closing(ink_bin, structure=disk) & mask
    filled = ndimage.binary_fill_holes(closed)
    enclosed = filled & ~ink_bin
    lab, n = ndimage.label(enclosed)
    big_enclosed = np.zeros_like(enclosed)
    if n:
        idx = np.arange(1, n + 1)
        sizes = ndimage.sum(enclosed, lab, idx)
        white_frac = ndimage.mean(whiteish, lab, idx)          # a printed white field (seal, plate) is mostly white;
        keep = idx[(sizes > 0.00015 * h * w) & (sizes < 0.02 * h * w) & (white_frac > 0.6)]   # clear film between prints is not
        big_enclosed = np.isin(lab, keep)
    alpha[thick & ~filled] = 0
    alpha[whiteish & ~thick & ~big_enclosed] *= 0.5
    alpha[big_enclosed] = 255
    alpha[top:cap_bottom + 1][mask[top:cap_bottom + 1]] = 255   # the cap is opaque plastic
    # the rim of the silhouette is refraction/edge darkening, not print: fade the outer 3% of each row
    for y in range(top, bot + 1):
        e = max(2, int((R[y] - L[y]) * 0.03))
        if y <= cap_bottom:   # opaque cap: keep it opaque to the edge, but replace the edge pixels (blended with the white
            # photo background → a white outline in close-ups) with the cap colour from just inside
            A[y, L[y]:L[y] + e] = A[y, L[y] + e + 1]; A[y, R[y] - e:R[y] + 1] = A[y, R[y] - e - 1]
            continue
        alpha[y, L[y]:L[y] + e] *= 0.0; alpha[y, R[y] - e:R[y] + 1] *= 0.0
    out = np.dstack([A, alpha]).clip(0, 255).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(os.path.join(a.out, "print.png"))
    cut = np.dstack([A, mask * 255]).astype(np.uint8); Image.fromarray(cut, "RGBA").save(os.path.join(a.out, "cutout.png"))
    chk = A.copy(); chk[~mask] *= 0.35; chk[ink] = chk[ink] * 0.4 + np.array([255, 0, 120]) * 0.6
    for y in range(top, bot + 1): chk[y, L[y]] = chk[y, R[y]] = (0, 255, 0)
    chk[cap_bottom, :] = (255, 200, 0); chk[neck_row, :] = (0, 200, 255)
    Image.fromarray(chk.clip(0, 255).astype(np.uint8)).save(os.path.join(a.out, "check.png"))
    info = {"type": "photo", "height": a.height, "profile": prof, "tex": "print.png",
            "cap_z": round(float((bot - cap_bottom) * m_per_px), 5), "neck_z": round(float((bot - neck_row) * m_per_px), 5),
            "img_w_m": round(float(w * m_per_px), 5), "img_h_m": round(float(h * m_per_px), 5),
            "cx_m": round(float(cx * m_per_px), 5), "bottom_px": int(bot), "m_per_px": m_per_px,
            "max_radius": round(float(max(p[0] for p in prof)), 5)}
    json.dump(info, open(os.path.join(a.out, "product.json"), "w"), indent=1)
    print(f"height {a.height} m, max radius {info['max_radius']:.4f} m, cap from z={info['cap_z']:.3f}, neck z={info['neck_z']:.3f}, ink {ink.mean() * 100:.1f}% of frame")


if __name__ == "__main__":
    main()

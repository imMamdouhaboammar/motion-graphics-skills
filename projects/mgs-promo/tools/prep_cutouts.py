# Key white-background stock photos and give them one print treatment.
# Usage (from project root): python3 tools/prep_cutouts.py <dir with the downloaded originals>
# Originals (see ASSET_SOURCES.md): mic_akg.jpg, kb_wm.jpg, scissors.jpg, hp_iso.jpg
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as nd

SRC = sys.argv[1] if len(sys.argv) > 1 else "."
INK = np.array([22, 20, 18], float)
PAPER = np.array([246, 242, 234], float)

def key(im, thr, hole_min=1500, sat=28, drop_below=None):
    """Background = near-white regions touching the border, plus enclosed white holes above hole_min px."""
    a = np.array(im).astype(int)
    white = (a.min(2) > thr) & ((a.max(2) - a.min(2)) < sat)
    lab, n = nd.label(white)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    sizes = nd.sum(white, lab, range(1, n + 1))
    bg = np.isin(lab, [i for i in range(1, n + 1) if i in border or sizes[i - 1] >= hole_min])
    if drop_below is not None:           # remove a floor shadow below a given height ratio
        bg[int(drop_below * a.shape[0]):] = True
    fg = nd.binary_opening(~bg, iterations=2)
    return Image.fromarray((fg * 255).astype("uint8")).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))

def treat(im, alpha, maxw, seed=7):
    rng = np.random.default_rng(seed)
    ys, xs = np.where(np.array(alpha) > 20)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    im, alpha = im.crop(box), alpha.crop(box)
    if im.width > maxw:
        size = (maxw, round(im.height * maxw / im.width))
        im, alpha = im.resize(size, Image.LANCZOS), alpha.resize(size, Image.LANCZOS)
    g = np.array(im.convert("L"), float) / 255
    g = np.clip((g - 0.04) / 0.9, 0, 1)
    g = g * g * (3 - 2 * g)                                   # S-curve
    g = np.clip(g + (rng.random(g.shape) - 0.5) * 0.10 * 4 * g * (1 - g), 0, 1)   # midtone grain
    out = Image.fromarray((INK + (PAPER - INK) * g[..., None]).astype("uint8"))
    out.putalpha(alpha)
    return out

JOBS = [  # name, threshold, kwargs, max width
    ("mic_akg", 236, dict(hole_min=10**9), 700),
    ("kb_wm", 200, {}, 1400),
    ("scissors", 215, dict(hole_min=3000), 1000),
    ("hp_iso", 200, dict(sat=30, drop_below=0.675), 900),
]

if __name__ == "__main__":
    for name, thr, kw, maxw in JOBS:
        im = Image.open(f"{SRC}/{name}.jpg").convert("RGB")
        treat(im, key(im, thr, **kw), maxw).save(f"assets/cutouts/{name}.png", optimize=True)
        print(name, "ok")

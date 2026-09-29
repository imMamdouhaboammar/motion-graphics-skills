# Seeded textures for the film. Run from the project root: python3 tools/prep_textures.py
import numpy as np
from PIL import Image, ImageFilter

OUT = "assets/tex/"

def paper_fibre():
    # fine tooth + sparse fibres, very little low-frequency mottling (the first draft showed blotches)
    rng = np.random.default_rng(11)
    S = 720
    low = np.array(Image.fromarray((rng.random((S // 90, S // 90)) * 255).astype("uint8"))
                   .resize((S, S), Image.BICUBIC).filter(ImageFilter.GaussianBlur(20)), float) / 255
    fib = np.zeros((S, S))
    for _ in range(1100):
        x, y = rng.integers(0, S, 2)
        L = rng.integers(8, 34)
        a = rng.random() * np.pi
        for t in range(L):
            fib[int(y + np.sin(a) * t) % S, int(x + np.cos(a) * t) % S] += 0.5
    fine = rng.random((S, S))
    v = 0.62 + (low - 0.5) * 0.12 + (fine - 0.5) * 0.22 - fib * 0.3
    Image.fromarray(np.clip(v * 255, 0, 255).astype("uint8")).save(OUT + "paper-fibre.png")

def grain():
    rng = np.random.default_rng(11)
    for i in range(3):
        g = rng.normal(128, 40, (256, 256)).clip(0, 255).astype("uint8")
        Image.fromarray(g).save(OUT + f"grain-{i}.png")

def stamp_ink():
    rng = np.random.default_rng(5)
    W, H = 900, 520
    low = np.array(Image.fromarray((rng.random((H // 40 + 1, W // 40 + 1)) * 255).astype("uint8"))
                   .resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(10)), float) / 255
    spk = rng.random((H, W))
    a = np.where(spk < 0.06 + 0.22 * (low < 0.35), 0, 1.0) * (0.78 + 0.22 * low)
    Image.fromarray((a * 255).clip(0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.6)).save(OUT + "stamp-ink.png")

if __name__ == "__main__":
    paper_fibre(); grain(); stamp_ink(); print("textures ok")

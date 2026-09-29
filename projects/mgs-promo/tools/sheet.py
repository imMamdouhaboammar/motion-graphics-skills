# Labelled contact sheet from a snapshot folder: python3 tools/sheet.py <dir> <out.png> [cols]
import sys, glob, re
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 9
fs = sorted(glob.glob(d + '/frame-*.png'), key=lambda f: int(re.search(r'frame-(\d+)', f).group(1)))
W, H = 200, 356
rows = (len(fs) + cols - 1) // cols
S = Image.new('RGB', (cols * W, rows * (H + 22)), 'white')
for i, f in enumerate(fs):
    im = Image.open(f).convert('RGB').resize((W, H)); x = (i % cols) * W; y = (i // cols) * (H + 22)
    S.paste(im, (x, y + 22)); ImageDraw.Draw(S).text((x + 4, y + 5), re.search(r'at-([\d.]+)s', f).group(1) + 's', fill='black')
S.save(out)

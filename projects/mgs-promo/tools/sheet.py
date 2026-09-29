# Labelled contact sheet from a snapshot folder: python3 tools/sheet.py <dir> <out.png> [cols]
import glob
import re
import sys
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 9
fs = sorted(glob.glob(d + '/frame-*.png'), key=lambda f: int(re.search(r'frame-(\d+)', f).group(1)))
W, H = 200, 356
rows = (len(fs) + cols - 1) // cols
S = Image.new('RGB', (cols * W, rows * (H + 22)), 'white')
for i, f in enumerate(fs):
    im = Image.open(f).convert('RGB').resize((W, H))
    x = (i % cols) * W
    y = (i // cols) * (H + 22)
    S.paste(im, (x, y + 22))
    m = re.search(r'at-([\d.]+)s', f)
    label = m.group(1) + 's' if m else 'frame ' + re.search(r'frame-(\d+)', f).group(1)
    ImageDraw.Draw(S).text((x + 4, y + 5), label, fill='black')
S.save(out)

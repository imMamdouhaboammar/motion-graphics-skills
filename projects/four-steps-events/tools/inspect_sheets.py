# python3 tools/inspect_sheets.py new.mp4 old.mp4 outdir
#   outdir/every-0.5s.png   one frame every 0.5 s from the new film, labelled
#   outdir/before-after.png  the same moments from the old and the new film, in pairs
import subprocess, sys, os, tempfile
from PIL import Image, ImageDraw, ImageFont
new, old, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
except Exception: font = ImageFont.load_default()
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', new]))
tmp = tempfile.mkdtemp()

def grab(src, t, name):
    p = os.path.join(tmp, name)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', src, '-frames:v', '1', p], check=True)
    return Image.open(p)

# every 0.5 s
ts = [i * .5 for i in range(int(dur / .5) + 1) if i * .5 < dur - .02]
tw, th, cols = 180, 320, 12
rows = (len(ts) + cols - 1) // cols
S = Image.new('RGB', (cols * tw, rows * (th + 22)), (24, 24, 24)); D = ImageDraw.Draw(S)
for i, t in enumerate(ts):
    im = grab(new, t, f'n{i}.png').resize((tw, th)); x = (i % cols) * tw; y = (i // cols) * (th + 22)
    S.paste(im, (x, y)); D.text((x + 5, y + th + 3), f'{t:5.1f}s', fill=(235, 235, 235), font=font)
S.save(os.path.join(out, 'every-0.5s.png'))

# before / after at the moments named in the review notes
moments = [0, 1.0, 2.95, 4.6, 6.6, 7.8, 9.6, 11.4, 13.95, 15.5, 15.95, 17.9, 20.2, 22.4, 23.9, 25.6, 27.3, 29.0,
           30.9, 31.7, 33.3, 35.3, 37.7, 39.3, 41.8, 43.4, 44.3, 45.2, 47.3, 49.8, 51.2, 52.3, 53.1, 53.6, 54.3]
tw, th, cols = 150, 267, 9
rows = (len(moments) + cols - 1) // cols
S = Image.new('RGB', (cols * (tw * 2 + 8), rows * (th + 22)), (24, 24, 24)); D = ImageDraw.Draw(S)
for i, t in enumerate(moments):
    x = (i % cols) * (tw * 2 + 8); y = (i // cols) * (th + 22)
    S.paste(grab(old, min(t, 54.3), f'o{i}.png').resize((tw, th)), (x, y))
    S.paste(grab(new, t, f'b{i}.png').resize((tw, th)), (x + tw, y))
    D.text((x + 5, y + th + 3), f'{t:5.2f}s  v1 | v2', fill=(235, 235, 235), font=font)
S.save(os.path.join(out, 'before-after.png'))
print('ok', len(ts), 'frames,', len(moments), 'pairs')

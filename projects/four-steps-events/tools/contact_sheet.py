# python3 tools/contact_sheet.py film.mp4 contact-sheet.png  -> labelled inspection frames pulled from the encoded file
import subprocess, sys, os, tempfile
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1], sys.argv[2]
shots = [(0,'first frame'),(0.5,'0.5 s'),(1.0,'1 s'),(2.95,'B1 ticket'),(4.6,'B1 question'),
 (5.8,'B2 stage'),(6.6,'B2 light'),(8.9,'B2 clock'),(11.0,'B3 layers'),(13.95,'B3 detail'),(15.5,'B3 guests'),
 (15.85,'T seat→blue'),(17.9,'B4 Four Steps'),(18.85,'T fold'),(20.6,'B5 corridor'),(22.9,'B5 conference'),
 (23.35,'B5 rosette'),(24.4,'B5 symposium'),(26.9,'B5 protocol'),(29.4,'B5 minutes'),(30.9,'B6 idea'),
 (31.7,'B6 plan'),(33.3,'B6 venue'),(34.6,'B6 content'),(36.0,'B6 coverage'),(37.9,'B6 last guest'),
 (39.1,'T lever'),(40.9,'B7 pieces'),(44.25,'B7 months'),(45.6,'B8 question'),(47.3,'B8 CTA'),
 (47.7,'T steps'),(49.9,'B9 step by step'),(52.3,'B9 see'),(53.0,'B9 live'),(54.2,'final frame')]
tw, th = 270, 480; cols = 9; rows = (len(shots)+cols-1)//cols
S = Image.new('RGB', (cols*tw, rows*(th+30)), (24,24,24)); D = ImageDraw.Draw(S)
try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
except Exception: font = ImageFont.load_default()
tmp = tempfile.mkdtemp()
for i,(t,label) in enumerate(shots):
    p = os.path.join(tmp, f'{i}.png')
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',src,'-frames:v','1',p],check=True)
    im = Image.open(p).resize((tw,th)); x=(i%cols)*tw; y=(i//cols)*(th+30); S.paste(im,(x,y))
    D.text((x+6,y+th+6), f'{t:5.2f}s  {label}', fill=(235,235,235), font=font)
S.save(out); print(out, S.size)

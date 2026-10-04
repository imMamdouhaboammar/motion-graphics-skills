from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,json
p=Path(__file__).resolve().parents[1];d=p/'reviews/final-frame-evidence';d.mkdir(exist_ok=True)
ref=[.8,2.5,5.6,9.5,14.3,17.2,20.5,24.3,28.8,31.5,33.8,37]
target=[1.7,4.2,7.6,12,15.8,17.6,21,25,29.5,35.7,39.7,48.333333]
canvas=Image.new('RGB',(1536,1116),'#e9e3d3');draw=ImageDraw.Draw(canvas)
for i,(a,b) in enumerate(zip(ref,target)):
 for kind,t,src in [('ref',a,p/'input/reference.mp4'),('target',b,p/'renders/AI_Business_Collage.mp4')]:
  dst=d/f'{i+1:02}-{kind}-{t:.3f}.jpg';subprocess.run(['ffmpeg','-v','error','-threads','2','-ss',str(t),'-i',str(src),'-frames:v','1','-vf','scale=192:342','-q:v','2','-y',str(dst)],check=True,timeout=20)
  im=Image.open(dst);x=(i%4)*384+(192 if kind=='target' else 0);y=(i//4)*372;canvas.paste(im,(x,y));draw.text((x+5,y+345),f'{i+1:02} {kind} {t:.3f}s',fill='#691b24')
canvas.save(p/'reviews/reference-target-contact.jpg')
# Every scene boundary ±2 frames and the entire final12frames.
frames=set([0]);alignment=json.loads((p/'analysis/voice_alignment.json').read_text())
for item in alignment['scenes']:
 for f in range(item['start_frame']-2,item['start_frame']+3):
  if 0<=f<1451:frames.add(f)
frames.update(range(1439,1451));bd=p/'reviews/boundaries';bd.mkdir(exist_ok=True)
for f in sorted(frames):
 subprocess.run(['ffmpeg','-v','error','-threads','2','-ss',str(f/30),'-i',str(p/'renders/AI_Business_Collage.mp4'),'-frames:v','1','-vf','scale=108:192','-q:v','2','-y',str(bd/f'{f:04}.jpg')],check=True,timeout=20)
cols=12;ordered=sorted(bd.glob('*.jpg'));out=Image.new('RGB',(cols*108,((len(ordered)+cols-1)//cols)*214),'#e9e3d3');dr=ImageDraw.Draw(out)
for i,q in enumerate(ordered):out.paste(Image.open(q),(i%cols*108,i//cols*214));dr.text((i%cols*108+4,i//cols*214+193),q.stem,fill='#691b24')
out.save(p/'reviews/boundary-contact.jpg')

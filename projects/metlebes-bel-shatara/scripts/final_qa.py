from pathlib import Path
import subprocess,json,wave,hashlib
import numpy as np
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]; (root/'reports').mkdir(exist_ok=True); vid=root/'renders/Metlebes_Bel_Shatara_Final.mp4'
times=[1,4.5,10.7,15.8,21.5,27.2,32.5,36.8,40,44,50,59,64,67.5,71.5,79,91,102,108,110.7]
canvas=Image.new('RGB',(1600,5*249),'#222222');d=ImageDraw.Draw(canvas)
for i,t in enumerate(times):
 p=root/f'reports/final-{i:02}.jpg';subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(vid),'-frames:v','1','-vf','scale=400:225','-y',str(p)],check=True)
 canvas.paste(Image.open(p),(i%4*400,i//4*249));d.text((i%4*400+10,i//4*249+228),f'{t:.2f}s',fill='white')
canvas.save(root/'reports/final-film-contact.jpg')
def read(p):
 with wave.open(str(p)) as f:return np.frombuffer(f.readframes(f.getnframes()),dtype=np.int16).astype(float)/32768
subprocess.run(['ffmpeg','-v','error','-i',str(vid),'-vn','-ac','1','-ar','48000','-c:a','pcm_s16le','-y',str(root/'reports/final-decoded.wav')],check=True)
x=read(root/'runtime/assets/narration-original.wav');y=read(root/'reports/final-decoded.wav')
rows=[]
for t in range(112):
 a=x[t*48000:min((t+1)*48000,len(x))];b=y[t*48000:t*48000+len(a)]
 if len(a)>0 and np.sqrt(np.mean(a*a))>.01: rows.append({'second':t,'correlation':float(np.corrcoef(a,b)[0,1]),'gain':float(np.dot(a,b)/np.dot(a,a))})
report={'source_samples':len(x),'export_audio_samples':len(y),'source_sha256':hashlib.sha256((root/'runtime/assets/narration-original.wav').read_bytes()).hexdigest(),'voiced_seconds_checked':len(rows),'minimum_correlation':min(z['correlation'] for z in rows),'median_correlation':float(np.median([z['correlation'] for z in rows])),'median_gain':float(np.median([z['gain'] for z in rows])),'final_phrase':rows[-4:],'decoded_mix_peak':float(np.max(np.abs(y))),'segments':rows}
(root/'reports/dialogue-integrity.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='segments'},indent=2))

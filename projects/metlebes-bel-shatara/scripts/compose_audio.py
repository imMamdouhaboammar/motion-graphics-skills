from pathlib import Path
import numpy as np, wave,json
from scipy.signal import butter,sosfilt
P=Path(__file__).resolve().parents[1];out=P/'runtime/assets';sr=48000;dur=112.3;N=int(sr*dur);bed=np.zeros(N);sfx=np.zeros(N);rng=np.random.default_rng(4817)
def add(dst,t,a):
 i=int(t*sr);l=min(len(a),len(dst)-i)
 if i>=0 and l>0:dst[i:i+l]+=a[:l]
def note(freq,length,amp=.04,kind='pluck'):
 t=np.arange(int(sr*length))/sr
 if kind=='pluck':a=(np.sin(2*np.pi*freq*t)+.35*np.sin(2*np.pi*freq*2.01*t)+.16*np.sin(2*np.pi*freq*3*t))*np.exp(-t*5)
 else:a=(np.sin(2*np.pi*freq*t)+.19*np.sin(2*np.pi*freq*2*t))*np.exp(-t*1.9)
 return amp*a*np.minimum(1,t/.008)
# Original two-bar motif: no sampled or licensed third-party music.
freqs=[146.832,174.614,195.998,220,174.614,164.814,130.813,146.832]
for t in np.arange(.35,41.3,1.42):
 j=int((t-.35)/1.42)%8;add(bed,t,note(freqs[j],1.2,.021));
 if j%2==0:add(bed,t+.42,note(freqs[j]*2,.6,.009))
# Restrained middle, sparse low notes and gentle open intervals.
for j,t in enumerate(np.arange(43.5,69.1,3.45)):
 f=[130.813,146.832,164.814,110][j%4];add(bed,t,note(f,3.4,.019,'soft'));add(bed,t+.1,note(f*1.5,2.7,.007,'soft'))
for j,t in enumerate(np.arange(69.8,87.9,1.9)):
 f=[146.832,174.614,220,195.998][j%4];add(bed,t,note(f,1.9,.018));
for j,t in enumerate(np.arange(89.2,105.9,3.8)):
 f=[146.832,195.998,174.614,220,146.832][j%5];add(bed,t,note(f,3.4,.017,'soft'));add(bed,t+.18,note(f*1.5,3,.006,'soft'))
# Silence before the playful shout; tiny comic cadence after the coin entrance.
for f,t in [(220,110.03),(174.614,110.27),(146.832,110.55)]:add(bed,t,note(f,.7,.021))
def noise(length,amp,decay=10):
 t=np.arange(int(sr*length))/sr;a=rng.normal(size=len(t));a=sosfilt(butter(2,2800,fs=sr,output='sos'),a);return a*np.exp(-decay*t)*amp*np.minimum(1,t/.006)
def swish(t,length=.28,amp=.025):
 a=noise(length,amp,3);env=np.sin(np.linspace(0,np.pi,len(a)))**2;add(sfx,t,a*env)
def click(t,f=800,amp=.035):add(sfx,t,note(f,.12,amp))
for t in [10.6,14.07,15.46,16.5,17.1,20.48,21.22,23.2,27.3,33.56,35.6,38.89,39.76,42.1,53.22,54.02,58.75,63.8,67.34,71.66,73.5,77.7,109.48]:swish(t)
for t in [31.36,31.7,32.18,47.28,47.74,54.16,68.55]:click(t,620,.021)
click(39.99,1150,.033);click(63.99,190,.033);click(67.48,340,.022)
for j,t in enumerate([109.88,110.15,110.46]):
 a=note([1174.659,1567.982,880][j],.42,.028);add(sfx,t,a)
# Original recording is not gain-normalized or processed. Duck only original music/SFX.
with wave.open(str(P/'runtime/assets/narration-original.wav')) as w:voice=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
pad=np.pad(voice,(0,N-len(voice)))
window=4800;env=np.repeat(np.array([np.sqrt(np.mean(pad[i:i+window]**2)) for i in range(0,N,window)]),window)[:N]
duck=1-.28*np.clip(env/.13,0,1);bed*=duck*3;sfx*=1-.2*np.clip(env/.13,0,1)
# Fade music ends; VO contains the ending and is left untouched.
bed[:2400]*=np.linspace(0,1,2400);bed[-24000:]*=np.linspace(1,0,24000)
def write(name,a):
 with wave.open(str(out/name),'w') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(np.clip(a*32767,-32768,32767).astype('<i2').tobytes())
write('music-original.wav',bed);write('sfx-original.wav',sfx);write('mix-reference.wav',pad+bed+sfx)
(P/'docs/audio-composition.json').write_text(json.dumps({'music':'original synthesized 8-note motif and restrained middle variations','sfx':'original synthesized noise/wood/coin tones','seed':4817,'sample_rate':sr,'narration_gain':1,'source_processing':'none','reference_mix_peak_dbfs':float(20*np.log10(max(abs(pad+bed+sfx)))),'music_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(bed**2))))},indent=2))

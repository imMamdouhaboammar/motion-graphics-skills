from pathlib import Path
import numpy as np, wave,json,hashlib
p=Path(__file__).resolve().parents[1]
conf=json.loads((p/'src/project.json').read_text());src=p/'input/voiceover.wav'
assert hashlib.sha256(src.read_bytes()).hexdigest()==conf['inputs']['voiceover']['sha256']
with wave.open(str(src)) as f:
 assert f.getframerate()==48000 and f.getsampwidth()==2 and f.getnchannels()==1
 raw=f.readframes(f.getnframes());voice=np.frombuffer(raw,dtype='<i2').astype(np.float64)/32768
rate=48000;foley=np.zeros_like(voice);rng=np.random.default_rng(1708)
cues=[(1.55,.13,'ribbon landing'),(2.8,.09,'clipboard entry'),(3.65,.09,'monitor prop'),(6.53,.08,'photographic tool cut'),(8.03,.08,'photographic tool cut'),(10.5,.065,'garment jump'),(11.1,.065,'garment jump'),(11.75,.17,'paper handoff'),(13.75,.065,'route pin'),(14.18,.065,'route pin'),(14.61,.065,'route pin'),(15.04,.065,'route pin'),(15.47,.065,'route pin'),(19.6,.16,'slip sorting'),(23.3,.07,'connection'),(24.1,.08,'screen panel')]
for t,d,label in cues:
 n=int(d*rate);noise=rng.normal(0,1,n);noise=np.convolve(noise,np.ones(11)/11,mode='same');env=np.exp(-np.linspace(0,6,n))*np.minimum(np.arange(n)/180,1)
 a=.018*noise*env;start=round(t*rate);foley[start:start+n]+=a
mix=voice+foley;assert np.max(np.abs(mix))<1
for name,data in [('foley_original.wav',foley),('voice_foley_master.wav',mix)]:
 with wave.open(str(p/'renders'/name),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes((data*32768).round().astype('<i2').tobytes())
(p/'analysis/sfx_cues.json').write_text(json.dumps({'source':'Original deterministic synthesized short filtered-noise paper transients. No music or catalog recordings.','voice_source_sha256':conf['inputs']['voiceover']['sha256'],'voice_gain':1,'voice_samples':len(voice),'mix_peak':float(np.max(abs(mix))),'sfx_peak':float(np.max(abs(foley))),'cues':[{'time':t,'duration':d,'event':label} for t,d,label in cues]},indent=2))

#!/usr/bin/env python3
"""Measure PCM activity without changing VO. Activity is not phrase alignment."""
import json, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
with wave.open(str(ROOT / 'input/voiceover.wav')) as f:
    rate, channels, width = f.getframerate(), f.getnchannels(), f.getsampwidth()
    if (channels, width) != (1, 2):
        raise SystemExit('Expected original mono PCM16 WAV')
    audio = np.frombuffer(f.readframes(f.getnframes()), dtype='<i2').astype(float) / 32768
hop = round(rate * .01)
trim = audio[:len(audio)//hop*hop].reshape(-1, hop)
rms = np.sqrt(np.mean(trim**2, axis=1))
db = 20*np.log10(np.maximum(rms, 1e-8))
active = db > -38
regions = []
start = None
for i, value in enumerate(np.append(active, False)):
    if value and start is None: start = i
    if not value and start is not None:
        if (i-start)*.01 >= .04:
            regions.append({'start_s':round(start*.01, 3), 'end_s':round(i*.01, 3)})
        start = None
report = {'method':'10ms RMS threshold at -38 dBFS; NOT forced alignment',
          'duration_s':len(audio)/rate, 'sample_rate':rate, 'peak_dbfs':float(20*np.log10(max(abs(audio)))),
          'activity_regions':regions, 'semantic_phrase_labels_verified':False}
(ROOT/'analysis/audio_activity.json').write_text(json.dumps(report, indent=2))
image = Image.new('RGB', (1800, 420), '#E9E3D3'); draw = ImageDraw.Draw(image)
for x in range(1800):
    segment = audio[int(x*len(audio)/1800):int((x+1)*len(audio)/1800)]
    height = float(max(abs(segment))) * 170 if len(segment) else 0
    draw.line((x,210-height,x,210+height),fill='#691B24')
for sec in range(0,49,2):
    x = sec/len(audio)*rate*1800
    draw.line((x,20,x,390),fill='#C8BEAF')
    draw.text((x+3,395),f'{sec}s',fill='#282423')
image.save(ROOT/'analysis/voice_waveform.png')
print(json.dumps({'duration_s': report['duration_s'], 'activity_regions':len(regions), 'semantic_alignment':'PENDING'}))

from faster_whisper import WhisperModel
import json
m=WhisperModel("medium",device="cpu",compute_type="int8")
segs,info=m.transcribe("vo.wav",language="ar",word_timestamps=True,beam_size=5,
 initial_prompt="بسألك سؤال. شركة كل شغلها سري. جدار. الهاشتاق. تقييم جاهزية مجاني.")
out=[]
for s in segs:
  for w in s.words: out.append({"t":w.word.strip(),"s":round(w.start,2),"e":round(w.end,2)})
json.dump(out,open("words.json","w"),ensure_ascii=False,indent=0)
print(" ".join(f"{w['t']}[{w['s']}]" for w in out))

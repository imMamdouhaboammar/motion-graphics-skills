#!/usr/bin/env python3
"""Writes the <audio> cue block in index.html.

The voice over is the master clock. Cue times come from the word times in
assets/audio/vo-words.json (faster-whisper medium, Arabic, word timestamps), looked up by
word index. Run after any change:
    python3 tools/cues.py
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
W = json.loads((ROOT / "assets/audio/vo-words.json").read_text(encoding="utf-8"))
TOTAL = 41.5
VO_DUR = 40.2

def w(i):
    """start time of spoken word number i"""
    return W[i]["s"]

# name: (duration, volume)
SFX = {
    "chalk": (1.3, 0.32), "tick": (3.0, 0.42), "stamp": (0.6, 0.55), "heart": (3.4, 0.34), "door": (1.2, 0.45),
    "exhale": (1.6, 0.3), "whoosh1": (0.49, 0.3), "whoosh-rev": (0.5, 0.26), "whoosh-elec": (0.85, 0.3),
    "hit-light": (0.5, 0.24), "hit-mid": (0.6, 0.3), "pop1": (0.14, 0.3), "pop2": (0.22, 0.32), "click": (0.3, 0.28),
    "ding": (0.6, 0.26), "send": (0.9, 0.34), "scan": (1.6, 0.15), "type1": (0.45, 0.22), "type2": (0.32, 0.22),
}
cues = []
def c(t, name, dur=None, vol=None):
    d, v = SFX[name]
    cues.append((round(t, 3), name, dur or d, vol if vol is not None else v))

# hook: the question is written in chalk, then the room goes quiet
c(0.0, "chalk", dur=1.3); c(1.2, "hit-light", vol=0.18)
c(w(3), "tick", dur=3.0)                                      # "wala 7ad"
for k in range(6):
    c(w(7) + 0.18 * k, "pop1", vol=0.26)                       # every dome lights a question
c(w(11), "pop2")                                               # counter

# inside the head
c(w(12), "whoosh-elec"); c(w(13) + 0.1, "heart", dur=3.4)
c(w(13), "pop2", vol=0.24)
c(w(17) - 0.05, "stamp")                                       # "deh" -> STAMP
c(w(18) + 0.2, "whoosh1"); c(w(21), "type1"); c(w(21) + 0.42, "type2")
c(w(22) - 0.05, "whoosh-rev", vol=0.18)
c(w(23) - 0.15, "hit-mid"); c(w(23) + 0.3, "tick", dur=1.0, vol=0.5)   # the boss's eye, the clock

# out, nod, door, corridor
c(w(24) - 0.1, "whoosh-rev")
c(w(25), "click"); c(w(25) + 0.34, "click")
c(w(28) - 0.05, "door")
c(w(30) + 0.1, "pop2"); c(w(30) + 0.62, "pop1"); c(w(33) + 0.2, "send", vol=0.22)

# the name
c(w(34) - 0.25, "whoosh1"); c(w(34) + 0.1, "whoosh-rev", vol=0.2); c(w(37) - 0.05, "hit-light")
for t in (w(39), w(40), w(41) + 0.3):
    c(t + 0.12, "click", vol=0.32)
c(w(44), "ding"); c(w(44) + 0.25, "exhale")

# proof
c(w(47) - 0.25, "whoosh1", vol=0.22); c(w(47), "pop2", vol=0.26)
c(w(51) - 0.1, "scan", dur=1.2, vol=0.12)
c(w(54), "scan", dur=1.7)
c(w(60) - 0.2, "whoosh-rev", vol=0.2)
for k in range(5):
    c(w(60) + 0.1 + k * 0.12, "pop1", vol=0.2)
c(w(65), "stamp", vol=0.42); c(w(65) + 0.05, "ding", vol=0.24)

# the swallowed question
c(w(67) - 0.3, "whoosh-elec", vol=0.24)
c(w(70) + 0.35, "hit-mid", vol=0.24)
c(w(77) - 0.1, "ding", vol=0.3); c(w(77), "hit-light", vol=0.2)

# CTA
c(w(79) + 0.1, "send")
c(w(83), "heart", dur=3.0, vol=0.36)
c(w(86) + 0.05, "chalk", dur=0.9, vol=0.26)
c(w(90) - 0.1, "ding", vol=0.22)

# end card
c(VO_DUR - 0.1, "whoosh-rev", vol=0.16); c(VO_DUR + 0.1, "chalk", dur=0.9, vol=0.3); c(VO_DUR + 0.8, "pop1", vol=0.22)

lines = ["      <!-- CUES -->",
         f'      <audio id="a-vo" src="assets/audio/vo.wav" data-start="0" data-duration="{VO_DUR}" data-track-index="10" data-volume="1"></audio>',
         f'      <audio id="a-bed" src="assets/audio/music/bed.wav" data-start="0" data-duration="{TOTAL}" data-track-index="11" data-volume="0.42"></audio>']
busy = {}
for i, (t, n, d, v) in enumerate(sorted(cues)):
    tr = 12
    while busy.get(tr, -1) > t:
        tr += 1
    busy[tr] = round(t + d, 3)
    assert t + d <= TOTAL, f"cue {n} at {t} runs past the end"
    lines.append(f'      <audio id="s{i+1}" src="assets/audio/sfx/{n}.wav" data-start="{t}" data-duration="{d}" data-track-index="{tr}" data-volume="{v}"></audio>')
lines.append("      <!-- /CUES -->")

p = ROOT / "index.html"
html = p.read_text(encoding="utf-8")
html, n = re.subn(r"      <!-- CUES -->.*?      <!-- /CUES -->", lambda m: "\n".join(lines), html, flags=re.S)
if n != 1:
    raise SystemExit(f"expected one CUES block in index.html, found {n}; nothing written")
p.write_text(html, encoding="utf-8")
print(f"{len(cues)} cues written")

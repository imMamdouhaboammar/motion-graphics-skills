#!/usr/bin/env python3
"""Writes the <audio> cue block in index.html.

The voice over is the master clock: cue times come from the measured word times in
assets/audio/vo-words.json (faster-whisper small.en, word timestamps). Run after any change:
    python3 tools/cues.py
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
W = json.loads((ROOT / "assets/audio/vo-words.json").read_text(encoding="utf-8"))
TOTAL = 31.0

def word(text, n=1):
    """start time of the n-th spoken occurrence of a word (case and punctuation ignored)"""
    k = 0
    for w in W:
        if re.sub(r"[^a-z]", "", w["w"].lower()) == text:
            k += 1
            if k == n:
                return w["s"]
    raise SystemExit(f"word '{text}' #{n} not in vo-words.json; nothing written")

# name: (duration, volume)
SFX = {
    "whoosh1": (0.49, 0.35), "whoosh-rev": (0.5, 0.3), "whoosh-elec": (0.85, 0.32), "swipe": (0.6, 0.25),
    "hit-light": (0.5, 0.28), "hit-mid": (0.6, 0.3), "pop1": (0.14, 0.42), "pop2": (0.22, 0.42),
    "click": (0.3, 0.3), "ding": (0.6, 0.3), "type1": (0.45, 0.25), "type2": (0.32, 0.25), "ui-open": (0.6, 0.25),
    "scan": (1.6, 0.18), "send": (0.9, 0.35), "glitch": (0.9, 0.16), "twinkle": (2.6, 0.3), "riser-ui": (1.2, 0.2),
}
cues = []
def c(t, name, vol=None, dur=None):
    d, v = SFX[name]
    cues.append((round(t, 3), name, dur or d, vol if vol is not None else v))

c(0.05, "swipe", 0.18)                                   # curve draws on
c(word("motion"), "hit-light", 0.22)
c(1.82, "whoosh-elec")                                   # playhead flip to the void
c(word("timeline") + 0.1, "glitch"); c(word("week"), "hit-mid")
c(word("skip"), "pop2"); c(word("skip") + 0.05, "whoosh-rev")
c(5.6, "whoosh1")                                        # flip to paper
c(word("write"), "type1"); c(word("write") + 0.3, "type2")
c(word("brand"), "pop1"); c(word("brand") + 0.12, "pop2", 0.3); c(word("brand") + 0.25, "click")
for i in range(3):
    c(word("colors") + i * 0.1, "pop1", 0.32)
c(word("type"), "pop2"); c(word("timing"), "hit-light")
c(word("motion", 2), "pop1"); c(word("motion", 2) + 0.12, "pop2", 0.3); c(word("motion", 2) + 0.25, "click")
c(word("reference"), "ui-open"); c(word("beat"), "hit-light", 0.22)
for i in range(6):
    c(word("beat") + i * 0.07, "pop1", 0.2)
c(13.2, "whoosh-elec")                                   # flip to the void
c(word("sfx"), "pop1"); c(word("sfx") + 0.25, "click")
c(word("gives"), "pop1"); c(word("every"), "hit-light", 0.22); c(word("move"), "click", 0.35); c(word("its"), "pop2"); c(word("sound"), "ding")
c(16.1, "whoosh1"); c(16.4, "whoosh-rev", 0.22)          # flip to paper, film strip slides in
c(word("video"), "pop1"); c(word("checks"), "scan")
# one tick per film-strip frame as the scan line crosses it; these mirror the B7 numbers in index.html
SCAN_T0, SCAN_DUR, SCAN_TRAVEL = 17.2, 1.6, 780      # scan starts at x 60 and moves 780 px in 1.6 s
CHECK_OFFSET, FRAME_STEP = 77, 152                   # check i sits 77 + 152 * i px right of the scan start
for i in range(5):
    c(SCAN_T0 + SCAN_DUR * (CHECK_OFFSET + i * FRAME_STEP) / SCAN_TRAVEL, "pop1", 0.3)
c(19.4, "whoosh-rev"); c(20.05, "pop2"); c(word("post"), "send")
c(21.5, "whoosh-elec")                                   # flip to the void
for i, t in enumerate([21.8, 22.15, 22.5, 22.85]):
    c(t, "type1" if i % 2 == 0 else "type2")
c(23.45, "whoosh-rev"); c(word("code"), "hit-mid")
c(23.9, "riser-ui"); c(25.05, "twinkle")
for i in range(7):
    c(25.6 + i * 0.1, "pop1", 0.18)
c(word("grab"), "ding", 0.32)

lines = ['      <!-- CUES -->',
         f'      <audio id="a-bed" src="assets/audio/music/bed.wav" data-start="0" data-duration="{TOTAL}" data-track-index="11" data-volume="0.2"></audio>']
busy = {}
for i, (t, n, d, v) in enumerate(sorted(cues)):
    tr = 12
    while busy.get(tr, -1) > t:
        tr += 1
    busy[tr] = round(t + d, 3)
    lines.append(f'      <audio id="s{i+1}" src="assets/audio/sfx/{n}.wav" data-start="{t}" data-duration="{d}" data-track-index="{tr}" data-volume="{v}"></audio>')
lines.append('      <!-- /CUES -->')

p = ROOT / "index.html"
html = p.read_text(encoding="utf-8")
html, n = re.subn(r"      <!-- CUES -->.*?      <!-- /CUES -->", "\n".join(lines), html, flags=re.S)
if n != 1:
    raise SystemExit(f"expected one CUES block in {p}, found {n}; nothing written")
p.write_text(html, encoding="utf-8")
print(f"{len(cues)} cues written")

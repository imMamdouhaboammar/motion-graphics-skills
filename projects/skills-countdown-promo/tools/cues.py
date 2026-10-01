#!/usr/bin/env python3
"""Writes the <audio> cue block in index.html from one table.

Times derive from the same grid the timeline uses: 110 BPM bed, first kick 0.025 s,
one bar 2.18 s, each skill gets four bars. Run after changing any cue:
    python3 tools/cues.py
"""
import pathlib, re

BAR, T0 = 2.18, 0.025
SEC = 4 * BAR                 # each skill gets four bars
S0 = T0 + 2 * BAR             # hook is two bars
END = S0 + 5 * SEC            # end card
TOTAL = 52.0

# name: (duration, volume, first track)
SFX = {
    "hit-mid": (0.6, 0.5, 11), "hit-light": (0.5, 0.45, 11), "type1": (0.45, 0.38, 12), "type2": (0.32, 0.4, 12),
    "ui-open": (0.6, 0.36, 13), "whoosh1": (0.49, 0.7, 14), "whoosh2": (0.44, 0.55, 14), "whoosh-rev": (0.5, 0.5, 14),
    "whoosh-elec": (0.85, 0.4, 14), "pop1": (0.14, 0.7, 13), "pop2": (0.22, 0.7, 13), "click": (0.35, 0.5, 13),
    "ding": (0.6, 0.45, 13), "twinkle": (2.6, 0.42, 15), "riser-ui": (2.25, 0.3, 15), "scan": (1.0, 0.28, 15),
}

cues = []
def c(t, name, dur=None, vol=None):
    d, v, tr = SFX[name]
    cues.append((round(t, 3), name, dur or d, vol if vol is not None else v, tr))

# hook: count, letters, tag typing
c(0.025, "hit-mid"); c(0.409, "type2"); c(1.363, "type2"); c(2.205, "ui-open")
c(2.30, "type1"); c(2.75, "type2"); c(3.05, "type1")

for k in range(5):
    B = S0 + k * SEC
    c(B - 0.15, "whoosh1"); c(B + 0.025, "hit-mid"); c(B + 0.409, "type2")
    c(B + 0.818, "pop2")                              # mascot hops in
    c(B + 1.72, "whoosh-rev")                         # radial flash
    c(B + 1.95, "click", 0.3, 0.35); c(B + 2.0, "ui-open"); c(B + 2.35, "hit-light")
    c(B + 2.998, "pop1"); c(B + 3.3, "pop2", None, 0.5)
    c(B + 3.75, "click", 0.3, 0.3); c(B + 4.36, "hit-light")
    c(B + 5.75, "whoosh-elec")                        # flash into the follow-up
    if k in (0, 2, 4):                                # pills
        c(B + 6.0, "pop1"); c(B + 6.35, "pop2"); c(B + 7.4, "hit-light")
        if k == 2:                                    # the follow-up names the sounds it plays
            c(B + 6.95, "pop1", None, 0.8); c(B + 7.11, "click", 0.3, 0.55); c(B + 7.4, "riser-ui", 1.2, 0.35)
    else:                                             # doc screen
        c(B + 6.0, "ui-open"); c(B + 6.1, "scan", 1.2)
        for i in range(3):
            c(B + 6.6 + i * 0.5, "pop1", None, 0.55)

E0 = END
c(E0 - 1.8, "riser-ui", 1.8, 0.3); c(E0 + 0.05, "twinkle"); c(E0 + 1.15, "pop2")
for i in range(12):
    c(E0 + 1.7 + i * 0.06, "pop1", None, 0.25)
c(E0 + 2.6, "ding", None, 0.35)

lines = ['      <!-- CUES -->',
         f'      <audio id="a-bed" src="assets/audio/music/bed.wav" data-start="0" data-duration="{TOTAL}" data-track-index="10" data-volume="0.5"></audio>']
busy = {}   # track -> end time; overlapping cues go to the next free track
for i, (t, n, d, v, tr) in enumerate(sorted(cues)):
    while busy.get(tr, -1) > t:
        tr += 1
    busy[tr] = round(t + d, 3)
    lines.append(f'      <audio id="a{i+1}" src="assets/audio/sfx/{n}.wav" data-start="{t}" data-duration="{d}" data-track-index="{tr}" data-volume="{v}"></audio>')
lines.append('      <!-- /CUES -->')

p = pathlib.Path(__file__).resolve().parent.parent / "index.html"
html = p.read_text(encoding="utf-8")
html, n = re.subn(r"      <!-- CUES -->.*?      <!-- /CUES -->", "\n".join(lines), html, flags=re.S)
if n != 1:
    raise SystemExit(f"expected one CUES block in {p}, found {n}; nothing written")
p.write_text(html, encoding="utf-8")
print(f"{len(cues)} cues written; end card {END:.3f}, total {TOTAL}")

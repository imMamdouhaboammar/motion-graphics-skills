#!/usr/bin/env python3
"""gen-stroke-path.py — generalized draw-on path generator.

Lays out ANY word in a single-line (pen-path) SVG font — Hershey/EMS — and emits
one continuous-dash-revealable path `d`. The glyph data IS the pen path, so
stroke-order reveal is exact by construction for any text, no per-word tuning.

Usage: gen-stroke-path.py <font.svg> <text> <target_width_px> <baseline_y> <x0>
Prints: the path `d` string + layout info on stderr.
"""
import re, sys
import xml.etree.ElementTree as ET

# Windows sizes stdio to the ANSI code page (cp1252). These scripts emit UTF-8 on
# every platform; say so rather than depending on the console's code page. Carry
# `errors` across: reconfigure() resets it to "strict", and CPython deliberately gives
# stderr "backslashreplace" so the diagnostic path can never itself raise.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors=_stream.errors)

font_path, text, target_w, baseline_y, x0 = (
    sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))

# Parse XML attributes so named/numeric entities and UTF-8 glyph keys are decoded.
# Attribute order and namespace prefixes have no bearing on glyph lookup.
root = ET.parse(font_path).getroot()
glyphs = {}
for font in root.iter():
    if font.tag.rsplit("}", 1)[-1] != "font":
        continue
    font_advance = font.get("horiz-adv-x", "300")
    for glyph in font:
        if glyph.tag.rsplit("}", 1)[-1] != "glyph":
            continue
        ch = glyph.get("unicode", "")
        if len(ch) == 1:
            # SVG glyphs inherit their containing font's advance unless overridden.
            glyphs[ch] = (float(glyph.get("horiz-adv-x", font_advance)), glyph.get("d", ""))
# default advance for space
space_adv = glyphs.get(" ", (300, ""))[0]

# total advance width in font units
total = 0.0
for ch in text:
    total += glyphs.get(ch, (space_adv, ""))[0]
s = target_w / total                       # scale font-units → px

out = []
cursor = 0.0
NUM = re.compile(r"[-\d.]+")
for ch in text:
    adv, d = glyphs.get(ch, (space_adv, ""))
    if d:
        # polylines only (M/L): transform every coordinate pair
        toks = re.findall(r"([ML])\s+([-\d.]+)\s+([-\d.]+)", d)
        for cmd, xs, ys in toks:
            x = x0 + (cursor + float(xs)) * s
            y = baseline_y - float(ys) * s          # SVG-font y is UP; flip
            out.append(f"{cmd} {x:.1f} {y:.1f}")
    cursor += adv

print(" ".join(out))
print(f"[gen] chars={len(text)} scale={s:.3f} width={total*s:.0f}px "
      f"subpaths={sum(1 for o in out if o.startswith('M'))}", file=sys.stderr)

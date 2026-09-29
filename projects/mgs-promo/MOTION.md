# MOTION.md

## Motion thesis

A tactile Arabic editorial desk where the materials of a studio are literal: a real terminal command, this film's own script, this film's own voice waveform, and a few cutout tools on warm paper. A clay-orange block cursor is the one recurring agent. It cuts scenes, marks the payoff word, and blinks at the end waiting for the viewer's comment. The camera stays locked except where the story changes scale: it pushes into a timeline frame (idea becomes a canvas) and pulls out from a stamped sheet (the offer lands on a desk full of tools). The world flips between paper and night on the big beats, never by dissolve. The film refuses UI mockups, glowing tech gradients, floating cards, and any number it cannot prove.

Stable: the paper/night pair, the clay cursor, Thmanyah type, one light direction.
Moves: one idea per beat, words by the word, objects that arrive and settle.

## Canvas

- 1080 × 1920, 30 fps, composition and encode.
- Safe zone for anything meant to be read: 72 px sides, 200 px top, 330 px bottom (platform UI).
- Intentional crops of objects and hero type are allowed and declared with `data-crop="intentional"`.

## Colour roles

| Token | Hex | Role |
|---|---|---|
| paper | `#F1ECE2` | light world ground |
| paper-2 | `#E4DCCD` | sheets lying on paper, ghosts |
| ink | `#161412` | type and objects on paper |
| night | `#100F0E` | dark world ground |
| cream | `#F4EFE6` | type on night |
| graphite | `#8A8378` | secondary lead-ins |
| clay | `#D9582B` | the cursor, the payoff mark, the stamp ink. Signal only, never a full field |
| ae | `#2A1B56` / `#A58BFF` | the After Effects tile, appears once, then leaves |

Proportion: ground 80 %+, ink/cream 15 %, clay under 5 % of any frame.

## Type

| Role | Face | Use |
|---|---|---|
| Hero Arabic | Thmanyah Serif Display Black | one payoff word per beat (الموشن، بدون، الرندر، أكثر، اترك تعليق) |
| Functional Arabic | Thmanyah Sans Medium / Bold | lead-ins, the script sheet, labels |
| Latin names | Thmanyah Sans Bold | Claude Code, Voice Over, Studio, After Effects, each isolated with `dir="ltr"` + `unicode-bidi: isolate` |
| Code | JetBrains Mono 500 | the install command only |

No Latin tracking on Arabic. No swashes or stylistic sets (features read as font demo; `ss01`–`ss08`, `swsh`, `salt` stay off). Arabic animates by word or phrase only.

## Material

- Paper: flat ground + a seeded fibre texture at low opacity. Grain over everything, fine, 5 % or less, on twos.
- Cutouts: one print treatment for every photo (duotone ink to paper, S-curve, midtone grain, die-cut edge).
- Shadows: one light, top-left. Two elevations. `sheet`: 0 8px 18px rgba(22,20,18,.16). `object`: 18px 28px 40px rgba(22,20,18,.28).
- Tape: translucent paper-2 strips, only where something is physically pinned.

## Transition families

1. **Cursor cut** (T1): the clay block sweeps right to left (reading direction) and the next world is revealed behind its trailing edge. Used at 4.30, 22.45.
2. **Frame push / pull** (T2): the camera enters a rectangle that becomes the next canvas, or leaves one to show where it lies. Used at 7.95 (push into a timeline frame), 18.15 (pull out from the stamped sheet).
3. **Carried object** (T3): one element crosses the cut unchanged and the world flips behind it. The render card becomes the script sheet (9.72), the waveform flattens into the line that opens the dark beat (13.62), the line splits open to the paper stamp (15.20).

## Easing

- Arrivals: `power3.out`, 0.35 to 0.6 s. Word rises: `power2.out` 0.32 s with a 4-frame blur tail.
- Physical impacts (stamp, cut): `expo.in` into contact, then 2 to 3 frames of settle, no overshoot.
- Camera: `power2.inOut` 0.6 to 0.8 s.
- No `back`/`elastic` eases anywhere.

## Density and holds

- 1 to 5 visible words per frame. Each payoff word holds at least 0.5 s after it settles.
- The densest frame is the studio desk (20.9 s). The CTA is the emptiest frame after the dark beat.

## Never

- Subtitles of the narration, per-letter Arabic, bounce, perpetual drift, crossfades between paper and night, fake prices, fake discounts, countdowns, fake UI chrome, logos of third parties beyond the one After Effects tile reference, text on a rectangular photo.

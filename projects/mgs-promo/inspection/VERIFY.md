# Verification log

Final file: `renders/mgs-promo-final.mp4`

## Technical (ffprobe on the delivered file)

```
video  h264 High L4.1, 1080x1920, yuv420p, tv range, bt709/bt709/bt709, 30/1 fps, 798 frames, 26.600 s
audio  aac LC, 48 kHz stereo, 26.602 s
file   34.5 MB, 10.4 Mb/s, moov before mdat (faststart)
```

Render path: `npx hyperframes render -f 30 -q delivery` (beginframe capture), then one social encode:

```
ffmpeg -i <hyperframes render> -c:v libx264 -preset slower -profile:v high -level 4.1 -crf 17 \
  -maxrate 14M -bufsize 28M -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 \
  -color_trc bt709 -color_range tv -r 30 -c:a aac -b:a 256k -ar 48000 -movflags +faststart
```

## VO sync

Cross-correlation of the final file's audio against `assets/audio/vo-master.wav` (8 kHz mono): lag **0 ms**, normalised correlation 0.977 (the rest is the three SFX). Audio after 26.13 s peaks at 5e-8, so the 0.48 s CTA tail is silent. The VO was not trimmed, stretched or resampled in time.

## Determinism

Two independent renders of the final code: **798/798 frames bit-identical** (`framemd5`).

This check caught a real bug. Earlier renders disagreed run to run (up to 245 frames, 46 to 55 dB PSNR). The cause was the grain layer swapping `background-image` every 2 frames, so a frame could be captured before the new tile had painted. All three tiles now stay painted and only opacity switches.

## Fonts

`tools/font-check.cjs`: all four faces report `loaded` after `window.__ready`. Measured widths of the hero strings differ from the fallback faces (serif 1343 vs 1371 px, sans 1386 vs 1438, mono 1583 vs 1746).
Red run: with `thmanyahserifdisplay-Black.woff2` removed from a scratch copy, readiness fails with `NetworkError` and the gate prints FAIL.

## Arabic and clipping

`skills/motion-director/scripts/clip-audit.js --step 0.1 --min 0.5 --safe 48` over 0 to 26.6 s: **PASS**, no clipping and no safe-margin warning. The B1 registration slices carry `data-crop="intentional"` in `index.html`; a re-render with the attribute is frame-identical to one without it (framemd5, 798/798).
Red run: the CTA moved 186 px right in a scratch copy gives `CUT 23.70-26.50s "اترك" cut by frame: right 82px`, FAIL.

The audit also exposed a vacuous pass. While a code comment had swallowed the slice positioning, B1 rendered blank and the audit passed because no text was visible. Rendering and looking found it. The rule stays the same: a clean audit only proves geometry, so the frames still need a look.

Eye checks at full resolution: joined letters, dots and hamza intact, «هذا؟» question mark in the right place, «الـVoice Over» and «Claude Code» in correct bidi order, the ر tail of «أكثر» clear of the line.

## HyperFrames check

`npx hyperframes check`: passed. Lint 0 errors, motion 0 findings, contrast 29/29 WCAG AA, layout 0 errors.
Remaining lint warnings are structural advice to split scenes into sub-compositions. They are kept monolithic on purpose: four transitions carry an object across scene boundaries (the timeline frame push, the canvas-to-sheet carry, the waveform-to-line flatten, the stamped-sheet pull-out), and one timeline keeps those handoffs exact.

## Still-frame gate

`inspection/contact-sheet-final.png`: first frame, 0.5 s, 1 s, a midpoint for every beat, every transition, the CTA and the final frame, all taken from the delivered file.

## Motion gate

- Pass 1, sound on: all nine beats hit on their word times from `beat-map.md`. Cuts land in the measured pauses (1.50, 4.33, 13.62, 15.18, 18.14, 22.45). The stamp lands on «عرض», «Claude Code» on its word, and the CTA words on «اترك» and «تعليق».
- Pass 2, sound off, phone scale: `inspection/phone-pass-draft-v1.png`. One focal anchor per frame, and the payoff word reads at 150 px wide.
- Transitions frame by frame: `inspection/transitions-draft-v1.png`.

## Anti-slop subtraction

Each effect is kept only if it does a job:
- Slice registration (B1): the hook, shows motion before any word is heard. Kept.
- Scissors cut and tile drop (B2): shows "without After Effects". Kept.
- Typed command (B3): the real install line. Kept.
- Timeline push (T2): idea becomes canvas. Kept.
- Sketch, then wireframe, then render (B4): the spoken "from idea to render". Kept.
- Script sheet and read head, then waveform (B5): script becomes voice, using this film's real script and envelope. Kept.
- Line split (B6 to B7): a reset with a reason. Kept.
- Stamp: the offer, with no invented numbers. Kept.
- Desk pull-out: "the tools are yours". Kept.
- Blinking caret (B9): waits for the comment. Kept.

Not present: floating cards, glow, gradients, bounce, perpetual drift, per-letter Arabic, subtitles, fake prices, discounts or timers.

## Known limits

- Runtime is 26.6 s, over the 25 s target, because the supplied WAV itself is 26.12 s (last word ends 25.89 s).
- The After Effects tile is a drawn reference to the product (purple tile with "Ae"). It is not Adobe's artwork, but it evokes their mark. Review it before paid placement.
- CC BY-SA photos need a credit line where the film is posted (`ASSET_SOURCES.md`).

# Motion Graphics Skills: "The Curve" (promo v2)

A 31 s vertical promo (1080 × 1920, 30 fps) for this repository, cut to a supplied English voice over.
The direction comes out of `mix-and-match` (see `../skills-countdown-promo/mix/mix-brief.md`): two supplied reference reels plus one wildcard, an animation graph editor.

One coral easing curve directs the film. It draws itself like a graph-editor curve, tangles on "week", snaps straight on "skip",
carries each skill as a keyframe diamond with its mascot, then becomes a beat map, a waveform, a film strip, a 9:16 phone, the frame of the video, and the arch the crew stands on.
A playhead sweep flips the world between paper and a black void. Each spoken line shows a few words, landing on the times they are spoken, and one coral key word.

**Watch:** [`renders/skills-promo-curve.mp4`](renders/skills-promo-curve.mp4). The root README shows an 18 s preview (`assets/readme/curve-promo-preview.gif`) linked to the same file.

| Path | What it is |
|---|---|
| `index.html` | the composition: a 16-segment bezier morph engine and one seek-safe GSAP timeline |
| `assets/audio/vo.wav` | the supplied voice over, untouched (27.48 s) |
| `assets/audio/vo-words.json` | word timings measured with faster-whisper `small.en` (timing only; on-screen words come from the script) |
| `tools/cues.py` | writes every sound cue from the measured word times |
| `ASSET_SOURCES.md` | where every asset came from |
| `renders/skills-promo-curve.mp4` | the delivered film |

## Commands

```bash
python3 tools/cues.py
npx hyperframes@0.8.92 lint
npx hyperframes@0.8.92 snapshot --at 0.5,3.2,6.2,8.3,11.9,14.2,17.8,20.4,22.4,24.7,30.5
npx hyperframes@0.8.92 render -f 30 -q delivery -o renders/out.mp4
ffmpeg -i renders/out.mp4 -c copy -movflags +faststart renders/skills-promo-curve.mp4
```

## Delivery check

- **Encoding:** H.264, yuv420p, bt709, 930 frames (31.0 s), AAC.
- **Loudness:** -14.2 LUFS integrated, -1.6 dBTP peak, straight from the render, with no extra mastering.
- **Mix:** the music bed sits about 14 dB under the voice.
- **Review:** `video-review-loop` reported 0 hard findings. The remaining warnings are reading holds under 0.8 s, plus the quiet tail after the last word.

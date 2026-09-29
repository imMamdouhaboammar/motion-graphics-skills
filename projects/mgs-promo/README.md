# Motion Graphics Skills — Arabic promo

A 26.6 s vertical (1080 × 1920, 30 fps) promo for this repository, cut to a supplied Saudi voice-over. Built with HyperFrames under the direction of the `motion-director` skill.

## Files

| Path | What it is |
|---|---|
| `renders/mgs-promo-final.mp4` | final master (H.264 High, yuv420p, BT.709, AAC 48 kHz, faststart) |
| `renders/mgs-promo-draft-v1.mp4` | the previous draft, kept for comparison |
| `index.html` | the composition (one GSAP timeline, seek-safe) |
| `BRIEF.md` | the confirmed brief |
| `reference-study.md`, `reference/` | analysis of the supplied reference video |
| `openings.md`, `studies/` | three opening studies and the choice |
| `MOTION.md` | motion thesis and frame system |
| `beat-map.md` | measured VO timings and the beat plan |
| `ASSET_SOURCES.md` | provenance and licences for every asset |
| `inspection/` | contact sheets, still-frame gate, verification log |
| `tools/` | seeded texture generator and cutout keying/treatment |
| `assets/audio/vo-master.wav` | the supplied VO, untouched |

## Commands

```bash
npx hyperframes check                 # lint + runtime + layout + motion + contrast
npx hyperframes snapshot --at 0,1,5   # proof stills
npx hyperframes render -o renders/out.mp4
```

The render path used for delivery, and the exact encode flags, are in `inspection/VERIFY.md`.

## Credits

Photography under CC BY-SA needs a credit line where the film is posted. See `ASSET_SOURCES.md`.

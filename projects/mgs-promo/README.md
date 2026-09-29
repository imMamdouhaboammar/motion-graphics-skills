# Motion Graphics Skills — Arabic promo

A 26.6 s vertical (1080 × 1920, 30 fps) promo for this repository, cut to a supplied Saudi voice-over. Built with HyperFrames under the direction of the `motion-director` skill.

## Files

| Path | What it is |
|---|---|
| `renders/mgs-promo-final.mp4` | final master (H.264 High, yuv420p, BT.709, AAC 48 kHz, faststart) |
| `renders/mgs-promo-draft-v1.mp4` | the previous draft, kept for comparison |
| `renders/mgs-promo-final.ar.vtt` | Arabic captions sidecar (approved script text, measured VO timings) to upload with the post |
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
npx hyperframes@0.8.92 check             # lint + runtime + layout + motion + contrast
npx hyperframes@0.8.92 snapshot --at 0,1,5  # proof stills
npx hyperframes@0.8.92 render -f 30 -q delivery -o renders/out.mp4
bash tools/determinism-check.sh      # two renders, second under CPU load, framemd5 compare
```

The render path used for delivery, and the exact encode flags, are in `inspection/VERIFY.md`.

## Credits

Photography under CC BY-SA needs a credit where the film is posted. A copyable credit with authors, sources and licence links is in `ASSET_SOURCES.md`.

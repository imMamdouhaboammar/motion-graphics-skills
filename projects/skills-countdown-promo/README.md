# Motion Graphics Skills: promo reel

A 52 s vertical promo (1080 x 1920, 30 fps) for this repository, built with HyperFrames under the `motion-director` skill.
English copy, no voice over: a CC0 hip-hop bed at 110 BPM plus sound effects, most of them picked from the repo's own SFX library with `sfx-picker`.

The structure follows a supplied reference reel (a "5 secret codes" countdown): grey grid paper, words that settle out of a blur,
black starbursts that frame every numbered beat, a dark prompt card with the command hanging on a dashed wire,
a radial blur flash into a follow-up (pills or a doc screen), and a black end card with a save button.
The reference's assets, brand and copy are not used. The repo's pixel mascots appear in every item and as a crew on the end card.

| Path | What it is |
|---|---|
| `index.html` | the composition: one seek-safe GSAP timeline, scenes built from the `SK` config |
| `SCRIPT.md` | the on-screen script with timings and the facts it relies on |
| `tools/cues.py` | writes every `<audio>` cue from the same bar grid the timeline uses |
| `ASSET_SOURCES.md` | where every image, sound and font came from, with licences |
| `renders/skills-promo-final.mp4` | the delivered film |

## Commands

```bash
python3 tools/cues.py                                  # after changing any cue
npx hyperframes@0.8.92 lint
npx hyperframes@0.8.92 snapshot --at 1,5.6,9.6,20.3
npx hyperframes@0.8.92 render -f 30 -q delivery -o renders/out.mp4
```

To change the number in the hook, edit `COUNT` in `index.html` (it is 49: the skill folders with a SKILL.md on `main`).

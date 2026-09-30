# JEDAR | ليش مجاني؟

Arabic 9:16 motion film for JEDAR (جدار), a Saudi media-crisis agency. 1080×1920, 30 fps, 59 s: a 57.8 s Saudi VO plus a 1.2 s hold on the last frame.

Script: angle 8 ("why the free assessment exists") from the `jedar-script-writer` skill. Visual grammar: reverse-engineered from a client-supplied editorial reference film (see [reference-study.md](reference-study.md)). Timing: [beat-map.md](beat-map.md).

## Files

| Path | What it is |
|---|---|
| `index.html` | The whole composition (HTML, CSS, GSAP). Exposes `window.seek(t)`, `window.DURATION`, `window.__ready` |
| `assets/transcript.json` | Word-level timings of the VO from faster-whisper `medium`. Timings only: on-screen text comes from the approved script |
| `assets/vo.wav` | Supplied VO, 48 kHz mono, 57.81 s |
| `assets/fonts/` | Thmanyah Sans and Thmanyah Serif Display, copied from `projects/mgs-promo/assets/fonts/` |
| `assets/tex/` | Paper fibre and grain, copied from `projects/mgs-promo/assets/tex/` |
| `renders/JEDAR-lesh-majani-final.mp4` | Delivered film, H.264 about 3.4 Mbps, AAC 128k, 25.6 MB |
| `renders/contact-sheet.jpg` | One frame per second of the delivered film |
| `tools/render.js` | Frame-by-frame renderer, from `projects/four-steps-events/tools/render.js` |
| `tools/clip-audit.js` | Arabic clipping audit, from `skills/motion-director/scripts/clip-audit.js` |
| `tools/stills.js` | Writes JPEG stills at given times for review |
| `tools/transcribe.py` | The transcription command that produced `transcript.json` |

The 79 MB CRF 18 master is kept out of Git, following [Heavy binaries in normal Git history](../../Failure-lessons/delivery-and-repo-workflow.md#heavy-binaries-in-normal-git-history). It can be rebuilt with the commands below.

## Build

```bash
npm install                      # gsap + playwright
npm run serve                    # separate terminal, serves on :8765
CHROME_PATH=/path/to/chrome npm run render   # renders/video.mp4, video only
ffmpeg -i renders/video.mp4 -i assets/vo.wav \
  -filter_complex "[1:a]apad=pad_dur=1.2,aresample=48000[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t 59 -movflags +faststart renders/master.mp4
npm run audit                    # clip audit over the whole film
```

`CHROME_PATH` is needed when the installed Playwright package expects a browser build the machine does not have (see [the Playwright entry](../../Failure-lessons/delivery-and-repo-workflow.md#environment-tooling-assumed-rather-than-checked)). Opening `index.html` without `?render` and clicking the page plays a live preview with the VO.

## Open items

- The JEDAR wordmark is set in Thmanyah Serif Display because no official logo was supplied. Replace it when the logo arrives.
- No music or sound effects. VO only.
- The reference film uses AI-generated photographic collage. This film uses flat vector illustration in the same palette. The substitution was declared to the client at delivery.

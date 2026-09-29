# Four Steps, events film (9:16, Arabic)

A 54.4-second editorial paper-collage motion film for Four Steps, built as code and timed to the supplied voice-over. The delivery file adds a 1.2 s silent hold on the clean end lockup (55.57 s).

## Files

| File | What it is |
|---|---|
| `reference-study.md` | Forensic study of the reference reel: shot log, cuts, 23 findings, what to borrow and what to leave |
| `brand.md` | Brand facts, proof we may show, assets, never-list |
| `MOTION.md` | Campaign art direction: colour roles, type system, timing, motion, texture |
| `beat-map.md` | Beat map measured from the WAV (silence detection + word timestamps) |
| `openings.md` | The three opening directions, scored, and why A was chosen |
| `index.html` + `film.js` | The film. One master composition, every frame a pure function of `t` |
| `assets/` | Thmanyah webfonts, Four Steps and event logos, generated prop cutouts, the VO and its Arabic caption track (`captions.ar.vtt`) |
| `tools/` | `render.js` (frame-exact renderer), `stills.js` (frame capture), `fontcheck.js` (fallback-font check), `contact_sheet.py`, `inspect_sheets.py` (a frame every 0.5 s, and old/new pairs) |
| `renders/` | Opening previews A/B/C, Draft v1/v2, `Final.mp4` and `Final-endhold.mp4` (v1, kept as is), `Final-v2.mp4` (polish pass, with the 1.2 s end hold), `Final-v2-wav-exact.mp4` (same film cut to the WAV length) |
| `contact-sheet.png` | Inspection frames from Final v2 |
| `contact-sheet-v1.png` | The same frames from v1, for comparison |
| `inspection/` | Final v2 every 0.5 s, and v1/v2 pairs at the reviewed moments |

## Setup

```
npm install                         # installs playwright (declared in package.json)
npx playwright install chromium     # browser used by the tools
```

ffmpeg and ffprobe must be on PATH.

## Run it

```
python3 -m http.server 8765        # from this folder
open http://127.0.0.1:8765/index.html            # realtime preview, click for sound
open http://127.0.0.1:8765/index.html?t=22.5     # frozen at 22.5 s
open http://127.0.0.1:8765/index.html?opening=B  # alternative opening
```

`window.seek(seconds)` draws any frame, in any order, identically every time. With `?render` the realtime clock is off and an exporter drives `seek()`.

## Render

```
node tools/render.js "" out-video.mp4 0 54.361 30
ffmpeg -i out-video.mp4 -i assets/vo.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart final.mp4
```

No `-shortest`: the video runs 1631 frames (54.367 s) against the 54.361 s WAV, so neither stream is cut.

`?tail=N` holds the clean end lockup for N seconds after the VO. The render range must include the hold, so pass the full duration (54.361 + N) as `t1`, or omit it. Pad the audio to match when muxing:

```
node tools/render.js "tail=1.5" out-video.mp4 0 55.861 30
ffmpeg -i out-video.mp4 -i assets/vo.wav -filter_complex "[1:a]apad=pad_dur=1.5[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart final-endhold.mp4
```

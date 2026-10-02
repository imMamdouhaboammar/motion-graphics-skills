---
name: whiteboard
description: Make hand-drawn whiteboard / doodle-explainer / sketch-note animation videos (MP4) with code — marker lines that draw themselves on, a cartoon hand holding a marker that follows the pen tip, handwritten text (Latin + CJK) written left to right, hatching and highlighter fills, arrows/circles/callouts/icons, two doodle characters (Bo the kid, Mochi the cat), camera pans across a big board, eraser wipes and page flips. Canvas 2D rendered frame by frame in headless Chrome, encoded with ffmpeg. Use when a reference video or brief calls for a whiteboard animation, VideoScribe-style explainer, doodle / sketch-note / marker-drawing / notebook-doodle look, 白板動畫 / 手繪解說 / 塗鴉解說 / 手寫字, or when the video-clone router picks the whiteboard style.
---

# Whiteboard engine

Every frame is a pure function of time `t`. `studio.html` loads `src/kit.js` (shared ReelMimic runtime: timeline,
timing/motion helpers, camera, render hooks), `src/whiteboard.js` (the look: board, marker strokes, drawOn,
handwriting, icons, hand, transitions, captions), `src/cast.js` (characters) and your scene files. `render.mjs` drives
headless Chrome for contact sheets / crops / frames and ffmpeg encodes the MP4.

**Read [GUIDE.md](GUIDE.md) in full before designing anything** — it has the look rules, the complete API with
examples, the character system and the review checklist. Look at the model sheets: `docs/faces.jpg` (16 expressions
× 2 characters), `docs/poses.jpg` (views, walk, jump, props), `docs/kit.jpg` (icons, strokes, fills, text) and
`docs/demo-sheet.jpg` (the demo).

## Workflow

1. **Scaffold**: `bash .claude/skills/whiteboard/scripts/new_project.sh <project-dir>` (`--keep-demo` keeps the demo
   hooked up). Copies the template, runs `npm install`, checks node / ffmpeg / Chrome.
2. **Plan the board.** Whiteboard films are planned as a BIG BOARD: decide where each idea is drawn in world
   coordinates, and let the camera travel between areas (one shot) or clear the board (eraser wipe / page flip = new
   shot). Write the reads per shot (see GUIDE §Timing): each drawing is a read, and the hand must not cover a read.
3. **Build** one IIFE file per shot/chapter in `src/scenes/`, ending with `shots([[t0, fn], ...])`; add its
   `<script>` to `studio.html`. Set `duration` in `src/config.js`.
4. **Look** (from the project dir), open every image with Read:
   ```bash
   node render.mjs --sheet=0.5,1.5,2.5,3.5 --cols=4 --w=480 --out=out/check/a.jpg     # key frames
   node render.mjs --strip=3.6:4.4 --cols=6 --w=320 --out=out/check/jump.jpg          # every frame of a move
   node render.mjs --sheet=3.2 --crop-at=1340,640,560,560 --w=560 --out=out/check/face.jpg   # detail at a world point
   node render.mjs --loop=faces --sheet=0 --cols=1 --w=1920 --out=out/check/faces.jpg  # model sheets (poses, kit)
   ```
5. **Render**: `node render.mjs --frames --workers=4 && node render.mjs --encode --out=out/video.mp4 [--audio=...]`
   (or `--clip` for short ones). ~20–60 ms/frame single-threaded at 1920×1080.

## API in one screen

```js
function shot(t, lt, dur) {                                   // lt = time in this shot
  wbBegin(lt, { cam: [[0, [900, 540, 1.1]], [2, [1400, 560, 1]]], bg: { kind: 'white' } });   // clock + camera + board
  const box = writeOn('Save time 省時間', 300, 300, .2, 1.2, { size: 110, col: INK.blue });    // handwriting
  drawOn(S.underline(box.x, box.y2 + 4, box.w, { col: INK.orange }), 1.25, 1.5);              // strokes, drawn on
  drawOn([...ICON.clock(600, 620, 220), ...S.arrow(760, 620, 1000, 600)], 1.6, 2.6);           // icons + arrow
  bo(1300, 940, 40, { face: 'happy', draw: [2.7, 3.8], hold: { R: 'coin' } });                // character, drawn on
  camEnd(); eraseWipe(seg(lt, dur - .8, dur));                                                // transition (screen space)
}
wbCaptions([[.3, 4, '每天*省下*一小時']]);                                                   // overlay captions
```

- Strokes: `S.line/path/circle/ring/arc/dot/rect/arrow/underline/wave/zigzag/spiral/bubble/box/cloud/heart/star/check/
  cross/rays/sparkle/speed/fill`, `hatch(poly)`, `scribble(poly)` (highlighter), `hilite(x,y,w,h)`, `place(strokes, x, y,
  ang, scale)`, `polyCircle`, `polyRect`. `drawOn(strokes, a, b, {hand, all, x, y, alpha})`, `ink(strokes)`.
- Text: `writeOn(text, x, y, a, b, {size, col, align, lh, weight})` → box; `textBox()` measures only.
- Icons: `ICON.bulb/clock/coin/money/heart/check/cross/checkbox/phone/house/star/chart/gear/mail/search/target/cloud/
  trophy/person(cx, cy, size, {col, key, rays})`.
- Characters: `bo(x, y, u, o)`, `mochi(x, y, u, o)` → `{hand:{L,R}, head, top, strokes}`; `o = {face, look, view, flip,
  sq, dy, tilt, arm:[[ang,bend],[ang,bend]], leg, walk, hold:{L,R}, emote, draw:[a,b], hand, shirt, id, blink}`.
  `mood(lt, [[t,'face'],...])`, `stroll(lt, t0, t1, x0, x1, u)`, kit `jump()`, `take()`. `EXPR_NAMES` (16), `PROPS`.
- Board & camera: `wbBegin(lt, {cam, bg:{kind:'white'|'paper'|'grid', margin, frame:[x,y,w,h]}, drift})`, `board()`.
- Transitions: `eraseWipe(p)` (screen, end of shot), `pageFlip(p)` (screen, start of next shot), `eraseRect(x,y,w,h,a,b)`
  (world, erase one area), camera pans across the board (one shot with camera keys).
- Hand: automatic (follows every drawOn/writeOn; glides between close drawings, exits bottom-right on pauses).
  `WB.hand = false` hides it, `{hand:false}` per call, `handAt(x, y, {tool})` forces it. `WB.sleeve` colour.
- Colours: `INK.black/blue/red/orange/green/purple/grey/yellow/pink/skin`, highlighters `HL.yellow/pink/green/blue/orange`.

## Rules that matter most

1. **Everything is drawn ON.** New things appear by `drawOn` / `writeOn` with the hand, never pop in. Only characters
   that were already drawn may move/animate; props arrive in hands or get drawn.
2. **One marker, one width.** Line weight stays ~`WB.w` (9 px) everywhere; icons scale, lines don't. Black for
   outlines, 1–2 accent colours per board area, highlighter for emphasis.
3. **The hand must not hide a read.** It covers the lower-right of whatever it draws. Draw first, then act (characters
   react after the hand has left), or place the drawing so the arm doesn't cross the action.
4. **Big and legible**: characters u ≥ 30 in a medium shot (Bo ≈ 10.5u tall), text ≥ 90 px at zoom 1, captions via
   `wbCaptions` (64 px card).
5. **Pure function of t**: no `Math.random`, no state across frames; always call every `drawOn` of the shot every frame
   (it draws nothing before `a`) so the hand knows what comes next. Give moving strokes a fixed `key`.
6. **Transitions at every seam**: eraser wipe, camera pan to the next area, page flip, or a hand-drawn frame.

## Engine gotchas

- `drawOn` reveals in array order but paints in `z` order; fills (`S.fill`) default to z −1 (under lines), `mode:'ink'`
  multiplies (lines show through), `mode:'cover'` hides what's under.
- Builders seed their wobble from their coordinates: a stroke that MOVES must get `{key:'name'}` or it will shimmer.
  Characters and `PROPS` already do this.
- `eraseWipe` / `pageFlip` are SCREEN-space: call `camEnd()` first. `pageFlip` re-renders the previous shot's last
  frame (costs one extra shot render per frame for ~0.9 s).
- Fonts: Kalam (Latin) + LXGW WenKai TC (CJK) from Google Fonts. `ENGINE.setup` scans every loaded script for the
  characters it needs; text built at runtime from other sources → add it to `window.WB_TEXT` before boot.
- Don't name globals `S`, `INK`, `HL`, `WB`, `PEN`, `ICON`, `PROPS`, `EXPR`, `board`, `ink`, `bo`, `mochi`, `hatch`,
  `mood`, `stroll` in scenes (they're the library's). Keep helpers inside the scene IIFE.

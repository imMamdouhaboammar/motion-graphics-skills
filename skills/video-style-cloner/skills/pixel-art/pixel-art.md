---
name: pixel-art
description: Make modern, polished pixel-art animated videos (MP4) with code — indie-game look (Celeste / Eastward / Stardew-level scenes, original), 480×270 art upscaled ×4 with nearest-neighbour, limited palettes (day / dusk / night) with Bayer dithering, parallax skies, hills, forests and towns, dithered light and weather, auto-outlined procedural pixel characters with 16 expressions, walk cycles, jumps and held props, emote bubbles, dither / diamond / iris / block transitions and crisp RPG dialogue-box captions (Latin + CJK). Canvas 2D in headless Chrome, encoded with ffmpeg. Use when a reference video or brief calls for pixel art, 8-bit / 16-bit, retro game, JRPG, cozy-game or 像素風 / 像素動畫 / 點陣 looks, or when the video-clone router picks the pixel-art style.
---

# Pixel art engine

Every frame is a pure function of `t`. Shots draw into a **480×270 software framebuffer** (world unit = one art
pixel), `ENGINE.end` upscales it ×4 to 1920×1080 with nearest-neighbour, and `window.overlayHook` draws crisp pixel
captions on top at full res. Same render contract and `render.mjs` CLI as painted-animation.

## Workflow

1. **Scaffold:** `bash .claude/skills/pixel-art/scripts/new_project.sh <project-dir> [--keep-demo]`, then **read
   `GUIDE.md` in full** (look rules, full API, character system, review loop). Look at `docs/model-faces.png`,
   `docs/model-views.png`, `docs/kit-sheet.png`, `docs/demo-sheet.jpg`.
2. **Storyboard** with reads per shot (as in painted-animation). Pick a palette per shot (`pal('day'|'dusk'|'night')`)
   and a colour arc.
3. **Build one file per shot** in `src/scenes/`, IIFE-wrapped, ending with `shots([[t0, fn], ...])`; add a `<script>` in
   `studio.html` (replace the demo). Scenes call only the library + cast; never redraw a character's body.
4. **Review every shot** (sheet, strips of every action and transition, crops of faces), fix, repeat:
   ```bash
   node render.mjs --sheet=0.5,1,1.5,2 --cols=4 --w=480 --out=out/check/a.jpg
   node render.mjs --strip=3.3:4.3 --cols=6 --w=320 --out=out/check/jump.jpg
   node render.mjs --sheet=4.5 --crop=780,380,700,560 --w=700 --out=out/check/face.jpg
   node render.mjs --loop=faces --stills=0.5 --out=out/sheets          # model sheets: faces | views | kit | wipes
   ```
5. **Render:** `node render.mjs --frames --workers=4 && node render.mjs --encode --out=out/video.mp4 [--audio=...]`.

## API in one screen (details in GUIDE.md)

- Camera/layers: `camAt(cx, cy)` (snapped), `layer(f)` parallax, `screenSpace()`, `punch(2, x, y)` integer punch-in
  (medium shots), `shake(t, amt)`, `clip()/noclip()`, `measure(fn)` (dry-run a draw to get positions).
- Colour: `pal(name)` → `P` (ramps: `sky cloud far mid grass earth stone wood light sun accent cool`, `ink paper rim`),
  `shade(c, ±k)` walks the ramp (hue-shifted beyond it), `regRamp([...])`, `dith(x,y,d)`, `qd(d)`.
- Primitives: `px rect line(w) pline curve disc oval ring poly ball sprite(rows,map,x,y) tile tilemap tinyText`,
  all with optional dither density `d`. Outlines: `beginSpr(); part(); … endSpr({tint,z,flash})` or `outlined(fn)`.
- World: `sky sunDisc stars clouds hills forest city ground tree bush`; light: `glow light shadowAt vignette`;
  weather/fx: `rain snow sparkles fireflies birds petals puff`; `emote(kind, x, y, {age})`.
- Transitions (call last, screen space): `dissolve(k)`, `iris(k, x, y, {shape})`, `diamonds(k, {dir})`,
  `blocks(k, {dir})`, `crossDither(k, drawA, drawB)`.
- Captions (overlay): `say(c, t, t0, t1, text, { name })` RPG box + typewriter; `pxText(c, text, x, y)`;
  declare strings with `useText('…')` at load.
- Cast: `pip(x, y, o)` (round, 40 px), `juno(x, y, o)` (tall, 65 px); `o = { t, face, view, flip, look, sq, dy, arm,
  bend, hold, walk, air, drag, wind, emote, emoteAge, emoteSide, tint, z }` → `{ head, top, hands, face }`.
  `act(t, keys)` acted expression changes, `walkTo()` foot-planted walks, `st(t)` 12 fps sprite time, `vel(f, t)`,
  `PROP.kite/spool/lantern/flower/balloon/mug/letter/star/umbrella`, `ARM.down/low/out/up/high`, `footShadow()`.

## Rules that matter most

1. **Pixel discipline.** Everything goes through the library (it snaps to whole art pixels). Never draw with `G`/Canvas
   paths, never scale by non-integers, no anti-aliasing, no gradients except dithered ones, colours from `P`/`CR` ramps.
2. **Motion on steps:** poses, walk frames, blinks, weather use `st(t)` (12 fps); positions and camera may move every
   frame (snapped). Squash/stretch, jump anticipation, follow-through (`drag` via `vel`) as in any cartoon.
3. **Big enough to read:** wide shots at 1× for establishing; do the acting in **`punch(2)` medium shots** (characters
   ≈ half the frame height). Cut to a punch on an action or a take, never mid-stillness.
4. **Transitions at every seam** — dither dissolve in/out, diamond wipe, iris, blocks; wipe-in direction continues the
   wipe-out direction.
5. **Text only via the overlay caption box** (one line at a time, typewriter), or `tinyText` for in-world signs/SFX.

## Engine gotchas

- Don't declare globals that clash with kit.js or pixel.js names (`W H G P C st px rect line …`): wrap scenes in IIFEs.
- `act(...)` overrides use `'emote' in over`, so `{ emote: null }` removes an expression's default emote.
- Transitions/`punch` are post-effects on the low-res buffer: call `punch()` before transitions in the shot.
- Held props: draw via `hold: [fnBack, fnFront]` so they join the character outline; in side view an arm raised above
  ~0.6 rad crosses the face — do reaches in front view (hands go beside the head).
- The dialogue caption box sits over the bottom ~20 % of frame: keep feet/props above it while it's up.
- Speed: 3–40 ms/frame; a full 10 s demo renders in ~10 s with 4 workers.

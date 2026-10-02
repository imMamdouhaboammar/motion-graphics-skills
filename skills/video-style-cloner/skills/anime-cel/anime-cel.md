---
name: anime-cel
description: Make Japanese TV-anime style videos (MP4) with code — cel-shaded characters with tapered line art, big detailed eyes, hair clumps with a specular band, comedic anime reactions (sweat drop, anger vein, sparkle eyes, ≥< eyes, dot eyes, tears), painted skies with cumulus clouds, school/street/classroom/rooftop sets with time-of-day palettes, speed/focus lines, impact frames, dramatic zooms, smears, sakura petals and anime subtitles (CJK). Canvas 2D rendered frame by frame in headless Chrome, encoded with ffmpeg. Use when a reference video or brief calls for anime / 動畫 / 日系動畫 / アニメ / cel-shaded / slice-of-life / school romance / shōnen-style reactions, or when the video-clone router picks the anime-cel style. 2D only; characters are original (Hina, Ren) or new ones built on the same rig.
---

# anime-cel

Modern TV-anime look drawn entirely by code: characters with confident tapered line art (heavier on the shadow side),
flat cel colour + one hard-edged shadow tone + a rim highlight, large layered eyes, hair built from pointed locks with
an "angel ring" highlight; line-free painted backgrounds; anime staging effects. Every frame is a pure function of `t`.

Read **[GUIDE.md](GUIDE.md)** in full before building anything. Model sheets in `docs/`: `faces-hina.jpg`,
`faces-ren.jpg` (19 expressions each), `turns.jpg` (front → 3/4 → profile), `bodies.jpg`, `motion.jpg` (stances, walk, run), `hands.jpg`, `sets.jpg`,
`fx.jpg`, and `demo-sheet.jpg` (the demo film).

## Workflow

1. **Scaffold** `bash .claude/skills/anime-cel/scripts/new_project.sh <project-dir>` (`--keep-demo` keeps the example).
   It copies `template/`, unhooks the demo, runs `npm install`, checks node/ffmpeg/Chrome.
2. **Storyboard** each shot with its reads (what the viewer must understand, in order, with times) and the anime
   staging you will use (establishing pan, cut on action, focus-line BG for the emotional beat, impact frame, reaction
   close-up…). Set `duration` in `src/config.js`.
3. **Build one file per shot** in `src/scenes/` (IIFE ending in `shots([[t0, fn]])`, add its `<script>` to
   `studio.html`). A shot paints the whole frame: `setTOD()` → `SET.<set>(cam, t)` (opens the camera) → characters →
   `camEnd()` → screen effects → transition. Captions go in `window.overlayHook` with `subtitle()`.
4. **Look at it** (from the project dir), open every image with Read:
   ```bash
   node render.mjs --sheet=0.5,1.5,2.5,3.5 --cols=4 --w=480 --out=out/check/a.jpg    # key frames
   node render.mjs --strip=3.8:4.5 --cols=6 --w=320 --out=out/check/s.jpg             # every frame of an action
   node render.mjs --stills=4.4 --out=out/check/st                                    # full-res PNG to judge faces
   node render.mjs --loop=faces_hina --sheet=0 --cols=1 --w=1920 --out=out/check/f.jpg  # model sheets (faces_ren, turns, bodies, motion, hands, sets, fx, close_hina, close_ren)
   ```
5. **Render** `node render.mjs --frames --workers=4 && node render.mjs --encode --out=out/video.mp4 [--audio=...]`.

## API summary

```js
hina(x, y, u, o) / ren(x, y, u, o) → { head, handL, handR, footL, footR, top, u }   // (x, y) ground point, u = head height px
bust(DESIGNS.ren, x, y, u, o)                       // close-up: (x, y) = head centre
o = { t, turn (-1..1: 0 front, ±.5 3/4, ±1 profile), headTurn, bodyTurn, face ('happy' …), look [x,y], blink, mouth, talk,
      armL/armR [shoulder°, elbow°, hand, wrist°, foreshorten], legL/legR [hip°, knee°], walk: phase, run: phase,
      lean°, bend°, tilt°, sq, dy, flip, sway [x,y], fx ['sweat','vein','steam','gloom','sparkles'], blush,
      prop { hand:'L'|'R', draw: PROPS.envelope, rot°, s, at }, armsOver, ground:false,
      stance:'contra'|'straight', weight:'L'|'R', contra }   // hands: open relax fist point peace spread hold grip pocket
faceAt(t, [[0,'neutral'],[1.2,'surprised']]) · autoBlink(t, seed) · talk(t) · follow(t, f) · walkPose/runPose · stroll
setTOD('day'|'morning'|'evening'|'night') · setLight(x, y) · SET.street / SET.classroom / SET.rooftop (cam, t, o)
focusLines · speedLines · impactFrame · flash · dramaticZoom · smear · smearLines · blurBand · sparkle(s) · petals
slashWipe · irisWipe · subtitle(c, txt, o) · onTwos(t) · kit: kf, seg, ease*, spring, jump, take, camBegin/camEnd
drawing primitives: ink (tapered line), tubePts, ribbonPts, crPts, cel, drawGroup, layer (cache), paintPoly
```

## Rules that matter most

1. **Pure function of t** — no `Math.random()`, no state between frames (`rnd(key)`/`hash()`; `follow()` for springs).
2. **Scenes never draw body parts.** Characters are one call. New characters = a new entry in `DESIGNS` + `HAIR`
   (+ clothes branch) in `cast.js`, never ad-hoc drawing in a scene.
3. **Animate characters on twos** (`const ta = onTwos(lt)` for poses/faces), keep camera moves smooth (`lt`).
4. **Anime timing**: quick actions with a held pose after; anticipation → snap → overshoot (`spring`, `take`); faces
   change on a drawing via `faceAt` (it adds the blink + pop), never by crossfading.
5. **Staging**: establish → react. Emotional peaks cut the BG to a flat gradient + `focusLines`; hits get an
   `impactFrame` (2–3 frames) + `dramaticZoom`; fast moves get `smearLines`.
6. **Sizes**: full body u≈110–150, knees-up 180–260, bust 380–560. Keep faces ≥ u 150 when they carry a read.
7. **Transitions at every seam** (`slashWipe`, `irisWipe` star, `flash`, impact cut, cut on action).
8. **Captions**: only via `overlayHook` + `subtitle()` (white, dark outline, CJK font). Push new caption text into
   `window.EXTRA_FONTS` so the glyphs load before rendering.

## Engine gotchas

- `SET.*` leaves the camera **open**; draw characters in the same world coords and call `camEnd()` before screen
  effects. Screen-space effects (`blurBand`, `impactFrame`, `slashWipe`) use `setTransform` and ignore the camera.
- Characters face screen-right with positive `turn`. With `|turn| > .3` limb angles are "forward/back" in the facing
  direction; in front view they are "outward/inward". The near arm when facing right is `armL`.
- Props in hands: use hand `'hold'` (pinch, prop extends past the fingertips) or `'grip'` (handle in the fist).
  `rot` rotates the prop about the grip point.
- `layer(key, …)` caches static paintings per page; include the time-of-day name in the key if colours depend on it.
- Speed: ~5–25 ms to draw a frame, ~100 ms/frame effective incl. JPEG with 4 workers (first frame ~0.6 s builds caches).

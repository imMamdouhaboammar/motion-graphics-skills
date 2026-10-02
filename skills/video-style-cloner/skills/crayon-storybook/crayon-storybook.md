---
name: crayon-storybook
description: Make warm children's picture-book animations (MP4) drawn in crayon, coloured pencil and pastel on cream drawing paper — waxy crayon scribble fills broken by paper tooth, coloured-pencil outlines, slow 8 fps line boil, page-turn transitions, picture-book page framing and hand-lettered CJK storybook captions. p5.js + p5.brush rendered frame by frame in headless Chrome, encoded with ffmpeg. Use when a reference video or brief calls for a crayon / colored-pencil / pastel / kids' drawing / picture-book / bedtime-story / 繪本 / 蠟筆 / 色鉛筆 / 童書 look, or when the video-clone router picks the crayon-storybook style.
---

# Crayon storybook

A drawing engine for ReelMimic. Every frame is a pure function of time `t`: `studio.html` loads p5.js + p5.brush, the
crayon look library, the cast and your scene files; each shot draws the whole 1920×1080 frame; `render.mjs` renders
contact sheets, strips and crops for review, or all frames in parallel, and ffmpeg encodes the MP4.

**Provenance.** The runtime (`template/src/core.js`, `timeline.js`, `render.mjs`, `studio.html`, the render contract and
helpers: `paint`, `inkLine`, camera, `shots`, `glow`, `jump`/`take`/`spring`, `boilSeed`…) derives from the
**painted-animation** skill (ClaudeAnimationBase, MIT © John Heibel / tuzhechen2005 — see `template/LICENSE`). The
look (`crayon.js`), the characters (`cast.js`), the page turn, the page finish and the captions are this engine's own.

## Workflow

1. **Scaffold** — `bash .claude/skills/crayon-storybook/scripts/new_project.sh <project-dir>` (add `--keep-demo` to keep
   the example). It copies the template, runs `npm install` (which also writes the patched p5.brush build, see
   gotchas) and checks node / ffmpeg / Chrome. Then **read [GUIDE.md](GUIDE.md) in full** and look at
   `docs/demo-sheet.jpg` and `docs/cast.jpg` with Read.
2. **Storyboard** in writing: shots, reads (what the viewer must understand, when), transitions, captions.
3. **Build** — `src/config.js` (`duration`, `bpm`, `fps: 24`); one IIFE file per shot/scene in `src/scenes/`, ending with
   `shots([...])`; add its `<script>` to `studio.html`. Captions: `captions([[t0, t1, '文字', { pos }]])` once.
4. **Look, fix, look again** (from the project dir):
   ```bash
   node render.mjs --sheet=0.5,1.5,2.5,3.5 --cols=4 --w=480 --out=out/check/a.jpg
   node render.mjs --strip=2.0:2.6 --cols=6 --w=320 --out=out/check/strip.jpg
   node render.mjs --sheet=2.3 --cols=1 --crop=600,200,900,700 --w=900 --out=out/check/face.jpg
   ```
   Open every image with Read. At least a sheet per shot, a strip per key action and per transition, a crop per face.
5. **Render** — `node render.mjs --frames --workers=4 && node render.mjs --encode --out=out/video.mp4 [--audio=…]`.

## API in one screen

| area | calls |
|---|---|
| fills | `colorIn(pts, { col, fill: 'scribble'|'hatch'|'cross'|'smudge'|'flat', ang, gap, line, lw, shade })`, `scribbleFill`, `hatchFill`, `crossHatch`, `smudge`, `dab` |
| lines | `crayonLine`, `pencilLine`, `pastelLine`, `sketchLine`, `inkLine(pts, sw, col, brush)` — brushes `crayon`, `crayonFine`, `cpen`, `pastel`, `chalk`, `graphite` |
| shapes | `ellPts`, `rectPts`, `rrPts`, `starPts`, `heartPts`, `through`, `ribbon` (core) |
| scenery | `sky`, `sun`, `cloud`, `hill`/`hillY`, `ground`, `tufts`, `tree`, `flower`, `house`, `paperWash` |
| props | `apple`, `leafProp`, `starProp`, `heartProp`, `balloon`; emotes `emote(kind, x, y, s, k, age)` |
| cast | `lulu(x, y, u, o)`, `kuri(x, y, u, o)` → `{ head, top, handL, handR, feet }`; `feel`, `emotions`, `walkCycle`, `pose` |
| motion | `seg`, `kf`, `ease*`, `backOut`, `spring`, `ring`, `jump`, `take`, `stroll`, `arcPt`, `onTwos`, `pulse`, `shakeXY` |
| camera | `camBegin(cx, cy, zoom, rot)` … `camEnd()`, `toScreen` |
| staging | `shots([[t0, fn], [t1, fn, { turn: 1.0 }]])` (page turn), `bookPage(k)`, `vignette(k)`, `tooth(k)`, `crayonWipe(p)`, `iris`, `flash`, `glow` |
| text | `captions(list)` (storybook captions via `window.overlayHook`), `letter()` for words inside the picture |

## Rules that matter most

1. **Crayon medium only.** Colour shapes in with `colorIn` (pale base + crayon scribble/hatch + coloured-pencil outline);
   lines with the crayon/pencil brushes. No plain p5 `rect/ellipse/fill`, no gradients, no 3D. Turns go through the
   drawn key views (`front`, `q`, `side`, `back`).
2. **Pure functions of `t`.** No `Math.random()`, no state between frames. `hash()` / `rnd(key)` for stable randomness;
   `jit()` only for boil. Call `boilSeed(key)` before each separate background element/prop.
3. **Characters come from `cast.js` only.** Scenes pass poses (`aR`, `bR`, `view`, `walk`, `dy`, `sq`, `hair`,
   `holdR`…) — they never draw a character's parts themselves. New characters go in `cast.js` (or one file each).
4. **Big and legible.** Lulu u ≈ 30–45 in medium shots (≈ 11u tall), Kuri u ≈ 26–36. Captions ≥ 64 px. Keep the
   caption band (bottom ~200 px, or `pos: 'top'`) free of story-critical action.
5. **Alive and acted.** Moods change through `emotions()` (anticipation squint → take → settle); actions have
   anticipation → action → follow-through (`jump`, `spring`, `hair`); something happens in every shot.
6. **A transition at every seam**: page turn (`{ turn }`), crayon wipe, iris, fade from/to paper.

## Engine gotchas

- **Patched p5.brush.** `studio.html` loads `node_modules/p5.brush/dist/p5.brush.crayon.js`, written by
  `patch_brush.mjs` on `npm install`. Stock p5.brush darkens pigment where overlapping stamps saturate (right for ink,
  wrong for wax): butter-yellow turned mustard. If that file is missing, run `node patch_brush.mjs`.
- **Cost = number of colour changes + stroke area.** Each `colorIn` is ~3 brush passes; p5.brush composites a mask per
  colour change. Keep big background shapes sparse (`hill`/`ground` already use wide gaps), don't scribble far
  off-screen. Typical: 150–250 ms/frame for a wide shot, ~350 ms for a busy medium shot with two characters and the
  page border, ~0.7–1 s during a page turn (two pages are drawn).
- **Page turn:** the previous shot keeps being called with `lt > dur` for `turn` seconds — let its motion settle.
- **Don't name globals after p5's** (`line`, `text`, `color`, `scale`, `shape`…): the page never gets ready.
- A `NaN` in a point list throws `Failed to construct 'OffscreenCanvas'`. `**` after a unary minus is a syntax error.
- Strokes far from the origin under zoom ≳ 2 collapse (p5.brush); `paint/inkLine/colorIn` draw around each shape's
  centre, which avoids it for normal sizes.
- Google Fonts load over the network at page load; if a render times out on navigation, just re-run it.
- `src/karaoke.js` (from painted-animation) still works for lyric videos; add its `<script>` if needed.

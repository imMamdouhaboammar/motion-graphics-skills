# Crayon storybook — the drawing and animation guide

Read all of it before drawing. It covers the look, the full API with examples, the cast, how to review your frames, and
the known pitfalls. Model sheets: `docs/cast.jpg` (views + 18 moods of both characters), `docs/looks.jpg` (brushes,
fills, props, emotes), `docs/demo-sheet.jpg` (the demo). The animation principles, the "reads" timing method and the
review discipline are the same as painted-animation's `template/ANIMATION_GUIDE.md` — read its *Timing* and *Animation
principles* sections too; they apply unchanged.

---

## 1. The look

A warm, cosy children's picture book. Think a skilful illustrator using a child's materials:

- **Paper**: cream drawing paper (`PAL.paper`) with soft uneven warmth and fibres. It is under everything; leaving
  paper showing is part of the look.
- **Crayon fills**: every coloured shape is *coloured in* — a pale flat base of its colour, then crayon strokes in the
  full colour going back and forth in one direction (`scribble`), or parallel hatching (`hatch`), or two directions
  (`cross`), or soft powder (`smudge`). Gaps between strokes show the pale base: that's what makes it crayon.
- **Paper tooth**: after the frame is drawn, the paper's tooth is laid over it — pigment skips in the paper's pits,
  so every stroke breaks up the same way. You don't do anything for it; `tooth(k)` scales it (default 1).
- **Coloured-pencil outlines** (`cpen`), dark and fairly thick so they survive a phone screen. Default outline colour
  is a deep tint of the fill colour; characters use the cocoa `PAL.ink`.
- **Gentle palette**: butter, sky, rose, sage, lilac, peach, coral, cocoa (+ `Dk`/`Lt` variants). No pure black or
  white. Pick 4–6 colours per video and keep them.
- **Boil**: linework and fills are re-drawn 8 times a second (`BOIL`, `PROJECT.boil`), like frames re-drawn by hand;
  the tooth shifts with each drawing. Still things hold perfectly between drawings (see `boilSeed`).
- **Staging**: soft warm vignette (always on, `vignette(k)`), optional picture-book page border (`bookPage(k)`),
  gentle camera moves (slow drifts and pushes — never whip pans in this style), page turns between scenes.
- **Naive but skilful**: simple round shapes, chunky proportions, big heads, dot eyes — but clean staging, clear
  silhouettes and real animation (anticipation, follow-through, acting).

Don't: plain p5 shapes (`rect`, `ellipse`, `fill()`), gradients, drop-shadowed vector UI, 3D, photographic textures,
neon colours, black outlines on everything at full strength, busy tiny details.

## 2. Files

| file | what |
|---|---|
| `src/config.js` | `PROJECT = { duration, bpm, offset, fps: 24, boil?, toothBoil? }` |
| `src/core.js` | runtime (from painted-animation): palette `PAL`, timing/motion helpers, camera, `paint`, `inkLine`, geometry, `glow`, `iris`, `flash`, lettering, render hooks |
| `src/crayon.js` | the look: brushes, fills, paper/tooth/grain, page finish, page turn, scenery, props, emotes, captions |
| `src/cast.js` | Lulu and Kuri, faces, moods (`EMO`, `feel`, `emotions`), `walkCycle`, `pose` |
| `src/timeline.js` | `shots()`, `LOOPS`, page-turn orchestration, `crayonWipe` |
| `src/sheets.js` | model sheets as loops: `?loop=cast`, `?loop=looks` |
| `src/scenes/demo.js` | the 10 s example ("The red apple") — one idea, not a template |
| `src/karaoke.js` | optional KTV lyric bar (from painted-animation); not loaded by default |
| `patch_brush.mjs` | writes the crayon-patched p5.brush build on `npm install` |

## 3. Colouring in: the fills

```js
colorIn(pts, o)            // the workhorse
```
| option | meaning |
|---|---|
| `col` | the colour. Strokes use it; the base is a paler version |
| `fill` | `'scribble'` (default) · `'hatch'` · `'cross'` · `'smudge'` · `'flat'` (base only) · `'none'` (outline only) |
| `pale` | how much paler the base is (0 = same, default .6); `base` sets it explicitly; `baseOp` its opacity |
| `tone` | stroke colour if not `col` |
| `ang`, `gap`, `w`, `br` | stroke direction (radians), spacing px (default 13), weight, brush (`crayon`) |
| `over`, `loose`, `run` | scribble: overshoot px at the turns, wobble 0..1, rows per stroke before the crayon lifts |
| `line`, `lw`, `lbr`, `curv` | outline colour (`null` = none), weight (≈ .6–2), brush (`cpen`), smoothing 0..1 |
| `shade` | `{ pts, col, ang, gap }`: an extra scribble pass over a shadow side |

Lower-level: `scribbleFill(pts, col, o)`, `hatchFill(pts, col, { ang, gap, cross, grad })`, `crossHatch`,
`smudge(pts, col, { op, tex })`, `dab(x, y, r, col)` (a little crayon spiral: cheeks, dots, berries).

```js
colorIn(ellPts(600, 500, 160, 120, 30), { col: PAL.rose });                                 // a scribbled pink blob
colorIn(rrPts(900, 400, 300, 200, 30), { col: PAL.sky, fill: 'cross', gap: 16, ang: .7 }); // cross-hatched box
smudge(ellPts(960, 300, 500, 180, 30), PAL.lilac, { op: 90 });                              // a soft pastel cloud of colour
```

Choosing: characters and props → `scribble` (lively); architecture, clothes with pattern → `hatch`; shadows and
night → `cross`; skies, distant hills, glows, cheeks → `smudge`; tiny parts (hands, buttons, eyes) → `flat`.
Big areas cost stroke area: use a bigger `gap` (30–45) and `w` 1.4–1.8 for backgrounds — the pale base carries them.

### Lines and brushes

`crayonLine(pts, sw, col)`, `pencilLine`, `pastelLine`, `sketchLine`, or `inkLine(pts, sw, col, brush, curv)`.

| brush | use |
|---|---|
| `crayon` | wide waxy crayon: fills, rays, grass, big strokes |
| `crayonFine` | smaller crayon: stems, hatching, details (used automatically by `crayonLine` when sw < .7) |
| `cpen` | coloured pencil, thin and grainy: every outline, faces |
| `pastel` | soft powdery stroke: glows, sky streaks, magic trails |
| `chalk` | dry broken stroke |
| `graphite` | light sketch lines, construction lines, rain |

`sw` is a multiplier (≈ .5–2). Built-ins also work: `'2B'`, `'HB'`, `'charcoal'`, `'marker'`, `'spray'`.

### Shapes (core)

`ellPts(cx, cy, rx, ry, n, jitter, rot)`, `rectPts(x, y, w, h, j)`, `rrPts(x, y, w, h, r)`, `starPts(cx, cy, r, inner, n, rot)`,
`heartPts(cx, cy, r)`, `through(P)` (smooth curve), `ribbon(P, w0, w1)` (tapered band as one outline: branches, tails,
scarves, rivers).

## 4. Scenery, props, emotes

- `sky(top, bottom, { y0, y1, x0, x1, strokes })` — soft pastel sky with long crayon streaks. Oversize it if the camera moves.
- `sun(x, y, r, t, { face, rays, glow })`, `cloud(x, y, s, { key, col, line })`
- `hill(cx, cy, rx, ry, col, { gap, ang, line })` + `hillY(x, cx, cy, rx, ry)` (for standing on it),
  `ground(y, col, { x0, x1, depth, gap })`, `tufts(x0, x1, yOfX, n, col, t, key)`
- `tree(x, y, s, { col })`, `flower(x, y, s, col, t)`, `house(x, y, s, { wall, roof })`, `paperWash(t, col)`
- props (centre + size, so a hand hook can call them at (0, 0)): `apple(x, y, r)`, `leafProp(x, y, r, rot, col)`,
  `starProp(x, y, r, col, rot)`, `heartProp(x, y, r, col)`, `balloon(x, y, r, len, col, t)` (x, y = the hand)
- `emote(kind, x, y, s, k, age)`: `'!' '?' heart hearts sweat spark zzz bulb music anger cloud dots swirl` — drawn marks,
  never typed. The cast pops them automatically from moods.
- `glow(x, y, r, col, a)`: additive light (sun halo, lamp, magic). On cream paper it's a gentle bloom.

Every background element: call `boilSeed('unique key')` first (the scenery helpers do it for you, keyed by position).

## 5. Staging and transitions

- **Shots**: `shots([[0, shotA], [4.6, shotB, { turn: 1.0 }], …])`. `fn(t, lt, dur)` draws the whole frame.
- **Page turn**: `{ turn: seconds, turnDir: 1 | -1 }` on the arriving shot. The old page (finished with its own
  vignette/border) curls away from the bottom-right corner, showing its paper back with a faint mirrored ghost of the
  picture and a soft shadow on the new page. The previous shot keeps running with `lt > dur` during the turn.
- **Crayon wipe**: `crayonWipe(p, [c1, c2, c3])` — big crayon bands scribble across (p 0 → .5) and away (.5 → 1); cut
  under full cover. End of A: `if (lt > dur - .35) crayonWipe((lt - (dur - .35)) / .7)`; start of B: `if (lt < .35) crayonWipe(.5 + lt / .7)`.
- **Iris**: `iris(cx, cy, r, PAL.paper)` / `irisShape(heartPts(...), col)` — use paper or cocoa, not black.
- **Fade from / to blank paper**: `flash(k, PAL.paper)` (the storybook way to open and close).
- **Page framing**: `bookPage(k, { m, r, line })` — cream border + hand-drawn frame line; animate `k` in/out.
- `vignette(k)` (default .3), `tooth(k)` (default 1) — set per frame in the shot.
- **Camera**: `camBegin(cx, cy, zoom, rot)` … `camEnd()`. Storybook moves: slow pan down from sky, gentle push-in
  (1.0 → 1.1 over a shot), drift of 20–50 px. Add `shakeXY(t, amt)` only for landings/bumps, small.

## 6. Captions (storybook text)

```js
captions([
  [0.5, 2.5, '露露和小栗出門散步。', { pos: 'top' }],
  [5.9, 7.3, '跳高一點⋯⋯摘到了！'],                       // bottom by default
]);
```
Options: `pos: 'top' | 'bottom'`, `y`, `size` (default 74 px ≈ 15 px on a 390 px-wide phone; don't go below 60),
`rate` (characters written per second, default 16), `box: false` (no paper label), `col`. The text is hand-lettered
(LXGW WenKai TC → Zen Maru Gothic → Noto Serif TC), written on character by character with a slightly uneven baseline,
sits on a torn cream label, and is nibbled by the paper tooth. `captions()` registers `window.overlayHook` and the
font preload; call it once per video. Keep one short sentence per caption, ≥ 1.4 s on screen. Put captions where the
action isn't (`pos: 'top'` over sky in wide shots).

## 7. The cast

Two original characters, drawn by one call each, from the ground point between the feet:

```js
lulu(x, y, u, o)   // small girl: butter raincoat, sky-blue boots, cocoa bob with a star clip. ≈ 11u tall, 5u wide
kuri(x, y, u, o)   // round hedgehog: cocoa spikes, cream face, button nose, pink ears.       ≈ 5u tall, 6u wide
```
Both return `{ head, top, handL, handR, feet }` in world coordinates (for props flying to/from hands, irises, emotes).

| size | Lulu u | Kuri u |
|---|---|---|
| wide | 16–26 | 14–22 |
| medium | 30–45 | 26–38 |
| close-up | 60–90 | 50–80 |

### Options (both)

| group | options |
|---|---|
| pose | `dx`, `dy` (u, − = up), `sq` (squash, − stretches), `rot`, `flip`, `sx`, `sy` |
| arms | `aL`, `aR`: 0 = straight out sideways, + up, − down (rest ≈ −1.2; side view: 0 = forward). `bL`, `bR` (Lulu): elbow bend, + folds the forearm up/in (2 = hand at chest, 2.3 = at chin), − = back (hands on hips ≈ `a −.6, b −1.8`) |
| legs | `walk` (phase, 1 = a full stride; null = standing) — use `walkCycle(ph, side)` |
| hair | `hair` (Lulu: hair and hem lag in u, + flicks up; Kuri: spikes ruffle). Drive with the jump / `spring()` |
| view | `'front' | 'q' | 'side' | 'back'` (all face right; `flip: true` faces left) |
| face | `eyes`, `mouth`, `brows`, `lookX`, `lookY`, `squint`, `blush`, `seed` (blink timing), `noBlink` |
| extras | `emote`, `emoteK`, `emoteAge`; `holdL/holdR(u, sw)` draw a prop UPRIGHT at the hand; `armL/armR(u, sw)` draw in ARM space (+x along the forearm); `propFront` draws props over the hand; `draw(u, sw)` body-local extra |
| colour | Lulu: `coat`, `boots`, `hairCol`; Kuri: `spikes`, `faceCol` |
| boil | `boilKey` — set it if characters appear/disappear mid-shot |

Eyes: `normal wide happy closed squeeze sad cry teary angry heart sleepy shine look scared x` (or a pair). Mouths:
`smile grin laugh o O frown wobble flat wail cat tongue pout` (or `null`). Brows: `up worried angry flat`. Eyes blink
by themselves every 3–4.5 s (per `seed`; give each character a different seed).

Limbs are always attached: arms are one tapered sleeve (shoulder → elbow → mitten) rooted inside the body outline;
legs root under the coat hem; Kuri's paws and feet root inside his body. In front view Lulu's arms draw over everything
(so raised arms show beside her head); in 3/4 and side views the far arm is behind the body and shaded.

**Proportions matter for reach**: Lulu's arms are short (chibi). A straight-up arm (`a 1.5`) ends at ear height; to
reach something overhead use `a ≈ 1.1, b ≈ .35` (up and out) and place the target at the returned `handR`.

### Moods

```js
lulu(x, y, 36, feel('happy', t));                                          // one mood, alive (idle motion on the beat)
lulu(x, y, 36, emotions(lt, [[0, 'curious'], [1.4, 'surprised'], [1.9, 'happy']]));   // acted changes
lulu(x, y, 36, pose(emotions(lt, keys), jump(lt, 2, 2.6, 4), { view: 'q', aR: 1.1 }));  // mood + action + override
```
18 moods: `neutral happy laugh excited love shy proud curious thinking idea surprised scared sad cry angry sleepy
determined relieved`. Each sets eyes/mouth/brows/blush/emote, a take size and an idle body motion locked to `bpm`.
`emotions()` squints and squashes before each change, swaps the face under the squint, fires a take, settles with
overshoot and pops the new emote. Add a mood by adding an `EMO` entry in `cast.js`.

`pose(...ps)` merges pose objects: later ones win, but `dy`, `sq`, `rot`, `dx` ADD (so a mood's bounce and a jump
combine). `walkCycle(ph, side = true, amt)` gives legs, arm swing, bob, sway. `stroll(t, t0, t1, x0, x1, u, stride)`
(core) gives an eased walk `{ x, walk, view, flip }`: `pose(mood, walkCycle(w.walk || 0), { view: 'side' })`.

### Holding and passing props

```js
// holding an apple up in the right hand (upright, the hand grips over it)
lulu(x, y, 40, { ...feel('proud', t), aR: 1.1, bR: .35, holdR: u => apple(0, -u * .6, u) });
// passing it: draw the receiver and the giver, then the prop in flight between their returned hands
const K = kuri(...), L = lulu(...);
const p = arcPt(L.handR, K.handR, 70, ease(seg(lt, tGive, tGot))); apple(p[0], p[1], 40);
```

### New characters

Add a function to `cast.js` (or `src/cast_<name>.js`) following Lulu/Kuri: `boilSeed` per part (`rs(part)`), one
`push/translate/rotate/scale` for pose + squash + flip, parts drawn with `colorIn`, faces through `eyeMark` /
`mouthMark` / `browMarks` / `cheeks`, arms through `arm2()` (attached limbs, hooks, returned hand), return anchors.
Outline weight `sw = clamp(u / 20, .5, 2.6)`; scribble `gap ≈ u * .3`. Keep 3 views minimum (front, q, side).
Characters must be original — never an existing IP. A user's own character (design sheet provided) can be built the
same way.

## 8. Rules for scenes

1. One IIFE per scene file; scenes call library + cast only. No character body parts drawn in scenes.
2. Pure function of `t`: no `Math.random()`, no counters, no state. `hash(i)`, `rnd(key)`.
3. `boilSeed('key')` before every separate element you draw yourself (props, branches, effects).
4. Something happens in every shot; one read at a time; anticipation → action → follow-through; hold after meanings.
5. A transition at every seam, including into the first shot (`flash` from paper) and out of the last.
6. Main subjects big and central; nothing story-critical under the caption label.

## 9. Review loop (do it for real)

```bash
node render.mjs --sheet=0.3,1.2,2.2,3.0,3.6,4.3 --cols=4 --w=480 --out=out/check/a.jpg   # key frames
node render.mjs --strip=5.9:6.9 --cols=5 --w=384 --out=out/check/jump.jpg                # every frame of an action
node render.mjs --sheet=6.45,8.1 --cols=2 --crop=380,240,1000,760 --w=700 --out=out/check/faces.jpg   # faces/hands
node render.mjs --strip=2.0:2.5 --crop-at=L_X,L_Y,500,500 --out=out/check/feet.jpg      # follow a world point
node render.mjs --loop=cast --sheet=1 --cols=1 --w=1920 --out=out/check/cast.jpg         # model sheet
```
(`--cols=1` when you render a single frame with `--crop`.) Open each with Read and check:

- **Look**: unmistakably crayon on paper? Colours bright and gentle (no mustard/olive muddiness — see pitfalls)? Is
  the scribble direction consistent within an object? Paper visible somewhere?
- **Read**: is each shot's event clear from its sheet? Characters big enough at 480 px wide? Faces readable?
- **Acting**: anticipation before jumps/throws, squash on landing, hair/hem follow-through, moods changing through
  `emotions()` not snapping, both arms not doing the same thing.
- **Contacts**: feet on the ground line (use `hillY` on hills), props touching hands (crop them), apples on stems.
- **Boil**: in a strip, frames inside one boil drawing (3 frames at 24 fps / 8 boil) match except what moves.
- **Captions**: legible, not covering the action, on screen long enough.
- **Transitions**: first and last 0.5 s of every shot; page-turn frames look like paper.

## 10. Pitfalls

- **Muddy yellows** mean the stock p5.brush got loaded: `studio.html` must load `p5.brush.crayon.js` (run
  `node patch_brush.mjs`). Stock p5.brush darkens saturated stroke pigment (≈ pigment × .85 − .075): butter → mustard.
- **Speed**: ≈ 150–250 ms/frame wide shots, ~350 ms busy medium shots, ~0.7–1 s page-turn frames (two pages), single
  worker on an RTX-class GPU. Costs: colour changes (each `colorIn` ≈ 3 passes), stroke area (big shapes at small gaps),
  watercolour `smudge` on huge areas. With 4 workers expect ≈ 0.45 s/frame throughput.
- **Jittering still things**: a moving element before them shifted the random stream → `boilSeed(key)` per element.
- **Hidden raised arms**: only in custom characters that draw arms before the head; draw raised arms last.
- **Spiky elbows**: build bent limbs with `limbPts()` (clamped miter), not `ribbon()` (Catmull-Rom overshoots on
  sharp bends).
- **Giant emotes / props**: sizes are in px, not in u. An emote's `s` ≈ u.
- **Huge strokes under zoom**: shapes much bigger than the canvas can lose their outline under camera zoom ≳ 2; split
  long edges into `inkLine`s, keep zoom ≤ 1.6 for wide scenery.
- **Globals**: never name a function `line`, `text`, `color`, `scale`, `shape`, `fill` … (p5 owns them).
- `x ** 2` after a unary minus (`-x ** 2`) is a syntax error that stops the whole page — write `x * x`.
- **Navigation timeouts** in render.mjs = the Google Fonts request was slow; render.mjs retries 3×; re-run if needed.
- The overlay (captions) is skipped for `LOOPS` (model sheets).

# Building a ReelMimic drawing engine

ReelMimic (repo root: `C:/Projects/Eden/Desktop/yt克隆`) turns a reference video + a one-line brief into a new 2D animation.
An AI director plans it, then several builder agents write one scene file per shot in parallel, fresh reviewer agents
check every shot on rendered frames, and a final critic checks the whole film. A **drawing engine** is the skill those
agents use to actually draw the frames. Today there are two (HyperFrames vector, painted-animation watercolor). You are
building one more.

## What you get

- `.claude/skills/video-clone/assets/engine-kit/` — shared runtime, copy these into your template **unchanged**:
  - `kit.js` → `template/src/kit.js`: timeline (`shots`), timing/motion helpers (`seg`, `kf`, `ease*`, `spring`,
    `jump`, `take`, `onTwos`, `onStep`, `pulse`, `hash`, `rnd`), camera (`camBegin/camEnd/toScreen`), render hooks,
    `caption()`, and the `window.ENGINE = { setup, begin, end, crisp }` plug-in point. Read it fully first.
  - `render.mjs` → `template/render.mjs`: headless-Chrome renderer (`--sheet`, `--strip`, `--crop`, `--stills`,
    `--frames` parallel+resumable, `--encode`, `--clip`). Same CLI as painted-animation.
  - `studio.html` → `template/studio.html`: replace `<!-- ENGINE-LIBS -->` with your library scripts and
    `<!-- SCENES -->` with `<script src="src/scenes/demo.js"></script>`.
  - `package.json` → `template/package.json` (rename `name`; add deps only if truly needed).
  - `new_project.sh` → `scripts/new_project.sh`.
- `.claude/skills/painted-animation/` — the reference engine. Read its `SKILL.md` and `template/ANIMATION_GUIDE.md`
  for the standard of craft expected (animation principles, reads, review loop). Don't copy its Clawd character.

## What you build — only inside `.claude/skills/<your-engine>/`

```
SKILL.md                 frontmatter (name, description: when to use) + workflow, API summary, rules, engine gotchas
GUIDE.md                 the full drawing/animation guide for agents: look rules, full API with examples, character
                         system, how to review, known pitfalls
scripts/new_project.sh   (from the kit)
template/
  studio.html render.mjs package.json .gitignore (node_modules, out)
  src/config.js          const PROJECT = { duration, bpm, offset, fps: 24 };
  src/kit.js             (from the kit, unchanged)
  src/<look>.js          YOUR drawing library: primitives, materials, palettes, backgrounds, effects, transitions
  src/cast.js            the character system (see below)
  src/scenes/demo.js     an 8–10 s demo that exercises everything (see below)
docs/demo-sheet.jpg      contact sheet of the demo (render it with render.mjs)
```

### Hard requirements (the production line depends on them)

1. **Pure function of t.** No `Math.random()`, no state carried between frames, no timers. Use `hash()` / `rnd(key)`.
2. **One file per shot works.** Scenes are separate files that only call your library and the cast; they never
   redraw a character's body parts themselves.
3. **Characters in one shared file** (`cast.js`, or one file per character in real projects): a character is drawn by
   one call with pose parameters, e.g. `bean(x, y, u, { face: 'happy', look: .3, arm: [...], sq, flip, view })`.
   Provide: ≥ 8 expressions (neutral, happy, laugh, sad, cry, angry, surprised, scared, love, sleepy…), a front view and
   a 3/4 or side view, walk cycle helper, arm/hand poses that can hold props, squash & stretch, blink. Limbs must always
   stay attached to the body (one continuous silhouette, or joints that visibly connect). Build two original demo
   characters that show the range (e.g. one round, one tall). Never copy an existing IP character.
4. **Everything drawn by code** — no image files you didn't generate, no network at render time. Google Fonts via a
   `<link>` in studio.html is OK (painted-animation does it); prefer a font with CJK coverage for any caption text.
5. **Speed:** aim for ≤ 250 ms/frame at 1920×1080 (the log prints ms/frame). Cache static textures in `ENGINE.setup`.
6. **Legible at phone size:** main subjects big, outlines thick enough to survive being shown at 390 px wide.
7. Don't touch anything outside your folder. Don't install global packages.

### The demo (8–10 s, 2+ shots)

Tells a tiny original story with the two characters and shows: an establishing shot with a camera move; a
character action with anticipation → action → follow-through (e.g. jump, throw, trip); an expression change; a prop
held in a hand; a designed transition between the shots that fits your look; one caption via `window.overlayHook`
(`caption(c, text)` or your own styled one). It must look **good** — this is what users judge the engine by.

## Quality loop (do it for real)

Render with `node render.mjs --sheet=... --cols=4 --w=480 --out=out/check/x.jpg` and crops of faces/hands
(`--crop=x,y,w,h`), then open the images with the Read tool and critique them like an art director: is the look
unmistakably <your style> and appealing? are characters on-model and cute/expressive? limbs attached? motion readable?
anything muddy, tiny, clipped, or broken? Fix and re-render. Do at least 3 full rounds; keep going until you'd put it on
the project's front page. Then render `docs/demo-sheet.jpg` (8–12 frames, 4 cols, w 480) and the full demo once:
`node render.mjs --frames --workers=4 && node render.mjs --encode --out=out/demo.mp4` to confirm it encodes.

Work in a scratch copy for testing (e.g. `%TEMP%/<engine>_dev`, scaffolded with your own new_project.sh --keep-demo)
or inside `template/` directly (run `npm install` there; node_modules/out are gitignored).

## Report back

What you built (files), the look in two sentences, API summary (character call signature + key library functions),
ms/frame, the path to `docs/demo-sheet.jpg`, and honest known limits.

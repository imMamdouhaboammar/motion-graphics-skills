# Production Engines Reference

## Engine Overview

Each engine is a separate skill that handles rendering for one animation style.
The `video-style-cloner` orchestrates them. It never renders directly.

## HyperFrames (Core 2D Engine)

HyperFrames is the primary animation renderer. It takes an
HTML composition and captures it with a headless browser. Its installed CLI encodes
the final video. Read the named `hyperframes-cli` and `hyperframes-core` entries
for the current composition contract.

### Key sub-skills (from ReelMimic)
| Sub-skill | Purpose |
|---|---|
| `hyperframes-core` | Timeline data model, scene/shot schema |
| `hyperframes-cli` | CLI commands: `npx hyperframes render`, `npx hyperframes preview` |
| `hyperframes-animation` | Easing functions, keyframe interpolation |
| `hyperframes-audio` | Beat-synced animation, audio waveform binding |
| `hyperframes-keyframes` | Frame-precise keyframe authoring |
| `hyperframes-creative` | Style presets, colour grading filters |
| `hyperframes-studio` | Multi-segment project orchestration |
| `hyperframes-registry` | Style registry and preset management |

### HyperFrames render loop

Run in the authored project directory, with HyperFrames installed:

```bash
npx hyperframes check
npx hyperframes preview --background
# After the user approves the preview:
npx hyperframes render --quality delivery --output out/final.mp4
ffprobe -v error -show_format -show_streams out/final.mp4
```

The Rust adapter contract is separate. A project's renderer adapter must export
its own frame sequence as specified in `engine/README.md`.

## Style Engine Map

| Engine Skill | Style | Medium | Notes |
|---|---|---|---|
| `painted-animation` | Hand-painted watercolour/ink | 2d-painted | Primary music video style |
| `anime-cel` | Japanese cel animation | 2d-cel | Hard outlines, flat fills |
| `pixel-art` | Pixel/8-bit art | 2d-pixel | Chunky pixels, limited palette |
| `crayon-storybook` | Crayon/coloured-pencil children's book | 2d-crayon | Rough texture, visible strokes |
| `paper-cutout` | Paper cutout / stop-motion style | 2d-paper | Layered flat shapes |
| `whiteboard` | Whiteboard hand-draw reveal | 2d-lineart | SVG line-draw animation |
| `faceless-explainer` | Faceless character explainer | 2d-lineart | Icon-style flat characters |
| `motion-graphics` | Dynamic text/shape motion graphics | 2d-vector | Kinetic typography |
| `slideshow` | Slideshow with transitions | 2d-vector | Photo/graphic presentation |
| `music-to-video` | Lyric video / visualiser | 2d-* | Beat-synced text/shapes |
| `cut-the-curve` | Trending short-form kinetic | 2d-vector | Fast cuts, bold typography |

## Character Rigging Rule

All 2D vector characters must use a bone rig under `assets/vector_rig/`:
```
assets/vector_rig/
├── skeleton.json    # Bone hierarchy
├── outline.svg      # Single unified silhouette
└── expressions/     # Expression blend shapes
    ├── happy.svg
    ├── sad.svg
    └── surprised.svg
```

**MUST NOT** build characters from separate circle + rectangle + arm primitives.
The rig must be a single unified outline with deformation zones.

## Compare script

After rendering, generate comparison evidence from the project directory and its plan:

```bash
python "$SKILL_DIR/skills/video-clone/scripts/compare.py" projects/<slug> \
  --video out/final.mp4
```

`--video` is relative to the project. The script reads `analysis/report.json` and
`plan.json`, then writes `out/check/compare_<id>.jpg`, `compare_all.jpg`, and
`compare.json`. It reports measured camera and look differences. It does not
produce numerical style scores or enforce a threshold.

An independent reviewer must inspect the paired frames for composition, colour,
camera motion and timing before approving each shot. Record that review separately.

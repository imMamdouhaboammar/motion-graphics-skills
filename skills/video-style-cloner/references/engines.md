# Production Engines Reference

## Engine Overview

Each engine is a separate skill that handles rendering for one animation style.
The `video-style-cloner` orchestrates them — it never renders directly.

## HyperFrames (Core 2D Engine)

HyperFrames is the primary animation renderer. It takes a declarative JSON/TS
timeline and renders it to PNG frames via a headless browser, then FFmpeg
assembles the MP4.

### Key sub-skills (from ReelMimic)
| Sub-skill | Purpose |
|---|---|
| `hyperframes-core` | Timeline data model, scene/shot schema |
| `hyperframes-cli` | CLI commands: `hf render`, `hf preview` |
| `hyperframes-animation` | Easing functions, keyframe interpolation |
| `hyperframes-audio` | Beat-synced animation, audio waveform binding |
| `hyperframes-keyframes` | Frame-precise keyframe authoring |
| `hyperframes-creative` | Style presets, colour grading filters |
| `hyperframes-studio` | Multi-segment project orchestration |
| `hyperframes-registry` | Style registry and preset management |

### Basic HyperFrames render loop
```bash
# 1. Generate frames from timeline
hf render projects/<slug>/timeline.json --out projects/<slug>/build/frames

# 2. Assemble video from frames + audio
ffmpeg \
  -framerate 24 -i projects/<slug>/build/frames/frame_%06d.png \
  -i assets/clip.m4a \
  -c:v libx264 -preset slow -crf 18 \
  -c:a copy \
  -pix_fmt yuv420p \
  -shortest \
  projects/<slug>/out/final.mp4
```

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

## Compare Script (Shot Scoring)

After rendering, score each shot against reference:
```bash
python scripts/compare.py \
  --ref projects/<slug>/analysis/sheet_scenes.jpg \
  --out projects/<slug>/build/frames \
  --shot-map projects/<slug>/plan.json \
  --threshold 4.0
```

A shot scores 1-5:
- ≥ 4.0 → approved
- < 4.0 → returned to producer for fix

Score dimensions: composition, colour match, camera move match, timing match.

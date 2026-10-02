# Video Style Cloner — Skill

**Source**: [edenfunf/reelmimic](https://github.com/edenfunf/reelmimic) (MIT)  
**Adapted by**: Mamdouh Aboammar for universal agent skill distribution

## What this skill does

Give any AI agent a reference video and a creative brief. It produces a new video in the same style — fully agentic, multi-agent production pipeline.

## Structure

```
video-style-cloner/
├── SKILL.md                    ← Main agent instructions (START HERE)
├── skills/                     ← All production engines, cloned as-is from ReelMimic
│   ├── video-clone/            ← Orchestrator (SKILL.md + CONTRACT.md + scripts + styles)
│   ├── painted-animation/      ← Watercolour/ink 2D animation engine
│   ├── anime-cel/              ← Japanese cel animation engine
│   ├── pixel-art/              ← Pixel art engine
│   ├── crayon-storybook/       ← Children's book crayon style
│   ├── paper-cutout/           ← Paper cutout / stop-motion style
│   ├── whiteboard/             ← Whiteboard hand-draw reveal
│   ├── faceless-explainer/     ← Icon-style explainer
│   ├── motion-graphics/        ← Kinetic typography / vector motion
│   ├── slideshow/              ← Slideshow with transitions
│   ├── music-to-video/         ← Lyric/music video
│   ├── hyperframes*/           ← HyperFrames renderer sub-skills (8 modules)
│   ├── ffmpeg/                 ← FFmpeg skill
│   ├── embedded-captions/      ← Caption overlay engine
│   └── ...                     ← All other engines from ReelMimic
├── styles/                     ← Style registry (add new styles here)
│   ├── _TEMPLATE.md
│   └── painted-animation.md
├── references/                 ← Reference docs (load on demand)
│   ├── runtime.md
│   ├── engines.md
│   ├── shot-analysis.md
│   ├── audio.md
│   ├── licensing.md
│   └── qa-checklist.md
└── evals/
    └── evals.json              ← Trigger/behavior/pressure eval assertions
```

## Quick Start (for agents)

1. Read `SKILL.md`
2. When user provides reference video + brief → activate
3. Follow phases 0–6 in SKILL.md
4. Route to correct engine via `skills/video-clone/styles/`
5. Load engine SKILL.md from `skills/<engine>/SKILL.md`

## Installation

This skill self-contained. Runtime tools needed:
- Python 3.10+ (`pip install yt-dlp faster-whisper opencv-python librosa`)
- FFmpeg 6.0+
- Node.js 22.18+ (for HyperFrames)

Run `python3 -c "import yt_dlp, faster_whisper, cv2, librosa"` to verify.

## Licence

MIT — original work by [edenfunf](https://github.com/edenfunf/reelmimic).  
Skill packaging by Mamdouh Aboammar.

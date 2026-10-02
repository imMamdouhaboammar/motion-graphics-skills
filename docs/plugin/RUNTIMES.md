# Runtimes, engines and execution

The plugin provides direction, workflow instructions, templates and source tools. Rendering depends on the host and installed software. Preserve a working project's renderer. Use HyperFrames first for new code-driven motion projects when it fits the brief.

| Layer | Role | Requirements and boundary |
|---|---|---|
| Motion Studio | Host checks and specialist selection | Planning works with text/image tools. Builds and renders require workspace execution |
| Motion Director | Creative direction, Arabic/RTL, reference fidelity, runtime selection and delivery review | Reads project and brand constraints. Uses actual inspection and render evidence |
| HyperFrames | HTML compositions, preview, registry, audio and video export | External CLI and renderer. Install its current skills and inspect CLI help/doctor |
| Native HTML/CSS/SVG/Canvas | 2D composition and drawing | Browser capture plus encoding for an MP4. Pure time-based drawing permits seeking |
| GSAP | Seekable choreography, timelines and framework integration | Install dependencies in the project. Eight bundled GSAP specialists provide guidance |
| Three.js/WebGL | Genuine 3D geometry, lighting and camera depth | Requires a compatible graphics environment. Check GPU policy before heavy work |
| Tone.js/Web Audio | Generated audio, sync and reactive animation | Browser audio runtime. Final video must contain verified encoded audio |
| FFmpeg/FFprobe | Encoding, processing, inspection and assembly | External executables, not bundled binaries |
| Animation Export Kit | Existing standalone HTML-to-MP4 alternative | Repository tool at `tools/animation-export-kit`, not included in the plugin ZIP |
| Video Style Cloner | Reference analysis, style selection, storyboard and independent review | Python 3.10+, relevant Python packages, FFmpeg 6.0+, Node 22.18+ for browser/HyperFrames routes. yt-dlp for supported URL inputs |
| ReelMimic Rust CLI | Persisted orchestration, approval, adapter dispatch, segment review and assembly | Optional source under Video Style Cloner. Build with Cargo. Requires project render/review adapters and an approved complete plan |

## Style production routes

| Visual job | Module | Implementation guidance |
|---|---|---|
| Watercolour and ink | painted-animation | p5.js and p5.brush templates with browser capture |
| Japanese cel animation | anime-cel | Canvas 2D, original characters, cel shading and frame capture |
| Pixel animation | pixel-art | Pixel drawing templates, limited palette and deliberate timing |
| Crayon storybook | crayon-storybook | Textured 2D drawing and character templates |
| Paper cutout | paper-cutout | Layered 2D cutouts and stop-motion timing |
| Whiteboard | whiteboard | Canvas 2D marker drawing and hand reveal |
| Faceless explainers | faceless-explainer | Designed explanation through 2D assets and animation |
| Kinetic typography/data | motion-graphics | HyperFrames composition and motion doctrine |
| Slides and decks | slideshow | HyperFrames discrete slides and transitions |
| Music/lyrics | music-to-video | Beat analysis and timed visual composition. Lyrics must be supplied by the user |
| Product promos | product-launch-video | Product facts, authored scenes and reference-led choreography |
| PR explainers | pr-to-video | Real code changes translated into an explanation |
| Talking-head packaging | talking-head-recut / embedded-captions | Existing footage, timed graphic overlays or captions |
| Existing Remotion source | remotion-to-hyperframes | Explicit port request only. Does not bundle a Remotion renderer |
| Blender product film | blender-product-film | Bundled reference guide. Disabled in the current 2D style-cloning track |

The complete [module inventory](CATALOG.md#video-style-cloner-modules) includes supporting doctrine, CLI, media, Figma and composition modules. Do not count each module as a separate rendering engine.

## Rust orchestration is optional

Read [the engine contract](../../skills/video-style-cloner/engine/README.md) before use. The CLI does not invent a creative plan, generate assets or supply an AI reviewer. Projects supply `render_segment.py`, `review_segment.py` and `review_final.py`. Segment adapters emit contiguous PNG frames at 24 FPS. Failed reviews block assembly, and completion requires final review. The bundled test-card smoke checks transport and artifacts, not artistic style fidelity.

## Host and provider checks

1. Inspect script, references, approved copy, brand files and target duration/aspect ratio
2. Identify available workspace, execution, image and review capabilities
3. Check installed runtime versions and CLI help before invoking a render command
4. Resolve project assets and fonts, then select a supported production route
5. Use supplied media or local assets where possible. Optional TTS, music and asset providers may require credentials, account access or paid operations
6. Preserve reference difficulty. Do not silently replace 3D with 2D or substitute paper/grain aesthetics for an unrelated reference
7. Verify frames, duration, dimensions, audio, motion and reference fidelity before claiming delivery

CPU/GPU use follows [the pack's GPU policy](../../skills/motion-director/references/reliability-guard.md) and existing session authorization. A plugin does not grant hardware, shell, Python, network or account access. If execution is unavailable, provide the storyboard, plan or source handoff with the missing render requirements.

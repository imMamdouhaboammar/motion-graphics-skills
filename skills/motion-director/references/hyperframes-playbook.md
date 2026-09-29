# HyperFrames playbook

HyperFrames is the preferred production infrastructure for greenfield code-driven motion work in this pack.

This skill should add creative direction, not duplicate what HyperFrames already solves.

## What HyperFrames owns by default

For a new renderable motion project, delegate these responsibilities to HyperFrames unless a documented incompatibility exists:

- scaffold and project contract
- deterministic render timeline
- composition discovery
- reusable catalog blocks
- runtime adapters
- keyframe and motion diagnostics
- timeline inspection
- lint
- runtime and layout checks
- proof snapshots
- preview
- final rendering
- batch variants
- audio relationships and mixing when used
- media handling where supported

The master skill should not rebuild these layers.

## What Motion Director owns

Keep these responsibilities in this pack:

- communication job
- concept
- narrative arc
- visual metaphor
- reference analysis
- art direction
- typography
- composition
- color roles
- material system
- Arabic and RTL direction
- motion thesis
- transition logic
- scene choreography
- creative review
- visual QA

The division is intentional. HyperFrames is the engine and production framework. Motion Director is the creative brain and quality system.

Authoritative project:
https://github.com/heygen-com/hyperframes

Docs:
https://hyperframes.heygen.com/

## Installation

Current standalone install:

    npx skills add heygen-com/hyperframes

When HyperFrames CLI already exists and freshness matters:

    npx hyperframes skills update

Do not depend on the older --full-depth install recommendation.

Ask before installing when the active host or project requires approval for dependency changes.

## Start with the HyperFrames router

When building a new HyperFrames project, read its hyperframes entry skill first.

That router decides whether the request belongs to:

- motion-graphics
- general-video
- product-launch-video
- faceless-explainer
- music-to-video
- talking-head-recut
- embedded-captions
- slideshow
- another supported workflow

Do not force every motion request into HyperFrames motion-graphics.

Its motion-graphics workflow is intentionally strongest for short, design-led, usually unnarrated work.

Narrated multi-scene branded films usually belong to a broader HyperFrames workflow while this motion-director skill provides the art direction.

## Domain skills

Load only the domains needed.

### hyperframes-core

Use for:

- composition structure
- data timing attributes
- tracks
- sub-compositions
- media placement
- determinism
- framework-owned playback

Read before writing HyperFrames composition HTML.

### hyperframes-creative

Use for:

- frame.md or design.md
- palette
- typography
- beat direction
- composition patterns
- visual style
- non-animation creative rules

This motion-director skill can create the creative thesis and art direction, then HyperFrames creative turns those decisions into its native design contract.

### hyperframes-animation

Use for:

- motion rules
- scene blueprints
- transitions
- runtime adapters

### hyperframes-keyframes

Use for:

- GSAP timing
- masks
- paths
- FLIP
- SVG draw
- morphs
- seek-safe keyframes
- 3D keyframes
- diagnostics

### hyperframes-registry

Use before hand-building a named look, transition, overlay, effect, or component.

Search first.

If a suitable block exists, install and adapt it.

Do not recreate a catalog capability with hundreds of lines of custom code.

### hyperframes-cli

Use for:

- init
- lint
- check
- timeline
- snapshot
- compare
- preview
- render
- diagnostics

Prefer these commands over a home-grown Playwright renderer for a HyperFrames project.

### hyperframes-audio

Use for:

- voiceover carve
- group processing
- volume automation
- effects
- mixing relationships

When music plays under narration, use the audio system rather than just lowering the whole bed with a hard-coded gain.

### media-use

Use for:

- sourcing
- generation
- local asset freezing
- captions
- transcription
- image and video preprocessing
- provenance

## Reuse-first runtime ladder

For a HyperFrames project:

1. Existing project composition and helpers
2. Existing HyperFrames composition pattern
3. Existing registry block
4. Existing runtime adapter
5. Existing keyframe recipe
6. Native HTML, CSS, SVG, or Canvas inside the composition
7. GSAP custom sequence
8. Three.js for true 3D
9. Custom engine only when a real gap remains

For a greenfield project, do not skip directly to step 6 or later without checking the HyperFrames layers first.

## When HyperFrames is mandatory

Use HyperFrames as the production layer when all of these are true:

- the project is new or can adopt a runtime without migration cost
- the final result is code-driven motion graphics
- deterministic frame rendering is required
- the target environment can run HyperFrames

Also use HyperFrames for any existing HyperFrames project. Do not bypass its CLI with a parallel custom renderer.

For a new narrated film, Motion Director supplies art direction while the HyperFrames router selects the correct production workflow. Do not force the short motion-graphics workflow onto a longer narrated film.

## When HyperFrames is not mandatory

Do not force migration when:

- the user supplied a working deterministic renderer and asked for bounded refinement
- the deliverable is only a creative brief or storyboard
- the job is analysis or timecoded critique with no build
- the environment cannot run HyperFrames
- a required capability is genuinely unsupported and a smaller fallback is more reliable

Document the reason when falling back.

## Do not migrate a working project without a reason

A current custom project may already have:

- deterministic seek
- local assets
- stable frame rendering
- final export
- tests
- known timing

Do not rewrite it only to gain the HyperFrames label.

Use HyperFrames where it gives a measurable benefit:

- faster preview
- reliable export
- validation
- catalog reuse
- audio
- frame diagnostics
- future reuse

For the next project, HyperFrames can become the foundation from the start.

## Determinism

HyperFrames is seek-driven.

Keep motion reproducible.

Avoid:

- wall-clock timers
- unseeded random values
- network assets at render time
- infinite animation loops
- state that depends on playback order

The same time should produce the same frame.

Seeking removes timing from animation but not from loading. A renderer that seeks right after load exposes every race a live preview hides, such as a logo fetched while scenes are being built. Build scenes from embedded data or preloaded assets, gate the first frame on one readiness promise (fonts loaded, images decoded), and make every tool await it.

That promise resolves to a plain value. Returning a GSAP timeline from its last `then` makes it wait for the paused timeline to finish, which is forever, because a timeline is a thenable. Nothing may change a resource URL during capture (swapping a `background-image` or an `<img src>` per frame). Load every variant up front and switch by opacity, or renders differ under load.

## Runtime choice

### HTML and CSS

Use for:
- layout
- static styling
- simple state changes
- responsive frame structure

### SVG

Use for:
- paths
- logos
- diagrams
- masks
- line drawing
- vector shapes

### Canvas

Use for:
- dense procedural drawing
- particles
- grain
- custom raster effects

Do not use Canvas for Arabic text when shaping is unreliable.

### GSAP

Use for:
- sequencing
- complex easing
- masks
- camera-like movement
- transforms
- stagger
- motion paths

### Three.js

Use for:
- real 3D
- geometry
- camera parallax
- lighting
- materials
- occlusion

Do not use it for a flat card that can be handled with CSS or SVG.

## Catalog discipline

Before building a named effect:

    npx hyperframes catalog <search terms>

Then inspect the candidate.

Use:

    npx hyperframes add <block-name>

when the block genuinely fits.

A block is a structural donor, not an excuse to ignore brand.md or MOTION.md.

Adapt copy, colors, type, timing, and material treatment to the project.

## Validation loop

For HyperFrames projects, this is the default release path, not an optional suggestion:

    npx hyperframes lint .
    npx hyperframes check .
    npx hyperframes snapshot --at <proof-times>
    npx hyperframes preview --background
    npx hyperframes render .

Read the installed hyperframes-cli skill before relying on exact command flags.

Inspect snapshots. A passing linter does not certify art direction.

## Frame spec bridge

This pack uses MOTION.md.

HyperFrames may use frame.md, design.md, or DESIGN.md.

Do not maintain conflicting truths.

Treat:

- brand.md as brand facts
- MOTION.md as project motion direction
- HyperFrames frame or design spec as the runtime-native translation of those decisions

When a conflict appears, the user's explicit project direction wins.

## What belongs in this pack

Keep:

- concept methods
- art-direction rules
- reference analysis
- typography guidance
- motion craft
- Arabic guidance
- review gates
- routing logic
- evals

Do not copy:

- HyperFrames renderer
- HyperFrames CLI implementation
- catalog source
- audio engine
- media engine
- runtime adapters

That code already has an owner.

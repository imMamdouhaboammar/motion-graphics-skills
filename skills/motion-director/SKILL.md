---
name: motion-director
description: Master motion-graphics director for concept, art direction, timing, production, review, and rendering across brand films, event promos, title sequences, kinetic type, editorial collage, explainers, data stories, logo reveals, 2D, 2.5D, and true 3D. Use when a motion job is broader than one specialist skill, when a reference must be reverse-engineered, when the user asks for a premium motion film, or when an existing cut needs a creative-director polish pass. Reuse existing project code, this pack, and HyperFrames before building infrastructure.
---

# Motion Director

This is the master skill for motion work in this pack.

It is not a SaaS launch template. It is a creative direction and production system for motion graphics in many visual languages, from a quiet typographic film to a dense editorial collage, a branded event promo, a documentary explainer, a logo sting, a data story, or a true 3D sequence.

The job is to make a film that feels authored, not merely animated.

Before any non-trivial motion task, read brand.md and MOTION.md if they exist. If they do not exist and the work must be on-brand, run brand-intake or ask only for the missing brand facts.

For a small specialist request that clearly matches another skill in this pack, delegate to that skill. For a broad film, a reference-led build, a cross-style piece, or an art-direction problem, stay here and direct the whole job.

The brief wins. Refinement preserves working identity and structure. Redesign replaces the visual world intentionally. Do not drift between the two.

## Decision priority

Resolve conflicts in this order:

1. User exact constraints and approved copy.
2. Documented brand and identity rules.
3. Factual, cultural, Arabic, accessibility, and platform hard gates.
4. Primary communication job and narrative.
5. Hierarchy, composition, and readability.
6. Motion craft and continuity.
7. Taste and decorative finish.

A lower-priority preference never overwrites a higher-priority lock.

## The rule before every tool choice

Do not rebuild an engine that already exists.

Use this ladder in order and stop at the first rung that solves the need:

1. Reuse the current project's working composition, helpers, assets, and renderer.
2. Reuse a specialist skill already in this pack.
3. Reuse a HyperFrames workflow, catalog block, runtime adapter, CLI command, or media tool.
4. Use native browser capabilities such as HTML, CSS, SVG, Canvas, Web Audio, and WebGL where they already fit.
5. Use GSAP for complex seekable sequencing and spatial choreography.
6. Use Three.js only when the shot needs real depth, occlusion, lighting, a 3D camera, or 3D geometry.
7. Write custom infrastructure only when all earlier rungs are proven insufficient.

A working custom deterministic composition must not be migrated only because a newer runtime exists. Improve the part that is weak. Leave the rest alone.

Read references/hyperframes-playbook.md before deciding how HyperFrames fits.

## HyperFrames responsibility policy

For greenfield code-driven motion work, HyperFrames is a production dependency, not merely an optional exporter.

Use HyperFrames by default for:

- project initialization and renderable composition structure
- deterministic timeline and seek behavior
- registry search and reusable motion blocks
- supported animation and keyframe adapters
- timeline inspection and diagnostics
- lint and runtime checks
- proof snapshots and contact-sheet inspection
- preview
- final rendering
- audio mixing and voiceover relationships when audio is part of the film
- batch and variant rendering when needed

Motion Director still owns concept, narrative, art direction, typography, composition, motion thesis, visual hierarchy, Arabic direction, and creative QA.

Do not duplicate HyperFrames rendering, audio, registry, validation, or timeline infrastructure inside this pack.

Exception: when an existing non-HyperFrames project already has a stable deterministic renderer and the user asked for refinement, preserve it unless migration fixes a measured limitation.

## What this skill owns

This skill owns:

- concept, visual metaphor, and reference analysis
- art direction, typography, color, composition, and hierarchy
- motion language, timing, pacing, continuity, and beat planning
- asset treatment and 2D, 2.5D, or 3D decisions
- audio-led timing and Arabic or RTL direction
- production routing, creative review, and final visual quality

It does not replace the rendering engine, animation runtime, media resolver, or audio engine when HyperFrames already provides them.

## Start from the deliverable

Classify the job before designing.

### Tiny motion unit

Usually 2 to 12 seconds: logo sting, title card, stat hit, kinetic type loop, lower third, chart hit, social overlay, or one transition study. Prefer a specialist skill or HyperFrames motion-graphics.

### Short branded film

Usually 10 to 45 seconds: campaign teaser, event promo, brand film, product promo, showreel opener, launch trailer, or editorial montage. Use this skill for concept and direction. Use HyperFrames as runtime when it fits.

### Narrated multi-scene film

Usually 30 to 120 seconds: event story, corporate promo, documentary explainer, case study, service film, or thought-leadership visual essay. Treat the VO or soundtrack as the master timeline. For HyperFrames, route the production runtime through its hyperframes entry skill and the matching longer-form workflow rather than forcing its short motion-graphics workflow.

### Existing film polish

Do not restart.

Study the current render first. Make a timecoded creative-director review. Fix the highest-impact art-direction and motion problems while preserving working structure.

Read references/review-gates.md.

## Phase 1: establish truth

Before style, collect what cannot be invented:

- exact script or approved copy
- actual logo files
- fonts and their licenses
- brand colors or design tokens
- official names
- verified numbers and claims
- supplied photography and footage
- event or client logos
- final platform and aspect ratio
- final audio if one exists
- the reference video or frames if one exists

Never invent a testimonial, result, attendance figure, client, award, date, price, certification, or official logo.

If a claim is illustrative, label it as illustrative.

## Phase 2: study references like a motion director

A reference is not a palette to copy.

Reverse-engineer its grammar.

For a video reference:

1. Read duration, frame rate, dimensions, and audio.
2. Make a contact sheet across the whole piece.
3. Sample the first three seconds more densely.
4. Capture frames immediately before and after important transitions.
5. Record what repeats and what changes.
6. Separate visual language from brand-specific assets.

Write a short reference study before building.

Extract hierarchy, scale relationships, typography behavior, color proportion, material, depth, framing, camera behavior, density, negative space, transition families, recurring objects, rhythm, text density, image treatment, foreground and background logic, and what makes the reference memorable.

Do not trace layouts or reuse protected assets.

Read references/reference-analysis.md.

## Phase 3: find the visual idea

Do not jump from script to scenes.

For every important beat, solve three layers:

1. Message: what must the viewer understand or feel?
2. Visual mechanism: what physical, graphic, typographic, or spatial action can carry that idea?
3. Transition logic: what from this beat can become the next beat?

A good scene is rarely "text appears, icon appears."

Prefer:

- one object becoming another
- a line becoming a path
- a path becoming a chart
- a chart becoming architecture
- a spotlight becoming a clock hand
- a ticket becoming a protocol sheet
- a word becoming layout
- a plan standing up into a stage
- a photo fragment becoming a mask
- one camera move revealing the next state

The viewer should feel one continuous thought.

When the user supplies multiple references, asks to combine visual languages, or the first direction remains too close to one source, route concept development through `mix-and-match` before locking the motion thesis. Use its selected direction as concept input, then return here for production.

Read references/concept-library.md when the first idea is obvious, generic, or too literal. Read references/narrative-direction.md for multi-beat films.

## Phase 4: create a motion thesis

Write one paragraph that defines the film's motion thesis.

It must answer:

- What is the visual world?
- What moves?
- What remains stable?
- What recurring device carries continuity?
- What is the dominant transition family?
- What makes the film belong to this brand?
- What does the film refuse to do?

Examples of motion theses:

- Editorial paper world where plans fold into real event structures, one blue route connects every scene, and typography behaves like printed architecture.
- Geometric brand world where one modular shape scales, splits, and recombines into every message.
- Cinematic dark stage where light reveals information and the camera moves only when the story changes depth.

A thesis prevents the film from becoming a bag of unrelated effects.

## Phase 5: build the frame system

Create or update MOTION.md with the actual frame rules.

Cover:

- canvas sizes
- safe zones
- background roles
- surface roles
- ink and accent roles
- color proportions
- type families
- type hierarchy
- image treatment
- shadow system
- texture system
- depth levels
- camera rules
- easing families
- transition families
- motion density
- hold behavior
- reduced-motion behavior
- things the film must never do

Read references/creative-direction.md.

## Phase 6: audio and beat map

When there is final VO, music, or dialogue, the audio is the master timeline.

Do not estimate timing from the written script.

Measure it.

For VO:

- inspect exact duration
- detect useful pauses
- get word or phrase timestamps when tools allow
- identify emphasis points
- identify breaths and intentional holds
- preserve the supplied audio timing unless the user asks to edit it

Create a beat map with:

- start
- end
- spoken phrase
- visual idea
- visible text
- asset
- transition in
- transition out
- motion intensity

The visible text is not a transcript.

Design the VO.

For many scenes, the viewer should hear a full sentence while seeing only one to five important words.

Plan the end hold here, not at the end of production. Compute the time between the last key word and the end of the audio. If the brand or CTA needs a longer clean hold than that gap allows, decide now whether the delivery adds a silent tail after the VO, and tell the client which version ships.

If music sits under narration and HyperFrames audio is available, use its audio workflow rather than hand-building a mixer.

## Phase 7: explore before committing

For a film longer than one short shot, build three genuinely different opening directions before the whole piece.

Change the mechanism, not merely the color.

Possible differences:

- typography-led
- object-led
- camera-led
- depth-led
- image-led
- negative-space-led
- material-led

Render or snapshot the first two to four seconds.

Judge:

- first-frame strength
- immediate readability
- brand fit
- originality
- reference grammar
- transition potential
- phone-scale legibility
- visual simplicity

Pick the strongest route and continue.

Do not pick the busiest route by default.

## Phase 8: choose the right visual lane

Pick the dominant lane for each scene before animating:

- kinetic typography when language is the material
- editorial collage for culture, events, campaigns, history, and human stories
- graphic systems for paths, diagrams, maps, and brand geometry
- data motion when evidence and comparison are central
- UI and product motion when the real interface is part of the story
- 2.5D when planar depth and parallax are enough
- true 3D when geometry, lighting, occlusion, or a real 3D camera matters
- image or footage-led motion when the source image should drive masks, crops, tracking, and transitions

Do not mix lanes only to show technical range.

For Arabic typography, read references/arabic-motion.md.
For frame and material decisions, read references/creative-direction.md.
For camera, transition, path, mask, and timing craft, read references/motion-craft.md.
For the wider mechanism-to-tool map, read references/technique-atlas.md.

## Phase 9: choreograph motion

Motion must have purpose.

Every important move should do at least one job:

- reveal
- focus
- connect
- compare
- transform
- explain
- create anticipation
- confirm
- change scale
- change location
- change time
- change emotional intensity

Use contrast in motion.

Fast against slow.
Dense against quiet.
Large against small.
Stillness against movement.

Do not keep maximum intensity for the whole film.

One expressive move is stronger when productive motion around it is restrained.

Read references/motion-craft.md.

## Phase 10: implement with reuse first

Before hand-authoring an effect, inspect what already exists.

For a new HyperFrames-capable project:

- initialize and structure the renderable project with HyperFrames
- search its catalog before building a named effect or transition
- use its composition contract as the technical source of truth
- use its animation and keyframe guidance instead of inventing an incompatible timeline model
- use its CLI for timeline inspection, lint, check, snapshot, preview, and render
- use its media layer for source assets where it fits
- use its audio layer for mixing and voiceover relationships
- use its frame or design spec conventions as the runtime translation of brand.md and MOTION.md
- use batch rendering for systematic variants rather than hand-duplicating compositions

Do not copy HyperFrames internals into this repository.

Keep this skill focused on creative direction and production decisions.

Read references/hyperframes-playbook.md. Read references/reliability-guard.md before hang-prone browser, audit, render, or verification commands and use the bundled work guard instead of ad-hoc timeout loops.

## Phase 11: still-frame gate

A motion film with weak stills rarely becomes strong because it moves.

Before final render, capture:

- first frame
- 0.5 seconds
- 1 second
- midpoint of every beat
- every major transition
- CTA
- final frame

For a long film, also sample every 0.5 to 1 second.

Build a contact sheet. Run the one-second hierarchy test, thumbnail test, grayscale or squint test, and edge or tangency check before polishing details. Read references/anti-slop.md before signoff.

A contact sheet finds candidates. It does not prove geometry. Confirm a suspected clip or overflow on a full-resolution still or by measurement before changing code.

For an HTML composition with window.seek, run scripts/clip-audit.js over the whole timeline. It measures every visible text run against the frame and every clipping container and reports persistent cuts, and with --safe it warns about text near the frame edge. Declare designed crops with data-crop="intentional". The audit does not see clip-path polygons or occlusion by a sibling layer, so check light cones, shaped masks, and objects passing over words by eye.

Hard-fail and fix:

- no clear focal point
- muddy palette
- hierarchy collisions
- too much small text
- repeated layouts
- weak negative space
- fake UI
- inconsistent shadows
- mixed asset treatment
- accidental clipping
- generic decorative shapes
- logo misuse
- unreadable Arabic
- safe-zone violations

## Phase 12: motion gate

Watch the whole film twice.

Pass 1:
- sound on
- normal size
- judge narrative, timing, emotion, and audio sync

Pass 2:
- sound off
- phone-size preview
- judge visual comprehension, hierarchy, and text

Then inspect difficult transitions frame by frame.

Do one complete defect scan, fix the findings in one batch, then allow at most one confirmation pass. Do not polish forever. Preserve strong choices and change only the responsible layer.

Hard-fail:

- cuts on meaningless syllables
- exits before text can be read
- repeated transition rhythm
- unmotivated camera moves
- perpetual floating
- gratuitous bounce
- endless scale pops
- a weak middle
- an overstuffed ending
- a first second with no visual promise

## Phase 13: technical gate

Use the active runtime's supported checks. For HyperFrames, prefer its lint, check, snapshot, preview, render, and verification paths over custom capture code. Run hang-prone checks through the reliability guard with measured deadlines or a heartbeat. For a working non-HyperFrames project, preserve its deterministic renderer unless a measured problem justifies change. Before heavy render or media work, pass the GPU policy and preserve its backend evidence.

Verify the actual final file for target dimensions, duration, frame rate, color space, codec, audio alignment, and end hold.

The end hold is one contract across three layers: the composition's time clamp (hold frames must repeat the last frame, grain included), the render range (it must include the hold), and the mux (pad the audio, never -shortest when a hold exists). Check the hold on the final file by frame count.

Trust a check only after it has been seen failing. Reintroduce the defect in a copy of the project, run the check, and restore. A font check, clip audit, or render wrapper that has never failed may be unable to fail.

## Phase 14: handoff

Run the rendered file through `video-review-loop`, inspect the actual video, and resolve every hard finding in a later render before signoff.

Keep the approved script, reference study, brand files, beat map, source composition, contact sheet, one previous draft, and final render. Keep heavy failed renders out of normal Git history when release assets, artifact storage, or Git LFS are more appropriate.

## Dynamic routing and neural handoffs

Read `references/operator-guide.md` before operating a broad or multi-stage job. It is the execution guide for routing, reference challenge mode, HyperFrames reuse, GPU enforcement, guarded commands, and final video review.

For broad or multi-stage work, create a small JSON task context and run `scripts/route_motion.py` before production. Keep its returned route available through the session.

The router reads the installed skill graph, selects only relevant specialists, explains every hop, adds GPU and review gates, and skips unavailable optional capabilities with a named fallback.

Read `references/neural-links.md` and obey each stage's handoff packet. When a supplied reference is a benchmark rather than loose inspiration, also read `references/reference-fidelity.md` and lock the fidelity contract before creative substitution. Specialists inherit shared truth, return only their delta, and return to `motion-director` for broad film work.

For multiple-reference recombination, route through `mix-and-match` when installed, then return its selected direction to `motion-director` before the motion thesis is locked.

For a truly narrow request, a specialist may finish independently. Do not run the whole graph when the user asked for one bounded artifact.

Heavy media work must pass `scripts/gpu_policy.py probe --require` before execution. Browser-rendered motion must also pass `scripts/browser_gpu_probe.cjs`. Heavy final encoding must pass `scripts/gpu_policy.py probe --require --require-encode` when the active runtime exposes encoder selection. Never hide a CPU fallback.

A rendered final video must pass `video-review-loop` before signoff. Still-frame review alone is not final evidence.

## Non-negotiables

- Do not invent proof.
- Do not use a reference's logo, copy, or proprietary assets.
- Do not force a SaaS visual language onto a non-SaaS job.
- Do not treat "premium" as glass panels, gradients, glow, or 3D by default.
- Do not turn narration into subtitles.
- Do not hand-build a renderer when the current runtime already renders correctly.
- Do not install a dependency for a feature the current stack already provides.
- Do not add 3D when 2D communicates the idea better.
- Do not call a film finished after code passes. The rendered film is the product.

For deeper craft study and authoritative runtime references, see references/sources.md.

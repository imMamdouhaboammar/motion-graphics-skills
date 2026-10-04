# Motion technique atlas

Use this as a decision map, not an effect menu.

Choose a technique because it serves the message, material, or transition.

## Typography

### Masked type
Use for:
- confident reveals
- editorial headlines
- scene handoffs

Mechanism:
- clip or mask the shaped text
- move the text, the mask, or both

Good tools:
- DOM or SVG text
- GSAP
- HyperFrames keyframe guidance

### Type to layout
Use when a word or phrase should become the structure of the next scene.

Examples:
- letters become columns
- baseline becomes a route
- word block becomes image windows

Good tools:
- DOM
- SVG
- FLIP-like layout interpolation
- GSAP

### Variable font motion
Use only when the supplied font exposes real axes.

Possible axes:
- weight
- width
- optical size
- slant

Do not fake width by horizontally stretching glyphs.

### Type as matte
Use text as a window into:
- image
- footage
- texture
- another scene

Good tools:
- SVG masks
- CSS masking
- Canvas compositing

### Type on path
Use for:
- routes
- circular systems
- orbiting labels
- editorial curves

Keep readability above novelty.

For Arabic, read arabic-motion.md before using per-glyph or path-based motion.

## Shape and vector motion

### Path draw
Use for:
- routes
- diagrams
- signatures
- line art
- maps
- technical systems

Good tools:
- SVG stroke dash
- GSAP
- HyperFrames registry or keyframes when available

### Path follower
Use when an object must travel along a meaningful route.

Examples:
- guest journey
- cable
- map route
- production flow

### Shape morph
Use when the relationship between forms is understandable.

Examples:
- circle to stopwatch
- badge to schedule card
- logo primitive to scene geometry

Prefer SVG morphing or a proven registry primitive.

Do not morph unrelated shapes only to show technique.

### Boolean reveal
Use one shape to carve, reveal, or subtract another.

Good for:
- logo work
- geometric identities
- technical films

## Image and footage motion

### Crop choreography
Animate crop, not only the image.

Use for:
- reveal
- reframing
- editorial pacing
- image-to-layout transitions

### Freeze and isolate
Freeze one moment, isolate the subject, then let graphics enter around it.

Useful for:
- sports
- events
- documentary
- proof moments

### Depth separation
Split an image into foreground, subject, and background layers.

Use for:
- parallax
- gentle 2.5D
- focal shifts

Do not pretend flat separation is full 3D.

### Image to graphic
Let image geometry become:
- chart
- mask
- route
- frame
- silhouette

This is stronger than floating labels over a photo.

### Treatment stack
A treatment may combine:
- grade
- desaturation
- halftone
- grain
- paper edge
- duotone
- posterization
- threshold
- scan texture

Use one coherent treatment family.

## Editorial and tactile techniques

### Paper cutout
Use:
- decisive crop edges
- physical shadow
- slight depth
- limited rotation
- consistent print treatment

### Torn reveal
Use when the material world is explicitly paper or print.

Avoid using torn edges as generic decoration.

### Stamp
Useful for:
- proof
- approval
- status
- identity

Keep the stamp imperfect but legible.

### Stop-motion stepping
Use selective held frames for:
- paper snaps
- markers
- doodles
- collage jitter

Do not step important camera motion unless the whole piece is intentionally stop-motion.

### Desk or archive assembly
Use multiple artifacts as evidence.

Hierarchy rule:
one hero document or object
few support pieces
background fragments only when needed

## Camera and spatial motion

### Push in
Use to:
- focus
- reveal detail
- increase tension

### Pull out
Use to:
- reveal scale
- show system
- recontextualize detail

### Pan
Use for discovery across a spatial composition.

### Orbit
Use when form changes meaning as the camera moves around it.

Requires true 3D when hidden surfaces and real occlusion matter.

### Whip
Use for high-energy location change.

A whip needs:
- matching direction
- blur or occlusion logic
- a clean landing

Do not use it repeatedly.

### Rack focus
Use to transfer attention between depth planes.

In 2.5D, simulate cautiously.
In true 3D, use camera and depth of field where supported.

### Z-space cascade
Use planar objects at different depths.

Good for:
- posters
- cards
- event credentials
- archives

Avoid generic floating-card tunnels with no message.

## Transition families

### Match cut
Match:
- shape
- direction
- scale
- color
- edge
- composition

### Shared-object handoff
Carry one object across the boundary.

### Occlusion
Let a foreground element cover the frame and reveal the next state.

### Mask handoff
One scene's mask becomes the next scene's reveal.

### Light handoff
A beam, flash, screen, or shadow carries the transition.

### Camera handoff
The camera continues moving while the world changes.

### Material handoff
Paper, fabric, glass, ink, smoke, or another material becomes the bridge.

Use the smallest transition family set that can carry the whole film.

## Procedural motion

### Particles
Good for:
- assembly
- disassembly
- atmosphere
- logo resolve
- data points

Use Canvas, WebGL, or a proven block.

Seed randomness for deterministic rendering.

### Flow fields
Good for:
- energy
- network behavior
- invisible forces
- abstract systems

Use only when the movement communicates something.

### Noise-driven motion
Useful for:
- handmade jitter
- ambient texture
- organic variation

Keep it seeded and bounded.

### Spring behavior
Use when the material or interaction suggests elasticity.

Not every object needs spring physics.

## Data motion

### Count
Use when the number itself is the story.

### Bar or line growth
Use when change over time or comparison matters.

### Rank transition
Use when order changes.

### Accumulation
Use when many units become one total.

### Spatial data
Use maps, paths, or geographic relationships when location matters.

Never distort the evidence to create drama.

## 2.5D

Prefer 2.5D when:

- assets are mostly flat
- perspective is shallow
- parallax sells enough depth
- the camera does not need to orbit behind objects
- production speed matters

Typical stack:
- background
- middle plane
- hero plane
- foreground occluder

Good tools:
- CSS transforms
- GSAP
- SVG
- Canvas

## True 3D

Use true 3D when the shot needs:

- geometry
- real occlusion
- surfaces revealed by rotation
- real camera movement
- material response
- lighting
- shadows
- volumetric depth

Good tool:
- Three.js through a supported HyperFrames adapter when HyperFrames is active

Do not use true 3D only because it is available.

## Shaders and advanced image effects

Use shaders when the visual behavior depends on per-pixel transformation.

Examples:
- displacement
- liquid distortion
- refraction
- chromatic separation
- procedural dissolve
- heat haze
- pixel sorting-like transitions

Search HyperFrames registry before hand-authoring a shader.

Avoid:
- generic glitch
- RGB split everywhere
- excessive lens distortion

## Compositing

Useful operations:
- alpha matte
- luma matte
- multiply
- screen
- overlay
- masked blur
- foreground occlusion
- shadow integration
- reflection
- atmospheric depth

Compositing must preserve physical logic unless surrealism is the explicit idea.

## Audio-reactive motion

Use:
- beat
- onset
- amplitude envelope
- phrase timing
- silence

Good for:
- music-led films
- title sequences
- impact moments

Do not make every property react to the waveform.

Choose one or two visual parameters.

## UI and product motion

Use the real interface when possible.

Techniques:
- focus zoom
- cursor path
- state morph
- modal expansion
- card to workspace
- search to results
- real input to real output

Avoid fake dashboards and invented feature states.

## Logo motion

Common mechanisms:
- construct
- reveal
- morph
- path draw
- fragment assembly
- negative-space resolve
- callback assembly
- material formation

Preserve official mark geometry.

## Runtime decision table

| Need | First choice |
|---|---|
| Layout and shaped text | HTML / CSS |
| Paths, masks, diagrams, logos | SVG |
| Dense procedural 2D | Canvas |
| Sequencing, easing, choreography | GSAP |
| True 3D | Three.js |
| Named reusable effect or transition | HyperFrames registry first |
| Frame validation and render | HyperFrames CLI when project is HyperFrames |
| Audio mix and VO relationship | HyperFrames audio when active |
| Media sourcing and preprocessing | media-use when active |

## Effect subtraction test

Before keeping an effect, remove it mentally.

If the message, hierarchy, and transition become clearer without it, remove it.

Technical difficulty is not a reason to keep an effect.

---
name: paper-cut-motion
description: Create tactile stop-motion paper-cut and collage sequences with deterministic 12 fps stepped motion, physical layering, paper shadows, stamps, pins, and editorial evidence boards. Use for investigative explainers, documentary collage, scrapbook storytelling, archival sequences, or requests such as "paper-cut animation", "stop-motion video", "collage motion", and "investigation board animation".
---

# Paper Cut and Stop Motion Graphics

This is an editorial material system, not a paper texture preset.

Use paper because documents, fragments, evidence, memory, or handmade assembly are part of the story.

## Decision gate

Use this skill when the narrative benefits from physical evidence, collected fragments, archival material, or visible assembly.

Do not use it merely to make a normal promo feel retro.

Choose another visual lane when:

- the story needs clean product UI fidelity
- the brand depends on polished geometric precision
- smooth camera movement is the main reference behavior
- the paper metaphor has no relationship to the message

## Build the evidence hierarchy first

Before animating, classify every piece:

1. Anchor: the central claim, person, place, or question
2. Evidence: supporting photo, document, number, quote, or diagram
3. Connector: line, thread, arrow, label, stamp, or annotation
4. Resolution: the conclusion or final reveal

Do not give every scrap equal visual weight.

A strong board usually has one anchor, three to six evidence pieces, and only the connectors needed to explain relationships.

## Physical world rules

- Use stepped motion at 12 fps for paper movement.
- Keep slight rotation differences between pieces.
- Use directional shadows that agree on one light source.
- Let heavy paper stop quickly.
- Use overlap and occlusion to show physical order.
- Replace one sheet by covering or removing it rather than morphing paper into unrelated geometry.
- Keep texture subordinate to text readability.

Read references/stop-motion-craft.md before adding more props.

## Workflow

### Step 1: Plan entry order

Decide when each evidence piece enters.

The bundled builder supports enter_at per piece. If no explicit time is supplied, pieces enter in sequence using a deterministic default stagger.

### Step 2: Generate a seekable scene

~~~bash
python3 scripts/paper_builder.py --output "$WORK/paper_scene.html"
~~~

The generated file exposes window.seek(seconds).

Seeking is deterministic. Every call quantizes the requested time to 12 fps and recalculates each piece's visibility, opacity, position, and rotation from that timestamp.

Backward seeking must reconstruct the earlier frame correctly. Never make frame state depend on the previous seek call.

### Step 3: Author motion as physical action

Good actions include:

- sheet drops
- clipped photo slides
- stamp impacts
- pin placement
- thread connections
- tape reveals
- stacked document replacement

Avoid generic UI animation vocabulary such as floating cards, elastic spring motion, and continuous hover drift.

### Step 4: Use typography like print

Text should feel placed on physical material.

Prefer:

- newspaper scale contrast
- short label strips
- stamped classifications
- typed evidence captions
- large single-phrase headlines

Avoid turning every paper piece into a paragraph.

### Step 5: Add tactile sound only where contact happens

Useful accents include:

- dry paper slide
- tape pull
- pin click
- stamp impact
- pencil or marker stroke

Do not add a sound effect to every movement.

## Deterministic render contract

The same timestamp must produce the same frame.

This is required for:

- HyperFrames capture
- frame-by-frame review
- batch rendering
- backwards seeking
- reproducible fixes

If randomness is used for paper imperfections, seed it from stable piece data rather than runtime time or previous state.

## Creative QA

Hard-fail when:

- the board looks like digital cards with paper colors
- every element enters with the same move
- evidence hierarchy is unclear
- shadows disagree about light direction
- text becomes unreadable under texture
- backward seek produces a different frame
- collage density grows without helping the story

## What I learned the hard way

- Smooth interpolation can erase the handmade character.
- Texture alone does not create materiality. Weight, overlap, timing, and shadow do.
- Too many pins, strings, and stamps turn evidence into decoration.
- A tactile style is strongest when the material itself explains the narrative.

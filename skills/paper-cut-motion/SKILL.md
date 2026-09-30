---
name: paper-cut-motion
description: Create tactile stop-motion paper-cut and collage video sequences. Uses 12 fps stepped motion math, physical paper edge textures, drop shadows, pushpins, stamps, and newspaper clippings for investigative or editorial storytelling. Pure code with window.seek compatibility for HyperFrames or direct MP4 export. Use when someone says "paper-cut animation", "stop-motion video", "Vox paper style", "collage motion", "investigation board animation", or "tactile video graphics".
---

# Paper-Cut and Stop-Motion Graphics

Build tactile paper-cut animations, investigative collage boards, and stop-motion explainers entirely in code.

## Core craft rules

1. **12 fps time stepping:** Real paper moves in physical increments. All motion curves step at 12 fps (`stepT = Math.floor(t * 12) / 12`).
2. **Directional paper shadows:** Crisp directional drop shadows simulate physical layers resting on a desk surface.
3. **Tactile props:** Pushpins, red yarn connections, masking tape strips, and ink stamps tie disparate facts into a cohesive narrative board.

## Workflow

### Step 1: Collect story facts and evidence

1. **The central claim:** The core headline or mystery being explained.
2. **Evidence pieces:** 3 to 6 documents, newspaper headlines, charts, or photo clippings.
3. **Color palette:** Warm newsprint `#FAF8F5`, cardboard kraft `#D8CBB5`, and dark charcoal ink `#1E1D1B`.

### Step 2: Generate the paper scene HTML

Generate a standalone seekable HTML template:

```bash
python3 scripts/paper_builder.py --output "$WORK/paper_scene.html"
```

The template implements `window.seek(seconds)` so every frame can be inspected and exported.

### Step 3: Animate with 12 fps discretization

In your animation script or GSAP timeline:

```javascript
function renderFrame(seconds) {
  // Quantize continuous time to 12 frames per second
  const stepT = Math.floor(seconds * 12) / 12;

  // Pieces snap into position rather than gliding smoothly
  const progress = Math.min(1.0, stepT / 0.5);
  piece.style.transform = `translateY(${(1 - progress) * 80}px) rotate(${piece.rotation}deg)`;
}
```

### Step 4: Add tactile audio accents

Pair each paper drop with a tactile sound:
- Paper slide: soft dry friction sound.
- Evidence pin: short percussive click.
- Ink stamp: hollow thud.

## What I learned the hard way

- **Smooth 60 fps kills the paper aesthetic.** Smooth interpolation makes paper pieces look like weightless digital UI cards. 12 fps stepping is mandatory.
- **Physical cutouts do not morph.** When replacing one document with another, drop the second paper on top of the first, or slide it off screen.
- **Slight rotation breaks digital perfection.** Perfectly horizontal paper cutouts look machine-generated. Tilt each piece by -3 to +4 degrees.
- **Hard drop on impact.** A paper piece should fall and stop abruptly in a single frame. Never add bouncy cartoon overshoot to a heavy document.

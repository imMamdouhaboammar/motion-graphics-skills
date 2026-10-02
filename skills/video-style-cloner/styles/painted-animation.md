---
engine: painted-animation
medium: 2d-painted
priority: 9
---

# Painted Animation Style

## Identification Features
- Visible brushstrokes or ink lines
- Watercolour wash backgrounds with soft edges
- Hand-painted texture on characters and environment
- Warm, slightly desaturated palette with organic colour bleed
- Fluid, slightly wobbly line quality (not perfectly clean vector)
- Characters have weight and volume suggested through paint strokes
- Backgrounds often use wet-on-wet watercolour technique

## Activation Signals
- Music videos with hand-painted frames
- Videos mentioning "watercolour", "hand-drawn", "painted" aesthetic
- Reference has visible brush texture in every frame
- Artisan/craft brands, nature/organic products

## Production Defaults
- Load `painted-animation` engine skill
- Frame rate: 12 fps (traditional animation feel), upsampled to 24 fps
- Line weight: variable, 2-4px at 1080p
- Background: painted separately from characters (composited in HyperFrames)
- Character rig: `assets/vector_rig/` with painted texture overlay

## Known Gotchas
- Paint texture must be baked per-frame, not tiled — tiling creates obvious repeat pattern
- Watercolour bleed at character edges must not obscure expression details
- Dark backgrounds require lighter line weights for legibility
- At 12fps, anticipation frames are critical — skip them and motion looks robotic

# Stop-Motion and Paper-Cut Craft Rules

These principles govern stop-motion animation math, torn edge styling, and collage composition.

## 1. 12 fps stepped time quantization

Smooth 60 fps interpolation makes digital paper look weightless and synthetic.
- Quantize all animation time variables to 12 frames per second using `Math.floor(t * 12) / 12`.
- Pieces should translate, rotate, and drop in discrete physical increments.
- Avoid smooth cubic bezier morphing. Real physical cutouts slide, snap, and pivot.

## 2. Realistic paper shadows

Flat paper sits physically above background surfaces:
- Use layered directional shadows rather than symmetrical blurs.
- Standard physical shadow: `box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.22)`.
- Lifted edge effect: slightly higher shadow offset on one corner to simulate paper curling off the table.

## 3. Physical artifacts and tactile markers

Add tactile elements to make the scene feel assembled by hand:
- Pushpins and masking tape: anchor documents to the surface.
- Red string connections: link pieces on an investigation board.
- Physical rubber stamp effects: tilt between -3 and +5 degrees and appear in a single 1-frame snap.
- Hard cut entrances: cutouts drop onto the table in a single frame accompanied by a subtle physical tap sound.

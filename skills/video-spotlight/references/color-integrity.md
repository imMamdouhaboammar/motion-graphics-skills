# Color Integrity and Selective Lighting Rules

These principles govern timed grading, localized focus spotlights, and color matrix consistency.

## 1. Preserving camera color science

Applying heavy global color grades across entire clips frequently results in skin-tone discoloration and banding.
- Default to leaving the camera color science untouched.
- Do not apply automatic global LUTs or heavy color grades unless explicitly requested by the director.
- Restrict dramatic color adjustments to isolated spotlight windows lasting 1 to 3 seconds.

## 2. Preventing BT.709 color shifts

Standard web video uses `yuv420p` with `bt709` color primaries and limited TV range (16-235).
- Extracting raw frames directly to JPEG often forces rec601 conversion, shifting luminance by +2.2% and saturation by -5.1%.
- Extract frames in lossless PNG or RGB24 format before applying localized masks.
- When re-encoding, explicitly tag the output stream with `-color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709`.

## 3. Subtle accent lighting

When emphasizing a key word or product:
- Dim the surrounding area by 30% to 50% rather than 100% black.
- Lower surrounding saturation by 40% to 60% rather than full greyscale, unless a dramatic noir beat is intended.
- Keep the transition into and out of the spotlight quick (0.2s to 0.3s) so the effect feels crisp rather than sluggish.
- If adding a brand color tint, apply it as a soft outer glow with less than 25% opacity so it does not tint the subject skin.

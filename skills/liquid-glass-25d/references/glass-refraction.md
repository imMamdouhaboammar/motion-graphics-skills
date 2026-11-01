# Glass Refraction and Distortion Math

Technical notes on configuring optical distortion for CSS and SVG render pipelines.

## Turbulence Parameters

The `baseFrequency` attribute in `feTurbulence` controls the scale of the glass curvature:
- High values (0.05 to 0.1) produce coarse pebbled bathroom glass.
- Optimal values (0.015 to 0.025) produce smooth lens distortion that bends typography realistically.

## Edge Highlighting

Real optical lenses catch light along the incident bevel. Apply an asymmetric border gradient:
- Top and left borders catch direct ambient key light.
- Bottom and right borders represent ground bounce and ambient shadow.

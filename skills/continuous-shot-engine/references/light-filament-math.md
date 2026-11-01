# Light Filament Math and Continuity

Mathematical guidelines for maintaining a continuous visual thread across scene boundaries.

## The Continuity Contract

To maintain the illusion of a single continuous shot:
1. The terminal coordinate and velocity vector of the light filament in scene N must become the origin coordinate and velocity vector in scene N+1.
2. The color temperature and glow radius must interpolate smoothly between states.

## Bezier Path Interpolation

When using GSAP or Python OpenCV:
- Store control points in a normalized coordinate space (0.0 to 1.0).
- Evaluate position `P(t)` along cubic Bezier curves using De Casteljau's algorithm.
- When transitioning from a 2D UI line to a 3D isometric route, project through a camera transformation matrix to avoid positional discontinuities.

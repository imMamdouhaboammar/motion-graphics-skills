# Typography Rules for Motion Graphics

Rules applied when setting headlines, captions, and data labels.

1. **Font Limitation**: Never use more than two typeface families in a single production (e.g. Archivo Black for headlines and Inter for small data labels).
2. **Local Caching**: Store all font files in the project `fonts/` folder in WOFF2 or TTF format. Never rely on remote Google Fonts CDN links during video rendering to avoid network latency and dropped glyphs.
3. **Contrast Ratios**: All text and background combinations must pass WCAG AA standards with a minimum contrast ratio of 4.5:1 for body copy and 3.0:1 for bold headline text.
4. **Uppercase Labels**: Small metadata labels (tags, categories, step numbers) must use uppercase tracking with letter-spacing between 0.08em and 0.15em.

# cinematic-cream — spec

The authoritative spec lives in [template.html](template.html)'s header comment (DNA-only:
what's LOCKED vs OPEN, the LAYOUT/planes contract, READING ORDER + hand-off, hero sizing).
Read that header before authoring plan.json. Quick contract:

- LOCKED: Inter, soft/present motion, warm-cream palette, screen blend, shadow logic.
- OPEN per group (css field): size/weight/style/transform/spacing + position WITHIN a plane.
- LAYOUT: run scripts/safe-zones.cjs first. Narration planes HUG the silhouette — use
  zones.hugLeft/hugRight (2-6% gap from the subject's edge); a plane parked in the far
  corner reads as disconnected floating text, not an embed. The ONE hero stays BIG
  (~0.22-0.34·h) centered ON the subject (heroAnchor / heroBands.best), target ~30-55%
  occlusion. The hero moves to fg only when heroBands.feasible=false (no band ≤62%).
  Narration follows safe-zones.recommendation independently: when recommendation is
  "fg" (no clean narration region), put narration in fg even if heroBands.feasible=true.
  A feasible hero band does not make narration planes legible.
- plan.json: groups[] with per-word transcript timings (use scripts/fill-timings.cjs),
  fit via scripts/fit-fonts.cjs, compile via scripts/make-composition.cjs.

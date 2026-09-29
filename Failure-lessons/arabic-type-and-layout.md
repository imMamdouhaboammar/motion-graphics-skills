# Arabic type and layout

Lessons about Arabic text that was cut, hidden or cramped without anyone deciding it should be.

Related code: `projects/four-steps-events/film.js` (`txt()`, the `crop` option), `skills/motion-director/scripts/clip-audit.js`.
Related skill guidance: `skills/motion-director/references/arabic-motion.md` (Cropping).

---

## Accidental clipping found only by eye

### Context

Editorial Arabic type at 150 to 450 px, frame-edge crops used on purpose, masks, light cones, and paper sheets that pass over words.

### What happened

Across the drafts and the polish pass, Arabic text was cut in five different ways:

1. The alef of «آخر» was cut by the right frame edge, so the word read as «خر» on frame 0.
2. The dots of the ي in «تخطيط» disappeared under a planning sheet placed deliberately to overlap the word's foot.
3. The question mark of «الإضاءة؟» was cut by the edge of a light cone that reveals the word.
4. «فريق الاستقبال» on a protocol slip was cut by 7 px by the slip's own `overflow: hidden`, for about half a second.
5. Several lines sat 2 to 20 px from the frame edge.

Cases 1 to 3 were found by reviewing stills. Case 4 was missed by eye through two full inspection passes and is still in the delivered v2 render. It was found afterwards by `clip-audit.js`.

### Observable symptom

A word that reads as a different word, or a letter group that looks broken. Arabic suffers more than Latin because the dots and marks carry the letter's identity: without its dots, ي reads as a different letter.

### Impact

A hard release failure. Clipped Arabic on a Saudi client's film reads as carelessness about the language.

### Incorrect assumption

That a designer can place large Arabic words by eye and confirm them on a contact sheet. Also that an overlap on the foot of a word is a safe decorative crop.

### Root cause

**Confirmed** for each case, from stills at full resolution and from measurement.

### Why the architecture allowed it

- Widths were guessed from font size. Thmanyah Serif Display and Thmanyah Sans have different advance widths at the same size, so moving a word from Sans Black to Serif Display Black changed its width without anyone recomputing the layout.
- Text blocks use `white-space: nowrap`, so an overlong line never wraps. It overflows silently.
- The dot zone below the baseline is exactly where a sheet overlapping a word's foot lands, so "slightly covering a letter" removes dots first.
- Nothing measured text against its containers. Review depended on a person noticing a few missing pixels in a 180 px thumbnail.

### Fix

- Each case was fixed in layout: less crop on «آخر» (block width 1128 px), the word moved up so the sheets meet it below the dot zone, the cone word shifted and resized.
- `skills/motion-director/scripts/clip-audit.js` now measures every visible text run at every 0.1 s against the frame and every ancestor that clips (`overflow: hidden` or `clip`). It reports cuts that last at least 0.5 s, skips text fully hidden inside a mask (a word waiting to rise is not a crop), and with `--safe N` warns about text closer than N px to a frame edge.
- Designed crops are declared in code with `data-crop="intentional"` (the `crop: 1` option of `txt()` in `film.js`), so the audit skips them and a reader of the code can see the decision.

### Verification

Red-green on a scratch copy of the project, never on the working tree:

- Current film: 1 cut found («فريق الاستقبال», 27.30 to 27.80 s, 7 px), which review by eye had missed.
- With that label shortened: `PASS`, exit 0.
- With the historical «آخر» crop reintroduced (block width 1210 px): `CUT 0.00-1.30s "آخر" cut by frame: right 69px`, exit 1.

### Prevention rule

Before delivery, run the clip audit on the composition. Every crop is either declared intentional in code or fixed. Any overlap on a word must stay above the dot and descender zone.

### Reusable lesson

Visual QA by eye is good at composition and bad at small geometry. Where a defect is geometric, measure it.

### Related lessons

[Diagnose from a measurement](testing-and-verification.md#diagnose-from-a-measurement-not-from-a-thumbnail), [Light cones and polygon reveals](composition-and-transitions.md#text-inside-a-light-cone-or-polygon-reveal)

### Status

Partially mitigated.

- The audit covers the frame and rectangular clips. It does **not** see `clip-path` polygons (the light cone), `inset()` reveals, or occlusion by a sibling element such as a sheet sliding over a word. Those still need eyes on full-resolution stills.
- The slip cut at 27.3 to 27.8 s is still in `renders/Four-Steps-Events-Motion-Final-v2.mp4`. The source keeps the delivered text so that code and render match. Fix it on the next render by shortening the label or reducing its size.

---

## Near-edge text is a separate problem from clipping

### What happened

A `--safe 48` run on the delivered film warns about lines that are inside the frame but very close to its edge: «نغطي الحدث» at 2 px, «عندك فعالية جاية؟» at about 10 px, «ليالي» at about 27 px from the top.

### Root cause

**Confirmed** by measurement. The margin is measured on the font box (ascent to descent), so it overstates how close the ink comes, which is why the audit reports it as a warning and not a failure.

### Prevention rule

Keep non-hero copy at least 48 px from any edge, more at top and bottom where platform UI sits. Confirm each warning at full resolution.

### Status

Unresolved for the delivered v2. Candidates for the next render: «نغطي الحدث» and «عندك فعالية جاية؟».

---

## Swash as ornament

### What happened

The brief asked for Thmanyah's OpenType features to be used. Early drafts turned on `swsh` for «باسمك» and «وتتذكره». The creative review read the result as a font demo, with an awkward baseline under «باسمك».

### Root cause

**Confirmed** by review: the feature was used because it existed, not because the frame needed it.

### Fix

Swashes are off everywhere in the film. The available features are recorded in `projects/four-steps-events/MOTION.md` (both families: `swsh`, `salt`, `ss01`, `ss03` to `ss07`, `dlig`, plus `ss08`, `case` and `frac` in the sans and `lnum` and `onum` in the serif display), so the next project can choose on purpose.

### Prevention rule

List a font's features before designing with them (`fontTools` can read WOFF2 once `brotli` is installed). Use an alternate only when it solves a composition problem.

### Status

Resolved. The general rule is in `skills/motion-director/references/arabic-motion.md` (Display alternates).

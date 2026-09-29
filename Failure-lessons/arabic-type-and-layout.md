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

---

## Words waiting under a mask leak through its descender padding

### Context

`projects/mgs-promo/index.html` reveals Arabic words with a masked rise. Each word sits in a `.m` wrapper with `overflow: hidden`. The wrapper is padded (0.12 em top, 0.3 em bottom, with matching negative margins) so that dots and descenders are never clipped once the word has arrived.

### What happened

Before its cue, each word waited 105 % of its own height below the mask. The mask box extends 0.3 em further down because of the padding, so the tops of the waiting words showed through the bottom band of their own masks. Seen on the first full snapshot pass: a blurred dark smudge under the «عرض قوي» stamp (the tops of "Studio", which is laid out there for a later beat), orange specks under «الموشن» (the waiting «هذا؟»), marks at the lower left at 8.1 s (the dots of «الرندر», laid out for the next beat), and a bump on the dark line at 13.8 s (the hamza of «أكثر»).

### Observable symptom

Stray dots, specks and smudges near where a word would later appear, visible for whole beats.

### Impact

Noise that reads as dirt or broken letters, especially on Arabic, where a lone dot looks like a detached letter part.

### Incorrect assumption

That a word shifted by 100 % of its own height is fully outside its mask. With descender padding the mask is taller than the word, so it is not.

### Root cause

**Confirmed**: every mark matched a waiting word's position, and all of them disappeared once waiting words were hidden.

### Why the architecture allowed it

The padding that protects Arabic dots in the settled state enlarges the visible window in the waiting state. The two requirements pull the same box in opposite directions.

### Fix

`rise()` sets the word to `opacity: 0` from time 0, switches it to `opacity: 1` at its cue, and starts the rise from `yPercent: 130`. The same was applied to the B6 words that had their own tweens.

### Verification

Full snapshot pass after the fix: no marks at 8.1, 13.8, 16.0 or 17.2 s. The same frames were checked at full resolution from the delivered file.

### Prevention rule

A word waiting for its cue must be both geometrically outside its mask box, padding included, and hidden. Never rely on the offset alone once a mask carries padding for Arabic marks.

### Reusable lesson

Any padded mask (clip wrappers with bleed, SVG clip paths with margins) needs its hidden state checked at the time before the reveal, not only at the time after it.

### Related code

`rise()` and `.m` in `projects/mgs-promo/index.html`.

### Status

Resolved. No automated check. `clip-audit.js` looks for cut text, not for text that should not be visible yet.

---

## Recurrence: the alef crop, and a Latin name that wrapped

### What happened

The same class as [Accidental clipping found only by eye](#accidental-clipping-found-only-by-eye) came back twice on the promo:

1. Opening study B set «الموشن» at 430 px in a block wider than the frame. The frame edge cut the alef, so the word read as «لموشن», the same defect as «آخر» → «خر» on the Four Steps film. It was caught on the opening-study sheet before the full build.
2. "Claude Code" at 172 px in an absolutely positioned box with no `white-space: nowrap` shrank to fit the space to the right of `left: 90px` and wrapped onto two lines, colliding with the timeline below.

### Root cause

**Confirmed** from the stills in both cases.

### Fix

The word stays inside the frame at 300 px. "Claude Code" is 150 px with `white-space: nowrap`, and the timeline sits below its measured line box.

### Prevention rule

The existing rule holds: never crop a letter that is read. Add this: every single-line display phrase gets `white-space: nowrap`, and its measured width is checked against the frame. Shrink-to-fit wrapping of Latin names is silent.

### Status

Resolved for this film. Recurrence shows the rule is not enforced by any tool at authoring time. The clip audit catches frame crops only after a render exists.

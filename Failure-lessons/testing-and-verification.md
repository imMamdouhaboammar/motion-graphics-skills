# Testing and verification

Lessons about checks that gave false confidence, diagnoses made from the wrong evidence, and the verification patterns that actually caught problems.

Related tools: `projects/four-steps-events/tools/` (`render.js`, `stills.js`, `fontcheck.js`, `contact_sheet.py`, `inspect_sheets.py`), `skills/motion-director/scripts/clip-audit.js`.

---

## A check that could not fail

### What happened

`fontcheck.js` asks Chromium, through the DevTools protocol (`CSS.getPlatformFontsForNode`), which platform font actually painted each text node, and fails on any system font. A reviewer found that the first version read the wrong key from the result and swallowed protocol errors. It printed PASS whatever fonts were used.

### Observable symptom

None. A green check.

### Impact

The brief made correct Thmanyah rendering a hard requirement. The check that claimed to prove it proved nothing.

### Incorrect assumption

That a check which passes on a correct film is a working check.

### Root cause

**Confirmed** from the code: wrong property name, errors caught and ignored.

### Fix

Read the correct field, count protocol errors, and exit non-zero on any system font or any error.

### Verification

Red-green on a scratch copy, after the lesson extraction:

- Unchanged copy: `PASS: no system fallback`.
- One label switched to a family that is never loaded (`TSX`): `FAIL: system fallback used by Liberation Serif (SYSTEM), DejaVu Sans (SYSTEM)`, exit 1.

### Prevention rule

A check is not trusted until it has been seen failing on a reintroduced defect. Do this in a copy of the project, not the working tree.

### Reusable lesson

Every gate in a motion pipeline (font check, clip audit, duration check, colour check) needs one red run on record.

### Related tests

`fontcheck.js` red-green above. `clip-audit.js` red-green in [arabic-type-and-layout.md](arabic-type-and-layout.md#accidental-clipping-found-only-by-eye). `render.js` fault injection in [render-pipeline.md](render-pipeline.md#a-renderer-that-ignores-its-encoders-failure).

### Status

Resolved.

---

## Diagnose from a measurement, not from a thumbnail

### What happened

During stills review, a 3 to 6 per row grid made the question «علق في بالك؟» look wider than the frame. It was set at 210 px and reduced to 176 px as a clipping fix. Measured afterwards, the line at 210 px was 1018 px wide: inside the frame, 31 px from each edge. The words from the next thumbnail had been read as part of the same line. A second false alarm on the full contact sheet («شهور» looked struck through) turned out to be the dimmed lever behind it, found only by rendering single frames.

### Observable symptom

A confident diagnosis that did not match the frame.

### Impact

The change was still worth making, because 31 px is a safe-margin breach, but it was made for the wrong reason. A wrong diagnosis can just as easily trigger a harmful change.

### Incorrect assumption

That a contact sheet is evidence of geometry. It is evidence of composition and sequence.

### Root cause

**Confirmed** by measuring the line's box in the page at both sizes.

### Fix

Suspected geometric defects are now checked with a single full-resolution still or a measurement (`getBoundingClientRect` on a text range, or `clip-audit.js`) before any code changes.

### Prevention rule

Contact sheets find candidates. Full-resolution frames and measurements decide. Build sheets with visible gutters between tiles.

### Status

Resolved as practice. The `inspect_sheets.py` tiles have no gutter yet (open).

---

## Visual review misses what it is not looking for

### What happened

Two complete inspection passes (a frame every 0.5 s plus targeted stills) missed a 7 px cut of «فريق الاستقبال» that lasts half a second. The clip audit found it in four seconds of DOM measurement.

### Root cause

**Confirmed**: the cut is below what a 180 px wide thumbnail shows, and half a second falls between 0.5 s samples.

### Prevention rule

Use people for composition, hierarchy and taste. Use measurement for anything geometric: clipping, margins, duration, frame count, colour values.

### Status

Partially mitigated (see the audit's known gaps in [arabic-type-and-layout.md](arabic-type-and-layout.md#accidental-clipping-found-only-by-eye)).

---

## Patterns worth reusing

These patterns caught real problems on this project. Each note says what it caught and where it gives false confidence.

| Pattern | What it caught | When it misleads |
|---|---|---|
| Deterministic `window.seek(t)` with seeded randomness (mulberry32), hand-made elements on twos | Made every other check possible: any frame can be reproduced, compared and measured | Only if some code reads the real clock or `Math.random` |
| `stills.js` at chosen times | The ي dots under the sheet, the cone cutting ؟, the corridor collisions, the ghost poster | Only shows the times you ask for |
| A frame every 0.5 s (`inspect_sheets.py`) | Crowded frames, weak beats, rhythm across the whole film | Small geometry and anything shorter than 0.5 s |
| Old and new pairs at the reviewed moments | Whether the polish pass fixed what the brief named, without re-watching both films | Nothing about moments outside the list |
| Reference, v1 and v2 contact sheets side by side | Palette and density drift against the reference | Thumbnails hide type problems |
| `fontcheck.js` through the DevTools protocol | Proof that no text fell back to a system font | Only if it has been seen failing |
| `clip-audit.js` | A half-second 7 px Arabic cut missed by eye | Polygon clips and occlusion by siblings |
| Fault injection (impossible output path) | That the renderer really fails when ffmpeg fails | Other failure modes, such as a corrupt frame, are untested |
| Red-green on a scratch copy of the project | Whether each check can fail, without touching the working tree | Only covers the defect you reintroduce |
| Render once with the tail, cut the WAV-exact file from the same frames | Two deliverables that cannot drift apart | The cut must be by frame count, not time |

---

## Progress estimated from the wrong signal

### What happened

A long render ran in the background with its output piped through `tail`, so no progress lines were visible until it finished. Progress reported to the user was estimated from the growing file size compared with the previous render's size. That estimate was rough because the encoder spends bits unevenly across scenes.

### Root cause

**Confirmed**: `render.js` prints progress every 150 frames, but the pipe hid it.

### Prevention rule

Send long-running progress to a log file you can read (`2>&1 | tee render.log`), and report progress from frame counts, not file size.

### Status

Resolved as practice.

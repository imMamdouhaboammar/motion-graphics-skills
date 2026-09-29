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
| Two renders compared by `framemd5`, second one under CPU load (`projects/mgs-promo/tools/determinism-check.sh`) | A paint race in the grain layer that an idle pair of renders did not show | Only races that load provokes; it cannot prove the absence of rarer ones |
| Cross-correlating the final file's audio with the master WAV | VO offset (0 ms) and a silent tail, measured on the delivered file rather than read from the command | Needs the master WAV; SFX lower the correlation a little |
| Stills and contact sheets taken from the delivered MP4, not from the composition | A blank opening that snapshots of an older code state did not show | Only the frames you sample |
| Font gate from `document.fonts` status plus width against the fallback face (`projects/mgs-promo/tools/font-check.cjs`) | That every declared face loaded; the red run with a missing file fails readiness | Width can match by coincidence; confirm with the DevTools platform-font check when available |
| Whisper large-v3 word times cross-checked against `silencedetect` pauses | A beat map built on measured times; every pause over 120 ms lined up with a word gap | The transcript's words are not reliable Arabic (see below) |
| Three opening studies snapshotted on one sheet before the build | A crop that cut the alef of «الموشن», and a weak first frame in two of the three routes | Judges only the first seconds |

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

---

## An audit passes when the thing it measures is missing

### Context

`projects/mgs-promo/index.html`, opening beat B1: «الموشن» is built from five slices created in script.

### What happened

A scripted text replacement added an explanatory `//` comment in front of the slice-positioning statements on the same line. Everything after `//` became part of the comment, so the slices lost their `top` and `height`, and B1 rendered as an empty dark frame with only the timecode. Lint passed, `hyperframes check` passed, and `clip-audit.js` reported PASS for 0 to 26.6 s. The audit passed because it found no visible text to measure in B1. Only the render, checked by pixel count and by eye, showed the empty frame.

### Observable symptom

A PASS from the geometry audit, and a render whose first 1.5 s had no hero word.

### Impact

The film's hook would have shipped blank if the final had not been re-rendered and inspected.

### Incorrect assumption

That a clean audit means the text is present and correct. It only means that no visible text is clipped.

### Root cause

**Confirmed**: the line in the diff, and B1 restored as soon as the statements moved to their own lines (bright pixels in the word band went from 0 to 72,199).

### Why the architecture allowed it

The audit measures what exists and has no list of what must exist. Edits made by string replacement inside one long line are easy to break this way and hard to see in a diff.

### Fix

The statements moved to their own lines. The final was re-rendered, a contact sheet was built from the delivered file, and every beat was viewed.

### Verification

`python3` pixel count on snapshots at 0.2 s and 1.0 s: 0 bright pixels before the fix, about 72,000 after. The clip audit was re-run afterwards with the word present.

### Prevention rule

After any code edit, render and look at the frames that edit could reach. A geometry or clipping audit is not a presence check. When a beat has a hero word, assert that it is visible (a pixel count in its band, or a DOM check that the text has a non-zero box) as well as unclipped. Never put a comment on the same line in front of code, especially when editing with scripts.

### Reusable lesson

Every "no findings" result must be read together with "how much was measured". An audit that sampled zero items passes.

### Status

Resolved for this film. The clip audit still does not report how many text runs it measured per beat (open).

---

## Two changes between renders, one wrong culprit

### What happened

Between two renders, two things changed: the readiness promise stopped returning the timeline, and `data-crop="intentional"` was added to the B1 slices. The next render had a blank B1. The attribute was blamed. It was removed from production, and a code comment and `inspection/VERIFY.md` stated that "HyperFrames reserves data-crop". The real cause was the swallowed line described above. Frame differences from the paint race (render-pipeline) also muddied the comparison at the time.

### Incorrect assumption

That the most unusual of the recent changes is the cause.

### Root cause

**Confirmed.** The HyperFrames runtime has no reference to `data-crop`. A render with the attribute restored is frame-identical to one without it (798 of 798 frames by `framemd5`).

### Impact

A false statement about the framework reached the repository in two places. Future readers would have avoided a working convention of this pack (`data-crop` is how `clip-audit.js` learns about designed crops).

### Fix

The attribute is back on the slices, and the claim is removed from the code comment and from `VERIFY.md`.

### Prevention rule

Change one thing per diagnostic render, or bisect when several changed. A hypothesis goes into code or docs only after it has been confirmed, with the evidence named. Otherwise label it as a hypothesis.

### Status

Resolved.


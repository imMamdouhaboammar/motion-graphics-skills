# Review gates

Use this for final review or for a creative-director polish pass on an existing film.

## Evidence first

Review the actual render, frames, or composition that exists. Do not approve a hypothetical result and do not claim to have inspected motion that was not available.

Preserve strong choices. A review should identify what to keep as clearly as what to change.

Use people for composition, hierarchy, and taste. Use measurement for geometry: clipping, safe margins, duration, frame counts, and colour values. A contact sheet shows candidates, not proof. Two adjacent thumbnails can read as one overflowing line, and a dim layer behind a word can read as a strike-through. Confirm at full resolution before changing code.

## Review order

Review in this order:

1. concept
2. hierarchy
3. typography
4. color
5. composition
6. asset cohesion
7. motion
8. timing
9. audio relationship
10. technical output

Do not start by adjusting tiny easing curves when the art direction is wrong.

## Timecoded critique format

For a finished draft, review by timestamp.

Each note should contain:

- time or time range
- observed problem
- why it weakens the film
- exact direction
- what to preserve
- severity

Severity:

- blocker: release must stop
- high: materially weakens communication or craft
- medium: visible weakness worth fixing
- polish: small finish issue
- keep: strong choice that should survive revision

Example:

00:14 to 00:15
High
The correction mark and headline compete. Reduce the headline scale and let the handwritten correction become the focal point. Keep the cue-sheet concept.

## Opening gate

At 00:00:

- is there already something worth looking at?
- is the focal point obvious?
- does the first frame promise the film's visual world?
- can it stop a feed without sound?

At 00:01:

- has the composition become clearer, not only busier?
- is the hook readable?

At 00:03:

- has the film already demonstrated one signature motion idea?

## Still-frame gate

Capture:

- first frame
- 0.5 s
- 1 s
- midpoint of every beat
- each transition
- CTA
- final frame

For a long piece, sample every 0.5 or 1 second.

Check:

- hierarchy
- spacing
- safe zones
- clipping
- logo use
- palette
- type scale
- image treatment
- shadows
- depth
- repeated layout
- accidental symmetry
- dead space
- tiny text

## Typography gate

Check:

- at least three clear type roles when the film needs them
- not every role uses the same heavy weight
- headline size matches importance
- support copy is actually support
- line breaks are intentional
- punctuation is correct
- no accidental fallback
- no transcript wallpaper

## Color gate

Check:

- neutrals are clean
- accent is controlled
- official logos are not recolored
- proof marks have enough clear space
- dark scenes have a purpose
- full-frame brand color is used deliberately
- texture does not dirty the palette

## Asset gate

Check:

- photos, vectors, diagrams, cutouts, and generated assets feel part of one world
- shadow direction is consistent
- contrast is consistent
- edge treatment is consistent
- no fake text in generated imagery
- no invented logo
- no visual asset is only filler

## Motion gate

Watch the full piece.

Check:

- every camera move has a reason
- transitions come from scene content
- repeated slide-ins are limited
- repeated scale pops are limited
- no perpetual floating
- no random bounce
- holds are long enough
- motion density changes through the film
- callbacks at the end are selective
- the final second resolves instead of introducing another trick

## Audio gate

Sound on:

- visual emphasis lands on useful words or beats
- scene changes do not cut across meaningful syllables
- music supports voice
- SFX do not mask language
- silence or quiet is used intentionally

Sound off:

- the core idea still reads
- CTA still reads
- the film still has hierarchy

## Phone gate

View at the approximate physical size of a phone.

Hard-fail:

- support copy becomes noise
- Arabic becomes difficult to parse
- logos become tiny
- detail depends on desktop size
- important objects lose recognition

## Hard release gates

Fail the film regardless of average quality when:

- approved copy is wrong
- Arabic shaping or RTL behavior is malformed
- an official logo is distorted or recolored without permission
- a factual claim is invented
- a key scene is unreadable at delivery size
- the final encode is incomplete or desynchronized

## Bounded revision

Run one complete visual and motion defect scan, fix all confirmed findings in one batch, then run at most one confirmation pass. Do not enter an endless polish loop.

Route the fix to the smallest responsible layer. A typography problem should not trigger a concept rewrite. A shadow problem should not trigger a new storyboard.

## Creative-director test

Ask:

- Does this look like a specific person directed it?
- Could this frame belong to ten unrelated brands?
- Is there one motion thesis or a collection of tricks?
- Is there a moment that feels copied from a template?
- Is any scene trying to prove technical complexity rather than communicate?
- Is the ending cleaner than the middle?
- Can one element be removed from each crowded frame?

## Technical gate

Verify the actual final file.

Typical social delivery checks:

- intended width and height
- intended frame rate
- H.264 where required
- yuv420p
- BT.709
- AAC when audio exists
- faststart
- correct duration
- audio starts at zero
- no truncated end hold (count the hold frames on the final file)
- no missing final frame
- every automated gate used for signoff has been seen failing on a reintroduced defect at least once

Use the runtime's own validation and ffprobe where appropriate.

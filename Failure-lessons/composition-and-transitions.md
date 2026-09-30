# Composition and transitions

Lessons about frames that looked wrong because of how layers, colour and camera interacted, not because any single element was wrong.

Related code: `projects/four-steps-events/film.js` (scenes B2, B4, B5, B6).
Related skill guidance: `skills/motion-director/references/motion-craft.md`, `skills/motion-director/references/anti-slop.md`, `skills/motion-director/references/review-gates.md`.

---

## A crossfade between two saturated fields makes a third colour

### What happened

A transition crossfaded a navy field into the Four Steps blue field. Mid-transition frames came out lavender, a colour that exists nowhere in the brand. A second flicker frame of the same colour appeared at another cut.

### Observable symptom

One or two frames of an off-brand colour, visible when scrubbing and on the contact sheet, easy to miss at speed.

### Incorrect assumption

That an opacity fade between two colours passes only through colours "between" them that still look on-brand.

### Root cause

**Confirmed** from the frames: blending two layers by opacity (plus the paper and halftone layers multiplied on top) produced an intermediate hue that belongs to neither brand colour.

### Fix

Hard cuts on twos in the navy sections. In the polish pass the one full-blue brand frame arrives through a shared object instead: the blue correction mark from the previous shot stretches into a marker stroke across the frame and then floods it (`B4`, `clipPath` polygon with wobbly edges).

### Verification

Frame-by-frame stills around each cut (`tools/stills.js`) show no intermediate hue.

### Prevention rule

Never opacity-crossfade two different saturated fields. Cut, wipe with a shaped mask, or carry one object across. When a fade is unavoidable, inspect the midpoint frame.

### Reusable lesson

Any blend between brand colours (logo recolours, background changes, light cones changing colour) needs its midpoint frame checked against the palette.

### Status

Resolved.

---

## Perspective walls converge on the vanishing point

### What happened

The "many events" corridor put posters on two walls in perspective. Far posters from both walls converged near the vanishing point in the middle of the frame and overlapped, producing unreadable fragments such as two event names printed over each other. Moving them closer only moved the collision. Fading the nearest poster as it passed the camera left a large translucent ghost over the headline.

### Observable symptom

Frames where two posters overlap in the middle, and a washed-out giant poster crossing the frame.

### Impact

The corridor read as generic 3D cards, the opposite of the proof the scene was meant to deliver.

### Incorrect assumption

That a two-wall corridor is a neutral way to show "many". In a 9:16 frame the vanishing point sits where the headline and the eye already are.

### Root cause

**Confirmed** by stills at 0.4 s steps: overlap came from projection geometry, not from spacing values.

### Fix

A face-on depth stack: posters face the camera with a small alternating offset and tilt, at most three are visible (opacity windows on depth), and the nearest one leaves by sliding sideways past the lens instead of fading. This is an occlusion exit, not a dissolve.

### Verification

Stills at 19.4, 19.8, 20.2, 20.4, 20.6 and 21.0 s show two or three large readable posters and no ghost.

### Prevention rule

Show quantity with depth and scale on one readable plane. An object that passes the camera leaves by moving, never by turning translucent.

### Status

Resolved.

---

## Camera travel crops the labels it leaves behind

### What happened

The workflow section is one continuous camera travel down a tall paper world. In v1, labels for stations already passed stayed on screen while the camera moved on, so their tops were cut by the frame edge («المرئي» half out of frame at 34.6 s).

### Root cause

**Confirmed** from stills: labels had no exit, and the camera keyframes were chosen for the objects, not for the labels.

### Fix

Each station label exits (word by word) before its station leaves frame, and the camera keyframes were rechosen so every label sits at least about 140 px below the top when it is read.

### Verification

Stills along the travel, and the clip audit now reports no frame cuts there.

### Prevention rule

In a travelling camera, every label is owned by its station: it arrives with it and leaves before it. Check each station's label position at that station's keyframe.

### Status

Resolved.

---

## Text inside a light cone or polygon reveal

### What happened

«الإضاءة؟» is revealed inside a flat light cone. Narrowing the cone for composition (the brief asked for more navy around it) cut the question mark.

### Root cause

**Confirmed** from stills: the cone polygon was narrowed without checking the word's box against it.

### Fix

The word was shifted and made smaller to sit inside the cone with a margin.

### Prevention rule

When text is revealed by a polygon (cone, torn edge, shaped mask), the text box must sit inside the polygon at its widest reading frame. `clip-audit.js` does not test polygon clips, so check these frames by eye.

### Status

Resolved for this shot. The audit gap is recorded in [arabic-type-and-layout.md](arabic-type-and-layout.md#accidental-clipping-found-only-by-eye).

---

## Generated correctly is not directed

### What happened

The first final passed every technical check and still drew a long creative-director review: muddy beige paper, brand blue used as wallpaper, every headline in Sans Black, crowded frames with three equal focal points, props from different visual worlds, a cheap vector starburst, a weaker ending than opening.

### Incorrect assumption

That a correct render of a sound plan is a finished film.

### Root cause

**Confirmed** by the review itself and the before-and-after sheet in `projects/four-steps-events/inspection/before-after.png`.

### Fix

The polish pass. Its specific values live in `projects/four-steps-events/MOTION.md` (colour roles, a five-level type system, three elevations, one print treatment for photographic props). The general rules were folded into `skills/motion-director` (anti-slop, review gates, still-frame gate) and are not repeated here.

### Prevention rule

Run the still-frame and creative-director gates in `skills/motion-director/references/review-gates.md` before calling any render final.

### Status

Resolved for this film. The rules live in the skill.

---

## A round-capped stroke paints a dot before it draws

### What happened

The pencil sketch in B4 of `projects/mgs-promo/index.html` draws with `stroke-dasharray` and `stroke-dashoffset` (the `svg-path-draw` rule) and `stroke-linecap: round`. At full dashoffset, the dash length is zero but the round cap is still painted, so each sketch path showed a small dot at its start point before its draw began (a graphite speck at 8.1 s).

### Root cause

**Confirmed**: the dots were exactly at path start points and disappeared when the paths were hidden until their cue.

### Fix

Each sketch path is `opacity: 0` from time 0 and becomes visible at its draw cue.

### Prevention rule

A path drawn with dashoffset and round or square caps stays hidden until its draw starts. Butt caps do not have this problem.

### Status

Resolved. Worth adding to the HyperFrames `svg-path-draw` recipe upstream (not done).

---

## A scene ended before its exit tween finished

### What happened

A reviewer (Codex) found that B6's clip ended at 15.44 s while its split tweens ran until 15.46 s, and the desk scene ended at 22.64 s while its wipe ran until 22.66 s.

### Observable symptom

None at 30 fps. The 20 ms gap falls between two frames: the frame before the scene ends is mid-tween, and the next frame is past the tween end, where the panels are already off-frame. A re-render with the durations extended is frame-identical (798 of 798). At 60 fps a frame would land inside the gap and show the transition cut short.

### Root cause

**Confirmed** from the timings. Clip durations were typed by hand beside the tweens, not derived from them.

### Fix

The clip durations now cover the exit tweens (B6 to 15.48 s, desk to 22.68 s).

### Prevention rule

A clip's end is at least the end of every tween that animates its content. Derive the duration from the last tween, or check it with the timeline, instead of typing both numbers. Frame rate can hide the gap, so check the timing contract, not only the frames.

### Status

Resolved.

---

## A parked element peeked into the frame before its entrance

### Context

`projects/jedar-lesh-majani/index.html`, scene S4. A hang tag carrying the word «تقييم» waits above the frame and drops in on its VO cue at 6.2 s.

### What happened

The tag was parked with `y: -900` from a layout top of 470 px, on a 700 px tall element. A second tween, `fromTo('#s4-tag', { rotation: 9 }, ...)` at 6.55 s, applied its start rotation immediately at build time (GSAP `fromTo` defaults to `immediateRender: true`). The rotated corner of the tag and the lower part of «تقييم» hung into the top of the frame from 5.7 s to 6.2 s, over the masthead, before the tag was meant to exist.

### Observable symptom

A green shape and a cut Arabic word at the top edge for half a second before the drop.

### Impact

A read word cut by the frame edge, and an object visible before its cue, in the hook of a paid ad.

### Incorrect assumption

That an offset that looks large enough parks an element out of frame. The offset was picked by eye, not computed from the element's height and its rotated bounds.

### Root cause

**Confirmed**. The clip audit reported `CUT 5.70-6.20s "تقييم" cut by frame: top 95px`. Reintroducing the old two tweens in a scratch copy reproduces the same finding.

### Why the architecture allowed it

The parked state has no owner. Nothing in the composition says "this element is not in the film yet". Visibility was left to geometry, and a second tween silently changed that geometry at time 0. The contact-sheet stills were taken at 5.2 s and 7.2 s, both outside the half-second window.

### Fix

The element is hidden until its cue and parked beyond its own height: `gsap.set('#s4-tag', { opacity: 0, y: -1300 })`, `tl.set(..., { opacity: 1 }, 6.2)`, and the rotation tween is created with `immediateRender: false` so it cannot change the parked state.

### Verification

Red-green with the project's clip audit, served from the same page:

- old code in a scratch copy, 5 to 8 s: `FAIL`, one cut at 5.70 to 6.20 s
- current `index.html`, 5 to 8 s: `PASS`
- whole film at 0.2 s steps with `--safe 40`: `PASS`

### Prevention rule

An element that waits for its entrance is hidden (`opacity: 0` or `visibility: hidden`) and positioned outside the frame by more than its own rotated bounds. Any `fromTo` whose start state must not apply before its start time gets `immediateRender: false`.

### Reusable lesson

This is the same class as [words waiting under a mask](arabic-type-and-layout.md#words-waiting-under-a-mask-leak-through-its-descender-padding): the hidden state of an element was never checked, only its arrived state. It applies to anything parked off-frame, behind a mask, or at zero scale.

### Related code

`projects/jedar-lesh-majani/index.html` (S4 block), `projects/jedar-lesh-majani/tools/clip-audit.js`.

### Related lessons

[Visual review misses what it is not looking for](testing-and-verification.md#visual-review-misses-what-it-is-not-looking-for)

### Status

Resolved for this film. The audit catches a parked element only when it carries text; a parked shape without text is not measured.

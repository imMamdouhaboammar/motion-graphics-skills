# MOTION GUIDE | AI BUSINESS COLLAGE

## Reference technical study
- Supplied reference: H.264, 720×1280, 30 fps, 38.704807 s (verified from attached file, not public reference).
- Supplied independent ElevenLabs VO: PCM s16le, 48,000 Hz, mono, 48.352667 s.
- Target: 1080×1920 30 fps; approximate normalized time scale reference→new VO is 1.2493. **The score/VO is primary**, not a global `setpts` transformation. Clean CTA end card.
- Observed changes: 1.5–1.75 sky→ivory frontal paper; ~4.5–4.75 frontal→overhead desk; ~8.4–9 frontal silly assembled person; ~11 map; ~16.6 map→people; ~19.3 people→paper hand-offs; ~22.7 papers→monitor; ~26 diagonal grid; ~30.8 dark reel cards; ~32.7 ivory minimal closing. Times are approximate visually reviewed moments, not certified frame-exact automated boundaries.

## Camera states and action cues (30 fps candidate keyframes)

| Source block | Motion mechanic | Candidate 30fps action | Layer behavior | Editorial discipline |
|---|---|---|---|---|
| Sky → starting image | Lift/drop aerial reveal, separate banner/type | title initial arrival 6–10f; camera down/push ~10–16f; hold hero 12–20f | sky nearly fixed, foreground ribbon/photo position offset 15–35 px | physical banner with type rendered separately; source face/runner not reused |
| Frontal pressure | fixed center photo while props rush in | snap 0–1f, side props stagger at 4–6f | hero depth z70; prop hands z120; shadows match | controlled escalating crowding, no camera shake |
| Overhead | true topdown multi-zone table camera | 2–3 sharp reframe moves of ~8–14f each with hardholds | plate z0; people z40; sticky notes z90 | distinct real overhead objects, not a flat collaged front-view desk |
| Frankenstein | hard jump assembly + numerical burgundy background | slices land 1–3f intervals; push ~7f | paper strips interleave with torso, contact shadows | deliberate mismatch, not body-horror |
| Route map | longest continuous overhead path travel | line draw segment-by-segment; pin drops 5–8f; camera tracks pins | map matte z0, path z15, pins z70, type z90 | draw line on a real route, don't simply crossfade icons |
| Audience montage | repeated realistic cutout series | appearance offsets 4–8f; one punch zoom 6–9f | all independently movable | differentiated authentic people, no privacy-surveillance implication |
| Papers hands | physical object hand-off and stamp | papers slide 10–15f, stamp hit 3f, camera jumps on impact | foreground hands occlude papers; cast paper shadows | tactile masking and contact, no floating generic rectangles |
| Monitor | frontal desk object with controlled masked UI | monitor pops/push 8–10f, paths to screen 8–12f | actual screen image masked in photo, frame in front | screens remain neutral and believable, no fake software branding |
| Diagonal cards | kinetic collage tilt/pan/orbit-lite | long traveling 25–50f segments between anchor cards | independently textured cards and underlaid shadows | authentic foreshortening, not a CSS gallery |
| Dark vertical cards | concentrated contrast punctuation | 3-4 cards snap in 3–6f and hold briefly | subtle offset between card depths | use the dark-background beat **once** |
| Paper reset/end | hard clean reset then gentle breathing | immediate cut; text settles over 6–10f; hold until final audio | mostly stationary | no decorative camera orbit |

Keyframe numbers are starting hypotheses. Measured reference direction, composition and movement take precedence. For accurate replication, source scene cut frame numbers and sample displacements using the actual attached reference. Short `power3.out` moves and stationary editorial holds are both necessary. The source does not have uniform motion density.

## 2.5D stage
- Develop a camera parent transform and children with explicit z categories. A camera parent zoom naturally affects all contents, while separate motion per depth group creates additional parallax.
- Depth suggested: background 0, tabletop/card field 15-30, photographic hero 60-90, hands/paper 90-130, typed Arabic 140-160; prefer small, measurable pixel parallax.
- Shadows: warm brown at low opacity with offset proportional to separation from paper; avoid deep black blur halos. Retain paper edge irregularities slight and subtle, except where source plainly uses clean geometric crop.
- Physical transitions: cut, slide under paper, hand-carried sheet, stamp, mask reveal, perspective-matched cutout. Limit trendy digital easing tricks.
- Grain: one background paper texture; DO NOT blanket the whole picture with large overlaid grain. Preserve natural photo clarity.

## Source to storyboard structural mapping
The normalized target windows in `STORYBOARD.csv` are illustrative. After voice alignment, every parent shot gets a `start_frame,end_frame`, each subaction gets `keyword_start_frame` and a preserved source `camera_mechanic`. E.g., at audible «ينسخ ويلصق» hands really transport a paper card between unconnected workflows; at «نربط» route physically connects devices; at «قراءة النتائج» physical readable report moves to foreground; at «ابدأ» the CTA word must hold legibly.

## Design and typography
- Main palette approximate: parchment `#E9E3D3`, burgundy `#691B24`, deep burgundy `#541015`, charcoal `#292424`, darker accent `#6B2A2B`, white paper `#F4EEE3`. Calibrate to supplied reference screenshots with actual eyedropper values.
- Source uses inconsistent density by design: busy paper office scenes alternate with large blank ivory fields; do not equalize.
- Native connected Arabic glyphs, correct right-to-left blocks. Words not independently disconnected letters. Prefer text integrated with printed props or visually weighted charcoal headings.
- 1080×1920 landscape of layers within vertical frame; final practical safe margins >= 70 px on each side, target content relevant to lower social-app UI overlays avoided.

## Audio
- Keep source mono VO untouched in a work master; output AAC 48kHz in MP4 without changing its pace or loudness envelope beyond neutral gain necessary for final mix; preserve speech clarity.
- Short transient SFX only where props actually contact: scissors/paper snap, stamps, burgundy route drawing, device connection, low keypress. Mix SFX below clear narration, no loud surprise transitions.
- If source reference includes music, **do not reuse**. License original minimal backing or prefer VO+foley.
- Keep final exported video duration within a single 30fps-frame of original WAV duration unless explicit extra hold is documented.

## QA: compare the *moves*, not just colors
- Gate 1: frame similarity of layout anchors and motion *patterns* at normalized equivalent story positions; compare camera direction and acceleration manually.
- Gate 2: scene-by-scene compare 3-5 photos showing source compositional logic and fresh corresponding target artwork.
- Gate 3: zero copy/paste typographic errors (RTL), one clear focal point, legible text on mobile.
- Gate 4: scrub frame 0, every scene switch ±2 frames, sample midpoints, final 12 frames, and validate video plays with full audio.
- Gate 5: run actual video-review-loop against reference and normalized reference-contract, note all deviations, review again after repairs.

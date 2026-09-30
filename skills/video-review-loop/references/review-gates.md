# Strict video review gates

Use these gates after the machine evidence pass.

The objective is not to find reasons to polish forever. The objective is to catch defects that survive still-frame review.

## Gate 1: frame integrity

Inspect:

- first visible frame
- last visible frame
- every machine-reported black interval
- every machine-reported freeze
- one frame before and after every important cut

Hard fail:

- accidental black frame
- one-frame flash
- stale frame from the previous scene
- incomplete first frame
- corrupt or partially rendered frame

## Gate 2: typography integrity

Inspect at full resolution and phone scale.

Hard fail:

- clipped letters
- clipped Arabic dots
- clipped Arabic descenders
- disconnected Arabic shaping
- bidi reversal
- unreadable mixed Arabic and Latin ordering
- text crossing a required safe zone
- glyph fallback
- text appearing before its font is ready

Warning:

- line break changes hierarchy
- phrase reads too slowly for its screen time
- display type becomes body-copy density

## Gate 3: composition continuity

Watch muted.

Look for:

- focal point jumping without narrative reason
- object scale discontinuity
- inconsistent shadow direction
- cutout edge treatment changing between scenes
- negative space collapsing during motion
- off-axis objects that appear to drift accidentally
- scene balance changing only because animation values were not settled

A still can look correct while the path between stills is wrong.

## Gate 4: transition mechanics

Inspect transitions at normal speed, then frame by frame.

Hard fail:

- one-frame flash
- object teleport
- mask reveals the wrong layer
- outgoing scene disappears before the handoff lands
- incoming type appears before its transition carrier
- camera crosses through geometry unintentionally

Warning:

- every transition uses the same timing shape
- transition exists only as decoration
- no visual element carries continuity into the next beat

## Gate 5: motion curves

Inspect starts, overshoot, settle, and exits.

Flag:

- accidental linear movement
- unmotivated bounce
- repeated scale-pop entrances
- visible snapping at keyframe boundaries
- object never settling
- camera drift with no spatial reason
- easing family changing inside one motion system

Do not demand smoothness everywhere. Abrupt motion can be intentional.

## Gate 6: temporal readability

Compare spoken emphasis with visible emphasis.

Hard fail:

- important text exits before it can be read
- text arrives after the VO has already moved on
- CTA appears too briefly to understand
- a scene holds so long that it feels like playback froze

Warning:

- every beat has equal duration
- no contrast between dense and quiet sections
- pause in narration has no visual breathing room

## Gate 7: asset quality

Inspect moving edges, not only static crops.

Flag:

- cutout halos
- mask chatter
- low-resolution stock exposed by scale
- inconsistent grain
- edge sharpening differences
- generated-image artifacts becoming visible during camera movement
- image grade changing accidentally between shots

## Gate 8: audio relationship

Listen with eyes closed for one pass.

Hard fail:

- clipped or distorted narration
- missing word
- audible edit pop
- music hides required speech
- video cut visibly misses an intentional audio hit when sync is part of the design

Warning:

- SFX on every movement
- impact sound on every word
- music intensity competes with the narrative hierarchy

## Gate 9: Arabic motion

For Arabic work, read the Arabic motion reference as well.

Inspect:

- shaping throughout animated states
- dot zones during masks
- punctuation direction
- Arabic and Latin isolation
- vertical crops during rises
- word-level reveals that accidentally expose partial joined forms

Never approve Arabic from a contact sheet alone.

## Gate 10: ending

Inspect CTA, final settle, and muxed tail.

Hard fail:

- final frame changes during the promised hold
- audio cuts before its natural end
- black appears after the CTA unintentionally
- final frame differs across hold frames because random grain is not time-clamped
- required loop has a visible seam

## Phone-scale gate

View the film at approximate phone size.

Ask:

- what is the focal point in one second
- can the important word be read
- does the cutout still read as intentional
- does motion remain clear without audio
- does small supporting text become noise

If the answer is unclear, reduce rather than add.

## Anti-slop pass

Remove effects that do not improve:

- meaning
- hierarchy
- continuity
- material
- emotion
- identity

Common failures:

- card soup
- random parallax
- constant float
- universal spring overshoot
- neon tech glow
- decorative particles
- fake dashboards
- generic AI gradients
- subtitle treatment for narration

## Review completion

A review round is complete only when:

- the actual video was watched with audio
- the actual video was watched muted
- all machine findings were inspected
- important transitions were inspected frame by frame
- Arabic gates ran when applicable
- timecoded visual findings were written
- every hard finding is either fixed in a later render or explicitly accepted by the user

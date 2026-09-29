# Mix and Match eval cases

Use these cases to test discovery, behavior, and anti-derivative discipline.

## Case 1: three supplied references

Prompt:

`I have three motion references. I like the pacing of A, the cutout treatment of B, and the typography of C. Give me an original direction that does not look like a mashup.`

Expected:

- skill should trigger
- references should be decomposed before concepts are proposed
- three concept hypotheses should be considered
- the final direction should identify transformed principles, not copy layouts

## Case 2: references are too similar

Prompt:

`All four references are fast black and white kinetic type reels. Mix them into something fresh for a Saudi event teaser.`

Expected:

- skill should trigger
- it should identify low diversity in the reference pool
- in Hybrid mode it should seek a wildcard from a different discipline if discovery is allowed
- it should not solve novelty by adding random colors or effects

## Case 3: one reference only

Prompt:

`I only have this one reference. Find a couple of unexpected references and build a new visual idea from them.`

Expected:

- Assisted discovery is valid because the user explicitly authorized it
- the original reference should not become the master template
- wildcard provenance should be recorded

## Case 4: hybrid without discovery permission

Prompt:

`Use these two references only. Do not browse for anything else.`

Expected:

- skill should trigger in User curated mode
- no external reference should be added
- the third hypothesis should use a distinct Constraint route instead of requiring a wildcard
- the tool may still create source-balanced gene recipes from the supplied references

## Case 5: pressure to copy

Prompt:

`Take the exact transition from A, the exact layout from B, and the character from C. Change the colors so it is ours.`

Expected:

- skill should not treat color replacement as transformation
- exact distinctive layout, character, and transition sequence should be marked protected
- it should offer principle-level alternatives that preserve the user's communication goal

## Case 6: Arabic motion

Prompt:

`Mix this editorial Arabic title sequence with this paper collage reference and this architecture reference for a vertical Arabic reel.`

Expected:

- skill should trigger
- Arabic typography should remain a first-class motion material
- the selected direction should hand off to motion-director for Arabic and RTL production rules

## Case 7: ordinary reference analysis

Prompt:

`Analyze this one reference and tell me what makes the transitions work.`

Expected:

- mix-and-match should not trigger
- route to ordinary reference analysis under motion-director

## Case 8: final render review

Prompt:

`Here is the final MP4. Review the timing, clipping, and Arabic legibility.`

Expected:

- mix-and-match should not trigger
- route to motion-director review and QA

## Case 9: no meaningful brief

Prompt:

`Here are six random videos. Mix them.`

Expected:

- the skill should ask for the communication job or infer it only when existing project context already establishes it
- it should not generate combinations with no project-specific objective

## Case 10: wildcard becomes decoration

Prompt:

`Use architecture as the wildcard, but just put a building texture behind the motion.`

Expected:

- reject decorative wildcard use
- extract a transferable architectural rule such as threshold, sequence, scale, circulation, or structure

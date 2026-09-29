# Failure lessons

This directory records engineering failures by reusable failure class, including what happened, why it happened, how it was fixed, how the fix was verified, and which invariant now prevents recurrence.

It exists so that a mistake in a motion project is paid for once. The next film, the next contributor, and the next coding agent should find the lesson here before they repeat it.

## How to use it

1. Before starting a film, skim [lessons-index.md](lessons-index.md) and the rules at its end.
2. When something breaks, search here for the symptom first. If a similar class exists, extend that entry instead of starting a new one.
3. When a lesson changes how a skill should work, update the skill as well. The skills in `skills/` are what agents actually load, so a lesson that lives only here is half done.

## Files

| File | Covers |
|---|---|
| [lessons-index.md](lessons-index.md) | One row per lesson, and the rules we now enforce |
| [render-pipeline.md](render-pipeline.md) | Deterministic HTML render, readiness, ffmpeg, end hold, file size |
| [arabic-type-and-layout.md](arabic-type-and-layout.md) | Accidental clipping of Arabic text and how to catch it |
| [composition-and-transitions.md](composition-and-transitions.md) | Colour mixing in crossfades, perspective stacks, camera travel, light cones |
| [testing-and-verification.md](testing-and-verification.md) | Checks that could not fail, diagnosis from thumbnails, red-green proofs, patterns worth reusing |
| [delivery-and-repo-workflow.md](delivery-and-repo-workflow.md) | Docs that claim unshipped files, stale outputs, history rewrites, heavy binaries, channel limits, reviewer triage, environment outages |
| [assets-and-media.md](assets-and-media.md) | Generation credit checks, keying stock cutouts, ASR versus script text |

## Entry format

Each entry states context, what happened, the observable symptom, impact, the wrong assumption, the root cause with a confidence label, why the architecture allowed it, the fix, the verification, a prevention rule, where else the lesson applies, related code and tests, and a status.

Root-cause labels:

- **Confirmed**: reproduced, or the mechanism was observed directly.
- **Strongly indicated**: the evidence points one way, but the cause was not isolated.
- **Unresolved**: only the symptom is known.

Status labels: Resolved, Partially mitigated, Unresolved, Superseded.

## When to update an entry

Update an entry when:

- the same problem reappears
- a deeper root cause is discovered
- an architecture change makes an old lesson wrong
- stronger verification is added
- a previous fix proves incomplete
- a new failure shows that two lessons are one shared class

Keep entries distilled. No raw logs, temporary IDs, secrets, or conversation dumps.

## Source

The first entries come from the Four Steps events film (`projects/four-steps-events/`): a 54-second Arabic 9:16 editorial collage built as a deterministic HTML composition, rendered frame by frame with Playwright and ffmpeg, then taken through a creative-director polish pass and several rounds of automated code review.

The second set comes from the Motion Graphics Skills promo (`projects/mgs-promo/`): a 26.6-second Arabic 9:16 film built as a HyperFrames composition over a supplied Saudi VO, verified with frame-hash determinism checks, a clip audit, a font gate and audio cross-correlation.

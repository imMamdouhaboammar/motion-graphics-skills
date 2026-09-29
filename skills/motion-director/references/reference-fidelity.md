# Reference fidelity and difficulty preservation

A reference can play different roles.

Do not silently choose the easiest role.

## Reference modes

### Structural fidelity

Use when the user says things like:

- make it like this
- match this motion language
- use this as the benchmark
- I want to test how close the system can get
- take the hard route
- preserve what makes this difficult

The output may use different copy, brand assets, language, and protected specifics, but it must preserve the reference's signature mechanics and production challenge.

### Translation

Use when the user wants the same motion grammar translated into another brand, language, aspect ratio, or message.

Preserve mechanics. Translate surfaces.

### Inspiration

Use only when the user asks for inspiration, principles, mood, or a loose direction.

This mode permits larger structural changes.

### Mix

Use when multiple references must be recombined into a new system.

Route to `mix-and-match` when installed.

## Default interpretation

When the user supplies one clear reference and asks to make something "like it", default to `structural-fidelity`.

Do not downgrade to `inspiration` just because the reference is difficult.

When the user's goal is explicitly to test the system's capability, set:

```json
{
  "reference_mode": "structural-fidelity",
  "difficulty_mode": "preserve"
}
```

## The fidelity contract

Before writing `MOTION.md`, create `reference-contract.json`.

It must describe observable mechanics, not adjectives.

Required signature dimensions:

- rhythm
- composition
- typography
- transitions
- density
- material

Then identify at least two `must_preserve` mechanisms.

In `difficulty_mode: preserve`, also lock salience before choosing an art direction:

- `dominant_language`: what actually dominates the reference across shots
- `secondary_motifs`: visible but supporting motifs that must not become the new film's dominant system
- `may_translate`: surfaces that can change without changing the benchmark
- `forbidden_shortcuts`: easier substitutions that would reduce the reference challenge

This distinction matters because presence is not prominence. A paper texture, tape strip, glow, grid, grain layer, glass panel, or 3D accent may exist in a reference without defining its visual language.

A good preserved mechanism has:

- stable ID
- observable mechanism
- why it is difficult
- how final video evidence will prove it

Example:

```json
{
  "id": "transition-causality",
  "mechanism": "major scene resets grow from an object already active in the outgoing scene",
  "why_hard": "requires cross-scene choreography instead of independent scene cards",
  "evidence": "inspect every major transition frame by frame"
}
```

Validate it:

```bash
python "$MOTION_DIRECTOR_DIR/scripts/reference_fidelity.py" validate reference-contract.json
```

Production does not begin when the contract fails.

## Difficulty preservation

Difficulty is a constraint when the user asked to test capability.

Do not substitute:

- object-led choreography with text cards
- complex masking with a wipe
- cross-scene handoff with independent cuts
- spatial movement with texture
- 3D or perspective logic with flat decoration
- dynamic framing with repeated centered layouts
- real asset integration with abstract placeholders

A simplification is allowed only when:

- the user approves it
- the source runtime makes the mechanism impossible and this is proven
- accessibility or delivery constraints require it

Record the reason.

"Faster" and "easier to implement" are not sufficient.

## Direction gate and salience lock

Before full production, the chosen direction must include a `visual_direction` block.

Example:

```json
{
  "visual_direction": {
    "dominant_language": "large cropped object-led scenes alternating between complete light and dark worlds",
    "preserves": [
      "world-flips",
      "object-scale",
      "transition-causality"
    ],
    "promoted_secondary_motifs": [],
    "new_dominant_motifs": [],
    "user_approved_style_expansion": false
  }
}
```

In preserve mode:

- every `must_preserve` ID must survive into the selected direction, not only the implementation details
- `promoted_secondary_motifs` must stay empty unless the user explicitly approves changing the reference hierarchy
- a new dominant visual system requires explicit user approval
- an attractive reinterpretation is not a substitute for the requested benchmark

### Salience inversion

A salience inversion happens when a secondary detail from the reference becomes the dominant visual language of the output.

Example failure:

```text
reference:
huge cropped objects + hard cream/black resets + causal circular masks
supporting details:
paper texture + tape + grain + print furniture

output:
paper desk + sheets + tape + grain become the entire film
```

This is not faithful translation even though every material existed somewhere in the source.

When challenge mode is active, reject the direction before full build.

## Implementation map

Before full production, map every preserved mechanism to an implementation.

Example:

```json
{
  "implementations": [
    {
      "contract_id": "transition-causality",
      "implementation": "the outgoing playhead expands into the mask that reveals the next scene",
      "verification": "transition frame audit"
    }
  ]
}
```

Validate contract and plan together:

```bash
python "$MOTION_DIRECTOR_DIR/scripts/reference_fidelity.py" validate \
  reference-contract.json \
  --plan reference-implementation.json
```

If one preserved mechanism is unmapped, stop.

## Do not let the brief rewrite the benchmark

The creative brief may adapt the content.

It must not quietly redefine the reference.

Bad sequence:

```text
reference says:
large isolated objects + world flips + causal resets

brief becomes:
tactile paper desk + grain + cards

production:
beautiful paper collage
```

The implementation can be attractive and still fail the assignment.


The same rule applies to opening studies. In challenge mode, do not select a study mainly because it is original, easy to read, fast to build, or aesthetically pleasant. Reference-mechanic coverage and difficulty preservation are the first selection criteria. Phone readability and originality are secondary gates after fidelity survives.

When fidelity is required, the brief must cite the contract rather than replacing it.

## Surface change versus structural change

Usually safe to translate:

- copy
- language
- brand accent
- specific photographed object
- logo
- product
- legal-safe substitute asset

Requires explicit justification in structural-fidelity mode:

- shot rhythm
- focal-object scale
- transition family
- typography entrance mechanic
- density curve
- camera or spatial behavior
- scene-world alternation
- ending structure

## Final review

Run `video-review-loop` with both reference and output when possible:

```bash
python "$VIDEO_REVIEW_SKILL_DIR/scripts/review_video.py" review final.mp4 \
  --reference reference.mp4 \
  --reference-contract reference-contract.json
```

The generated paired contact sheet is not final proof.

Watch both videos.

Compare each `must_preserve` mechanism in motion.

If the output chose a noticeably easier mechanism, mark the fidelity gate failed even if the frame looks polished.

## Hard rule

A good-looking deviation is still a deviation.

When structural fidelity and difficulty preservation are active, success means the new film solves the new message while retaining the hard motion grammar that made the reference worth choosing.

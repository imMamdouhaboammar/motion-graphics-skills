---
name: video-review-loop
description: Use when a rendered motion video, MP4, MOV, reel, promo, title sequence, or final export must be reviewed from recorded video evidence before signoff. Detect technical and temporal defects with FFprobe and FFmpeg, package timecoded evidence, then require an agent visual pass on the actual film. Do NOT use for still-only design review, source-code linting, or UI interaction testing.
---

# Video Review Loop

A rendered film is the product.

This skill reviews the video artifact itself and packages evidence that can be checked again after fixes.

It is inspired by the evidence-round principle used by `amElnagdy/ui-review-loop`: review recorded behavior instead of trusting isolated screenshots. This implementation is motion-specific and does not copy the browser recorder.

## What this skill owns

Use it for:

- final render review
- existing MP4 or MOV review
- pre-delivery technical gate
- timecoded motion defects
- black or frozen interval detection
- audio and video drift
- unexpected silence or clipping risk
- end-hold verification
- evidence contact sheets
- re-review after fixes

It does not replace:

- `motion-director` for creative direction
- source-level geometry audits
- Arabic typography guidance
- brand review
- the renderer
- human or agent judgement of narrative and taste

## Resolve the installed skill directory

Resolve the directory containing this `SKILL.md` and store it as `VIDEO_REVIEW_SKILL_DIR`.

The bundled review tool is:

```bash
python "$VIDEO_REVIEW_SKILL_DIR/scripts/review_video.py"
```

Do not assume the current project contains this repository.

## Review rule

A screenshot can prove one frame.

It cannot prove:

- timing
- pacing
- transition continuity
- flashes
- dropped or frozen time
- audio sync
- end behavior
- whether a defect appears only while moving

Final signoff requires video evidence.

When structural fidelity is active, final signoff also requires direct reference-versus-output comparison. Do not approve from a rewritten brief alone.

## Start a review round

From the project containing the rendered film:

```bash
python "$VIDEO_REVIEW_SKILL_DIR/scripts/review_video.py" review final.mp4 \
  --expect-width 1080 \
  --expect-height 1920 \
  --expect-fps 25 \
  --expect-audio
```

When the film was built against a benchmark reference, include both the source reference and the validated fidelity contract:

```bash
python "$VIDEO_REVIEW_SKILL_DIR/scripts/review_video.py" review final.mp4 \
  --reference reference.mp4 \
  --reference-contract reference-contract.json
```

This creates paired reference-versus-output evidence and inserts every required preserved mechanism into the review checklist.

A polished video can still fail when it chooses an easier motion grammar than the benchmark.

Heavy review defaults to GPU-required execution.

If the environment truly has no supported GPU and CPU work is explicitly acceptable:

```bash
python "$VIDEO_REVIEW_SKILL_DIR/scripts/review_video.py" review final.mp4 \
  --allow-cpu
```

Never add `--allow-cpu` merely to make a blocked run continue.

After the base round returns its `round_dir`, run the strict frame-level signal audit:

```bash
python "$VIDEO_REVIEW_SKILL_DIR/scripts/strict_video_signals.py" final.mp4 \
  --output "$ROUND_DIR/strict-signals.json"
```

This surfaces one-frame luma flashes and extreme frame-to-frame brightness changes that contact sheets can miss. These are review candidates, not automatic creative failures. Inspect every candidate on the actual video.

## Evidence package

A review round lives under:

```text
.motion-review/rounds/<round-id>/
```

The tool creates or attempts to create:

- `manifest.json`
- `technical.json`
- `findings.json`
- `strict-signals.json` after the strict temporal pass
- `review.md`
- `visual-findings.json` after timecoded visual review starts
- `review-state.json` after the visual pass is attested
- `evidence/contact-sheet.jpg`
- `evidence/waveform.png` when audio exists
- sampled scene frames
- machine analysis logs

The source video is not copied into the round by default.

`.motion-review/` is private local evidence and receives its own `.gitignore`.

Do not commit review rounds unless the user explicitly asks.

## Severity model

### Hard

A factual delivery contract failed.

Examples:

- wrong dimensions
- wrong required frame rate
- required audio missing
- video duration outside an explicit tolerance
- audio and video duration drift beyond the hard threshold
- required end hold is not proven

A hard finding blocks signoff.

### Warning

Machine evidence is suspicious and requires visual confirmation.

Examples:

- black interval
- mid-film frozen interval
- long silence
- clipping risk
- variable-frame-rate signal
- analysis pass failure

A warning is not automatically a defect.

### Review

The machine cannot decide.

Examples:

- weak visual hierarchy
- ugly crop
- bad Arabic shaping
- wrong creative emphasis
- awkward easing
- generic transition
- poor brand fit
- confusing narrative

Claude must inspect the video.

## Mandatory visual pass

After the tool finishes, review the actual video.

Do all of these:

1. watch the full film once with audio at normal speed
2. watch it again muted
3. inspect the first second densely
4. inspect every important transition
5. inspect every machine warning at its timestamp
6. inspect CTA and final hold
7. inspect the contact sheet at phone scale
8. compare against the approved motion thesis and delivery contract

Do not infer a clean film from a clean machine report.

## Timecoded findings

Do not leave the visual pass as prose only. Record each confirmed defect in the round state:

```bash
python "$VIDEO_REVIEW_SKILL_DIR/scripts/review_round.py" add "$ROUND_DIR" \
  --time "00:04.280" \
  --severity hard \
  --defect "Arabic headline clips at the top edge" \
  --fix "increase the safe area and rerender" \
  --evidence "full playback plus frame inspection"
```

Use `hard`, `warning`, or `review` deliberately.

Each finding needs:

- timestamp or interval
- severity
- observable defect
- responsible layer when known
- fix
- evidence reviewed

Avoid vague notes such as "make it better."

After the required visual pass, attest exactly what was inspected:

```bash
python "$VIDEO_REVIEW_SKILL_DIR/scripts/review_round.py" attest "$ROUND_DIR" \
  --watched-with-audio \
  --watched-muted \
  --first-second-inspected \
  --transitions-inspected \
  --ending-inspected \
  --strict-signals-inspected \
  --reference-compared
```

Omit `--reference-compared` only when no benchmark reference was part of the job.

Pass `--machine-findings-inspected` when machine warnings or findings are recorded for the round.

Check the round before signoff:

```bash
python "$VIDEO_REVIEW_SKILL_DIR/scripts/review_round.py" status "$ROUND_DIR"
```

The status command exits nonzero until the mandatory visual pass is attested and no machine or visual hard finding blocks the round.

## Review rounds

A confirmed defect is resolved by a later rendered artifact.

Use this loop:

```text
round 1
  -> findings
  -> source fix
  -> rerender
  -> round 2
```

Do not mark a finding fixed only because the source code changed.

The new video is the proof.

When a later render proves a visual finding is fixed, resolve it with evidence:

```bash
python "$VIDEO_REVIEW_SKILL_DIR/scripts/review_round.py" resolve "$ROUND_DIR" \
  --id V001 \
  --resolution "fixed in round 2" \
  --later-artifact "round-2/final.mp4" \
  --evidence "headline safe area restored at 00:04.280"
```

A source-code change is not resolution evidence.

After a meaningful first review, allow at most two confirmation rounds unless a hard defect still exists.

## GPU policy

The tool reads the GPU policy bundled with `motion-director`.

Heavy video decode and evidence extraction require a supported GPU path by default.

The policy may select:

- CUDA
- VideoToolbox
- VAAPI
- D3D11VA
- QSV

The exact backend depends on observed runtime capability.

Do not claim GPU acceleration only because the machine contains a GPU. The selected media path must pass runtime verification.

Some analytical FFmpeg filters remain CPU filters. That is allowed when the input decode is hardware assisted where supported and the analysis pass is bounded.

## Objective checks

The tool may prove:

- technical stream metadata
- dimensions
- frame rate contract
- audio presence
- duration contract
- audio and video duration drift
- black intervals
- freeze intervals
- silence intervals
- peak-volume clipping risk
- end-hold evidence

It must not invent certainty about:

- taste
- storytelling
- typography quality
- cultural correctness
- brand fit
- visual originality

## End hold

When a clean end hold is required, pass its minimum duration:

```bash
--expect-end-hold 1.0
```

The tool checks for tail freeze evidence near the actual video end.

A static ending can be correct.

A frozen frame in the middle of a transition is different.

Interpret evidence in context.

## Failure behavior

If FFprobe is missing, stop.

If FFmpeg is missing, stop before claiming visual evidence was generated.

If GPU is required and no supported path is available, stop.

If an analysis filter fails, record that failure as evidence instead of silently dropping the check.

If the video cannot be decoded, the round fails.

## Return to Motion Director

For broad film work, return:

- round path
- technical result
- hard findings
- warnings
- timecoded visual findings
- unresolved risks
- pass or fail recommendation

`motion-director` owns the final decision and the next production action.


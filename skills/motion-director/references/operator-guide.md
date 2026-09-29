# Claude operator guide

This guide tells the coding agent how to operate the motion pack as one production system.

The pack is not a menu of prompts. `motion-director` owns the job, the router selects bounded specialists, HyperFrames owns reusable production infrastructure where it fits, GPU gates protect heavy execution, and `video-review-loop` reviews the rendered artifact before signoff.

## 1. Start every serious motion job here

Read, in order:

1. the user's exact brief and supplied assets
2. `skills/motion-director/SKILL.md`
3. this operator guide
4. `brand.md` and `MOTION.md` when present
5. the returned route from `route_motion.py`
6. only the specialist skills and references selected by that route

Do not preload every skill. Do not let a specialist silently replace the director.

## 2. Compile the task into a route

Create a small `motion-route.json` before broad production work.

Example:

```json
{
  "deliverable": "broad-film",
  "brand_ready": true,
  "reference_count": 1,
  "reference_mode": "structural-fidelity",
  "difficulty_mode": "preserve",
  "mix_references": false,
  "language": "ar",
  "heavy_media": true,
  "hang_prone": true,
  "final_video": false
}
```

Then run:

```bash
python "$MOTION_DIRECTOR_DIR/scripts/route_motion.py" --context motion-route.json
```

Keep the JSON result as the production route. Every hop must have a reason, inherited truth, and a return contract.

If the router returns `"status": "blocked"`, stop. A required capability is missing. Do not silently replace a fidelity gate, GPU gate, or final review gate with an easier path.

Re-route only when evidence changes the job, not because another effect looks easier.

## 3. Challenge mode means preserve the hard part

When the user says the goal is to test the system, match a difficult reference, avoid the easy route, stay close to the reference grammar, or preserve its ambition:

- set `reference_mode` to `structural-fidelity`
- set `difficulty_mode` to `preserve`
- build a reference contract before implementation
- run the reference-fidelity gate
- map every preserved mechanism into the implementation plan

Validate the contract:

```bash
python "$MOTION_DIRECTOR_DIR/scripts/reference_fidelity.py" validate reference-contract.json
```

Then validate the implementation mapping:

```bash
python "$MOTION_DIRECTOR_DIR/scripts/reference_fidelity.py" validate reference-contract.json \
  --plan implementation-plan.json
```

Do not continue while the gate fails.

Before choosing an opening study or art direction, apply the salience lock:

- identify the reference's dominant visual language
- identify secondary motifs that are present but not dominant
- require the selected direction to preserve every hard mechanism
- reject any direction that promotes a secondary motif into the dominant system
- reject any new dominant visual language unless the user explicitly approved that expansion

This matters even when the new direction looks good. A reference can contain paper, grain, tape, glow, grids, glass, or other furniture without those details being the thing the user asked you to match.

Surface styling is not fidelity. Paper texture, grain, glow, glass, gradients, collage, 3D, or any other familiar treatment cannot substitute for the reference's actual rhythm, composition, transition causality, object scale, depth logic, typography behavior, and density curve.

If the reference is technically or compositionally difficult, difficulty is part of the contract unless the user explicitly allows simplification.

## 4. Use the smallest correct specialist

`motion-director` keeps shared truth. A specialist receives only the bounded problem it owns.

Examples:

- missing brand truth -> `brand-intake`
- brief only -> `motion-brief-writer`
- chart-first scene -> `animated-chart`
- one named effect -> `motion-effects`
- short true-3D title -> `title-sequence-3d`
- multiple references that must become a new direction -> `mix-and-match` when installed
- final rendered video -> `video-review-loop`

The specialist returns decisions, artifacts, risks, and the next required gate to `motion-director`.

Do not ask a specialist to rediscover facts already established upstream.

## 5. HyperFrames owns reusable production machinery

For a greenfield code-driven film, use HyperFrames as the production runtime when compatible.

Before hand-building infrastructure:

1. inspect the current project
2. inspect the selected specialist
3. inspect HyperFrames router and registry
4. reuse a supported block, adapter, timeline, preview, audio, or render path
5. write custom infrastructure only for a proven gap

Do not reimplement a renderer, registry, media resolver, audio mixer, or deterministic timeline that already exists.

Preserve a stable existing runtime when the user asked for refinement and migration does not fix a measured problem.

## 6. GPU execution is three separate claims

Never say "GPU is being used" as one vague statement.

### Browser rasterization

For browser-rendered motion, run:

```bash
node "$MOTION_DIRECTOR_DIR/scripts/browser_gpu_probe.cjs"
```

The probe must report a hardware renderer, not SwiftShader, llvmpipe, lavapipe, or another software path.

### Media decode

Before heavy FFmpeg analysis or decode:

```bash
python "$MOTION_DIRECTOR_DIR/scripts/gpu_policy.py" probe --require
```

The selected backend must be verified against the actual media before claiming accelerated decode.

### Final video encode

Before a heavy final encode:

```bash
python "$MOTION_DIRECTOR_DIR/scripts/gpu_policy.py" probe --require --require-encode
```

Use the returned `video_encoder` and `encoder_args` when the active renderer permits an explicit FFmpeg encoder.

Typical hardware encoders include:

- Apple: `h264_videotoolbox`
- NVIDIA: `h264_nvenc`
- Intel Quick Sync: `h264_qsv`
- VAAPI: `h264_vaapi`

Do not silently fall back to libx264 or another CPU encoder for a heavy render.

If the active runtime does not expose encoder control, record that limitation and use its supported hardware path if documented. If no verified GPU path exists, block the heavy run unless the user explicitly permits CPU fallback.

`--allow-cpu` is an explicit exception, not a convenience flag.

## 7. Keep heavy commands bounded

If `work-guard` is installed, put hang-prone preview, browser, audit, and render commands behind it.

The guard may repair process state. It may not silently edit source code, publish, or retry unsafe commands.

If the guard is unavailable, use explicit timeouts, preserve logs, and do not retry destructive work automatically.

## 8. Review the video, not only the code

A clean build is not a clean film.

After each candidate final render:

```bash
python "$VIDEO_REVIEW_SKILL_DIR/scripts/review_video.py" review final.mp4 \
  --expect-width 1080 \
  --expect-height 1920 \
  --expect-fps 30 \
  --expect-audio
```

Use the returned `round_dir` for the strict temporal audit:

```bash
python "$VIDEO_REVIEW_SKILL_DIR/scripts/strict_video_signals.py" final.mp4 \
  --output "$ROUND_DIR/strict-signals.json"
```

Then inspect the actual playback with audio and muted, inspect the first second densely, inspect all important transitions frame by frame, inspect every strict-signal candidate, inspect the CTA and ending, and compare the result against the approved motion thesis and reference contract.

Record confirmed visual defects with `review_round.py add`. When attesting the visual pass, include `--strict-signals-inspected` after inspecting every candidate in `strict-signals.json`, and include `--reference-compared` whenever a benchmark reference exists. Then run `review_round.py status` before signoff.

Machine findings are evidence, not taste.

A confirmed defect is closed only by a later rendered artifact and a `review_round.py resolve` entry that points to that later video.

Never mark a video complete because screenshots look fine.

## 9. The anti-shortcut rule

When a difficult reference is supplied, do not choose the easiest visual language the agent already knows.

Before committing to a direction, ask:

- Did the output preserve the reference's signature mechanics or only its mood?
- Did scene construction become simpler than the reference without permission?
- Did a difficult object-led or spatial system collapse into text cards, paper, grain, generic wipes, or repeated panels?
- Did transition causality become decorative transitions?
- Did the density curve flatten into one repeated scene template?
- Did the renderer or available component library start deciding the art direction?
- Did a supporting motif from the reference become the dominant visual system in the output?
- Did the selected opening study win on originality or ease while preserving fewer reference mechanics than another candidate?

If any answer indicates collapse, stop and revise the plan before producing the full film.

## 10. Signoff contract

A broad motion job is ready for signoff only when all applicable gates have evidence:

- truth and brand constraints established
- route compiled and followed
- reference-fidelity gate passed when challenge mode applies
- GPU path verified for heavy work
- runtime validation passed
- final video reviewed as video evidence
- every hard review finding resolved in a later render or explicitly accepted by the user
- final file metadata matches the delivery contract

The rendered film is the product. Source code is only one part of the evidence.

# Neural Routing, GPU Policy, and Video Review Design

## Goal

Turn the motion graphics pack from a flat collection of skills into a coordinated production system.

The system adds four capabilities:

1. typed neural links between `motion-director` and specialist skills
2. a dynamic, inspectable router that builds the production path from task context and installed capabilities
3. an evidence-based video review loop that reviews the rendered film itself, not screenshots alone
4. a GPU-first execution policy for heavy media and browser rendering work

The existing skills remain usable on their own. `motion-director` becomes the orchestration entry point.

## Architecture

```text
user brief
   |
   v
motion-director
   |
   +--> route_motion.py
            |
            +--> installed skill discovery
            +--> skill-network.json
            +--> task context
            |
            v
      ordered route + handoff contracts
            |
            +--> brand intake / creative / specialist skills
            +--> GPU preflight for heavy stages
            +--> render
            +--> video-review-loop
            +--> fix and repeat review when hard findings remain
            |
            v
         handoff
```

## Neural links

The term neural link means a typed handoff relationship, not hidden model state.

Every link has:

- source node
- destination node
- relationship
- trigger
- payload passed forward
- expected output
- return target

Supported relationships:

- `prepares`: creates truth or constraints used later
- `specializes`: handles a narrow creative or production problem
- `augments`: adds a capability without owning the whole film
- `reviews`: inspects an artifact produced by another node
- `returns`: sends the result back to the director
- `fallback`: used only when a preferred capability is unavailable

The network lives in:

`skills/motion-director/router/skill-network.json`

The graph may mention optional capabilities that are not installed yet. The router must mark them unavailable rather than failing the whole route.

This allows pending skills such as `mix-and-match` and the work guard from a separate PR to join the network automatically after installation.

## Handoff packet

Every route stage gets a small contract:

```json
{
  "from": "motion-director",
  "to": "launch-video",
  "purpose": "shape the short product launch structure",
  "inherits": [
    "approved copy",
    "brand truth",
    "motion thesis",
    "reference constraints"
  ],
  "must_return": [
    "scene structure",
    "beat decisions",
    "specialist risks"
  ],
  "return_to": "motion-director"
}
```

Specialists receive project truth. They do not restart discovery or silently replace approved constraints.

## Dynamic router

Create:

`skills/motion-director/scripts/route_motion.py`

The router accepts a JSON context file plus an optional task description.

Example context:

```json
{
  "deliverable": "short-branded-film",
  "language": "ar",
  "brand_ready": false,
  "reference_count": 3,
  "mix_references": true,
  "has_final_audio": true,
  "needs_3d": false,
  "review_only": false,
  "heavy_media": true
}
```

It produces plain JSON with:

- detected installed capabilities
- primary owner
- ordered stages
- optional skipped capabilities
- GPU requirements
- review requirements
- typed handoff packet for every stage
- reason for every route decision

The router is deterministic. It does not call another LLM.

Claude performs semantic classification. The router validates and composes the route.

### Core routing rules

- `motion-director` always owns broad film work
- missing brand truth adds `brand-intake`
- brief-only work routes to `motion-brief-writer`
- known deliverable classes route to the matching specialist
- multi-reference recombination requests prefer `mix-and-match` when installed
- final rendered film or review tasks add `video-review-loop`
- Arabic work adds the Arabic motion reference as a director requirement
- heavy media adds GPU preflight
- hang-prone stages add the work guard only when it is installed
- every specialist returns to `motion-director` unless the request explicitly asks only for that specialist artifact

## Video review loop

Add a specialist skill:

`skills/video-review-loop/SKILL.md`

The workflow is inspired by the evidence-round principle in `amElnagdy/ui-review-loop`, not its browser recorder implementation.

The motion review loop operates on a rendered video file.

One review round creates a private local package under:

`.motion-review/rounds/<round-id>/`

Artifacts:

- `manifest.json`
- `technical.json`
- `findings.json`
- `review.md`
- `evidence/contact-sheet.jpg`
- `evidence/waveform.png` when audio exists
- machine logs
- sampled frame evidence
- scene-transition evidence when available

Do not copy the entire source video into the package by default. Record its path, size, modification time, and optional hash.

Add `.motion-review/` to the project gitignore when possible. Never commit review evidence by default.

### Review tool

Create:

`skills/video-review-loop/scripts/review_video.py`

The tool uses FFprobe and FFmpeg already available in the environment. It adds no Python package dependency.

It performs objective checks where machine evidence is meaningful:

- dimensions and aspect ratio
- frame rate and variable-frame-rate signals
- codec and pixel format
- color metadata
- video and audio duration drift
- missing expected audio
- black intervals
- frozen intervals
- unexpected silence
- audio peak / clipping risk
- end-hold evidence when requested
- contact-sheet generation
- scene-change samples
- first and last frame evidence

The tool must distinguish:

- `hard`: factual delivery failure
- `warning`: suspicious machine evidence requiring visual confirmation
- `review`: questions only a visual review can decide

It must not pretend to infer typography quality, cultural correctness, brand fit, or narrative clarity from numeric filters.

Those require the agent to inspect the actual video and evidence package.

### Mandatory agent review

After the tool runs, Claude must review:

1. the full video once at normal speed with audio
2. the full video once muted
3. every machine finding at frame or short-segment level
4. first second densely
5. every important transition
6. CTA and ending
7. contact sheet at phone scale

The agent writes timecoded findings into `review.md`.

A screenshot alone is not sufficient evidence for final signoff.

### Review rounds

A hard or confirmed visual defect requires:

```text
round N
  -> findings
  -> fix
  -> render
  -> round N+1
```

A finding is resolved only by a later rendered artifact, not by editing the report.

The default maximum is two confirmation rounds after the first meaningful review, unless a hard defect remains.

## GPU-first policy

Create:

`skills/motion-director/scripts/gpu_policy.py`

Heavy media work must preflight hardware acceleration before execution.

The policy detects:

- operating system
- FFmpeg hardware acceleration backends
- NVIDIA availability when `nvidia-smi` exists
- VAAPI device availability on Linux
- VideoToolbox capability on macOS
- common software-only fallback signatures

The output is plain JSON.

For heavy work, the default mode is `require`.

If no usable GPU path is found, the tool exits nonzero and Claude must not silently fall back to CPU.

CPU fallback is allowed only with an explicit `--allow-cpu` flag or a user constraint that requires it.

### Scope of GPU enforcement

GPU-first applies to:

- final rendering when the selected runtime supports GPU rendering
- video decoding for review and frame extraction when FFmpeg hardware decode is supported
- browser/WebGL rendering when a hardware renderer is available
- transcoding or proxy generation when a hardware encoder is available and output requirements permit it

GPU-first does not mean every filter executes on the GPU.

Some analytical FFmpeg filters are CPU filters. The review tool may use them on sampled or bounded passes after GPU-assisted decode when possible.

Never claim a step was GPU accelerated without evidence from the selected backend or runtime.

## Browser GPU verification

The guide must require hardware-renderer verification for browser-rendered motion.

Software renderers such as SwiftShader or llvmpipe do not count as GPU acceleration.

The initial implementation may expose the policy and launch guidance without creating a second browser orchestration framework.

Use existing HyperFrames or Playwright launch controls where they already exist.

## Claude operator guide

Create:

`docs/CLAUDE_MOTION_GUIDE.md`

It is the first operational guide for agents using the pack.

The guide defines:

1. resolve the installed pack directory
2. read `motion-director`
3. classify the task into router context
4. run the router
5. read only the skills and references selected by the route
6. keep one shared truth set across handoffs
7. run GPU preflight before heavy work
8. use the work guard when available for hang-prone commands
9. render
10. run the video review loop
11. fix confirmed defects
12. rerender and review again
13. ship only after technical and visual gates pass

The guide must include short examples for:

- short Arabic promo with references and VO
- data-driven explainer
- one named motion effect
- review-only request on an existing MP4

## Integration with pending PRs

This PR is based on `main`.

It must not depend on unmerged code from other PRs.

The graph may define these as optional:

- `mix-and-match`
- work guard capability under `motion-director`

If absent, the router states the fallback.

If present after later merges, the router discovers them automatically.

## Testing

### Router

Tests cover:

- broad film ownership
- missing brand truth
- specialist selection
- Arabic reference requirement
- optional mix-and-match absent and present
- final video adds review loop
- heavy media adds GPU preflight
- deterministic output
- no duplicate stages

### GPU policy

Tests cover pure backend selection without depending on CI hardware:

- CUDA preferred when verified signals exist
- VideoToolbox on macOS
- VAAPI on Linux
- software-only environment rejected in require mode
- explicit CPU fallback
- no unsupported backend invented

### Video review

Tests cover parsers and review contract:

- ffprobe metadata parsing
- duration drift
- black interval parsing
- freeze interval parsing
- silence parsing
- clipping-risk parsing
- severity classification
- evidence package paths
- CPU fallback denied by default when GPU is required
- malformed FFmpeg output does not crash the report

CI may use fake command outputs for deterministic tests. Real FFmpeg integration remains a runtime preflight.

## Non-goals

- no hidden model-to-model messaging
- no autonomous multi-agent daemon
- no vector database
- no new ML model dependency
- no replacement for HyperFrames
- no claim that numeric video metrics can replace human visual judgement
- no silent CPU fallback for heavy work
- no copy of `ui-review-loop` code

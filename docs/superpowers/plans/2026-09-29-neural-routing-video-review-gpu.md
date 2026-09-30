# Neural Routing, GPU Policy, and Video Review Implementation Plan

**Goal:** Add a typed skill graph, deterministic router, GPU-first execution policy, evidence-based video review loop, and Claude operator guide without depending on pending PRs.

**Architecture:** `motion-director` remains the orchestration owner. A JSON skill graph describes typed handoffs. A Python router composes the route from task context plus installed capabilities. A GPU policy tool gates heavy execution. A separate video-review specialist packages objective FFmpeg evidence and requires an agent visual pass before signoff.

**Tech:** Python standard library, JSON, existing FFmpeg/FFprobe runtime tools, markdown skills and references.

## Task 1: Skill graph and router

- Add `skills/motion-director/router/skill-network.json`
- Add router tests first
- Implement installed-skill discovery and deterministic route composition
- Include optional nodes for pending capabilities
- Verify no duplicate stages and explain every decision

## Task 2: GPU policy

- Add GPU policy tests first
- Implement pure backend selection plus runtime probe CLI
- Default heavy mode to require GPU
- Require explicit CPU fallback
- Return machine-readable execution hints

## Task 3: Video review specialist and tool

- Add `skills/video-review-loop/SKILL.md`
- Add references for review gates and evidence format
- Add parser and packaging tests first
- Implement FFprobe/FFmpeg evidence collection
- Use the GPU policy before heavy decode or extraction
- Create review package and machine findings
- Keep aesthetic judgement in the agent review protocol

## Task 4: Neural handoff guidance

- Add typed handoff rules to `motion-director`
- Add `references/neural-links.md`
- Route every specialist result back to the director for broad film work
- Keep specialist standalone behavior for narrow requests

## Task 5: Claude operator guide

- Add `docs/CLAUDE_MOTION_GUIDE.md`
- Include route examples
- Include GPU and review requirements
- Include optional work-guard and mix-and-match behavior

## Task 6: Validation and PR

- Update CI with router, GPU policy, and video review tests
- Run skill validation
- Run correctness review
- Run Ponytail over-engineering review
- Open the PR only after targeted red/green evidence exists

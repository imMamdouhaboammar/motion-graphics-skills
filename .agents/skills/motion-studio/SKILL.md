---
name: motion-studio
description: Master operating system and coordinator for Claude Code Motion Studios. Use when starting a motion graphics project, choosing a specialist from this studio, guiding onboarding, checking director gates, or managing the production lifecycle from concept to delivery.
---

# Claude Code Motion Studios: Master Studio Orchestrator

The unified coordinator for code-driven motion graphics, animation, and video production. Organizes creative roles, tracks production stages, enforces director gates, and routes tasks to specialized craft agents.

## Studio Stage Lifecycle

Every production progresses through six discrete stages tracked in `studio.yaml`:

```
1. Concept       -> Narrative hook, core premise, audience, and creative brief
2. Storyboard    -> Second-by-second beat sheet locked to voiceover audio
3. Animatic      -> 3-second vertical slice or grey clay preview proving motion
4. Audio Lock    -> Voice, music bed, and tactile foley mastered to -14 LUFS
5. Production    -> Full scene choreography across chosen rendering engines
6. Delivery      -> Director gate sign-off, safe zone proof, 16:9 and 9:16 masters
```

## Department Routing Catalog

| Request or Domain | Lead Agent / Skill | Primary Deliverables |
|---|---|---|
| First-time studio onboarding or project setup | `motion-studio` | Guided walkthrough and stage initialization |
| Storyboard and continuous single shot | `continuous-shot-engine` | Unbroken shot beat sheet and light filament path |
| Frame-exact timeline and speech sync | `beat-sheet-director` | Whisper audio timestamps and bar grid sync |
| Clear liquid glass and 2.5D depth planes | `liquid-glass-25d` | SVG displacement filter and talking head depth |
| Physical 3D models and contact shadows | `blender-3d-studio` | Blender MCP clay preview and Cycles beauty render |
| Standard UI animation and data callouts | `canonical-motion-moves` | 10 canonical moves with verified GSAP easing |
| Audio stem balancing and broadcast mastering | `audio-mastering-mixer` | -14 LUFS master and 90-cue tactile foley mix |
| Vertical mobile safety and button clearance | `safe-zone-qa` | 9:16 re-layout and overlay collision proof |
| Headless algorithmic rendering in Python | `opencv-fast-renderer` | NumPy and OpenCV 2.5D video rendering |
| Transparent overlays for Premiere and DaVinci | `transparent-alpha-export` | ProRes 4444 MOV and PNG sequence export |
| Design tokens, typography, and palette | `motion-bible` | Foundation `motion-bible.md` contract |
| Stage readiness and director sign-offs | `director-gate-check` | Pass or block evaluation across 5 quality gates |

## Director Quality Gates

Before rendering final masters, evaluate the five mandatory director gates:
1. Gate 1 (Creative Director): Immediate hook within first 2 seconds.
2. Gate 2 (Technical Director): Verified local assets with zero network latency dependencies.
3. Gate 3 (Art Director): Motion Bible compliance and anti-slop visual standards.
4. Gate 4 (Audio Director): Master loudness at -14.0 LUFS and true peak under -1.25 dBTP.
5. Gate 5 (Platform QA): Vertical 9:16 safe zone clearance verified with test overlay.

## Studio Command Recipes

- Inspect project status: `bash tools/scripts/studio-state.sh`
- Audit asset dependencies: `bash tools/scripts/asset-scan.sh`
- Verify safe zones: `python3 tools/scripts/safe-zone-verify.py`
- Measure loudness: `python3 tools/scripts/lufs-check.py renders/master.mp4`
- Run director gate audit: `bash tools/scripts/gate-check.sh`

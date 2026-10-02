# ReelMimic orchestration engine

This engine orchestrates analysis and project-provided renderer and independent reviewer processes. Creating the creative storyboard and implementing a renderer for the chosen production engine require a production agent or human. There is no bundled autonomous AI service. Missing adapters or missing artifacts are errors.

The default configuration uses the suite's bundled scripts and style registry, or an installed `.claude/skills` tree when present. Set `REELMIMIC_SCRIPTS` to override the script directory. `run --skills-dir` overrides the skills and associated scripts unless the environment override is set. `run` analyses and routes the reference, then pauses at `AwaitingApproval`. Write and review `STORYBOARD.md` and the machine-readable `plan.json` before continuing:

```bash
reelmimic resume my-project --projects-dir /path/to/projects --approve-storyboard
```

Resuming without `--approve-storyboard` leaves the approval gate paused. `--auto-approve` only approves an existing complete `plan.json`, and cannot invent a plan. `plan.json` is a `Storyboard` object containing `logline`, `colour_arc`, `motif`, `shots`, `required_inputs` and `approved`. Shot entries follow `references/shot-analysis.md`. Approval rejects missing shots, duplicate IDs and unresolved required inputs.

## Project adapters

Place these Python scripts in the project directory:

| Script | Arguments | Required output |
| --- | --- | --- |
| `render_segment.py` | `--project`, `--plan`, `--segment`, `--engine`, `--shot-ids` (comma-separated), `--frames`, optional `--fixes` | Fresh contiguous PNG sequence from `frame_000001.png` at 24 FPS |
| `review_segment.py` | `--project`, `--plan`, `--segment`, `--frames` | ReviewResult JSON on stdout |
| `review_final.py` | `--project`, `--plan`, `--video` | ReviewResult JSON on stdout |

Render adapters call the chosen engine's actual renderer. Review adapters run independently and inspect frames against the reference and approved plan. Diagnostic messages go to stderr. A ReviewResult has this shape:

```json
{"passed": false, "score": 2.0, "failures": [{"category": "camera", "item": "Reference push-in is missing", "severity": "Critical"}]}
```

Approval requires `passed`, a finite score at least 4 and no `Critical` failures. Failed reviews are supplied to the renderer via `--fixes`, up to the configured number of fix rounds. Each retry removes the segment's old frames. Renderer failures propagate after all active tasks finish. Failed QA blocks assembly. Approved segment sequences are concatenated in storyboard order, must total the requested duration at 24 FPS, and are decoded before assembly. Final completion requires a separately executed final review.

## Runnable smoke example

`examples/smoke-project` contains real FFmpeg test-card rendering and independent technical checks. These adapters verify the transport and video artifacts only. They do not assess style matching or creative quality and must be replaced for production.

The integration smoke test creates a complete one-second approved plan, resumes from a custom project directory, runs these adapters, assembles the frames with FFmpeg and checks `final.mp4` and the persisted `Complete` state:

```bash
cargo test --test regressions real_renderer_review_assembly_and_custom_resume -- --nocapture
```

Python 3, FFmpeg and FFprobe must be installed for this test.

---
name: video-style-cloner
description: >
  Style-cloning video director for AI agents. Give it a reference video (local
  file, screen recording, or YouTube/URL) and a one-line brief, and it
  autonomously: analyses editing rhythm, shot lengths, BPM, transitions, colour
  palette and camera moves, selects the matching 2D production style, writes a
  shot-by-shot storyboard, dispatches parallel production sub-agents, reviews
  every shot with an independent reviewer agent, assembles and exports the final
  MP4, and iterates on user feedback. Use when the user says "make a video like
  this", "clone this style", "video in the same style", "mimic this video",
  "i want something like X but about Y", "create a video inspired by", or
  provides a video URL/file and asks for a new one.
  Do NOT use for: simple video edits, subtitles-only tasks, or when the user
  has NOT provided a reference video or URL.
version: "1.0.0"
author: "Mamdouh Aboammar (adapted from edenfunf/reelmimic)"
license: MIT
source: "https://github.com/edenfunf/reelmimic"
hosts:
  - antigravity
  - claude
  - codex
  - cursor
  - gemini
  - universal
tags:
  - video
  - style-clone
  - animation
  - multi-agent
  - content-creation
  - motion-graphics
  - hyperframes
  - ffmpeg
---

<!--
  ╔═══════════════════════════════════════════════════════════╗
  ║              VIDEO STYLE CLONER: AGENTIC SKILL           ║
  ║  Adapted from edenfunf/reelmimic (MIT)                    ║
  ║  Skillified by Mamdouh Aboammar for universal agents      ║
  ╚═══════════════════════════════════════════════════════════╝
-->

# Video Style Cloner

> Show an AI agent a video you love. Get a new video in the same style.
> The host agent analyses, plans, produces and reviews using the available tools. Production requires an approved storyboard and an installed renderer.

$$\text{Reference Video} \xrightarrow{\text{Phase 1: Analyse}} \text{Style DNA} \xrightarrow{\text{Phase 2: Plan}} \text{Storyboard} \xrightarrow{\text{Phase 3: Produce}} \text{Multi-agent Shots} \xrightarrow{\text{Phase 4: Review}} \text{Final MP4}$$

---

## When to activate

**Activate on:**
- "make a video like this / in this style"
- "clone this video's style"
- "create something similar to [URL or file]"
- "video inspired by / based on the style of"
- user provides video + a creative brief for new content
- "mimic / copy the aesthetic / editing rhythm of this video"

**Do NOT activate on:**
- Simple video trim or subtitle requests → use general-video skill
- No reference video provided → ask for one first
- 3D rendering requests → skill handles only 2D, explain and proceed with nearest 2D style

---

## Absolute Rules (inherited from source)

1. **Style only - no assets**: Learn technique from reference, never copy footage, characters, logos, or licensed music.
2. **2D only**: Current track supports 2D animation styles only. If reference is 3D or live-action, reproduce rhythm/composition/mood in closest 2D style and inform the user.
3. **User-provided lyrics**: Never transcribe, invent, or quote song lyrics. Only use text the user explicitly provides.
4. **Evidence-gated fixes**: Every "fixed" shot must include before/after frame comparison. A reviewer validates the evidence before accepting the fix.
5. **Human approval gate**: Storyboard/plan must be approved before production starts (unless user explicitly said "just do it" or "decide yourself").
6. **Asset attribution**: Log every fetched asset (source, author, licence) in `ASSETS.md`. Unknown licence → flag "Licence unconfirmed".

---

Set `SKILL_DIR` to the absolute path of this `video-style-cloner` directory before running commands. Engine entry points are named `skills/<engine>/<engine>.md`.

The optional Rust CLI coordinates project-provided render/review adapters. It does not generate creative assets or supply an AI reviewer by itself. Read `engine/README.md` before using it. Its technical smoke example proves encoding and approval flow, not visual style fidelity.

## Required Tools / Runtime

Read `references/runtime.md` for version requirements and install commands.

| Tool | Purpose | Min Version |
|---|---|---|
| Python | analyse.py, align_lyrics.py, fetch_assets.py | 3.10+ |
| FFmpeg | Audio/video encoding, frame extraction | 6.0+ |
| yt-dlp | Download YouTube reference (analysis only) | latest |
| Node.js | HyperFrames animation renderer | 22.18+ |
| faster-whisper | Lyrics timestamp alignment | 0.10+ |

---

## Phase 0: Intake

Collect from the user:

| Input | Required | Default |
|---|---|---|
| Reference video | **YES** | None |
| Creative brief (what new video is about) | **YES** | None |
| Target length | No | 30 s |
| Aspect ratio | No | 16:9 |
| Music/audio file | No | Silent or user-provided |
| LRC/lyrics text | No (needed if lyrics appear in video) | None |
| Character design sheets | No | AI-designed original characters |

Create project workspace:
```
projects/<slug>/
├── analysis/          # Output from analyse.py
├── inputs/            # User-provided files (audio, lyrics, design sheets)
├── assets/            # Fetched CC0/CC-BY assets + ASSETS.md log
├── build/             # production.json, rendered frames
├── out/               # Final MP4 output
└── STORYBOARD.md      # Approved plan
```

---

## Phase 1: Analyse Reference

```bash
python "$SKILL_DIR/skills/video-clone/scripts/analyze.py" "<file_or_url>" \
  --out projects/<slug>/analysis
```

This script produces:
- `report.json`: video metadata under `video`, audio measurements under `audio`, editing rhythm under `pacing`, and each shot's nested `camera` and `look` measurements under `shot_details`. Read `references/shot-analysis.md` for the emitted schema.
- `sheet_1fps.jpg`: one frame per second contact sheet
- `sheet_scenes.jpg`: one frame per scene break

**After running**, visually inspect `sheet_1fps.jpg` and `sheet_scenes.jpg` using the Read tool. Then write `analysis/STYLE.md`:

```markdown
# Style Analysis

## Medium (REQUIRED — first line, determines skill routing)
2d-painted | 2d-crayon | 2d-vector | 2d-pixel | 2d-paper | 2d-lineart | 2d-cel

## Shot List
| # | Seconds | Content | Camera Move | Speed | Brightness |
|---|---------|---------|------------|-------|-----------|
...

## Colour Arc
[Describe colour palette evolution across the video]

## Editing Rhythm
- Total shots: X
- Avg shot length: Y s (Z beats)
- Cuts on beat: Yes/No
- Transitions: [list types]

## Narrative Structure
[Hook / conflict / resolution / recurring motifs / how jokes land]

## Typography
[Caption style, size, placement, animation]

## Key Techniques (why this video works)
1. ...
2. ...
3. ...
```

Report the analysis to the user: shot table + 3-5 "why this video works" insights.

---

## Phase 2: Select Style → Route to Production Engine

Read all `styles/*.md` files in this skill directory. Each has frontmatter:
```yaml
engine: <engine-skill-name>
medium: 2d-painted | 2d-cel | 2d-pixel | ...
priority: 1-10
```

**Routing logic (strict order):**
1. Filter to styles whose `medium` matches the reference medium.
2. Score each matching style against `analysis/STYLE.md` identification features.
3. Pick highest score, break ties with `priority`.
4. If no same-medium style exists, pick closest medium, inform user.
5. If user explicitly names a style or tool → use that.
6. If no style fits → use closest engine, create a new `styles/<name>.md` entry afterwards.

Tell the user: "Detected style: X → using engine: Y because [reason]."

Load the engine skill and follow its instructions for production details.

---

## Phase 3: Music (skip if silent)

If the video has music:
1. User must provide the audio file (do not download copyrighted music).
2. Analyse the audio:
   ```bash
   python "$SKILL_DIR/skills/video-clone/scripts/analyze.py" "<audio_file>" \
     --out projects/<slug>/analysis/song
   ```
3. Check `report.json`:
   - `audio.silent: true` → ask user to re-record with system audio
   - `audio.phase_inverted: true` or `audio.noise_floor_db > -45` → warn user about audio quality
4. Trim to target length starting on a beat:
   ```bash
   ffmpeg -ss <start> -t <len> -i audio.wav \
     -af "loudnorm=I=-14:TP=-1.5,afade=t=in:d=0.08,afade=t=out:st=<len-2>:d=2" \
     -c:a aac -b:a 192k assets/clip.m4a
   ```
5. All shot timings in storyboard use **beats**, not seconds. BPM change = re-render timing only.

If user provides lyrics:
```bash
python "$SKILL_DIR/skills/video-clone/scripts/align_lyrics.py" <audio> inputs/lyrics.txt \
  --out analysis/lyrics/subs.lrc
```
Use ONLY user-provided lyric text. Never invent or transcribe lyrics.

---

## Phase 4: Storyboard

Write `projects/<slug>/STORYBOARD.md`:

```markdown
# Storyboard — <project slug>

## Logline
[One sentence: what is this video about]

## World & Colour Arc
[Setting, colour palette evolution: opening → climax → end]

## Motif
[Recurring visual symbol or joke structure]

## Character Arc
[Protagonist emotional journey, if applicable]

## Shot Table
| # | Beats | Transition-In | Event | Reaction | Camera |
|---|-------|--------------|-------|----------|--------|
| 1 | 4     | cut          | ...   | ...      | slow-push, fill=0.6, region=face |
...
```

**Shot-for-shot style cloning (critical):**

Each shot in the storyboard must reference the original:
```json
{
  "shot": 3,
  "ref_shot": 7,
  "ref_what": "slow zoom in on subject with warm backlight",
  "camera": {
    "move": "slow-push",
    "focal": "85mm",
    "fill": 0.6,
    "region": "face",
    "depth_of_field": "shallow",
    "angle_start": 0,
    "angle_end": 3
  }
}
```

Self-check after writing: compare each planned shot against `shot_details` in `report.json`.
- Camera speed must match (ref = slow-push → planned = slow-push, not static)
- Shot ratio of text-only cards must be ±30% of reference
- Average shot length must be ±30% of reference

Present storyboard to user with brief summary. Wait for approval unless user said "decide yourself."

---

## Phase 5: Production Pipeline

**Order is mandatory. Never skip a gate.**

### Gate 0: Required Inputs Checklist
Before production agent starts, list everything only the user can provide:
- Lyrics text (if needed)
- Character design sheets (if using user's IP)
- Product photos (if applicable)

Missing items block production. Write them to `plan.json → required_inputs`. Do not generate placeholders silently.

### Gate 1: Director Setup
Create `build/production.json`:
```json
{
  "segments": [
    {"id": "A", "shots": [1,2,3], "engine": "painted-animation"},
    {"id": "B", "shots": [4,5,6], "engine": "painted-animation"}
  ],
  "shared_assets": {...},
  "character_definitions": {...}
}
```

### Gate 2: Character Approval
1. Production agent renders character sheets: front view, 8+ expressions, 6+ poses.
2. A **fresh independent reviewer agent** (not the production agent) inspects full-resolution crops using this checklist:

**Visual QA Checklist (use on every gate):**
- [ ] All limbs attached, no floating parts
- [ ] Neck present and natural
- [ ] No seams or double-stroke outlines
- [ ] Consistent with character design sheet
- [ ] Uniform line weight
- [ ] No clipping/mesh intersection
- [ ] Subject fills frame appropriately
- [ ] Text is legible
- [ ] No colour banding or flicker
- [ ] Motion has anticipation and follow-through

Fail → return to production agent for fix (max 3 rounds). Pass → proceed.

### Gate 3: Parallel Segment Production + Inline Review
- Up to 6 production agents work simultaneously on different segments.
- Each finished segment immediately goes to a **fresh reviewer agent** (not the same one that made it).
- Reviewer checks every shot's frame sheet, strip, and character crops against Visual QA Checklist.
- Fail → returned to producer for fix, with specific failure reason.
- Fix must include: `fixes.json` entry with before/after full-resolution crops.
- Reviewer validates the before/after before accepting.

### Gate 4: Assembly + Final Review
- Assemble all segments in sequence.
- Final reviewer (fresh agent, not any prior producer or reviewer) checks:
  - [ ] Segment seams are clean
  - [ ] Visual continuity across segments
  - [ ] Rhythm matches reference BPM feel
  - [ ] Subtitle consistency throughout
  - [ ] Every previously-logged "fixed" issue is actually fixed

---

## Phase 6: Output & Feedback Loop

Report to user:
```
✅ Output: projects/<slug>/out/final.mp4
⏱ Duration: XX.Xs | 📐 Resolution: 1920×1080 | 🎬 X shots
Shot summary:
  1. [one sentence]
  ...
⚠️ Known limitations / placeholder sections: [honest list]
```

**Feedback handling:**
- User gives time-coded feedback: "at 0:12 the character looks wrong"
- Extract affected shots only (from `report.json` shot boundaries)
- Re-render only those shots
- Re-run Gate 3 reviewer for changed shots only
- Re-run Gate 4 seam check

---

## Asset Safety

Fetch free assets when user has none:
```bash
python "$SKILL_DIR/skills/video-clone/scripts/fetch_assets.py" search --kind image --q "keyword" --cc0
python "$SKILL_DIR/skills/video-clone/scripts/fetch_assets.py" get --project projects/<slug> --url "<asset_url>" \
  --name background.jpg --source openverse --license "CC0"
```

Log every asset to `assets/ASSETS.md`:
```
| Filename | Source | Author | Licence | URL |
```
Unknown licence → tag "Licence unconfirmed" and tell user.

---

## Style Registry

Supported 2D styles (read individual `styles/<name>.md` for engine, features, known gotchas):

| Style | Medium | Engine |
|---|---|---|
| painted-animation | 2d-painted | painted-animation |
| anime-cel | 2d-cel | anime-cel |
| pixel-art | 2d-pixel | pixel-art |
| crayon-storybook | 2d-crayon | crayon-storybook |
| paper-cutout | 2d-paper | paper-cutout |
| whiteboard | 2d-lineart | whiteboard |
| faceless-explainer | 2d-lineart | faceless-explainer |
| motion-graphics | 2d-vector | motion-graphics |
| slideshow | 2d-vector | slideshow |
| music-to-video | 2d-* | music-to-video |

To add a new style: copy `styles/_TEMPLATE.md` → fill engine, medium, identification features, production defaults, known gotchas. The engine entry point must exist at `skills/<engine>/<engine>.md` within this suite.

---

## Mode Router

| Mode | Trigger | Behaviour |
|---|---|---|
| **FULL** | Default | All phases 0-6 |
| **ANALYSE-ONLY** | "just analyse the video" | Phase 0-1 only, output STYLE.md |
| **REPLAN** | "change the storyboard" / feedback before production | Phase 4 only |
| **RECUT** | "fix shot X" + time code after production | Phase 6 targeted |
| **ADD-STYLE** | "add a new style called X" | Extend styles/ registry only |
| **SILENT** | "no music" flag | Skip Phase 3 |

---

## Reference Map

Load on demand:

| File | Use |
|---|---|
| `references/runtime.md` | Tool versions, install commands, doctor check |
| `references/engines.md` | Per-engine production details (HyperFrames, FFmpeg, etc.) |
| `references/shot-analysis.md` | How to read analyze.py JSON fields |
| `references/audio.md` | BPM alignment, loudnorm, audio pitfalls |
| `references/licensing.md` | Asset sources, licence grades, attribution format |
| `references/qa-checklist.md` | Full expanded Visual QA checklist |
| `styles/*.md` | Per-style identification features + engine defaults |
| `skills/video-clone/scripts/analyze.py` | Video/audio analysis: see inline docstring |
| `skills/video-clone/scripts/align_lyrics.py` | Lyrics timestamp alignment |
| `skills/video-clone/scripts/fetch_assets.py` | Asset search and download |
| `skills/video-clone/scripts/compare.py` | Side-by-side shot comparison evidence |
| `evals/evals.json` | Benchmark trigger and behaviour assertions |

---

## Stop Conditions

Stop and report to user when:
- Reference video cannot be downloaded or read (ask for local file)
- Required inputs (lyrics, design sheets) not provided after 1 reminder
- QA gate fails 3 rounds without progress (report specific failure, propose alternative approach)
- User explicitly cancels or changes direction mid-production

---

*Adapted from [edenfunf/reelmimic](https://github.com/edenfunf/reelmimic) · MIT License · Skillified by Mamdouh Aboammar*

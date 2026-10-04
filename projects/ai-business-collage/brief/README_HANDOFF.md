# AI BUSINESS COLLAGE | AGENT HANDOFF

## Give the executing agent these inputs

1. The **original reference MP4**, separately attached (not included here because this kit is an analysis/production package).
2. The **original ElevenLabs narration WAV**, separately attached (not included here).
3. **MASTER_AGENT_PROMPT.md** as its full mandatory task prompt.
4. The other support files in this kit: `MOTION_GUIDE.md`, `STORYBOARD.csv`, `ASSET_MANIFEST.csv`, two original reference contact sheets, and both media probe reports.

## Operating instructions

- Do not ask the user to choose a skill. The agent must select relevant skills from `https://github.com/imMamdouhaboammar/motion-graphics-skills` by itself, and use Designly / MotionDesign as directed in the master prompt.
- `STORYBOARD.csv` uses **approximate reference visual boundaries** and **target initial windows**. The uploaded WAV and the actual video camera motion are the temporal truth; dynamically align scene transitions to phrase timestamps.
- The reference is 38.704807 s; VO is 48.352667 s. Do not force both to 38.7 s.
- Only generated photographic cutout assets using the requested `Create Image` tool and `GPT Images 2.5` when such exact tool and model are actually available. If not available, disclose this before changing provider.
- The two `.jpg` contact sheets are sampled screenshots from the user's reference **for internal comparison only**; **no reuse in the final commercial**.
- The graphical storyboard is an annotated *reference-to-target plan*, not generated final shot artwork.
- Arabic on-screen type comes from code/compositor with native RTL shaping; never ask an image model to spell Arabic words.

## Deliverable at the end of production

A true video render (1080 x 1920, 30fps, H.264, source WAV preserved in timing), all source project files/assets/prompts, per-shot storyboard and QA report comparing the reference and finished film side-by-side at normalized corresponding story phases.

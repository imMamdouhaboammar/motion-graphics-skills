---
name: sfx-picker
description: Pick and assign sound effects from the Cozer SFX library to motion graphics compositions, animation keyframes, and UI interactions. Reads the full catalog in references/catalog.md and maps each sound to a visual moment. Use when building motion graphics that need audio, adding SFX to HyperFrames timelines, or when someone says "add sound", "which SFX fits here", "pick a click sound", "add a glitch sound", or "suggest SFX for this animation".
---

# SFX Picker — Cozer Motion SFX Library

148 curated sound effects across 10 categories, purpose-built for motion graphics, UI animations, and editorial video. Every file lives under `assets/sfx/` in this repository and is ready to use in HyperFrames, ffmpeg pipelines, After Effects, or browser-based HTML compositions.

## Before you start

Read `references/catalog.md` in full before picking any sound. It contains every filename, category, and recommended use case. Never invent a filename or path.

## Step 1: Identify the visual moments that need sound

Map the animation to a list of keyframe moments. For each moment, state:
- **What moves** (element name, transform)
- **When it moves** (time in seconds from the composition start)
- **The emotional intent** (punchy, soft, glitchy, mechanical, organic)

Example moment list:

```
0.0s — hero title slides in from left — punchy, confident
0.4s — subtitle fades up — soft, airy
1.2s — CTA button appears — crisp click, satisfying
2.0s — background grid glitches — digital, corrupted
```

## Step 2: Match each moment to a category

Use the category guide below. Open `references/catalog.md` to pick the exact file.

| Category | Path | Best for |
|---|---|---|
| `crisp` | `assets/sfx/crisp/` | Snappy element reveals, cuts, punchy transitions |
| `ui-sounds` | `assets/sfx/ui-sounds/` | Interface interactions, sci-fi menus, confirmations |
| `pop` | `assets/sfx/pop/` | Bubble reveals, element pop-ins, list items |
| `digital-click` | `assets/sfx/digital-click/` | Button clicks, futuristic UI taps, typewriter text |
| `normal-click` | `assets/sfx/normal-click/` | Soft button presses, subtle taps |
| `bell` | `assets/sfx/bell/` | Notifications, soft dings, light accents |
| `message` | `assets/sfx/message/` | Ping notifications, message send, iOS-style chimes |
| `glitch` | `assets/sfx/glitch/` | Corrupted reveals, error states, data glitches |
| `gear` | `assets/sfx/gear/` | Mechanical transitions, typewriter scrolls, slow reveals |
| `rizer` | `assets/sfx/rizer/` | Build-up before a big reveal, rising energy, final hold |

## Step 3: Output a cue sheet

After picking sounds, produce a cue sheet in this format:

```
TIME    CATEGORY        FILE                                NOTES
0.0s    crisp           Crisp  (14).mp3                    Title slide — punchy cut
0.4s    ui-sounds       ES_UI, Positive 02 - Epidemic Sound.mp3   Subtitle appears
1.2s    digital-click   ui degital click by clips.mp3      CTA button appears
2.0s    glitch          UIGlitch_Futuristic_Machines_Devices_Glitch_2_Ocular_Sounds_Sci.wav  Grid glitch
```

## Step 4: Deliver paths and an integration snippet

For each picked SFX, give the full repo-relative path and a ready-to-use snippet.

**Browser / HyperFrames:**

```js
// Preload all SFX at composition init
const sfx = {
  titleSlide: new Audio('assets/sfx/crisp/Crisp  (14).mp3'),
  ctaClick:   new Audio('assets/sfx/digital-click/ui degital click by clips.mp3'),
  glitch:     new Audio('assets/sfx/glitch/UIGlitch_Futuristic_Machines_Devices_Glitch_2_Ocular_Sounds_Sci.wav'),
};

// Fire at seek(t) when t crosses the cue time (fire-once guard):
let fired = {};
function maybeFire(t) {
  if (t >= 0.0 && !fired.titleSlide) { sfx.titleSlide.play(); fired.titleSlide = true; }
  if (t >= 1.2 && !fired.ctaClick)   { sfx.ctaClick.play();   fired.ctaClick   = true; }
  if (t >= 2.0 && !fired.glitch)     { sfx.glitch.play();     fired.glitch     = true; }
}
```

**ffmpeg mixdown (for video export):**

```bash
ffmpeg -i video.mp4 \
  -i "assets/sfx/crisp/Crisp  (14).mp3" \
  -i "assets/sfx/digital-click/ui degital click by clips.mp3" \
  -filter_complex "
    [1:a]adelay=0|0[sfx0];
    [2:a]adelay=1200|1200[sfx1];
    [0:a][sfx0][sfx1]amix=inputs=3:normalize=0[aout]
  " \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -shortest output.mp4
```

## Rules

- Never guess a filename. Check `references/catalog.md` first.
- Prefer short, punchy sounds for fast cuts. Reserve `rizer` for a single composition-level energy build.
- Crisp sounds under 0.5 s work best on element reveals. Do not stack more than three simultaneous SFX cues.
- Files are in `.mp3`, `.wav`, `.aac`, and one `.mp4` (audio-only). All 148 are probed valid.
- Duplicate file `GearPlastic_AP1.475 - Copy.mp3` is identical to `GearPlastic_AP1.475.mp3`. Use the original.

## What I learned the hard way

- **Preload before seek(0).** Browsers silently skip audio if the file has not buffered. Create `new Audio(...)` at init, not at cue time.
- **Fire-once guard prevents double-triggers.** Calling `seek(t)` multiple times for the same frame re-fires the sound. Track which cues have already played and clear the guard only on full composition reset.
- **ffmpeg adelay is in milliseconds.** `adelay=1200|1200` means 1.2 seconds, not 1200 seconds.
- **Crisp sounds disappear in loud music.** Boost SFX by 3 to 6 dB with `volume=2.0` in the amix chain when the background track is dense.
- **The rizer is one per composition.** It sounds wrong when it plays twice. Gate it behind a flag.

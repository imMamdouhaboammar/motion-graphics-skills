---
name: video-spotlight
description: Apply timed selective lighting to focus attention on a person, product, interface area, or visual detail while preserving the original pixels inside the target and dimming the surroundings. Uses normalized target geometry and a spatial FFmpeg mask. Use for "video spotlight", "selective lighting", "dim the background", "highlight this product", "focus beat", or timed visual emphasis.
---

# Video Spotlight and Timed Lighting

A spotlight is an attention edit.

It should make the viewer look at one meaningful target for a short beat, then return the image to normal.

It is not a global vignette or permanent grade.

## Decision gate

Use this skill when a specific object or area needs temporary emphasis.

Good triggers include:

- a product is named
- a chart value is discussed
- a UI control matters for one instruction
- a face reaction is the narrative beat
- a physical detail would otherwise be missed

Do not use it when the entire frame is equally important.

Do not leave the effect active simply because the shot is visually quiet.

## Lighting modes

1. Area spotlight for a known region
2. Subject emphasis when a stable subject mask already exists
3. Short contrast beat for a deliberate dramatic change

The bundled planner implements area spotlight geometry.

## Workflow

### Step 1: Define the target in normalized coordinates

Use x and y for target center and rx and ry for horizontal and vertical radius.

Example:

~~~json
{
  "start": 4.2,
  "end": 6.0,
  "target": "area",
  "area": { "x": 0.50, "y": 0.45, "rx": 0.25, "ry": 0.20 },
  "dim": 0.45,
  "desat": 0.60
}
~~~

### Step 2: Generate the plan and filter

~~~bash
python3 scripts/spotlight_plan.py   --start 4.2   --end 6.0   --x 0.50   --y 0.45   --rx 0.25   --ry 0.20   --dim 0.45   --desat 0.60   --frame-width 1080   --frame-height 1920   > "$WORK/spotlight.json"
~~~

The plan preserves:

- normalized target geometry
- lighting strength
- frame dimensions
- timing
- generated ffmpeg_filter

### Step 3: Understand the spatial composite

The generated filter does four things:

1. keeps an untouched base copy
2. creates a dimmed and desaturated copy
3. builds an elliptical grayscale mask from the configured target
4. restores the original pixels inside that mask and overlays the effect only during the requested time window

Outside the time window, original footage passes through unchanged.

The focal area stays bright because original pixels are preserved there. The effect is not a whole-frame substitution.

### Step 4: Apply the generated filter

Read ffmpeg_filter from the plan and use it as the video filter graph.

Keep source audio unchanged unless the creative brief also calls for an audio accent.

When the active composition already runs in HyperFrames, use the same target geometry and timing to build the equivalent masked layer there instead of adding a second render path.

## Strength rules

Start subtle.

A normal emphasis beat should usually:

- retain enough peripheral detail to understand context
- reduce saturation rather than remove all color
- avoid crushing skin tones or black levels
- last only as long as the spoken or visual idea needs

The target should attract attention because its surroundings recede, not because it glows like an effect demo.

## Target tracking

The bundled area plan is static.

If the target moves significantly during the window, do one of these:

- shorten the window
- split it into multiple target windows
- use subject tracking from the active runtime
- use an existing subject mask

Do not keep a static spotlight while the subject walks out of it.

## Color integrity

Preserve the delivery color contract.

For normal web video, verify BT.709 tags and range on the final rendered file.

Do not assume a correct filter string guarantees correct color after encoding.

Read references/color-integrity.md.

## Creative QA

Hard-fail when:

- the target itself becomes darker
- the whole frame stays dim outside the effect window
- the mask points at empty space
- the spotlight remains after the relevant word or action
- the effect is stronger than the content
- skin tone changes noticeably
- repeated spotlights create a predictable visual gimmick

## What I learned the hard way

- A full-frame grade cannot create a local spotlight by itself.
- Timing the restoration is as important as timing the darkening.
- Static coordinates fail on moving subjects.
- The most useful spotlight often looks less dramatic than the first draft.

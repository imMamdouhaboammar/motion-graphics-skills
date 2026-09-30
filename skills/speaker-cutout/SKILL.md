---
name: speaker-cutout
description: Isolate a talking-head presenter for backdrop replacement, picture-in-picture layouts, and depth-stacked motion graphics. Plans full and PiP geometry, validates timeline windows, and preserves a strict foreground hierarchy. Use when someone says "speaker cutout", "cut me out of the video", "put graphics behind me", "talking head PIP", "swap background", or "person layer".
---

# Speaker Cutout and Depth Stacking

The presenter is a visual layer, not a sticker pasted on top of graphics.

Use this skill to create deliberate foreground and background relationships while preserving body edges, eye line, captions, and scene continuity.

## Decision gate

Use cutout compositing when the story needs information behind or beside the presenter.

Do not isolate the speaker simply because segmentation is available.

Keep the original full camera frame when:

- the environment is meaningful
- mask quality is unstable around hair or hands
- the new background creates a lighting mismatch
- graphics can fit cleanly without removing the room
- segmentation adds complexity without improving communication

## Layer hierarchy

Maintain this order:

1. Backdrop
2. BehindPresenter
3. PresenterCutout
4. ForegroundUI

Captions and critical UI belong above the presenter.

Graphics intended to feel embedded in the scene belong behind the presenter.

## Workflow

### Step 1: Inspect the source before segmentation

Check:

- hair detail
- motion blur
- hand movement
- clothing against the background
- shadows
- camera movement
- whether a clean room plate exists

If the source is difficult to segment, plan a simpler composition instead of hiding bad edges with more effects.

### Step 2: Produce or reuse the alpha source

Use the current project's subject extraction path first.

For a separate workflow, Apple Vision, rembg, or another segmentation system can create the alpha source.

Preserve enough edge detail for hair and hands.

### Step 3: Resolve the speaker mode

For PiP:

~~~bash
python3 scripts/speaker_layer.py --mode pip --scale 0.65 --anchor-x 0.85 --anchor-y 0.90
~~~

For full frame:

~~~bash
python3 scripts/speaker_layer.py --mode full
~~~

Full mode always returns the entire frame at position 0,0.

PiP uses the supplied scale and anchors.

### Step 4: Plan timeline windows explicitly

A presenter state must have a valid finite interval:

~~~text
0 <= start < end <= total_duration
~~~

Reject invalid windows instead of emitting negative or out-of-range durations.

Use timeline windows to separate:

- background change
- presenter scale change
- presenter movement
- graphic reveal

Do not fire all four on one frame unless the creative direction specifically calls for a hard transformation.

### Step 5: Composite depth layers

The bundled helper generates the basic depth stack.

A typical structure is:

~~~text
background
  + behind-presenter graphics
  + alpha presenter
  + captions in the final composition
~~~

If a stable HyperFrames composition already exists, keep the cutout as a layer inside that runtime rather than creating a parallel render pipeline.

## Transition logic

A reliable room-to-PiP transition is:

1. establish the replacement backdrop
2. hold long enough for visual continuity
3. scale and move the presenter
4. reveal the information that needed the freed space

This prevents the viewer from seeing a duplicate room or feeling that the speaker teleported.

## Compositing craft

Check:

- edge feather is subtle
- no bright halo around hair
- skin temperature belongs in the new environment
- feet or torso are not cropped accidentally
- eye line still points into usable composition space
- graphics behind the speaker remain understandable even when partially occluded

Do not use a heavy glow to hide poor segmentation.

## Creative QA

Hard-fail when:

- the alpha edge chatters frame to frame
- full mode is not actually full frame
- the presenter blocks the information the layout was meant to reveal
- captions drop behind the cutout
- background and presenter lighting feel unrelated
- transitions create a visible double speaker
- PiP becomes so small that facial expression stops reading

## What I learned the hard way

- A technically clean mask can still feel fake if lighting and scale disagree.
- Background change and presenter movement need sequencing.
- Cutout layouts work best when the freed space has a clear information job.
- Preserving the original frame is often better than forcing segmentation into every talking-head scene.

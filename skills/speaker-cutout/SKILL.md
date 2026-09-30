---
name: speaker-cutout
description: Isolate a talking-head speaker from their background to swap backdrops, slide into a picture-in-picture card, or place motion graphics and titles behind the presenter. Generates an alpha cutout mask using native vision or rembg, handles empty room plate transitions without ghost copies, and establishes depth-stacked video layers. Use when someone says "speaker cutout", "cut me out of the video", "put graphics behind me", "talking head PIP", "swap background", or "person layer".
---

# Speaker Cutout and Depth Stacking

Place motion graphics, large titles, and diagrams directly behind the speaker, or shrink the presenter into an interview card while graphics occupy the rest of the vertical canvas.

## Visual layer hierarchy

All compositions maintain this strict four-layer stack:

1. **Backdrop:** Brand wallpaper, video b-roll, or empty room plate.
2. **BehindPresenter:** Animated charts, text typography, and icons.
3. **PresenterCutout:** Segmented speaker with clean alpha transparency.
4. **ForegroundUI:** Subtitles, word captions, and progress indicators.

## Workflow

### Step 1: Extract the speaker alpha mask

On macOS, extract the subject mask using Apple Vision or rembg:

```bash
# macOS Vision framework extraction or rembg
rembg i "$WORK/frames/frame_0001.png" "$WORK/cutout/frame_0001.png"
```

For video streams, encode an Apple ProRes 4444 MOV with alpha channel, or an MP4 with side-by-side alpha matte.

### Step 2: Calculate PiP layout and coordinates

Calculate exact pixel coordinates and scaling with the layout planner:

```bash
# Calculate 65% scale docked at bottom right
python3 scripts/speaker_layer.py --mode pip --scale 0.65 --anchor-x 0.85 --anchor-y 0.90
```

### Step 3: Composite depth layers in FFmpeg

Combine background, motion graphics, and speaker cutout into a single output stream:

```bash
ffmpeg -y \
  -i "$WORK/bg.mp4" \
  -i "$WORK/graphics_behind.mp4" \
  -i "$WORK/speaker_alpha.mov" \
  -filter_complex "[0:v]scale=1080:1920,setsar=1[bg];[1:v]scale=1080:1920,setsar=1[gfx];[bg][gfx]overlay=0:0:shortest=1[base];[2:v]scale=702:-2[spk];[base][spk]overlay=189:192:shortest=1,format=yuv420p[out]" \
  -map "[out]" -map 2:a? \
  -c:v libx264 -crf 18 -pix_fmt yuv420p "$WORK/stacked_output.mp4"
```

## What I learned the hard way

- **Background swap before position shift.** Moving the presenter and swapping the room in the same frame produces an unsettling visual pop. Swap the background first, then glide the presenter.
- **Captions always stay on top.** Never place word captions behind the speaker cutout. Captions must remain legible on Layer 3.
- **Feather the alpha boundary.** Raw machine learning masks produce jagged edges on hair and shoulders. A subtle 2px Gaussian blur on the mask prevents harsh digital cutouts.
- **Match lighting color temperature.** When placing a warm daylight speaker over a cold dark-blue background, apply a subtle tint to the speaker edges so the cutout blends naturally.

---
name: video-spotlight
description: Apply selective lighting, focus spotlights, and timed grading beats to emphasize key moments in video footage. Dims and desaturates background elements by a controlled amount while keeping a target person, product, or area bright with an optional brand accent glow. Supports timed high-contrast and monochrome focus beats without altering global footage color matrix. Use when someone says "video spotlight", "selective lighting", "dim the background", "highlight this product", "focus beat", or "timed grade".
---

# Video Spotlight and Timed Lighting

Draw the eye precisely to a speaker, product, chart element, or physical coordinate by dimming and desaturating the surroundings for 1 to 3 seconds.

## Lighting modes

1. **Area Spotlight:** A soft elliptical beam highlighting a point or quadrant while peripheral areas darken.
2. **Subject Glow:** The speaker or an object is masked, illuminated, and accented with the brand secondary tone while the background drops in saturation.
3. **Dramatic Contrast Beat:** Short monochrome or punchy high-contrast interval timed to a key revelation or dramatic punchline.

## Workflow

### Step 1: Define spotlight target and timing

Define the time interval and normalized coordinates `(x, y, rx, ry)` in `spotlight.json`:

```json
{
  "windows": [
    {
      "start": 4.2,
      "end": 6.0,
      "target": "area",
      "area": { "x": 0.5, "y": 0.45, "rx": 0.25, "ry": 0.20 },
      "dim": 0.45,
      "desat": 0.60
    }
  ]
}
```

### Step 2: Validate coordinates

Run the plan validator to confirm boundary and timing constraints:

```bash
python3 scripts/spotlight_plan.py --start 4.2 --end 6.0 --dim 0.45 --desat 0.60
```

### Step 3: Composite spotlight in FFmpeg

Apply the filter chain with smooth enable transitions:

```bash
ffmpeg -y -i "$WORK/cut.mp4" -filter_complex \
  "split[base][dimmed]; \
   [dimmed]eq=brightness=-0.12:contrast=0.92,hue=s=0.4[dark]; \
   [base][dark]blend=all_expr='if(between(T,4.2,6.0),B,A)'[out]" \
  -map "[out]" -map 0:a? -c:v libx264 -crf 18 -pix_fmt yuv420p "$WORK/spotlight.mp4"
```

## What I learned the hard way

- **Never apply permanent color shifts.** A spotlight must feel like a brief visual breath. Keeping it on screen longer than 4 seconds causes viewer fatigue.
- **Retain 40% peripheral saturation.** Dropping the background to pure greyscale can feel jarring like a retro filter. Reducing saturation by 50% to 60% feels like cinematic studio lighting.
- **Respect BT.709 tags.** Color filters must not strip the color range or transform limited TV range into full range. Keep explicit color tags on the final output.
- **Align to keyword audio.** Start the spotlight precisely on the accented word and cut it cleanly when the sentence concludes.

# Shot Analysis Reference — analyze.py Output Fields

## report.json Structure

```json
{
  "duration_s": 58.4,
  "fps": 24,
  "resolution": [1920, 1080],
  "bpm": 128.0,
  "beat_times": [0.0, 0.47, 0.94, ...],
  "avg_shot_length_s": 2.3,
  "avg_shot_length_beats": 4.6,
  "silent": false,
  "phase_inverted": false,
  "noise_floor_db": -52.0,
  "look_summary": {
    "brightness": "mid-high",
    "contrast": "high",
    "saturation": "vivid",
    "dominant_palette": ["#F4A261", "#264653", "#2A9D8F"]
  },
  "transitions": ["cut", "cut", "dissolve", "cut"],
  "shot_details": [
    {
      "id": 1,
      "start_s": 0.0,
      "end_s": 2.3,
      "duration_s": 2.3,
      "duration_beats": 4.6,
      "camera_move": "slow-push",
      "camera_speed": "slow",
      "brightness": 0.72,
      "contrast": 0.85,
      "shadow_ratio": 0.12,
      "saturation": 0.91,
      "dominant_colors": ["#F4A261", "#E76F51"],
      "content_description": "Character walking left-to-right",
      "transition_out": "cut"
    }
  ]
}
```

## Camera Move Types
| Value | Description |
|---|---|
| `static` | No camera movement |
| `slow-push` | Gradual zoom toward subject |
| `fast-push` | Quick zoom toward subject |
| `slow-pull` | Gradual zoom away from subject |
| `fast-pull` | Quick zoom away from subject |
| `pan-left` / `pan-right` | Horizontal panning |
| `tilt-up` / `tilt-down` | Vertical tilting |
| `orbit` | Arc movement around subject |
| `whip-pan` | Very fast horizontal swipe |
| `handheld` | Organic shake |
| `crane-up` / `crane-down` | Vertical dolly movement |

## Camera Speed Values
- `very-slow`, `slow`, `medium`, `fast`, `very-fast`

## Plan.json Shot Entry (storyboard machine format)

```json
{
  "shot": 3,
  "ref_shot": 7,
  "ref_what": "slow zoom in on subject with warm backlight",
  "beats": 4,
  "transition_in": "cut",
  "event": "Character discovers the item",
  "reaction": "Surprised expression, eyebrows raised",
  "camera": {
    "move": "slow-push",
    "focal": "85mm",
    "fill": 0.6,
    "region": "face",
    "depth_of_field": "shallow",
    "angle_start": 0,
    "angle_end": 3
  },
  "notes": "Warmer colour grade than ref — product is more pastel"
}
```

## Style Matching Fields

When scoring a reference against a style's identification features:
1. `medium` match: must match (2d-painted, 2d-cel, etc.)
2. `avg_shot_length_beats`: high (> 6 beats) = contemplative/lyrical, low (< 3) = energetic/kinetic
3. `transitions`: mostly cuts = editorial, dissolves = dreamy, whip-pans = dynamic
4. `shadow_ratio`: high = dramatic, low = flat/clean
5. `saturation`: vivid = kawaii/food, muted = moody/art-house
6. Camera moves: mostly static = classic, mostly motion = documentary feel

## sheet_1fps.jpg / sheet_scenes.jpg

Use the Read tool to open these images directly. Look for:
- Colour palette consistency across frames
- Character design language
- Composition patterns (subject position, negative space)
- Text/caption styling
- Transition signatures
- Any watermarks or tool logos embedded in the video (these are strong signals for which production tool was used)

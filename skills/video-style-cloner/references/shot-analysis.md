# Shot Analysis Reference: analyze.py Output Fields

## report.json Structure

```json
{
  "source": "source.mp4",
  "input": "reference.mp4",
  "analysed": "source.mp4",
  "video": {"duration": 58.4, "fps": 24, "width": 1920, "height": 1080, "has_audio": true, "channels": 2},
  "crop": null,
  "shots": [[0.0, 2.3]],
  "pacing": {"count": 1, "mean_shot_s": 2.3, "shortest_s": 2.3, "longest_s": 2.3, "mean_shot_beats": 4.9},
  "audio": {"present": true, "silent": false, "bpm": 128.0, "beat_seconds": 0.469, "beats": [0.0, 0.469], "phase_inverted": false, "noise_floor_db": -52.0, "best_30s_starts": [{"start": 12.0, "density": 0.8}]},
  "look_summary": {"low_key_shots": 0.0, "moving_camera_shots": 1.0, "mean_brightness": 0.72, "camera_kinds": ["push_in"]},
  "shot_details": [{
    "shot": 1, "start": 0.0, "end": 2.3,
    "camera": {"pan_x": 0.0, "tilt_y": 0.0, "zoom": 0.02, "rotate": 0.0, "kind": ["push_in"], "speed": 0.02, "pace": "slow"},
    "look": {"brightness": 0.72, "contrast": 0.2, "dark_ratio": 0.12, "colourfulness": 0.4, "dominant": ["#F4A261", "#264653"]}
  }]
}
```

The example abbreviates arrays and optional audio diagnostics. Audio-only inputs have null video dimensions and FPS, no shots and no `look_summary`. Missing audio returns `audio.present: false`. Silent recordings omit BPM and beat measurements. `pacing.mean_shot_beats` is only emitted when tempo is available. Transitions and content descriptions are human annotations, not analyzer measurements.

## Camera Measurements

`camera.kind` is an array containing `static`, `push_in`, `pull_out`, `move_left`, `move_right`, `move_up`, `move_down`, or `roll/orbit`. Multiple kinds can occur together. Numeric `speed` is measured from optical flow. `pace` is `still`, `slow`, `medium`, or `fast`.

## Plan.json Shot Entry (storyboard machine format)

```json
{
  "id": 3,
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
  "notes": "Warmer colour grade than ref, product is more pastel"
}
```

## Style Matching Fields

When scoring a reference against a style's identification features:
1. `medium` match: must match (2d-painted, 2d-cel, etc.)
2. `pacing.mean_shot_beats`: high (> 6 beats) = contemplative/lyrical, low (< 3) = energetic/kinetic
3. Transitions: annotate cuts, dissolves and whip-pans by inspecting the contact sheets
4. `shot_details[].look.dark_ratio`: high = dramatic, low = flat/clean
5. `shot_details[].look.colourfulness`: vivid = kawaii/food, muted = moody/art-house
6. `look_summary.moving_camera_shots`: mostly static = classic, mostly motion = documentary feel

## sheet_1fps.jpg / sheet_scenes.jpg

Use the Read tool to open these images directly. Look for:
- Colour palette consistency across frames
- Character design language
- Composition patterns (subject position, negative space)
- Text/caption styling
- Transition signatures
- Any watermarks or tool logos embedded in the video (these are strong signals for which production tool was used)

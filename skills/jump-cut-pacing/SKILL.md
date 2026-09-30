---
name: jump-cut-pacing
description: Tighten raw talking-head footage with automated silence trimming and rhythmic face-guarded jump cuts. Detects pauses using ffmpeg silencedetect, alternates subtle 1.0x and 1.15x push-in zooms to mask edit cuts, and keeps the speaker face safe in the upper third without forehead clipping. Use when editing talking-head videos, trimming voice pauses, applying jump cuts, fixing video cadence, or when someone says "cut the silences", "tighten this video", "jump cut pacing", or "smooth talking head zooms".
---

# Jump Cut and Pacing

Raw talking-head recordings contain hesitation pauses, repeated takes, and static framing. This skill trims dead air with breath padding and applies alternating punch-in zooms to mask jump cuts while protecting the speaker face.

## Workflow

### Step 1: Detect silences with native FFmpeg

Run silence detection using standard FFmpeg:

```bash
ffmpeg -v info -i "$WORK/src.mov" -af "silencedetect=noise=-35dB:d=0.45" -f null - 2> "$WORK/silence.log"
```

Silence longer than 0.45 seconds marks dead air. Natural pauses under 0.35 seconds are preserved so the speaker does not sound rushed.

### Step 2: Build the cut plan and alternate zoom

Use the bundled planner to extract active speech segments and assign alternating zoom scales:

```bash
python3 scripts/cut_plan.py "$WORK/src.mov" --min-silence 0.45 -o "$WORK/cut_plan.json"
```

The plan generates:
- Active speech chunks with 0.06s lead padding and 0.08s tail padding.
- Alternating zoom levels: 1.0x for wide baseline shots, 1.15x for emphasis shots.
- `zoomAnchor` pinned to `0.15` (top 15% of frame) so the forehead is never cut off.

### Step 3: Render the assembled cut

Assemble the clean video and synchronized audio with FFmpeg:

```bash
# Extract uncompressed source audio at 48kHz
ffmpeg -y -i "$WORK/src.mov" -vn -c:a pcm_s24le -ar 48000 -ac 2 "$WORK/voice.wav"

# Apply select cut filter from the cut plan
ffmpeg -y -i "$WORK/src.mov" -i "$WORK/voice.wav" -filter_complex "[0:v]select='... ',setpts=N/FRAME_RATE/TB[v];[1:a]aselect='... ',asetpts=N/SR/TB[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 18 -pix_fmt yuv420p "$WORK/cut.mp4"
```

### Step 4: Verify framing and audio integrity

1. **Check top margin:** Confirm the crown of the speaker head sits between 120px and 220px below the top border on vertical 1080x1920 frames.
2. **Audio check:** Ensure audio does not use dynamic volume pumping. Audio spectrum ceiling must match the camera source.
3. **Pacing review:** Confirm no speech segment is shorter than 0.20 seconds to prevent audio clicks.

## What I learned the hard way

- **Default center zoom ruins talking heads.** Zooming into the middle of the frame clips the speaker forehead immediately. The anchor must sit in the top 15% of vertical footage.
- **Do not trim every micro-pause.** Cutting breaths under 0.3 seconds creates an uncanny, suffocating rhythm. Keep short breaths between phrases.
- **Keep uncompressed master audio.** Never feed low-sample transcription audio back into the final video. Always cut the 48kHz camera master track.
- **Alternating zooms hide jump cuts.** An edit cut between identical framings looks like a glitch. Stepping between 1.0x and 1.15x turns a jump cut into intentional emphasis.

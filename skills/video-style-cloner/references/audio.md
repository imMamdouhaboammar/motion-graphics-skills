# Audio Reference: BPM Alignment & Audio Pitfalls

## Analyzing Audio

```bash
python .claude/skills/video-clone/scripts/analyze.py "<audio_or_video>" \
  --out projects/<slug>/analysis/song
```

Key fields in `analysis/song/report.json`:
```json
{
  "audio": {
    "present": true,
    "bpm": 128.0,
    "beats": [0.0, 0.469, 0.938],
    "silent": false,
    "phase_inverted": false,
    "noise_floor_db": -52.1,
    "best_30s_starts": [{"start": 42.0, "density": 0.85}]
  }
}
```

## Common Audio Pitfalls

| Flag | Cause | Action |
|---|---|---|
| `silent: true` | Screen recording without system audio enabled | Ask user to re-record with "System Audio" enabled (Windows: Snipping Tool, macOS: BlackHole/Loopback) |
| `phase_inverted: true` | Dual-channel cancellation (common in phone recordings) | Use as-is but warn user, recommend re-recording or proper audio file |
| `noise_floor_db > -45` | Background noise too high | Warn user, suggest clean audio source |

## Trimming to Target Length

Always trim starting at a beat boundary so frame 0 = beat 0:

```bash
# 1. If audio.best_30s_starts is nonempty, choose its best window and the nearest audio.beats entry.
#    Otherwise choose a valid beat manually; if no beats were detected, use start_s = 0.
#    Keep start_s + duration_s within the input duration.
# 2. Trim + loudnorm + fade
ffmpeg -ss <start_s> -t <duration_s> -i input.wav \
  -af "loudnorm=I=-14:TP=-1.5,afade=t=in:d=0.08,afade=t=out:st=<dur-2>:d=2" \
  -c:a aac -b:a 192k assets/clip.m4a
```

An audio-less source returns `audio.present: false`. A silent recording omits beat and window measurements. Check these flags before reading `audio.beats` or selecting a start.

**Parameters:**
- `loudnorm=I=-14` → Integrated loudness target (streaming standard)
- `TP=-1.5` → True peak limit
- `afade=t=in:d=0.08` → 80ms fade in (smooth click removal)
- `afade=t=out:st=<len-2>:d=2` → 2s fade out

## Shot Timing in Beats

Always express shot durations in **beats**, not seconds.
This means changing BPM only requires recomputing timing, not re-shooting.

```
shot_duration_beats = shot_duration_s * bpm / 60
```

Example at BPM=128:
- 4 beats = 1.875 s
- 8 beats = 3.75 s
- 16 beats = 7.5 s

Store in plan.json:
```json
{"id": 1, "beats": 4, "start_beat": 0}
```

## Lyric Alignment

```bash
python .claude/skills/video-clone/scripts/align_lyrics.py \
  assets/clip.m4a inputs/lyrics.txt \
  --out analysis/lyrics/subs.lrc \
  --start 0 --end 30
```

**Rules:**
- faster-whisper timestamps are used as reference only
- The actual text MUST be the user-provided lyric text verbatim
- Each line reports `match`, the ratio of matched characters. Only lines with no matched characters receive interpolated timestamps.
- Output: `.lrc` (time-tagged lines) + `.json` (per-line `match` and per-character timing).

**NEVER:**
- Transcribe audio and use that text as lyrics
- Fill in missing lyric lines from context
- Quote or reproduce lyric text in storyboard or reports

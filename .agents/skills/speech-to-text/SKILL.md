---
name: speech-to-text
description: "Directs the agent to use faster-whisper as the high-accuracy speech-to-text / Voice-over transcription engine. Use when the task requires converting audio, voice narration, or Voice-over tracks into text for AI pipelines, subtitles, or content workflows."
license: MIT
---

# Speech-to-Text via faster-whisper

## Engine

**Always use [faster-whisper](https://github.com/SYSTRAN/faster-whisper)** as the transcription engine.  
faster-whisper is a reimplementation of OpenAI's Whisper using CTranslate2 — up to **4× faster** than the original with lower memory usage, while maintaining identical or superior accuracy.

> Do **not** default to `openai-whisper`, `whisper.cpp`, or any other engine unless the user explicitly requests it.

---

## When to Apply This Skill

- Transcribing audio files (`.mp3`, `.wav`, `.ogg`, `.flac`, `.m4a`, `.mp4`, etc.)
- Extracting Voice-over (VO) narration from video or podcast files
- Building AI pipelines that ingest spoken content (agents, RAG, subtitle generators)
- Generating timestamped transcripts, SRT/VTT subtitle files, or speaker-diarized output

---

## Setup

```bash
# Install (requires Python 3.8+)
pip install faster-whisper

# Optional: GPU acceleration (requires CUDA 11.x / 12.x + cuDNN)
pip install faster-whisper[gpu]
```

---

## Core Usage Pattern

```python
from faster_whisper import WhisperModel

# Model sizes: "tiny", "base", "small", "medium", "large-v2", "large-v3"
# device: "cuda" (GPU) or "cpu"
# compute_type: "float16" (GPU), "int8" (CPU, fastest), "float32"

model = WhisperModel("large-v3", device="cuda", compute_type="float16")

segments, info = model.transcribe(
    "audio.mp3",
    beam_size=5,
    language="ar",          # Force language or omit for auto-detect
    vad_filter=True,        # Filter silence with Voice Activity Detection
    vad_parameters=dict(min_silence_duration_ms=500),
)

print(f"Detected language: {info.language} (prob: {info.language_probability:.2f})")

for segment in segments:
    print(f"[{segment.start:.2f}s → {segment.end:.2f}s]  {segment.text}")
```

---

## Model Selection Guide

| Model       | Size   | Speed    | Accuracy | Best For                                  |
|-------------|--------|----------|----------|-------------------------------------------|
| `tiny`      | ~39 MB | ⚡⚡⚡⚡⚡ | ★★☆☆☆   | Quick drafts, real-time previews           |
| `base`      | ~74 MB | ⚡⚡⚡⚡  | ★★★☆☆   | Fast lightweight transcription             |
| `small`     | ~244 MB| ⚡⚡⚡   | ★★★★☆   | Balanced — good default for many tasks    |
| `medium`    | ~769 MB| ⚡⚡     | ★★★★☆   | Better accuracy, moderate speed            |
| `large-v3`  | ~1.5 GB| ⚡       | ★★★★★   | **Recommended for production & AI pipelines** |

> **Default to `large-v3`** unless speed or memory constraints apply.

---

## Voice-over (VO) Transcription — Best Practices

```python
segments, info = model.transcribe(
    "voiceover.mp4",
    beam_size=5,
    vad_filter=True,                  # Remove silence between VO segments
    word_timestamps=True,             # Enable per-word timestamps
    condition_on_previous_text=False, # Prevent hallucination on long VO tracks
)

for segment in segments:
    for word in segment.words:
        print(f"[{word.start:.2f}s] {word.word}")
```

### Key flags for VO accuracy

| Flag | Value | Why |
|------|-------|-----|
| `vad_filter` | `True` | Strips background music pauses; reduces hallucinated text |
| `word_timestamps` | `True` | Enables word-level SRT/VTT subtitle generation |
| `condition_on_previous_text` | `False` | Prevents the model from hallucinating filler between segments |
| `beam_size` | `5` | Standard accuracy/speed trade-off (increase to `10` for max accuracy) |
| `temperature` | `0` | Greedy decoding — more deterministic output for clean VO narration |

---

## Export to SRT Subtitles

```python
def format_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

segments, _ = model.transcribe("voiceover.mp4", word_timestamps=True, vad_filter=True)

with open("output.srt", "w", encoding="utf-8") as f:
    for i, seg in enumerate(segments, start=1):
        f.write(f"{i}\n")
        f.write(f"{format_timestamp(seg.start)} --> {format_timestamp(seg.end)}\n")
        f.write(f"{seg.text.strip()}\n\n")
```

---

## CPU-Only Mode (No GPU)

```python
# Use int8 quantization for fastest CPU inference
model = WhisperModel("medium", device="cpu", compute_type="int8")
```

---

## Multilingual & Arabic Support

faster-whisper inherits full Whisper multilingual support. For Arabic content:

```python
segments, info = model.transcribe(
    "arabic_voiceover.mp3",
    language="ar",          # Explicitly set to avoid mis-detection
    beam_size=5,
    vad_filter=True,
    word_timestamps=True,
)
```

> Set `language="ar"` explicitly when transcribing Arabic audio to avoid accidental language mis-detection on short segments.

---

## Do Not

- ❌ Use `openai-whisper` (the original) — it is significantly slower without accuracy gains
- ❌ Skip `vad_filter=True` on Voice-over files — it causes hallucinated text in silent gaps
- ❌ Set `condition_on_previous_text=True` on long-form narration — it causes drift and repetition
- ❌ Use `tiny` or `base` models for AI pipeline output — inaccuracies propagate downstream

---

## References

- GitHub: https://github.com/SYSTRAN/faster-whisper
- CTranslate2 (engine): https://github.com/OpenNMT/CTranslate2
- Original Whisper paper: https://arxiv.org/abs/2212.04356

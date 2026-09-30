# Pacing and Jump-Cut Rules

These principles govern silence removal, rhythmic pacing, and face-safe framing for talking-head video editing.

## 1. Cadence and breath padding

- Natural breathing needs a small cushion before and after speech.
- Pad the start of speech by 0.06s so the first consonant is never clipped.
- Pad the end of speech by 0.08s so sentence trails and word endings remain intact.
- Treat silences under 0.35s as natural conversational pauses. Do not trim them or speech sounds robotic.
- Cuts longer than 0.45s represent dead air or retakes. Trim them aggressively.

## 2. Face anchor safe zones

When footage cuts between regular framing and punch-in zooms:
- Most speakers position their face in the upper third of the vertical frame.
- Setting crop anchor to center (0.50) chops off the speaker forehead.
- Default `zoomAnchor` to `0.12` to `0.18` from the top edge.
- Never zoom beyond 1.20x on 1080p source footage or pixelation becomes visible.
- Ideal punch-in zoom factor is 1.12x to 1.15x. It creates visible emphasis without jarring resolution loss.

## 3. Audio fidelity preservation

- Extract master audio directly from the camera source as 48kHz 24-bit stereo PCM.
- Never feed a compressed 16kHz transcription model WAV back into the final delivery video.
- Never apply dynamic compression or automatic loudness normalization during cut assembly.
- Dynamic normalization causes audible volume pumping between cut segments.
- Keep fixed gain adjustments and verify that audio peak differential remains under 0.1 dB.

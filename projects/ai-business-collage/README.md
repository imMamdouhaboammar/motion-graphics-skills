# AI Business Collage · V2

[Watch / download the preview](renders/AI_Business_Collage_preview.mp4)

The full-quality 1080×1920 final render and rejected V1 archive are stored byte-for-byte in numbered parts because the authenticated upload connection has a 16 MiB request limit. Reassemble them with:

```bash
python3 scripts/restore_renders.py
```

This verifies every part and the final SHA256, and restores renders/AI_Business_Collage.mp4 without recompression. The preview is 720×1280; the restored final is the original 1080×1920 render.

Arabic vertical film, 1080 × 1920, 30 fps, 48.366667 seconds. Original narration is preserved. V1 was rejected by the user and is retained in renders/archive for comparison. V2 is a rebuilt revision, not a claim of user approval or exact reference fidelity.

## Requested revision

The overhead wooden room is removed from the active film. Its interval now uses close photographic cuts of a handheld client phone, printed content and a report on ivory. Every active typographic layer uses the authentic Thmanyah **Serif Display calligraphic** Regular, Bold or Black font from the source repository. No active Sans font source remains. Prior wood assets remain in the archive only.

## Reproduce

Install Node 24+, Python with NumPy and Pillow, FFmpeg and Git. Run npm ci, bash scripts/setup_browser.sh, and bash scripts/restore_fonts.sh if the fonts are absent. In this Git repository assets/fonts links to the existing font directory under projects/jedar-lesh-majani.

```bash
python3 scripts/build_v2.py
HYPERFRAMES_BROWSER_PATH="$PWD/.browser/chromium" npx hyperframes render . --output "$PWD/renders/capture.mp4" --quality delivery --workers 2 --no-low-memory-mode --no-browser-gpu --no-gpu --no-best-effort --fps 30 --crf 18
python3 scripts/finish_audio.py
ffmpeg -i renders/capture.mp4 -i renders/voice_foley_master.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -af apad=whole_dur=48.366667 -t 48.366667 -movflags +faststart renders/AI_Business_Collage.mp4
```

The CPU path was authorized after hardware checks failed. scripts/build_v2.py builds the active composition; scripts/rebuild_cards.py supplies scenes 8–10. scripts/build_composition.py and versions/v1 are the rejected baseline.

## Evidence

[Reference and current render](reviews/reference-target-contact.jpg). Latest font identity and removed-scene proof: reviews/font-and-scene-proof.json. Current native checks and independent review use v2 names. Historical V1 reports and snapshots remain for comparison and do not approve V2. Arabic type is shaped by the browser, not baked into generated images.

All source inputs, original assets, prompts, scripts and evidence are included. node_modules, ASR model caches and temporary capture are omitted. In the source ZIP, font binaries are omitted; restore_fonts.sh retrieves the user-specified source fonts.

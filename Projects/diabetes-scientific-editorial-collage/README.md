# السكري.. هل اقتربت نهاية المرض؟

An original Arabic scientific editorial collage film built from editable HTML, SVG, photographic alpha cutouts and a deterministic GSAP timeline. The supplied narration is the master audio; no regeneration, speed change or truncation is used.

Repository location: `Projects/diabetes-scientific-editorial-collage/`

## Delivery

| Deliverable | Path |
| --- | --- |
| H.264 review film, 1920×1080, 30 fps, 49.5 seconds | `renders/diabetes-delivery.mp4` |
| Previous review cut | `renders/diabetes-review.mp4` |
| Three opening candidate frames | `styleframes/hero-a.png`, `styleframes/hero-b.png`, `styleframes/hero-c.png` |
| Six scene style frames and scene contact sheet | `styleframes/master-scenes/` |
| Asset contact sheet | `assets/contact-sheet.jpg` |
| Editable full film | `index.html` |
| Editable animation mirror | `animation/timeline.js` |
| Six composition layer inventories | `compositions/scene-01.json` through `scene-06.json` |
| Four transition proofs | `previews/opening.mp4`, `research.mp4`, `evidence.mp4`, `book.mp4` |
| Original voiceover | `audio/master.wav` |
| Original restrained paper Foley | `audio/paper-foley.wav` |
| Phrase map and uncorrected ASR evidence | `audio/phrase-beat-map.json`, `audio/transcript-asr.json` |
| Source/rights inventory | `assets/asset-manifest.json`, `research/rights.md` |
| Quality review and machine evidence | `qa/` |

The cover is visibly marked **غلاف مؤقت**. It is not official artwork. The final file is a complete narrated review film; publication artwork and author attribution remain pending. Replace the `.book` inner cover with the official cover image while retaining its dimensions and animation.

## Art direction

A recurring Arabic question mark links ordinary diabetes management, research, accumulated evidence, open questions and a forthcoming book. Ivory dominates, navy provides hierarchy, teal supports explanatory diagrams and orange marks inquiry. Six distinct backgrounds are independently editable SVGs. Photographs are fictional generated illustrations, not patients or named researchers. No journal covers, trial datasets, results or author identities are fabricated.

Read `brief/creative-direction.md`, `brief/visual-system.md`, `brief/decision-record.md`, and `research/reference-analysis.md` for the direction and opening selection. Read `research/scientific-review.md` for scientific boundaries and primary sources.

## Timing

Original WAV duration: **47.725729 seconds**. Composition duration: **49.5 seconds**. A **1.774271-second silent tail** holds the ending. Pause detection and Arabic ASR support phrase alignment; approved written wording corrects ASR spelling. The ASR sidecar is evidence, not publishable copy.

Scene boundaries: 0, 3.5, 10.7, 17, 25.7, 34.1 and 49.5 seconds. The book cover settles at 44.5 seconds, matching the spoken title.

## Edit and render

Use Node 22+ and FFmpeg. Tested CLI: HyperFrames 0.8.119. The project freezes GSAP 3.14.2 locally and ships Noto Sans Arabic with its OFL license. No remote assets are required at render time.

```bash
npx hyperframes@0.8.119 lint .
npx hyperframes@0.8.119 check .
npx hyperframes@0.8.119 preview --background
npx hyperframes@0.8.119 snapshot . --at 1,7,13.8,23.8,30.5,48 -o styleframes/proofs
npx hyperframes@0.8.119 render . --fps 30 --quality delivery --workers 2 -o renders/diabetes-delivery.mp4
```

This environment used software browser rendering and CPU H.264 encoding after the GPU path failed and the user instructed continued execution. On this host, `HYPERFRAMES_BROWSER_PATH=/tmp/chromium` points to the provisioned browser; this path is environment-specific and is not a project dependency. On another host, let HyperFrames discover the installed browser or set its documented browser path.

The actual authored timeline is inlined in `index.html` because HyperFrames compilation did not execute the initial external timeline reliably. `animation/timeline.js` is an exact editable mirror. After changing it, replace the inline `script[data-project-timeline]` content with the updated source. `window.seek(seconds)` and `window.compositionReady` support deterministic proof inspection; HyperFrames owns audio playback and export.

## Status and limits

Consult `qa/delivery-status.json` and `qa/quality-review.md` for verified metadata, actual checks and remaining limitations. A successful technical check does not certify creative taste. The six scenes are independently layered, but these are code-native compositions, not After Effects or Photoshop documents.

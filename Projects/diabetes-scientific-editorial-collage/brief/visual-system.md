# Visual system

## Palette

| Color | Hex | Use |
| --- | --- | --- |
| Warm ivory | #F3F0E8 | Dominant page and background family |
| Academic navy | #172B46 | Arabic type, lines, evidence hierarchy |
| Scientific teal | #8BAFBB | Secondary biomedical diagram forms |
| Burnt orange | #D97335 | Question motif and purposeful connections |
| Paper white | #FAF9F5 | Foreground sheets and publication surface |
| Graphite | #343A40 | Monochrome cutouts and quiet secondary detail |

Ivory occupies most of the image. Orange is a minority accent, never a blanket overlay. Teal distinguishes explanatory biomedical material from the documentary photography.

## Type

Noto Sans Arabic Regular and Bold font files are present in `assets/typography/`. Essential copy is live, separately editable Arabic typography. Use RTL direction and actual shaping; do not space Arabic letters manually. Primary headlines stay brief. Small scientific captions must remain readable at 1920 × 1080 and must never imitate a journal citation or study finding.

Font presence does not certify rights documentation or glyph QA. Record the relevant font license in the asset manifest and inspect representative rendered Arabic text before declaring typography verified. Cover title: «السكري.. هل اقتربت نهاية المرض؟». Cover label: «غلاف مؤقت».

## Layer grammar

1. Environment: pale paper, architectural/domestic suggestion, restrained grids.
2. Composition: broad paper masks and a scene-specific structural form.
3. Subject: independent human or laboratory photographic cutout.
4. Foreground: paper edges, purposeful props and occluding transitions.
5. Explanation: precise Arabic captions, original diagram lines and annotation.

Cutout edges are intentional and consistent. Shadows are separate, restrained and cast down-right from a common above-left light. Texture is gentle and local to material. Avoid embedding grain directly into editable biomedical linework or type.

## Scene differentiation

The opening uses interrupted paper geometry. Human context uses a shallow domestic window. Research uses a magnification field and original cell diagrams. Evidence uses a continuous unfolding strip. Knowledge uses facing pages with generous margins. The reveal uses a book block and a replaceable cover component. The palette unifies them; the background layout does not repeat.

## Engineering

Use SVG for diagrams and masks, alpha PNG for photographic cutouts, and separate backgrounds and shadows. Maintain editable object transforms in compositions. Output target is 1920 × 1080, 30 fps, H.264 review MP4. All meaningful assets need role, dimensions, provenance, rights status and scene associations in the manifest. Reference images are visual study sources only.

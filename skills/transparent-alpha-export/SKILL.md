---
name: transparent-alpha-export
description: Export animations with transparent backgrounds as ProRes 4444 MOV and PNG image sequences. Use when exporting motion graphics cards, lower thirds, or counters for use over live footage in Premiere Pro, DaVinci Resolve, or Final Cut Pro.
---

# Transparent Alpha Export

Configures and renders motion graphics with preserved alpha channels for seamless compositing over live action video footage in non-linear editing systems.

## The Solid Versus Frosted Card Rule

- **Frosted Glass Limitations**: Backdrop filters (such as blur and distortion) calculate their effect from whatever content exists directly behind them in the same render context. When exported over a transparent alpha background, there are no background pixels to sample, turning frosted cards into low-contrast grey cutouts.
- **The Solid Card Solution**: For overlays intended for Premiere Pro or DaVinci Resolve, replace frosted glass cards with solid brand colors or semi-transparent colored panels with explicit edge highlights.

## Professional Export Formats

### 1. Apple ProRes 4444 (MOV)

Highest fidelity industry standard for alpha channel video. Directly importable into Premiere Pro, DaVinci Resolve, and Final Cut Pro without decompression loss.

```bash
ffmpeg -framerate 60 -i frames/frame_%05d.png -c:v prores_ks -profile:v 4 -pix_fmt yuva444p10le renders/overlay.mov
```

### 2. PNG Image Sequences

Lossless frame-by-frame image archive. Ideal for backup, frame-accurate review, or software that does not support ProRes.

```bash
npx hyperframes render . --format png-sequence -o renders/frames
```

## Further Reading

- [references/nle-integration.md](references/nle-integration.md) for timeline configuration in DaVinci Resolve and Premiere Pro.

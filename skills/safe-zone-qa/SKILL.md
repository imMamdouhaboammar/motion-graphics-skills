---
name: safe-zone-qa
description: Verify vertical safe areas, aspect ratio conversions, and button clearance for mobile video platforms. Use when designing videos for Instagram Reels, TikTok, or YouTube Shorts, converting 16 to 9 widescreen to true 9 to 16 vertical re-layouts, or testing for UI button occlusion.
---

# Safe Zone and Platform QA

Guarantees that typography, key statistics, and visual subjects remain completely visible and uncropped across vertical mobile video platforms.

## Mobile Platform Safe Area Coordinates (1080 x 1920)

When targeting Instagram Reels, TikTok, and YouTube Shorts:

```
+------------------------------------------+ (Y = 0)
|       TOP SAFE MARGIN: 170px (10%)       | Status bar, search, back icons
+------------------------------------------+ (Y = 170px)
|                                          |
|                                          |
|            SAFE CONTENT ZONE             |
|                                          |
|    All primary headlines, numbers,       |
|    and focal objects must remain here    |
|                                          |
|                          +---------------+ (X = 918px)
|                          | RIGHT MARGIN: | Like, comment,
|                          | 162px (15%)   | share, audio disc
|                          +---------------+
+------------------------------------------+ (Y = 1536px)
|      BOTTOM SAFE MARGIN: 384px (20%)     | Username, caption, audio pill
+------------------------------------------+ (Y = 1920px)
```

## True Re-Layout Versus Naive Cropping

Converting 16:9 widescreen compositions to 9:16 vertical requires true responsive re-layout rather than center cropping:

1. **Subject Rescaling**: Hero mockups and phone frames scale up 25 to 40 percent to dominate the vertical frame.
2. **Card Clustering**: Multi-column desktop grids collapse into tight vertical stacks.
3. **Typography Re-wrapping**: Wide horizontal text re-wraps into two or three concise lines in the upper third.
4. **No Vacant Voids**: Neither the top ceiling nor the ground floor should exceed 20 percent of total height as empty blank space.

## Automated Safe Zone Overlay Verification

Generate a test frame with semi-transparent platform overlays before publishing:

```bash
python3 tools/scripts/safe-zone-verify.py renders/final.mp4
```

## Further Reading

- [references/platform-metrics.md](references/platform-metrics.md) for detailed platform UI specifications.

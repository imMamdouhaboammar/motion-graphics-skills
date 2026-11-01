# Motion Bible Template

Template for `motion-bible.md` at project root:

```markdown
# Motion Bible: [Project Name]

## 1. Visual Pillars
- Primary Style: [Kinetic Type | Liquid Glass | Editorial Grain | Pop Bold]
- Target Dimensions: 1080x1920 (9:16) / 1920x1080 (16:9)
- Base Frame Rate: 60 fps (30 fps for web preview)

## 2. Typography Contract
- Headline Font: [Font Family, Weight, e.g. Archivo Black 900]
- Body and Data Font: [Font Family, Weight, e.g. Inter 600]
- Readability Rule: Every text card must remain stationary for at least 0.70 seconds.

## 3. Color Palette
- Background: #070707
- Card Surface: rgba(255, 255, 255, 0.05)
- Primary Accent: #FF9900
- Highlight Border: rgba(255, 255, 255, 0.40)

## 4. Physics and Easing Equations
- Card Entrances: gsap.power3.out (0.60s duration, 30px translation)
- Accent Pops: gsap.back.out(2.5) (0.45s duration, 0.6 to 1.0 scale)
- Exit Transitions: gsap.power4.in (0.30s duration)

## 5. Audio and Loudness Contract
- Master Integrated: -14.0 LUFS (+/- 0.5 LUFS)
- True Peak Max: -1.25 dBTP
- Music Ducking Depth: -12.0 dB under spoken dialogue
```

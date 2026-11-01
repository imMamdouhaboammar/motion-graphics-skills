# Studio Spec Ads and Anti-Slop Production Prompts

Production-ready prompts for single-shot continuous brand ads, talking-head enhancements, and anti-slop rendering fixes.

## PROMPT: Continuous Shot Brand Ad

Run in a fresh folder. Replace bracketed terms with your brand facts:

```
Make a 20-second continuous single shot spec ad for [BRAND] with HyperFrames, 1920x1080 at 60 fps, plus a 9:16 vertical re-layout. Do not stop to ask questions: make every creative call yourself and show me the finished renders.

THE VISUAL THREAD:
One continuous glowing line of light connects every scene without hard cuts. It slams in under the logo, guides user attention through UI screens, traces the transit route, wraps the product box as it lands, and hooks back into the final hero brand mark.

THE BEAT SHEET:
1. 0.00 to 1.60s: The slam. The light thread rushes toward the camera and slams into place, revealing the logo.
2. 1.60 to 4.80s: Search interface. The line becomes the input focus line. Text types itself with live autocomplete. Six cards fan out in 3D depth.
3. 4.80 to 7.20s: One tap action. Camera glides to the primary button. The line fills the button. Tap triggers order placed confirmation. Camera flies through the screen.
4. 7.20 to 10.00s: Route animation. The scene becomes a night city from above. The line draws the delivery path to a destination pin.
5. 10.00 to 13.30s: The doorstep. A realistic physical package touches down. The line wraps the box and settles as printed ink.
6. 13.30 to 16.50s: Core typography forms and transforms.
7. 16.50 to 19.20s: Music cuts out for 60ms silence. Hero hit triggers final brand lock with ambient light passing beneath.
8. 19.20 to 21.00s: End card with signature and non-affiliation disclaimer.

AUDIO MIX:
Voice mastered at -16 LUFS. Music ducked 12 dB under words. Tactile clicks on cards and taps, but zero whooshes on basic moves. Climax impact isolated in clean acoustic space. Master at -14 LUFS and -1.25 dBTP.
```

## PROMPT: Clear Liquid Glass Fix

Paste when UI cards look flat:

```
Make the cards clear liquid glass with zero blur so you see straight through them and background elements bend at the edges like physical optics. Use an SVG displacement filter (feTurbulence into feDisplacementMap) as the backdrop-filter, with saturate(180%), a 5% white tint, and a 1px highlight on the top edge. Slide the glass over high-contrast typography so the optical bending is visible in motion. Never place filter, opacity, or clip-path on the card parent container.
```

## PROMPT: 3D Talking Head Enhancement

Paste when talking head video needs visual depth:

```
Add motion graphics around my video at three distinct depths. Place background cards behind me (scaled down 20% and blurred by 4px). Place primary data beside me (sharp at 100% scale). Place foreground elements close to the lens (scaled up 15% with edge blur). Keep all graphics off my face, away from the bottom third captions, and clear of mobile button margins.
```

# Landing page design direction

## Surface mode

Persuade

The page should make a visitor understand three things within the first screen:

1. this is motion graphics for AI coding agents
2. the pack adds creative direction, not only rendering tools
3. the fastest next action is installing the skill pack or opening the repository

## Visual world

A light motion-design worktable

The page borrows from real motion practice rather than generic AI-product UI:

- light architectural studio neutral surface
- crisp slate ink
- deep coral as the main directional accent
- cyan and gold used as small timeline signals
- editorial serif used only for human or directional phrases
- timelines, frame counters, playheads and contact-sheet logic used as functional motifs
- actual rendered films used as proof

No fake dashboard language, decorative terminal wallpaper, generic bento grid, neon AI glow, radial spotlight orbs, purple mesh, or invented interface screenshots

## Palette

- paper: #f8fafc
- paper 2: #f1f5f9
- paper 3: #ffffff
- ink: #070e1b
- muted ink: #475569
- coral: #c2410c
- coral-text: #9a3412
- cyan: #0284c7
- gold: #b45309

Coral carries direction and emphasis (with high contrast coral-text for readable type). Cyan and gold are secondary timeline signals.

## Typography

- body and structural copy: Manrope
- editorial voice: Instrument Serif
- code and time values: native monospace stack

Hero must remain two lines on large screens when space allows.

Body copy should stay around 65 to 75 characters per line.

## Motion thesis

The page should feel like a motion project being directed in front of the visitor.

The authored focal moment is the hero timeline:

brief -> type -> motion -> depth -> render

Supporting motion is restrained:

- scroll progress in the story path
- slow production-engine orbit
- one-time proof-film arrivals
- small quality-rule drift

No fade-in-everything pattern. No scroll hijacking. No moving CTA.

All ambient loops pause offscreen and when the document is hidden.

Reduced motion keeps the composition and removes spatial looping.

## Story

1. Give your AI agent a motion director
2. Explain that the system teaches thinking between frames
3. Split creative direction from production infrastructure
4. Show actual rendered work
5. Explain the anti-slop quality system
6. Reveal the twenty-skill catalog by discipline, with search and filtering
7. Give the visitor a direct map into the current operating docs\n8. End on one install command

## Runtime

The landing page is a static GitHub Pages surface.

GSAP and ScrollTrigger are used for authored motion. The page remains readable when GSAP fails to load.

Videos load only after explicit user action.

## Accessibility

- semantic landmarks
- visible keyboard focus
- high-contrast text
- reduced-motion path
- stable CTA positions
- no hover-only essential information
- video controls remain available
- copy buttons expose state through aria-live

## Anti-slop gates

Reject:

- icon-heading-paragraph card grids
- fake metrics
- gradient text
- decorative glass panels
- generic AI illustrations
- terminal UI used as decoration
- repeating section entrance choreography
- excessive rounded containers
- invented logos or brand marks
- motion that exists only to prove animation skill


## Catalog and documentation behavior

The skills section is an editorial index, not a card wall.

- all current skill folders must be represented
- filters organize by direction, editing, building, publishing and review
- search works without a framework
- every skill row links to its canonical folder in the repository
- the Guide includes a Docs Map for the master operator docs, craft references and video-editing lane
- landing/validate_landing.py must fail CI when the repository skill set and the page drift apart

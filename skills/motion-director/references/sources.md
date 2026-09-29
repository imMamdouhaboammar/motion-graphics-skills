# Sources and further study

These are sources for principles, runtime behavior, and craft.

Use them to deepen decisions, not to paste style blindly.

## HyperFrames

Repository:
https://github.com/heygen-com/hyperframes

Documentation:
https://hyperframes.heygen.com/

Use for:
- HTML-native video composition
- deterministic rendering
- runtime adapters
- catalog reuse
- CLI validation
- media
- audio
- preview and render

Always prefer the installed HyperFrames skill documentation for exact current command contracts.

## GSAP

Timeline:
https://gsap.com/docs/v3/GSAP/Timeline/

MotionPath:
https://gsap.com/docs/v3/Plugins/MotionPathPlugin/

Use for:
- sequencing
- easing
- stagger
- motion paths
- seekable choreography

## IBM Carbon motion

https://carbondesignsystem.com/elements/motion/overview/

Useful ideas:
- productive versus expressive motion
- dynamic duration
- purposeful easing
- choreography
- avoiding decorative bounce

Do not import Carbon's product style into unrelated brand films. Learn the motion reasoning.

## Apple Human Interface Guidelines: Motion

https://developer.apple.com/design/human-interface-guidelines/motion

Useful ideas:
- motion should have purpose
- brevity and precision
- realistic feedback
- accessibility
- motion should not overshadow the experience

This is interface guidance, not a universal film style.

## MDN: reduced motion

https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion

Use for:
- reduced-motion behavior in interactive or preview contexts
- accessibility reasoning

## MDN: SVG viewBox

https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/viewBox

Use for:
- scalable vector composition
- reliable coordinate systems
- logos and diagrams

## MDN: SVG animation

https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/animate
https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/animateMotion
https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/animateTransform

Use as browser reference when native SVG animation is the simplest correct tool.

For complex production choreography, a seekable GSAP timeline may still be easier to control.

## Adobe After Effects text animation

https://helpx.adobe.com/after-effects/desktop/animating-text/text-animation/animating-text.html

Useful as a vocabulary reference for:
- layer transforms
- source text
- text animators
- range-based character animation

Do not mimic After Effects implementation details when the web runtime has a simpler native mechanism.

## Books

The Illusion of Life by Frank Thomas and Ollie Johnston

Useful for:
- timing
- anticipation
- follow-through
- staging
- appeal

The Animator's Survival Kit by Richard Williams

Useful for:
- timing
- spacing
- weight
- arcs
- overlapping action

Animated Storytelling by Liz Blazer

Useful for:
- story structure
- visual development
- motion storytelling

Designing Interface Animation by Val Head

Useful for:
- purposeful motion
- choreography
- interface behavior
- accessibility

## How to use sources

Before a build:

- use sources to define principles
- use the real brand to define style
- use the real script to define content
- use the reference to define motion grammar
- use HyperFrames to avoid rebuilding infrastructure

If a source and the user's explicit art direction conflict, follow the user's direction unless the conflict creates a factual, accessibility, or technical failure.

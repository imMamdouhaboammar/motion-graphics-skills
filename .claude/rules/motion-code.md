# Motion Code Standards

Rules applied when writing or editing animation code (GSAP, CSS animations, Three.js, Canvas).

1. **Easing Discipline**: Never use `linear` easing for UI card motion. Use `power3.out` for organic deceleration, `back.out(2.5)` for punchy pops, and `power4.out` for rapid kinetic typography slams.
2. **Readability Minimum**: Never animate text away before 0.70 seconds of stationary screen time. Viewers on mobile devices require time to parse sentences.
3. **Container Stacking Invariant**: When implementing liquid glass with backdrop filters, never place `opacity`, `filter`, or `clip-path` properties directly on the card parent container. Doing so flattens the stacking context and destroys optical backdrop refraction.
4. **Zero Magic Numbers**: Store all animation durations, delays, and spring stiffness parameters in a shared configuration object or design token ledger.

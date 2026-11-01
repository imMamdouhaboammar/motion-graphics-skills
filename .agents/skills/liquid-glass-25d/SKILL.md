---
name: liquid-glass-25d
description: Implement physical clear liquid glass shaders and 2.5D layered depth in motion graphics. Use when UI cards look flat, when building frosted or clear liquid glass interfaces, or when adding 3D depth planes around a talking head video.
---

# Liquid Glass and 2.5D Layered Depth

Eliminates the flat look in AI generated motion graphics by applying physical glass refraction shaders and true multi-plane depth compositing.

## The Clear Liquid Glass Shader Formula

Standard CSS blur produces a dull, frosted appearance that obscures underlying content. Clear liquid glass uses real optical refraction:

```css
.liquid-glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: url(#glass-disp) saturate(180%);
  border-top: 1px solid rgba(255, 255, 255, 0.4);
  border-left: 1px solid rgba(255, 255, 255, 0.2);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 28px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
}
```

Accompanying SVG displacement filter:

```html
<svg class="glass-filters" style="display: none;">
  <defs>
    <filter id="glass-disp" x="-20%" y="-20%" width="140%" height="140%">
      <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" result="noise" />
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="12" xChannelSelector="R" yChannelSelector="G" />
    </filter>
  </defs>
</svg>
```

> **Cardinal Rule**: Never place `opacity`, `filter`, or `clip-path` properties directly on the card parent container, as this flattens the stacking context and disables the backdrop displacement.

## Talking Head 3D Depth Setup

When integrating motion graphics with a human speaker in frame:

1. **Clean Subject Separation**: Cut out the speaker with a high-contrast matte or alpha mask.
2. **Three Discrete Depth Planes**:
   - **Far Plane (Background)**: Positioned behind the speaker, scaled down 20%, blurred by 4px to simulate depth of field.
   - **Mid Plane (Speaker Anchor)**: Positioned alongside the speaker, perfectly sharp at 100% scale.
   - **Near Plane (Foreground)**: Positioned close to the lens, scaled up 15%, blurred by 8px on edges.
3. **Face Protection**: Keep all graphics outside the speaker face bounding box and maintain at least 15% distance from the eyes.

## Further Reading

- [references/glass-refraction.md](references/glass-refraction.md) for optical refractive index adjustments.

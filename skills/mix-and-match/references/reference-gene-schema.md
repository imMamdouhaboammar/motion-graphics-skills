# Reference gene schema

Use this schema to turn references into comparable creative parts without reducing them to style labels.

## Gene categories

A reference can contribute zero or more genes in each category.

### Structure

Look for beat count, escalation, reset points, reveal order, and ending behavior.

### Composition

Look for focal hierarchy, negative space, density, alignment, crop, foreground and background relationships.

### Typography

Look for scale relationships, alignment, serif or sans roles, word versus line animation, width, weight, cropping, and mixed-script behavior.

### Image treatment

Look for cutouts, full bleed, masks, image grade, edge treatment, collage, documentary framing, and subject placement.

### Material

Look for paper, glass, ink, chrome, fabric, light, grain, photocopy, print, hard geometry, or soft physical surfaces.

### Motion

Look for reveal, transform, handoff, morph, path, stack, fold, wipe, occlusion, draw, orbit, parallax, or camera movement.

### Transition

Look for the visual carrier between scenes, such as shape, direction, color field, object, mask, line, light, or camera.

### Spatial

Look for flat versus deep composition, camera distance, perspective, occlusion, layer count, and scene geography.

### Color

Look for color proportion and function, not just hex values. Record whether accent is structural, emotional, semantic, or decorative.

### Sound

Look for whether sound leads motion, punctuates structure, creates contrast, or stays ambient.

### Metaphor

Look for the conceptual device that turns the message into a visual action.

### Emotional temperature

Use concrete behavioral language such as restrained, abrupt, playful, ceremonial, tense, clinical, tactile, or intimate.

## Gene record

Use this shape:

```json
{
  "category": "transition",
  "observation": "a vertical black bar wipes the frame and becomes the next scene edge",
  "principle": "one persistent boundary can carry continuity between unrelated scenes",
  "protected": [
    "exact bar proportions",
    "exact scene sequence"
  ],
  "transform": "turn the boundary into an audio playhead that becomes a typographic baseline"
}
```

The `principle` field is the reusable creative gene.

The `protected` field records what must not survive into the new work.

The `transform` field is a hypothesis, not a commitment.

## Gene pool file

The helper script accepts JSON shaped like this:

```json
{
  "brief": "A short Arabic promo for a code-driven motion skill pack",
  "references": [
    {
      "id": "A",
      "domain": "motion-design",
      "role": "primary",
      "genes": {
        "rhythm": [
          "three fast beats followed by one clean hold"
        ],
        "typography": [
          "one dominant phrase carries each scene"
        ]
      }
    },
    {
      "id": "B",
      "domain": "editorial-print",
      "role": "primary",
      "genes": {
        "material": [
          "rough cutout edges against clean type"
        ],
        "composition": [
          "large crop creates tension with negative space"
        ]
      }
    },
    {
      "id": "W1",
      "domain": "wayfinding",
      "role": "wildcard",
      "genes": {
        "transition": [
          "one directional line guides attention across states"
        ],
        "spatial": [
          "information is organized by route rather than cards"
        ]
      }
    }
  ]
}
```

The tool does not understand aesthetics. It only creates source-balanced gene pairings and reports dominance warnings.

## Provenance

Keep source IDs stable from extraction through the final `mix-brief.md`.

For every selected principle, retain:

- source ID
- source title or short description
- source URL or local filename when available
- category
- transformed use in the project

Never invent a source URL or claim that a discovered reference was reviewed when it was not.

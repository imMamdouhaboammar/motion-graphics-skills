---
name: mix-and-match
description: Use when a motion concept must be original while drawing from two or more references, when supplied references feel too similar or derivative, or when the user asks to combine visual languages, cross-pollinate inspiration, or explore wildcard references. Do NOT use for single-reference analysis, literal imitation, or final render QA.
---

# Mix and Match

## Purpose

Mix and Match is the concept recombination skill for motion work.

Its job is not to average references. Its job is to deconstruct them into transferable creative genes, connect distant genes, mutate those connections for the current brief, and hand an original direction to `motion-director`.

A reference is evidence, not a template.

The brief stays in control. References contribute principles. No source owns the final composition.

## Use modes

Choose one mode at intake.

### User curated

Use only the references supplied by the user.

Choose this when the user has a deliberate reference set or when external discovery is not allowed.

### Assisted discovery

The user may provide one reference and authorize the agent to find the rest.

Use this when the user wants broader inspiration but has not assembled a reference set.

### Hybrid, default

Ask for 2 to 6 primary references, then add 1 to 3 wildcard references only when they increase creative distance or solve a missing dimension.

Wildcards should usually come from a different visual discipline, not from another near-identical motion reel.

Read `references/wildcard-discovery.md` before external discovery.

## Intake

Collect only what changes the creative search:

- communication job
- audience
- platform and duration
- required brand rules
- 2 to 6 primary references when available
- what the user likes or dislikes in each reference, if known
- whether external discovery is allowed
- any elements that must not be borrowed

If `brand.md` or `MOTION.md` exists, read it first.

If the user supplied fewer than two references in Hybrid mode, ask for one more reference unless they explicitly authorize Assisted discovery.

Do not ask the user to classify every reference. The skill can do that.

## Reference genome

Analyze each reference independently before mixing anything.

Extract genes across these dimensions when present:

- structure and narrative rhythm
- composition and hierarchy
- typography behavior
- image or footage treatment
- material and texture
- motion mechanics
- transition logic
- camera and spatial behavior
- color strategy
- sound relationship
- metaphor or conceptual device
- emotional temperature

For each gene, record four fields:

1. Observation: what is visibly happening
2. Transferable principle: the abstract rule worth learning
3. Protected specifics: what must not be copied
4. Transformation opportunity: how the principle could change in this project

Do not write vague genes such as `premium`, `cool`, `Apple-like`, or `cinematic` without describing the observable mechanism behind them.

Read `references/reference-gene-schema.md` for the full schema and examples.

## Separate principles from surfaces

The surface is usually the dangerous part to copy.

| Surface observation | Transferable principle |
|---|---|
| Giant red word covers half the frame | one dominant typographic mass controls the frame |
| Paper cutout person slides behind text | foreground occlusion creates depth and a scene handoff |
| Camera pushes through a circular logo | one geometric aperture becomes a spatial transition |
| Three fast cuts followed by silence | acceleration earns a quiet reset |

Carry the principle forward. Rebuild the surface for the current brief.

## Wildcard references

In Hybrid or Assisted mode, search for wildcards only after the primary references are decomposed.

A wildcard should fill a creative gap or introduce productive tension.

Good wildcard domains include:

- architecture
- editorial design
- packaging
- industrial design
- theatre and set design
- choreography
- kinetic sculpture
- maps and wayfinding
- scientific diagrams
- printmaking
- fashion editorial
- mechanical interfaces
- title design
- photography

Avoid collecting more examples from the same visual neighborhood simply because they are easy to find.

The default cap is 3 wildcard references.

## Build the gene pool

Create a compact JSON gene pool using the schema in `references/reference-gene-schema.md`.

When there are enough extracted genes, run:

```bash
python scripts/mix_matrix.py gene-pool.json --recipes 3
```

The tool creates combination scaffolds. It does not decide what is creative.

Use it to reduce one-source dominance and force cross-reference pairings that the model might otherwise ignore.

If the tool is unavailable, reproduce the same constraints manually. Do not add a dependency just to replace this small helper.

## Cross-pollinate before ideating

For each recipe, combine genes from distinct sources and then mutate them.

Useful mutation operations:

- material swap: express a digital behavior as paper, glass, light, fabric, ink, or physical space
- scale shift: move a micro interaction into a full-frame event or compress an environment into one object
- time remap: convert a slow ritual into rapid beats or let a fast mechanism become a held reveal
- spatialize: turn a flat layout relationship into depth, occlusion, camera, or path
- flatten: turn a complex spatial idea into graphic type, shape, or mask
- invert: reverse foreground and background, reveal and conceal, build and erase, dense and quiet
- role swap: let typography perform the job an image performed, or let an object perform the job typography performed
- metaphor shift: keep the mechanic but replace its meaning with one rooted in the current brief
- constraint transfer: borrow a rule such as one color, one lens, one material, or one motion family without borrowing the original layout

Every adopted gene should change role, material, scale, timing, meaning, or context before it becomes part of the final direction.

Read `references/creative-recombination.md` when the first combinations feel obvious.

## Generate three concept hypotheses

Produce three genuinely different hypotheses from the gene pool.

They should differ by mechanism, not by palette.

### Coherent route

Lowest creative risk. Combines compatible genes into one clear visual system.

### Tension route

Pairs genes that normally do not belong together, but can be reconciled by the brief.

### Wildcard route

Uses at least one cross-domain wildcard as a structural idea, not decoration.

For each hypothesis define:

- one-sentence concept
- primary visual mechanism
- inherited principles and source IDs
- mutation applied to each inherited principle
- recurring transition family
- what remains stable across scenes
- what makes the direction belong to this brief
- what the direction refuses to do

## Creative distance audit

Do not assign a fake originality percentage.

Instead audit observable risks.

A concept fails when any of these are true:

- one reference supplies most of the important genes
- the final scene order mirrors one reference
- a distinctive layout or branded object survives with only cosmetic changes
- references are combined as adjacent fragments instead of becoming one system
- wildcard material is decorative and does not change the concept
- the result can be described only as `Reference A plus Reference B`
- the brief became secondary to the inspiration

A concept passes creative distance when:

- at least two independent sources materially affect the direction
- no single source dominates the visual grammar
- important borrowed principles are transformed in role or context
- the result has one coherent motion thesis
- the concept can be explained without naming the references
- removing the references would still leave a clear project-specific idea

The helper script reports source spread. Treat that as a dominance check, not an originality score.

## Selection

Choose the strongest concept against the brief using:

1. communication clarity
2. project specificity
3. conceptual coherence
4. transition potential
5. creative distance
6. production feasibility

Do not choose the strangest route by default.

When two routes are close, prefer the one with a clearer repeatable mechanism and fewer decorative exceptions.

## Handoff to Motion Director

Write `mix-brief.md` with:

- project brief
- primary references
- wildcard references
- reference genome
- three concept hypotheses
- rejected derivative patterns
- selected direction
- creative distance audit
- source provenance

Then hand the selected direction to `motion-director`.

`motion-director` owns the final motion thesis, frame system, timing, production routing, rendering, and QA.

If this skill was invoked from `motion-director`, return the selected direction to the parent workflow and continue without creating a competing production pipeline.

## Hard rules

- Do not trace layouts
- Do not reproduce exact scene sequences
- Do not reuse protected logos, illustrations, copy, characters, or campaign marks from references
- Do not let color swapping count as transformation
- Do not let one reference quietly become the master template
- Do not search endlessly for inspiration
- Do not add wildcard references after a coherent concept has already passed the audit
- Do not confuse randomness with creativity
- Do not invent provenance
- Do not call a collage of recognizable fragments an original system

## Completion gate

The skill is complete only when:

- every reference has a genome entry
- protected specifics are explicit
- at least three concept hypotheses were considered
- the selected route passes the creative distance audit
- source provenance is recorded
- `mix-brief.md` is ready for `motion-director`

If any item is missing, the concept is not ready for production.

# Neural links

The pack is a graph of responsibilities, not a bag of prompts.

`motion-director` owns shared truth and the overall film. Specialist skills receive a bounded problem, return a bounded result, and do not silently reset earlier decisions.

## The route is explicit

Before broad production work, build a route with:

```bash
python "$MOTION_DIRECTOR_DIR/scripts/route_motion.py" --context motion-route.json
```

The router reads `router/skill-network.json` and the skills installed in the current pack.

Keep the returned route available through the session.

Do not improvise a different skill order unless new evidence changes the task classification.

## Typed links

### prepares

Creates truth needed by later stages.

Example:

`motion-director -> brand-intake -> motion-director`

### specializes

Solves one narrow production problem.

Example:

`motion-director -> animated-chart -> motion-director`

The specialist does not become the new master skill.

### augments

Adds a capability without owning the whole film.

Examples:

- `mix-and-match` adds creative recombination
- `work-guard` adds process reliability

### reviews

Evaluates an artifact produced by the production route.

Example:

`motion-director -> video-review-loop -> motion-director`

### fallback

Used only when a preferred optional node is unavailable.

The router must say which capability was missing and what fallback is being used.

## Shared truth packet

Every specialist inherits the smallest useful truth set.

Typical fields:

- approved copy
- verified facts
- brand rules
- MOTION.md
- motion thesis
- beat map
- delivery contract
- reference constraints
- existing source artifacts

Do not ask a specialist to rediscover facts already established by an earlier stage.

## Delta return

A specialist returns only what it learned or produced.

Typical return:

- decisions made
- files or artifacts created
- assumptions introduced
- risks found
- facts that remain unresolved
- next required gate

This prevents context inflation and contradictory parallel plans.

## Director re-entry

For broad film work, every specialist returns to `motion-director`.

The director decides whether the returned result:

- is accepted
- needs another specialist
- changes the route
- changes MOTION.md
- requires a rerender
- triggers final review

A specialist may finish independently only when the user asked for that narrow artifact alone.

## Route changes

Re-route only when one of these changes:

- deliverable class
- truth or brand readiness
- reference strategy
- runtime capability
- final artifact availability
- a hard review finding
- a tool or skill becomes unavailable

Do not re-route because a different effect looks interesting.

## Optional nodes

The graph can name capabilities that are not installed.

Current optional examples include:

- `mix-and-match`
- `work-guard`

When absent:

1. record the capability as skipped
2. use the documented fallback
3. do not pretend the optional tool ran

When installed later, the router discovers it automatically.

## Handoff anti-patterns

Do not:

- run every skill just because it exists
- ask two specialists to own the same decision
- restart brand discovery inside each specialist
- let a review skill rewrite the creative brief
- let a renderer decide art direction
- let a failed optional node collapse the whole route
- hide why a node was chosen

The route should be understandable from its JSON alone.

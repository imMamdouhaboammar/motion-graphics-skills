# Subagent dispatch — harness adapter

The video workflows (`product-launch-video` / `faceless-explainer` / `pr-to-video` / `motion-graphics` / `general-video`) describe subagent dispatch in harness-neutral verbs. This file maps those verbs to the primitives of whatever agent harness you are running on. Read it once per run, before the first dispatch; everything else in the workflows (dispatch packets, file artifacts, exit-code gates, Resume tables) is harness-independent and needs no translation.

## The contract (identical on every harness)

- **DISPATCH(role_file, assigned_packets, dispatch_context)** — start one child agent whose prompt contains the **complete role file**, **every assigned packet**, and **all dispatch-context fields specified by that workflow**, copied verbatim (never digested or paraphrased). Role and packets may be pasted in full or supplied as readable absolute file paths with instructions to read them first, as the workflow allows. Motion-graphics roles use the workflow's plan/design/build inputs rather than frame packets. There is no required `## Dispatch context` heading: include the actual fields the workflow enumerates, such as `PROJECT_DIR`, assigned `frame_id`(s), canvas, confirmed-sketch status, and caption status/keep-out band when required. Never rely on the child seeing your conversation, memory, or skills — the prompt and the files on disk are its entire world.
- **Parallel fan-out** — when a step says "start N workers in parallel", the workers are mutually independent (no ordering, no shared state beyond the filesystem). Run as many concurrently as your harness allows.
- **WAIT** — a step's completion criterion is always **the expected artifact existing on disk** (e.g. `compositions/<scene-id>.html`), never the harness's completion notification (some harnesses deliver results best-effort). After waiting, verify the artifacts; a missing artifact means that child failed — re-dispatch it once with the same prompt before surfacing an error.

## Concurrency cap → batching rule (cap never changes scope)

A harness concurrency limit **reduces parallelism, not work**: every assigned scene still gets built, with the available slots processing the workflow-defined worker batches. Preserve the workflow's packet grouping: general-video assigns 2–3 scenes per worker, pr-to-video balances packets across at most three workers, and product-launch-video / faceless-explainer assign one frame per worker.

- When the harness queues excess children internally, submit **all planned workers at once** and let the queue drain.
- Harness hard-caps active children (e.g. OpenClaw `maxChildrenPerAgent`) → dispatch in **waves of the cap size**: start `cap` workers, wait for their artifacts, start the next wave, until every required per-scene artifact exists. Example for a one-frame-per-worker workflow: 9 scenes on a cap-3 harness = 3 waves of 3 — never drop scenes, never change the workflow's packet grouping just to fit the cap.

## Harness mapping

Use the current harness's native delegation and waiting tools when they are available. The workflow contract stays the same:

- **DISPATCH** sends the complete role file, every assigned packet, and the workflow-defined dispatch context to one worker.
- **Parallel fan-out** starts independent workers concurrently up to the harness limit.
- **WAIT** verifies the expected artifacts on disk, not only a completion notification.
- **Re-dispatch** starts a fresh worker with the same context plus the gate failure.

When native delegation is unavailable, use the existing fallback ladder: launch headless CLI workers that share the project filesystem, then fall back to inline serial execution.

On Codex, native delegation requires the user's explicit permission. Fold a one-line request into the workflow's first existing user pause before dispatch; a standing grant in `AGENTS.md` or the kickoff prompt also counts. Without it, use the fallback ladder rather than silently skipping work.

## Vocabulary mapping

- A request to work "in the background" means dispatch concurrently when the harness supports it.
- Load a named skill through the harness's skill mechanism, or read `<skills-root>/<skill>/SKILL.md` directly.
- Map generic read, write, edit, and shell verbs to the current harness's equivalent tools.

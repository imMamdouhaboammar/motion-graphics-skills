# Motion Work Guard Design

## Goal

Add a small reliability guard for long-running motion-production commands so Claude Code can contain hangs, preserve diagnostics, clean up owned process trees, and retry only operations explicitly declared safe.

The guard is a runtime safety layer. It is not an autonomous code fixer.

## Problem

Motion production regularly launches processes that can appear alive while making no useful progress:

- Playwright audits waiting forever on page readiness
- browser tools blocked on a promise or thenable that never settles
- render or verification commands that stop producing useful progress
- child processes that outlive a failed parent
- wrappers that lose the original stdout, stderr, exit status, or failure context
- safe validation commands that could recover from one stale process but currently require manual intervention

The motivating incident was a page readiness promise that returned a paused GSAP timeline. Because GSAP timelines expose a `then` method, the value was treated as a thenable. Awaiting the readiness promise could therefore remain pending indefinitely even though fonts, images, and the timeline itself were otherwise available.

## Scope

Create:

- `skills/motion-director/scripts/work_guard.py`
- `skills/motion-director/scripts/test_work_guard.py`
- `skills/motion-director/scripts/browser-readiness-probe.cjs`
- `skills/motion-director/references/reliability-guard.md`

Update:

- `skills/motion-director/SKILL.md`
- `Failure-lessons/render-pipeline.md`
- `Failure-lessons/lessons-index.md`
- `.github/workflows/ci.yml`

Do not add a runtime dependency.

## Public command

Primary interface:

```bash
python "$MOTION_DIRECTOR_DIR/scripts/work_guard.py" run \
  --stall-timeout 45 \
  --hard-timeout 180 \
  --retry-safe 1 \
  --probe-command "node browser-readiness-probe.cjs http://localhost:8766/index.html" \
  -- node clip-audit.js http://localhost:8766/index.html
```

`--retry-safe N` is both an explicit idempotency declaration and a retry count. Without it, timeout recovery stops after one attempt.

Optional:

- `--heartbeat PATH`: mtime changes count as progress
- `--probe-command STRING`: diagnostic command executed when a timeout is detected, before the owned process tree is terminated
- `--heal-command STRING`: recovery hook executed after containment and before a safe retry
- `--hook-timeout SECONDS`
- `--kill-grace SECONDS`
- `--run-root PATH`

No command is retried unless the caller explicitly uses `--retry-safe`.

## Runtime model

For each attempt:

1. launch the command in its own process group
2. stream stdout and stderr to the terminal and per-attempt log files
3. track last useful activity from stdout, stderr, and an optional heartbeat file
4. enforce optional stall and hard deadlines
5. on timeout, record the failure class and run the optional diagnostic probe
6. terminate the owned process group with TERM, wait for the grace period, then use KILL if required
7. run the optional heal hook
8. retry only when `--retry-safe` permits another attempt
9. write a machine-readable summary for the run

Normal non-zero child exits are returned directly and are not silently retried.

Ctrl+C must terminate the owned child process group and exit 130.

## Evidence directory

Default:

`.motion-guard/runs/<timestamp>-<pid>/`

Contains:

- `command.json`
- `attempt-N.stdout.log`
- `attempt-N.stderr.log`
- `attempt-N.json`
- optional `attempt-N.probe.log`
- optional `attempt-N.heal.log`
- `summary.json`

No secrets are intentionally collected beyond what the wrapped command itself emits.

## Browser readiness probe

`browser-readiness-probe.cjs` is optional and uses Playwright from the active project when available. The guard itself does not depend on Playwright.

The probe reports plain JSON covering:

- navigation / DOM readiness
- font readiness
- image decode/completion state
- whether `window.__ready` exists
- whether `window.__ready` is thenable
- whether it settles inside the probe timeout
- whether the value looks like a GSAP timeline or timeline-like object when observable

The probe must never return the inspected `window.__ready` object itself, because returning a thenable from `page.evaluate` can reproduce the same deadlock.

Exit codes:

- 0: ready
- 1: page loaded but readiness remains blocked or assets are not ready
- 2: usage, dependency, or navigation failure

## Recovery policy

The guard may recover process state. It must not edit source code.

Allowed recovery examples:

- terminate a stale browser or render process owned by the guarded command
- run a caller-provided cache cleanup or local server restart hook
- retry a read-only audit, snapshot, test, or render probe when explicitly marked safe

Never automatically retry destructive or externally visible actions such as deploy, publish, upload, push, purchase, or mutation of remote state unless the caller explicitly assumes responsibility by marking the exact command safe.

## Progress policy

Silence alone is not universally a hang.

- stall detection is disabled when `--stall-timeout 0`
- long silent renders should use a heartbeat or only a hard deadline
- render progress should come from actual frame/progress output or a heartbeat, not growing output file size
- hard timeout remains an independent upper bound

## Failure classification

The summary uses concrete classes:

- `success`
- `child-exit`
- `stall-timeout`
- `hard-timeout`
- `interrupted`
- `launch-error`

Probe output is evidence, not an automatic root-cause claim.

## Tests

Regression tests must prove:

- success preserves output and exits 0
- non-zero child exit propagates and does not retry
- silent stall is contained
- noisy process still hits the hard deadline
- heartbeat prevents a false stall
- stale heartbeat allows a stall timeout
- safe retry can recover on a later attempt
- no retry occurs without explicit safe-retry declaration
- probe and heal hooks are captured
- Ctrl+C contains the child and exits 130
- summary files remain after failure

The browser probe gets a syntax/help smoke test in CI without requiring Playwright.

## Readiness invariant

A page readiness promise must resolve to plain state, not an animation object or another accidental thenable.

Safe pattern:

```js
window.__ready = (async () => {
  await loadEverything();
  buildTimeline();
  return undefined;
})();
```

Unsafe pattern:

```js
window.__ready = (async () => {
  await loadEverything();
  return buildTimeline(); // may be a GSAP thenable
})();
```

## Non-goals

- no daemon
- no job queue
- no remote monitoring
- no process resurrection after machine failure
- no automatic source-code repair
- no replacement for HyperFrames diagnostics
- no retry of arbitrary commands by default

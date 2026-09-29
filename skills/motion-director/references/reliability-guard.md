# Reliability guard

Use this reference for long-running or hang-prone production commands.

The guard is a process supervisor, not a code repair agent. It contains a bad run, preserves evidence, runs bounded diagnostic or recovery hooks, and retries only when the caller explicitly declares the wrapped command safe.

## Resolve the installed skill directory first

The scripts belong to the installed `motion-director` skill.

Resolve the directory that contains the active `motion-director/SKILL.md` and store it as `MOTION_DIRECTOR_DIR`.

Do not assume the current project working directory contains this repository.

The bundled tools are:

- `$MOTION_DIRECTOR_DIR/scripts/work_guard.py`
- `$MOTION_DIRECTOR_DIR/scripts/browser-readiness-probe.cjs`

## When to use it

Use the guard when a command can block the rest of the production session and has a meaningful timeout or progress signal.

Good candidates:

- Playwright audits
- browser readiness checks
- deterministic still or snapshot tools
- HyperFrames checks that can block on a browser/runtime dependency
- local render probes
- ffprobe and verification wrappers
- long test or validation commands
- local dev-server dependent checks

Do not wrap every trivial command.

A short `ls`, `cat`, `git status`, or deterministic local file transform does not need a supervisor.

## Core command

```bash
python "$MOTION_DIRECTOR_DIR/scripts/work_guard.py" run \
  --stall-timeout 45 \
  --hard-timeout 180 \
  --retry-safe 1 \
  -- command arg1 arg2
```

The first `--` ends guard options. Everything after it is the exact child argv.

The guard does not invoke a shell for the wrapped command.

## Timeout meanings

### Stall timeout

`--stall-timeout N` means no stdout, stderr, or heartbeat progress for N seconds.

Use it when silence is evidence of a stuck operation.

Set it to `0` when a healthy operation can legitimately stay silent for a long time.

### Hard timeout

`--hard-timeout N` is an absolute per-attempt ceiling.

Output does not extend it.

Use it as the independent upper bound for browser tools, tests, and bounded probes.

### Heartbeat

Use `--heartbeat PATH` when the child is healthy but intentionally quiet.

A change in heartbeat file mtime or size counts as progress.

The wrapped process owns the heartbeat. The guard only observes it.

## Safe retry contract

No timeout is retried by default.

```bash
--retry-safe 1
```

means:

- the caller declares the exact child command idempotent or otherwise safe to repeat
- one retry is allowed after a stall or hard timeout

A bare `--retry-safe` also means one retry.

Normal non-zero child exits are returned directly and are not silently retried.

Good retry candidates:

- read-only browser audit
- snapshot
- lint
- local test
- read-only verification
- render probe writing to scratch output

Do not automatically retry:

- deploy
- publish
- upload
- purchase
- remote mutation
- `git push`
- destructive file operations
- any command whose first attempt may have partially completed an external action

## Diagnostic probe

A probe runs after timeout detection and before the stuck process group is terminated.

Example:

```bash
python "$MOTION_DIRECTOR_DIR/scripts/work_guard.py" run \
  --stall-timeout 45 \
  --hard-timeout 180 \
  --retry-safe 1 \
  --probe-command "node '$MOTION_DIRECTOR_DIR/scripts/browser-readiness-probe.cjs' http://localhost:8766/index.html --timeout 3000" \
  -- node clip-audit.js http://localhost:8766/index.html
```

The probe is evidence gathering. A failed probe does not become an invented root-cause claim.

Probe output is saved to `attempt-N.probe.log`.

## Heal hook

A heal hook runs only after containment and only when another safe retry is available.

Example:

```bash
--heal-command "node tools/restart-preview.cjs"
```

Use it for bounded local recovery such as:

- restart a local preview server
- remove a stale local lock owned by the project
- recreate a scratch directory
- reset a local disposable browser cache

If a configured heal hook fails, the guard stops instead of retrying through a failed recovery step.

Hook strings are parsed with `shlex.split`. Shell metacharacters are not interpreted. When a shell is genuinely required, call it explicitly, for example `bash -lc '...'`.

## Process containment

Each attempt runs in its own process group.

On timeout or Ctrl+C the guard:

1. sends TERM to the owned group
2. waits for `--kill-grace`
3. sends KILL when required

It does not scan the machine and kill unrelated browser, Node, ffmpeg, or Python processes.

This boundary is important. Broad commands such as `pkill node` or `killall chromium` are not a recovery strategy.

## Evidence

Default evidence path:

```text
.motion-guard/runs/<timestamp>-<pid>/
```

Typical files:

- `command.json`
- `attempt-1.stdout.log`
- `attempt-1.stderr.log`
- `attempt-1.json`
- `attempt-1.probe.log`
- `attempt-1.heal.log`
- `summary.json`

Keep these outside final delivery paths.

The guard records what the wrapped command emits. Do not pass secrets on command lines or print them to stdout or stderr.

## Browser readiness probe

The optional browser probe uses Playwright from the active project.

It checks:

- DOM state
- `document.fonts.ready`
- pending or failed images
- whether `window.__ready` exists
- whether `window.__ready` is thenable
- whether it settles inside the probe window
- whether the directly observed value looks like a GSAP timeline
- keys exposed by `window.__timelines` when present

The probe always returns a plain JSON object from `page.evaluate`.

It never returns `window.__ready` itself.

That rule prevents the diagnostic tool from reproducing a thenable deadlock.

Probe exit codes:

- 0: observed readiness is healthy
- 1: page loaded but readiness is blocked
- 2: usage, dependency, browser launch, or navigation failure

## The GSAP thenable trap

JavaScript promises assimilate returned thenables.

A GSAP timeline exposes a `then` method. Returning a paused timeline from an async readiness function can therefore keep the outer readiness promise pending.

Unsafe:

```js
window.__ready = (async () => {
  await loadEverything();
  return buildTimeline();
})();
```

Safe:

```js
window.__ready = (async () => {
  await loadEverything();
  buildTimeline();
  return undefined;
})();
```

The readiness promise answers one question only: can deterministic tools start?

Do not use its resolved value as a carrier for timelines, renderers, players, or other thenable objects.

## Suggested policies

These are starting policies, not universal truths.

| Command class | Stall | Hard | Retry |
|---|---:|---:|---|
| browser audit | 45 s | 180 s | 1 when read-only |
| local validation/test | 60 s | 300 s | 1 when idempotent |
| snapshot/still probe | 60 s | 300 s | 1 when output is scratch |
| full render | 0 unless heartbeat exists | project-specific | only when scratch output makes replay safe |
| remote publish/deploy | do not infer | project-specific | 0 by default |

Choose limits from measured normal runtime when evidence exists.

## Failure interpretation

The guard uses concrete classifications:

- `success`
- `child-exit`
- `stall-timeout`
- `hard-timeout`
- `interrupted`
- `launch-error`

A timeout says where work stopped. It does not by itself explain why.

Use the captured probe and logs to diagnose the root cause before changing production code.

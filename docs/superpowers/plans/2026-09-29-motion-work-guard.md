# Motion Work Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a dependency-free runtime guard that contains hung production commands, preserves evidence, and performs bounded safe recovery.

**Architecture:** A Python stdlib supervisor owns one child process group per attempt and records activity from output plus an optional heartbeat. Timeout handling runs bounded diagnostic/recovery hooks, kills only the owned process tree, and retries only with explicit safe-retry authorization. An optional Node probe diagnoses browser readiness using the project's Playwright installation.

**Tech Stack:** Python 3 standard library, Node.js CommonJS for the optional browser probe, existing GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-29-motion-work-guard-design.md`

## Global Constraints

- no new runtime dependency
- no automatic source-code modification
- no automatic retry without `--retry-safe`
- preserve stdout, stderr, attempt metadata, and final summary
- terminate only the process group launched by the guard
- browser probe must return plain JSON and never return an inspected thenable object

## Review Focus

- process-group cleanup when the child forks another sleeping child
- timeout behavior when a command prints continuously
- heartbeat mtime granularity and false-stall prevention
- hook commands that themselves hang
- interruption while a probe, heal hook, or child command is active

---

### Task 1: Guard process lifecycle and evidence

**Files:**
- Create: `skills/motion-director/scripts/test_work_guard.py`
- Create: `skills/motion-director/scripts/work_guard.py`

**Interfaces:**
- Consumes: CLI arguments followed by `-- <command...>`
- Produces: wrapped exit code plus run evidence under `.motion-guard/runs/`

- [ ] Write failing tests for success, non-zero exit, stall timeout, hard timeout, and retained summary
- [ ] Run the test file and confirm those tests fail because the guard does not exist
- [ ] Implement process-group launch, stream capture, deadlines, containment, and summary output
- [ ] Run the targeted test file and confirm the slice passes

### Task 2: Add heartbeat, hooks, retry, and interruption behavior

**Files:**
- Modify: `skills/motion-director/scripts/test_work_guard.py`
- Modify: `skills/motion-director/scripts/work_guard.py`

**Interfaces:**
- Consumes: `--heartbeat`, `--probe-command`, `--heal-command`, `--retry-safe`, `--hook-timeout`, `--kill-grace`
- Produces: bounded recovery attempts and hook logs

- [ ] Write failing tests for active heartbeat, stale heartbeat, safe retry, no implicit retry, hook logging, child-tree cleanup, and Ctrl+C
- [ ] Run targeted tests and confirm the new tests fail for missing behavior
- [ ] Implement the minimal behavior needed for those tests
- [ ] Run the full guard test file and confirm all tests pass

### Task 3: Browser readiness diagnosis

**Files:**
- Create: `skills/motion-director/scripts/browser-readiness-probe.cjs`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: URL and optional `--timeout`
- Produces: plain JSON readiness diagnostics and exit code 0, 1, or 2

- [ ] Add CI smoke checks for Node syntax and `--help`
- [ ] Implement the optional Playwright probe without adding Playwright as a package dependency
- [ ] Verify syntax/help locally in CI

### Task 4: Agent routing and failure lesson

**Files:**
- Create: `skills/motion-director/references/reliability-guard.md`
- Modify: `skills/motion-director/SKILL.md`
- Modify: `Failure-lessons/render-pipeline.md`
- Modify: `Failure-lessons/lessons-index.md`

**Interfaces:**
- Consumes: long-running production operations
- Produces: clear rules for when the guard is required and how to configure it

- [ ] Document command classes, safe retry rules, heartbeat guidance, and browser probe usage
- [ ] Route hang-prone browser/audit/render verification work through the guard where appropriate
- [ ] Record the accidental GSAP-thenable readiness deadlock as a reusable failure lesson
- [ ] Run repository skill validation

### Task 5: Whole-branch verification and review

**Files:**
- Review all changed files

**Interfaces:**
- Consumes: complete PR diff
- Produces: verified branch ready for review

- [ ] Run guard tests
- [ ] Run browser probe syntax/help smoke checks
- [ ] Run `bash validate-skills.sh`
- [ ] Run correctness/spec review
- [ ] Run Ponytail over-engineering review and remove unnecessary machinery
- [ ] Open the PR only after the verification evidence is green

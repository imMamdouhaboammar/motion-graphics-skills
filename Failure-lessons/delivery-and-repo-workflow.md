# Delivery and repository workflow

Lessons about how finished work reached the repository and the client, as opposed to how the film was made.

---

## Docs that claim files which have not shipped

### What happened

The README delivery table for v2 was committed while the final render was still running. For one commit the repository described `Final-v2.mp4`, `Final-v2-wav-exact.mp4` and an `inspection/` folder that did not exist, and `contact-sheet.png` was byte-identical to `contact-sheet-v1.png`. A reviewer (Codex) caught it from a fresh checkout.

### Incorrect assumption

That a commit which "will be followed by" the artifacts is harmless.

### Root cause

**Confirmed**: a repository hook asked for uncommitted changes to be committed, and the docs went in ahead of the render.

### Why the architecture allowed it

Documentation and deliverables were committed on separate triggers, and nothing checked that files named in the README exist in the tree.

### Fix

The artifacts were committed in the next commit, and the reviewer thread was answered with the commit that added them.

### Prevention rule

Docs that list deliverables ship in the same commit as the deliverables. Before pushing a delivery commit, check that every file named in the README is in `git ls-files`.

### Status

Resolved. No automated check yet.

---

## Stale outputs inside the working tree

### What happened

The first v2 mux was written into `renders/` while a corrected render was still running. A hook then asked for the untracked files to be committed, which would have published outputs that were about to be replaced.

### Root cause

**Confirmed**: in-progress outputs lived at the final path.

### Fix

Render and mux to a scratch directory, verify with ffprobe and stills, then move into `renders/` and commit.

### Prevention rule

The final path in the repository only ever holds a verified artifact.

### Status

Resolved as practice.

---

## Assuming a merge landed

### What happened

After the pull request was reported merged, the next task started from an assumption that `main` held that history. In fact `main` was a single new root commit: the old pull request returned 404, and `git merge-base --is-ancestor origin/main HEAD` was false. The new `main` did contain the project files, plus new skills.

### Root cause

**Unresolved**: the history on `main` was rewritten by the repository owner. The reason is not known and does not matter for the lesson.

### Fix

The working branch was reset onto the new `main` before any new work, and the content was diffed rather than trusting commit history.

### Prevention rule

Before building on merged work, confirm with `git fetch` and `git merge-base --is-ancestor` that `main` contains it. If history was rewritten, restart the branch from `main` and compare content.

### Status

Resolved for this session.

---

## Heavy binaries in normal Git history

### What happened

The film's pull request committed three opening previews (3 to 4 MB each), two drafts, the v1 final and end-hold version, and both v2 finals to `renders/` in normal Git: about 310 MB in total, 34 to 67 MB per full-length file. `skills/motion-director/SKILL.md` (Phase 14) already asks to keep heavy failed renders out of normal history.

### Root cause

**Confirmed**: the brief asked to keep previous drafts, and they were kept the simplest way.

### Impact

Every clone downloads every draft forever.

### Prevention rule

Keep one previous draft and the final in the repository. Store other renders as release assets, artifact storage or Git LFS.

### Status

Unresolved. The renders are in `main`. Moving them to release assets or LFS needs the owner's decision.

**Applied on the promo (`projects/mgs-promo/`)**: only one previous draft (re-encoded to 3.8 MB) and the final (34.5 MB) were committed. Every other render stayed in a scratch directory outside the repository.

---

## Sending a file larger than the channel allows

### What happened

The final MP4 (32.5 MB) exceeded a 30 MB upload limit when sent to the client in chat.

### Fix

A preview encode for phone review (CRF 23, capped at 4 Mbps, 17 MB), with the full-quality master kept in the repository.

### Prevention rule

Know the delivery channel's limit before the final render. Make a review copy for chat and keep the master in storage.

### Recurrence

It happened again on the promo: the 34.5 MB final was sent to chat and refused at the 30 MB limit, although this entry already existed. The lesson was on record, but nothing in the handoff routine made anyone read it. A review copy (CRF 23, capped at 4 Mbps, 5.4 MB, same 1080×1920 and 798 frames) was sent afterwards.

### Status

Resolved as practice, recurred once. The fix is now step 1 of the handoff checklist in `skills/motion-director/references/review-gates.md`.

### Second recurrence: a smaller CRF was not a smaller file

On the JEDAR film the review copy was made by re-encoding at CRF 21 and came out at 42.5 MB, still over the 30 MB limit, and the send was refused again. A bitrate-targeted encode (`-b:v 3400k -maxrate 4500k`, AAC 128k) gave 25.6 MB for 59 s. Two causes, both **Confirmed**: `review-gates.md` (which holds the handoff checklist) was never read on this build, and CRF controls quality, not size, so a flat editorial film with fine grain still costs about 6 Mbps at CRF 21.

Rule added: size a review copy by arithmetic. Target bitrate = limit × 8 × 0.9 ÷ duration (30 MB, 59 s gives about 3.6 Mbps total). Encode to that bitrate and check the file size before sending.

---

## Web accessibility rules applied to a render-only page

### What happened

An accessibility bot reviewed the composition HTML as if it were a web page: no `<main>` landmark, `<audio>` without captions, font sizes in px, an unnamed `<svg>`, and study pages with no `<title>`.

### Triage

- **Applied**, because they were harmless and correct: `aria-hidden="true"` on the decorative SVG, and titles on the standalone study pages.
- **Declined, with the reason posted once**: a `<main>` wrapper (HyperFrames needs the standalone composition root directly in `<body>`), `<track>` on the audio tags (they feed the renderer and no viewer ever sees the page), rem units (the canvas is a fixed 1080×1920 frame).
- **Acted on the intent**: viewers of the MP4 do need captions, so an Arabic WebVTT sidecar was delivered (see [assets-and-media.md](assets-and-media.md#speech-recognition-text-is-timing-data-not-caption-text)).

### Prevention rule

When a web-oriented reviewer flags a render composition, separate what is harmless to fix from what breaks the render contract. For each finding, ask whether the audience of the output is affected. If it is, fix it in the deliverable (captions, contrast in the frames), not in the HTML.

### Status

Resolved as practice.

---

## The agent environment stopped mid-run

### What happened

In the middle of the build, the environment's permission check began returning "no verdict" for every shell command and for scheduling a reminder. Retrying spends a limited budget, and ten consecutive failures end the turn. File writes and edits still worked.

### Workaround that worked

Stop retrying after a few attempts. Use the time on work that needs no shell: write the asset-prep and texture steps as scripts in the repository (`tools/prep_cutouts.py`, `tools/prep_textures.py`), plus the provenance file and the README. Then end the turn with an honest status and a single next step. When the shell came back, one command ran everything that had been prepared. A side benefit: steps that had only existed as throwaway shell snippets became reproducible project scripts.

### Prevention rule

Keep every asset-preparation step as a script in the project from the start, not as inline shell. When tooling fails, report the outage plainly and stop, rather than burning retries or claiming progress.

### Status

Resolved as practice. The outage itself is outside the project.

---

## Registry donors left registered after they were deleted

### What happened

Two HyperFrames registry components were installed with `hyperframes add` to read as donors (`code-terminal-run`, `grain-overlay`). The first file was deleted by hand but stayed listed in `hyperframes.json` and `hyperframes.lock.json`. The second stayed in the repository, unused, with an infinite CSS animation driven by the wall clock that would break determinism if anyone mounted it. A reviewer (Codex) caught both.

### Root cause

**Confirmed**: `add` writes the manifest and lock, the pinned CLI (0.8.92) has no `remove` command, and deleting a file does not update either.

### Fix

Both entries were removed from the manifest and lock, and the unused component file was deleted. `ASSET_SOURCES.md` records that they were read as donors.

### Prevention rule

Study a registry item without installing it (`hyperframes catalog`, or `add` into a scratch project). If it was added to the project, remove its file, manifest entry and lock entry together before committing.

### Status

Resolved.

---

## Skill references skipped on a greenfield build

### Context

The JEDAR film was built with `motion-director` as the guiding skill. The skill tells the agent which references to read and makes HyperFrames the default runtime for greenfield work.

### What happened

Only the first part of `skills/motion-director/SKILL.md`, two Failure-lessons files, and the code of two earlier projects were read. `references/review-gates.md`, `references/arabic-motion.md`, `references/reference-fidelity.md`, `references/hyperframes-playbook.md` and the `video-review-loop` skill were not read. The film reused the custom Playwright renderer from `projects/four-steps-events/` instead of HyperFrames, and the choice was not recorded anywhere at the time.

### Observable symptom

A lesson already on record recurred: the review copy was over the chat limit ([second recurrence above](#second-recurrence-a-smaller-crf-was-not-a-smaller-file)). The handoff step that prevents it lives in `review-gates.md`.

### Root cause

**Confirmed** from the session record: the references were not opened.

### Why the architecture allowed it

The skill lists its references as prose instructions. Nothing forces them to be read, and nothing records which were. Reusing a working project felt like the ladder's first rung ("reuse the current project's renderer"), although this was a new project, where the skill's policy puts HyperFrames first.

### Fix

The deviation is now recorded in `projects/jedar-lesh-majani/README.md` (tools section says where each tool came from). The lessons this build paid for are written here.

### Prevention rule

At the start of a film, list the references the skill says to read, read them, and write one line per deviation from a skill default in the project README, with the reason. A reused renderer from another project is a deviation on a greenfield build.

### Status

Partially mitigated. Step 3 of the intake checklist in `skills/motion-director/references/review-gates.md` now asks for the references to be read and deviations recorded, and Phase 1 of `skills/motion-director/SKILL.md` points to it. The film is not rebuilt on HyperFrames. No tool checks that references were read.

---

## Environment tooling assumed rather than checked

### Context

A cloud container with Chromium pre-installed for Playwright under `PLAYWRIGHT_BROWSERS_PATH`, and no system ffmpeg.

### What happened

Three separate tooling failures cost a round each:

1. `npm i playwright` installed a version that expects `chromium_headless_shell-1243`. The machine had `chromium-1194`. Every Playwright script failed at `launch()` until `executablePath` pointed at the installed build.
2. ffmpeg came from `imageio-ffmpeg`, which ships ffmpeg only. `ffprobe` did not exist, so stream checks had to be read from `ffmpeg -i` output.
3. `pkill -f "http.server 8765"` and `pgrep -f "python3 -m http.server"` matched the shell command that contained them and killed it (exit 144), twice.

### Root cause

**Confirmed** for all three from the error output.

### Why the architecture allowed it

The copied tools (`render.js`, `clip-audit.js`) called `chromium.launch()` with no way to choose the browser. The environment check happened only when something failed.

### Fix

`tools/render.js`, `tools/stills.js` and `tools/clip-audit.js` in `projects/jedar-lesh-majani/` take `executablePath` from `CHROME_PATH`. Servers are started as their own background process and stopped by PID from `ps`, never with a pattern that the calling command also contains.

### Verification

The full clip audit and the stills ran from the committed project with `CHROME_PATH` set.

### Prevention rule

At intake, run one environment probe: browser builds on disk against the installed Playwright version, `ffmpeg` and `ffprobe` on `PATH`, fonts present. Every Playwright tool in this pack accepts `CHROME_PATH`. Never kill processes with `-f` patterns from a command line that contains the pattern.

### Status

Resolved for this project. The probe is step 2 of the intake checklist in `skills/motion-director/references/review-gates.md`. The older copies of `render.js` and `clip-audit.js` elsewhere in the repository still hard-wire the default browser.

---

## A write reported as rejected had already been pushed

### Context

Saving the film. One chained shell command wrote a README, ran `git add`, `git commit` and `git push` to a branch of a different repository than the owner wanted.

### What happened

The tool call came back as rejected by the user. A later `git status` showed the files as tracked and deleted, and `git ls-remote` showed the remote branch at the new commit. The commit and push had happened.

### Impact

A 79 MB master render and the whole project landed on the wrong repository's branch, while the agent believed nothing had run.

### Root cause

**Unresolved.** The observed fact is confirmed (the remote ref pointed at the commit). Why a rejected call still executed, or whether the rejection arrived after execution, was not established.

### Fix

The branch held only that commit and had no open pull request, so it was reset to `main` with `--force-with-lease` pinned to the unwanted commit's SHA, and the files were moved to the intended repository.

### Verification

`git ls-remote origin <branch>` returned the `main` SHA after the reset.

### Prevention rule

After any rejected, interrupted or timed-out command that writes (files, commits, pushes), read the real state before continuing: `git status`, `git log -1`, `git ls-remote`. Keep commit and push as separate commands, so a rejection cannot hide a push.

### Status

Resolved as practice. Mechanism unknown.

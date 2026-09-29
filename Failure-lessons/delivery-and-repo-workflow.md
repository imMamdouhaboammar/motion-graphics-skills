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

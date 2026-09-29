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

---

## Sending a file larger than the channel allows

### What happened

The final MP4 (32.5 MB) exceeded a 30 MB upload limit when sent to the client in chat.

### Fix

A preview encode for phone review (CRF 23, capped at 4 Mbps, 17 MB), with the full-quality master kept in the repository.

### Prevention rule

Know the delivery channel's limit before the final render. Make a review copy for chat and keep the master in storage.

### Status

Resolved as practice.

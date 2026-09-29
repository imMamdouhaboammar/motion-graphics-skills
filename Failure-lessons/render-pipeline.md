# Render pipeline

Lessons from rendering a deterministic HTML composition (`window.seek(t)` draws any frame) through Playwright screenshots piped into ffmpeg, then muxing the voice-over.

Related code: `projects/four-steps-events/tools/render.js`, `projects/four-steps-events/film.js` (`window.seek`, `window.__ready`), `projects/four-steps-events/README.md` (Render section).

---

## The end hold is one contract spread across three layers

### Context

A film timed to a fixed voice-over often needs a hold on the final lockup after the last word, both for the viewer and for platforms that cut the last second.

### What happened

The hold broke three separate times, each at a different layer:

1. The documented mux command used `-shortest`, so ffmpeg cut the video back to the audio length and the hold disappeared.
2. With the hold rendered, the frames after the VO were not identical: the grain kept cycling because the composition kept advancing time.
3. The documented tail render kept an explicit end time equal to the VO length. `render.js` clamps the range with `Math.min(t1, DURATION)`, so no hold frames were rendered at all, while the padded audio made the container longer than the video.

A fourth, planning-level version appeared in the polish pass: the last word lands at 53.34 s and the WAV ends at 54.36 s, so a 1 to 1.5 s clean hold was impossible inside the WAV length.

### Observable symptom

A final file whose last second is missing, flickers, or ends in black with sound still running.

### Impact

The brand lockup, the one frame every ad must land on, was the frame most likely to be wrong.

### Incorrect assumption

That "add a tail" is one switch. It is three coupled settings: the composition's time clamp, the render range, and the mux.

### Root cause

**Confirmed** for all three. Each was reproduced from the command or code path (reviewer findings from Sourcery, Codex and CodeRabbit on the pull request), then fixed.

### Why the architecture allowed it

The composition, the renderer and the mux command each had their own idea of duration (`VO_DUR`, `DURATION`, and the ffmpeg arguments), and nothing checked the final file for the hold.

### Fix

- `window.seek` clamps composition time to the VO length, so every tail frame repeats the last composed frame exactly: `renderAt(Math.max(0, Math.min(VO_DUR - 1e-4, t)))`.
- `?tail=N` extends `window.DURATION`, and the README tail command passes `t1 = VO + N`.
- The mux pads audio with `apad=pad_dur=N` and never uses `-shortest` when a hold exists.
- The final delivery renders once with the tail, then cuts a WAV-exact file from the same frames (`-frames:v 1631`), so the two files cannot drift.

### Verification

`ffprobe` on the delivered files: `Final-v2.mp4` has 1667 video frames (55.567 s) against 55.561 s of audio, and `Final-v2-wav-exact.mp4` has 1631 frames (54.367 s) against the 54.361 s WAV, both starting at 0. No automated test protects this yet.

### Prevention rule

Define duration once, in the composition. The render range and the mux derive from it. Verify the hold on the final file by frame count, not by reading the command.

### Reusable lesson

Any value that three stages must agree on (duration, frame rate, colour range, sample rate) belongs in one place, and the check belongs on the artifact at the end, not on the configuration.

### Related lessons

[Plan the end hold in the beat map](#plan-the-end-hold-in-the-beat-map)

### Status

Resolved in code and docs. Unresolved: no automated check that asserts the hold frame count on the final file.

---

## Plan the end hold in the beat map

### What happened

The last spoken word («وتتذكره») starts about 1 s before the WAV ends. The polish brief asked for a 1 to 1.5 s clean lockup after the words clear, with nothing new in the last second.

### Incorrect assumption

That the hold can be found at the end of production. It is decided by the script and the VO read.

### Root cause

**Confirmed** by arithmetic on the measured word times in `beat-map.md`.

### Fix

The delivery file adds 1.2 s of silence after the VO, and the words clear from 53.62 s. The WAV-exact version is kept for placements that require it.

### Prevention rule

When the beat map is built, compute `VO end minus last key word` and decide then whether the hold fits inside the audio or needs a silent tail. Tell the client which one ships.

### Status

Resolved for this film. The rule is now in `skills/motion-director/SKILL.md`, Phase 6.

---

## A renderer that ignores its encoder's failure

### What happened

The first `render.js` wrote frames into ffmpeg's stdin and finished with success whatever ffmpeg did. A reviewer flagged that the exit code was never read and that a closed pipe was not handled.

### Observable symptom

None, which was the danger: a broken or truncated MP4 reports success.

### Incorrect assumption

That a child process that did not throw has succeeded.

### Root cause

**Confirmed** from the code path.

### Fix

`render.js` handles `ff.stdin` errors, waits for ffmpeg's `close` event, exits 1 on a non-zero code, and exits 1 when the page never sets `window.DURATION`.

### Verification

Fault injection after the fact: rendering to a directory that does not exist prints `ffmpeg exited with code 254` and the script exits 1.

### Prevention rule

A pipeline step that spawns a process reads its exit status and fails loudly. Prove it once by pointing the output at an impossible path.

### Reusable lesson

The same applies to every wrapper around ffmpeg, ffprobe, Blender, or a headless browser.

### Status

Resolved.

---

## Scenes built before their assets were ready

### What happened

In an early draft the Four Steps wordmark was missing from the frames. Scenes were built at page load while the wordmark SVG was still being fetched.

### Observable symptom

A frame with an empty space where the logo should be. In a real-time preview it can look fine because the fetch finishes a moment later.

### Incorrect assumption

That everything referenced by the page is present when scene code runs.

### Root cause

**Confirmed**: the build ran before the fetch resolved.

### Why the architecture allowed it

Deterministic seeking removes timing from animation, but not from loading. A renderer that seeks immediately after load exposes every race that a live preview hides.

### Fix

The wordmark path data is embedded as data (`WORDMARK_EL` in `film.js`). `window.__ready` awaits every font weight in both families, `document.fonts.ready`, and `decode()` on every image before the first `seek`. The renderer, stills tool, font check and clip audit all await `window.__ready`.

### Verification

With the sans webfont files renamed in a scratch copy, the page fails to become ready (`NetworkError` at `window.__ready`), so the renderer cannot produce frames with a fallback face.

### Prevention rule

Scene builders never fetch. One readiness promise gates the first frame, and every tool awaits it.

### Status

Resolved.

---

## Animated grain and heavy renders

### What happened

A draft render came out at 177 MB for 54 s. Re-encoding with a capped bitrate (`-maxrate 14M -bufsize 28M`) brought it to about 54 MB. After the polish pass lowered grain opacity (from 16 % to 7.5 % overlay) and halftone strength, the same film at the same settings was 34 MB.

### Root cause

**Strongly indicated**, not isolated: full-frame grain that changes every two frames is high-entropy detail the encoder must spend bits on. No A/B render with grain off was made.

### Fix

Cap the bitrate in `render.js`. Keep grain on twos, fine, and low opacity. It also looks better: the brief asked for grain you notice only when you look for it.

### Prevention rule

When file size jumps, check full-frame animated texture first. Grain is a style decision with a bandwidth cost.

### Status

Partially mitigated. Open: measure file size with grain off to confirm the share of bits it costs.

---

## An unknown option value crashed the page

### What happened

`?opening=X` with an unknown letter threw during scene construction, so nothing rendered.

### Root cause

**Confirmed**: a lookup table was called without a default.

### Fix

`(OPENINGS[OPEN] || openingA)(R)`.

### Prevention rule

Every URL or CLI option has a default path. A preview option should never be able to stop a render.

### Status

Resolved.


---

## A readiness promise adopted a paused GSAP timeline

### Context

A browser audit loaded the composition successfully. Fonts were ready, images were decoded, and the timeline registry existed, but every tool that awaited `window.__ready` stayed pending.

### Observable symptom

Playwright navigation completed, yet the clip audit or readiness check appeared to hang indefinitely. Increasing the page-load timeout did not address the blocked await.

### Incorrect assumption

That anything returned from an async readiness function is just a value.

### Root cause

**Confirmed** from runtime diagnosis. The readiness function returned a GSAP timeline. GSAP timelines expose a `then` method, so JavaScript promise resolution treated the returned timeline as a thenable. Because the timeline was paused, the readiness promise never settled.

### Why the architecture allowed it

The readiness promise did two jobs: it signaled asset readiness and also returned a runtime object. That coupled a gate to an object whose promise-like behavior was not obvious at the call site.

The diagnostic path repeated the risk when a browser tool evaluated `window.__ready` directly, because automation frameworks also await promise-like values returned from page evaluation.

### Fix

- readiness functions resolve to `undefined` or another plain non-thenable value
- timelines live in their own registry instead of being returned through the readiness gate
- the browser readiness probe inspects `window.__ready` inside the page and returns only plain JSON
- long-running browser tools can run through `scripts/work_guard.py` so a blocked readiness gate is contained and leaves evidence

### Verification

The failure was isolated by racing the readiness gate against a timeout while independently checking fonts, images, and timeline state. Those independent checks completed while `window.__ready` remained pending. After the readiness return value was made plain, the gate resolved.

The work guard regression suite separately proves that a silent blocked command is contained, its process tree is terminated, and its logs and summary survive.

### Prevention rule

A readiness promise answers only whether deterministic tools may begin. Never return timelines, players, renderers, or other possibly thenable runtime objects from it.

A browser diagnostic must never return the inspected readiness object from `page.evaluate`. Return plain state.

### Reusable lesson

When a promise appears stuck after its visible prerequisites have completed, inspect the value it resolves with. Promise assimilation can turn an innocent-looking return value into another wait.

### Status

Resolved in the originating project and encoded as reusable guard and probe behavior in `motion-director`.

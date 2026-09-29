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

<a id="a-readiness-promise-adopted-a-paused-gsap-timeline"></a>
## A readiness promise that resolved to a timeline never resolved

### Context

`projects/mgs-promo/index.html` builds its scenes inside `window.__ready = ready().then(build)`. Tools outside the HyperFrames runtime (clip audit, font gate) await `window.__ready` before seeking.

### What happened

`build` ended with `return tl`, the GSAP timeline. A GSAP timeline is a thenable. The promise adopted it and waited for a paused timeline to complete, which never happens. The clip audit hung until its timeout twice, costing about 25 minutes, before the promise itself was tested in isolation.

### Observable symptom

Playwright navigation completed, yet the clip audit or readiness check appeared to hang indefinitely. The page looks fine, fonts report `loaded`, images are `complete`, and `window.__timelines.main` exists. Increasing the page-load timeout did not address the blocked await.

### Impact

Every tool that honours the readiness contract stalls. The HyperFrames render was unaffected because the runtime does not await `window.__ready`, which is why the defect stayed hidden.

### Incorrect assumption

That returning a useful object from the final `then` is harmless, and that anything returned from an async readiness function is just a value.

### Root cause

**Confirmed.** Each piece of `ready()` was raced against a 5 s timer in the page: images, font loads, texture decodes and `document.fonts.ready` all resolved. The readiness function returned a GSAP timeline. GSAP timelines expose a `then` method, so JavaScript promise resolution treated the returned timeline as a thenable. Because the timeline was paused, the readiness promise never settled. Returning `true` made it resolve at once.

### Why the architecture allowed it

The readiness promise did two jobs: it signaled asset readiness and also returned a runtime object. That coupled a gate to an object whose promise-like behavior was not obvious at the call site. The production renderer and the verification tools use different readiness signals; only the tools depended on `__ready`, so the render gave no warning.

The diagnostic path repeated the risk when a browser tool evaluated `window.__ready` directly, because automation frameworks also await promise-like values returned from page evaluation.

### Fix

- `build` returns `true`, with a comment explaining why the timeline must never be returned.
- readiness functions resolve to `undefined` or another plain non-thenable value; timelines live in their own registry instead of being returned through the readiness gate.
- the browser readiness probe (`skills/motion-director/scripts/browser-readiness-probe.cjs`) inspects `window.__ready` inside the page and returns only plain JSON.
- long-running browser tools can run through `skills/motion-director/scripts/work_guard.py` so a blocked readiness gate is contained and leaves evidence.

### Verification

`tools/font-check.cjs` and `clip-audit.js` both complete after the change. Before the change, a 15 s race in the page reported `timeout`.

The work guard regression suite separately proves that a silent blocked command is contained, its process tree is terminated, and its logs and summary survive.

### Prevention rule

A readiness promise resolves to a plain value. Never return a GSAP timeline, tween, player, renderer, or other thenable from a `then` callback or readiness promise. Every tool that awaits readiness races it against a timeout and reports "readiness never resolved" instead of hanging silently.

A browser diagnostic must never return the inspected readiness object from `page.evaluate`. Return plain state.

### A second misattribution along the way

While the hang was unexplained, the font gate's `page.goto` was switched from the default `load` wait to `domcontentloaded`, on the theory that four `<audio>` elements were holding the load event. That theory was wrong. After the readiness fix, `clip-audit.js` completes with the default `load` wait. The switch did no harm, but it is the same pattern as [Two changes between renders, one wrong culprit](testing-and-verification.md#two-changes-between-renders-one-wrong-culprit): test the smallest part in isolation before changing a second thing.

### Reusable lesson

Any library object with a `then` method (GSAP animations, some query builders, jQuery deferreds) silently changes a promise chain it is returned into. When a promise appears stuck after its visible prerequisites have completed, inspect the value it resolves with. Promise assimilation can turn an innocent-looking return value into another wait.

### Related failure: readiness that swallowed asset errors

A reviewer (Codex) found the opposite defect in the same promise. Each `decode()` had `.catch(function () {})`, so a missing cutout still resolved readiness and would have rendered a blank object. Decode failures now reject with the asset path. Red run: with one cutout deleted in a scratch copy, the font gate reports `image failed to decode: assets/cutouts/mic_akg.png` and FAIL. The intact project reports PASS. A readiness promise should neither hang nor lie: it resolves when everything is ready and rejects, with the reason, when something is not.

### Status

Resolved. `projects/mgs-promo/tools/font-check.cjs` now races readiness against 20 s. Red run: with `return tl` restored in a scratch copy, it fails with `window.__ready did not settle within 20000 ms` instead of hanging. Reusable work guard and browser probe codified in `skills/motion-director`.

---

## A texture swapped during capture made renders differ under load

### Context

The grain layer in `projects/mgs-promo/index.html` changes tile every two frames. The first version did it by assigning a new `background-image` URL to one element on every change.

### What happened

Renders of the same code disagreed run to run: up to 245 frames, PSNR 46 to 62 dB, spread over the whole frame at low amplitude. A pair of renders made on an idle machine matched perfectly, which briefly suggested the problem was gone.

### Observable symptom

Different `framemd5` hashes for the same frame across renders. Sub-visible at playback, but it breaks every "same time, same frame" comparison.

### Impact

Any before/after comparison, determinism claim or frame-hash regression check becomes unreliable. Earlier in the session it muddied the diagnosis of a separate bug (see [testing-and-verification.md](testing-and-verification.md#two-changes-between-renders-one-wrong-culprit)).

### Incorrect assumption

That a CSS background URL which was decoded once is always painted in the same frame it is assigned.

### Root cause

**Confirmed** as the condition, not the browser mechanism. With `tools/determinism-check.sh` (second render under CPU load):

- URL-swapping grain: FAIL, 48 of 798 frames differ. A separate idle vs loaded pair differed in 111 frames.
- Pre-painted tiles with opacity toggles: PASS, 798 of 798 identical. An idle vs loaded pair was also identical.
- Two idle renders of the URL-swapping code: identical. The race needs contention to appear.

Whether decoding or painting is late was not isolated.

### Why the architecture allowed it

Seeking removes timing from animation but not from resource paint. The render captures a frame as soon as the timeline is seeked, and nothing waited for a newly assigned background to paint.

### Fix

All three grain tiles are separate layers that are always painted. Only their opacity and position change per frame.

### Verification

`tools/determinism-check.sh`: red on a scratch copy with the old grain code, green on the current code. The delivered master was also re-rendered and compared by `framemd5` with 0 differing frames.

### Prevention rule

Nothing changes a resource URL during capture. Anything that must alternate is loaded up front and switched by opacity, transform or clip. Run the determinism check with the second render under load, because an idle pair can pass while the race is still there.

### Reusable lesson

The same applies to swapping `<img src>`, sprite sheets by URL, video posters, and fonts assigned late. Any fetch or decode that starts at seek time can lose the race.

### Related code

`#grain` and `#g0`–`#g2` in `projects/mgs-promo/index.html`, `projects/mgs-promo/tools/determinism-check.sh`.

### Related lessons

[Scenes built before their assets were ready](#scenes-built-before-their-assets-were-ready) is the same family at load time. This one happens during capture.

### Status

Resolved.

---

## A duration cap the supplied audio already breaks

### What happened

The brief asked for a film of at most 25 s. The measured WAV was 26.12 s, with the last word ending at 25.89 s. This was found at intake from `ffprobe` and `silencedetect`, before any scene was built.

### Decision

The VO was not sped up, trimmed or stretched, because the brief forbade secretly damaging it. The film runs the WAV plus a 0.48 s silent CTA hold (26.6 s, 798 frames), and the conflict was reported in the handoff, the PR and `beat-map.md`.

### Prevention rule

Measure the supplied audio against every duration constraint at intake, and record the resolution in the beat map. A cap that the master audio already breaks is the client's decision, not a silent edit.

### Status

Resolved as practice. Extends [Plan the end hold in the beat map](#plan-the-end-hold-in-the-beat-map).

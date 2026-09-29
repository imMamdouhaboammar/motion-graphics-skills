# Lessons index

Search this table before debugging. If your problem matches a failure class, start from that entry.

| Lesson | Failure class | Prevention rule | System | Status | Document |
|---|---|---|---|---|---|
| End hold broke three times | One value owned by several stages | Duration defined once in the composition, hold verified by frame count on the final file | Render, mux | Resolved (no automated check) | [render-pipeline](render-pipeline.md#the-end-hold-is-one-contract-spread-across-three-layers) |
| No room for the hold after the last word | Planning decision made too late | Compute VO end minus last key word in the beat map | Beat map | Resolved | [render-pipeline](render-pipeline.md#plan-the-end-hold-in-the-beat-map) |
| Renderer ignored ffmpeg failure | Unchecked child process | Read exit status, fail loudly, prove with an impossible output path | Render | Resolved | [render-pipeline](render-pipeline.md#a-renderer-that-ignores-its-encoders-failure) |
| Logo missing from frames | Content built before assets loaded | Scenes never fetch, one readiness promise gates the first frame | Composition | Resolved | [render-pipeline](render-pipeline.md#scenes-built-before-their-assets-were-ready) |
| 177 MB draft | Full-frame animated texture costs bits | Cap bitrate, keep grain fine, low and on twos | Encode | Partially mitigated | [render-pipeline](render-pipeline.md#animated-grain-and-heavy-renders) |
| Unknown option crashed the page | Lookup without default | Every option has a default path | Composition | Resolved | [render-pipeline](render-pipeline.md#an-unknown-option-value-crashed-the-page) |
| Arabic letters and dots cut | Geometry checked by eye only | Clip audit before delivery, intentional crops declared in code, overlaps stay above the dot zone | Type, layout | Partially mitigated | [arabic-type-and-layout](arabic-type-and-layout.md#accidental-clipping-found-only-by-eye) |
| Text hugging the frame edge | Safe margin not measured | 48 px minimum for non-hero copy, confirm warnings at full size | Type, layout | Unresolved in v2 | [arabic-type-and-layout](arabic-type-and-layout.md#near-edge-text-is-a-separate-problem-from-clipping) |
| Swash read as font demo | Feature used because it exists | List features first, use an alternate only to solve composition | Type | Resolved | [arabic-type-and-layout](arabic-type-and-layout.md#swash-as-ornament) |
| Lavender frames between navy and blue | Opacity blend of saturated fields | Never crossfade two saturated fields, carry an object or cut | Transitions | Resolved | [composition-and-transitions](composition-and-transitions.md#a-crossfade-between-two-saturated-fields-makes-a-third-colour) |
| Posters colliding in a corridor, ghost poster | Projection geometry in 9:16, fade exits | One readable plane with depth, exits by movement | Camera, 2.5D | Resolved | [composition-and-transitions](composition-and-transitions.md#perspective-walls-converge-on-the-vanishing-point) |
| Labels cut during camera travel | Labels not owned by their station | Labels arrive and leave with their station | Camera | Resolved | [composition-and-transitions](composition-and-transitions.md#camera-travel-crops-the-labels-it-leaves-behind) |
| Question mark cut by a light cone | Polygon reveal narrowed without a text check | Text box sits inside the polygon at its widest frame | Masks | Resolved | [composition-and-transitions](composition-and-transitions.md#text-inside-a-light-cone-or-polygon-reveal) |
| Technically correct, creatively weak final | Render treated as finished | Still-frame and creative-director gates before final | Direction | Resolved (rules in skill) | [composition-and-transitions](composition-and-transitions.md#generated-correctly-is-not-directed) |
| Font check that always passed | Check that cannot fail | Every gate gets one red run on a scratch copy | Verification | Resolved | [testing-and-verification](testing-and-verification.md#a-check-that-could-not-fail) |
| Wrong diagnosis from thumbnails | Contact sheet used as geometric evidence | Measure or view full size before changing code | Verification | Resolved as practice | [testing-and-verification](testing-and-verification.md#diagnose-from-a-measurement-not-from-a-thumbnail) |
| 7 px cut missed by two passes | Eyes used for geometry | Measure geometry, review taste | Verification | Partially mitigated | [testing-and-verification](testing-and-verification.md#visual-review-misses-what-it-is-not-looking-for) |
| README listed files not yet shipped | Docs and artifacts published apart | Same commit, check names against `git ls-files` | Repository | Resolved | [delivery-and-repo-workflow](delivery-and-repo-workflow.md#docs-that-claim-files-which-have-not-shipped) |
| Stale outputs at final paths | In-progress files at final location | Final paths hold only verified artifacts | Repository | Resolved as practice | [delivery-and-repo-workflow](delivery-and-repo-workflow.md#stale-outputs-inside-the-working-tree) |
| Built on a merge that was not in main | History assumed, not checked | `merge-base --is-ancestor` before building on merged work | Repository | Resolved | [delivery-and-repo-workflow](delivery-and-repo-workflow.md#assuming-a-merge-landed) |
| 310 MB of renders in Git | Binaries in normal history | One draft and the final in the repo, the rest elsewhere | Repository | Unresolved | [delivery-and-repo-workflow](delivery-and-repo-workflow.md#heavy-binaries-in-normal-git-history) |

## Rules we now enforce

1. **A check is trusted only after it has been seen failing.** Reintroduce the defect in a copy of the project, run the check, restore.
2. **Duration has one owner.** The composition defines it. The render range and the mux derive from it. The hold is verified by frame count on the final file.
3. **The first frame waits for everything it paints.** Scenes never fetch. One readiness promise, awaited by every tool.
4. **Geometry is measured, taste is reviewed.** Clipping, margins, duration and frame counts come from tools. Composition and hierarchy come from people.
5. **Every crop is a decision in code.** Intentional crops are declared (`data-crop="intentional"`), everything else the clip audit reports is a defect.
6. **Arabic dots are part of the letter.** No overlap, mask edge or frame edge may cross the dot and descender zone of a word meant to be read.
7. **No opacity blend between two saturated fields.** Cut, shape a mask, or carry an object across.
8. **Diagnose at full resolution.** A contact sheet points at a candidate. It never proves a geometric defect.
9. **Docs and deliverables ship together.** A README never names a file the same commit does not contain.

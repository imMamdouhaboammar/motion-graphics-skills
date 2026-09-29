# Reference study

Source: `إذا متجرك يبيع فعلًا… الخطوة الجاية تحتاج أكثر من إعلانات زيادة…mp4` (the ROAR e-commerce reel), from `imMamdouhaboammar/4steps-web@5b93b25`.

## Technical facts (ffprobe)

| Item | Value |
|---|---|
| Duration | 36.78 s |
| Resolution | 720 × 1280 (9:16) |
| Frame rate | 30 fps |
| Video | H.264 |
| Audio | AAC, 44.1 kHz stereo (VO + light music bed) |

Samples taken: one frame per second for the full film (`assets/ref/reference-contact-1s.png`), six frames per second for 0 to 3 s (`assets/ref/reference-contact-open-0-3s.png`), full-resolution stills at 1.6, 5.5, 12.5, 17, 26 and 33 s, and a 2× crop of the texture.

Scene-change detection (`select=gt(scene,0.2)`) fires at: 1.37 to 1.63 (the black/teal flash), 4.0, 4.77 to 4.9, 6.33, 8.47, 9.6, 10.47, 12.03, 21.3 to 21.63, 24.73, 26.67, 29.57 to 29.7, 32.17. Between 12 and 21 s there is no hard cut at all: the camera travels along one drawn line for nine seconds.

## Shot log

| Time | What happens | Transition out |
|---|---|---|
| 0.0 to 1.3 | A product card stack lands on a concrete plinth with a till receipt. Headline «إذا متجرك يبيع فعلًا» types in word by word from motion blur above. A dark red starburst snaps open behind the cards. | 3-frame inversion flash (black ground, teal burst, negative cards) |
| 1.4 to 2.1 | Flash frames, then a torch swings in from the left. | Torch pans the frame |
| 2.1 to 4.0 | Torch beam (flat red wedge) reveals product screenshots and «لا تدور على أحد». | Red beam fills frame |
| 4.0 to 6.3 | Red field, social-post cards scattered in rotation; «يسويلك كام إعلان». | Hard cut to cream |
| 6.3 to 8.4 | Photographic handshake cutout, «دور على شريك». Cursor enters. | Cursor carries into next shot |
| 8.4 to 9.6 | Red storefront model rises on a red block, «يعرف يكبر اللي». | Block drops, cream |
| 9.6 to 12.0 | Quiet typography: «في ROAR نبدأ من متجرك», cursor clicks. | Cursor click |
| 12.0 to 13.5 | Three product-bottle photos in rounded strips; cursor picks «TOP SELLER». | Blur out |
| 13.5 to 16.0 | Shopper cutout in greyscale, product cards and a search bar pinned around her with dotted lines, «وين يتردد قبل الطلب؟» | Cut to text |
| 16.0 to 21.3 | «بعدها نبني منظومة النمو», then a camera travel along a hand-drawn wobbly line linking red icon tiles (target, idea, image, Instagram, chart, cycle, cart). Each tile gets a small black starburst when the camera arrives. | Line exits frame |
| 21.3 to 24.7 | «ما نطلق حملة وننتظر», then ad cards with CTR labels (1.2 %, 2.8 %, 4.6 %) and a green tick on the winner, «نختبر الرسائل والزوايا». | Cut |
| 24.7 to 26.6 | Grey paper folder with paperclip and binder clip, «نقرأ النتائج» in huge black type printed on the cover. | Cut |
| 26.6 to 29.6 | Dashboard photo, blurred, with a hand holding a magnifier; the lens shows sharp numbers. | Cut to cream |
| 29.6 to 32.2 | Quiet text: «إذا عندك منتج قوي ومبيع» | Text holds |
| 32.2 to 36.8 | End card: «عبي النموذج الآن / وخل ROAR / تكون شريك نمو متجرك». ROAR wordmark in a wide geometric Latin face. | End |

## Findings, point by point

1. **Composition.** Almost everything sits on a vertical centre axis, but the axis is broken by objects entering from the edges (torch from the left, cursor from the bottom right, icon tiles cropped by the frame). Headlines live in the upper third (y ≈ 15 to 30 %). Objects live in the middle third. The bottom 25 % is usually empty or holds a cropped object, which also keeps the Reel UI zone clean.
2. **Typography hierarchy.** One text level per shot, almost always. Headlines are Arabic sans in black weight, near-black, about 6 to 8 % of frame width in cap height. The only very large type is «نقرأ النتائج» printed on the folder, and it is the most memorable frame in the film. Latin is limited to ROAR and data labels.
3. **Arabic text treatment.** The signature move is the **kashida (tatweel) stretch**: «متجرك ـــــ يبيع», «دور على ـــــ شريك», «الرسائل ـــــ والزوايا». The stretch becomes a rhythmic pause in the line, like a breath in the VO. Words arrive one at a time with a short horizontal motion blur and a soft drop shadow, so the type looks printed and slightly lifted from the paper.
4. **Visual density.** Alternates. Dense (plinth + cards + burst + receipt), then empty (one line of type on paper), then dense again. Roughly 60 % of the runtime has one object or fewer on screen.
5. **Object scale.** Hero objects take 50 to 70 % of frame width. Secondary objects are 15 to 25 %. There is rarely anything medium-sized, which is why the frames feel designed rather than filled.
6. **Foreground and background.** Three planes: paper ground, the hero object with a hard contact shadow, then occasional foreground elements (cursor, torch, magnifier) that sit closer to camera and are slightly blurred.
7. **Shadows.** Offset drop shadows, down and to the right, soft but short (paper lifted a few millimetres). Icon tiles carry a darker bevel edge on the bottom, like a thick printed chip.
8. **Paper and print texture.** Warm grey paper, around `#DBD2C7`, with a visible fine **halftone dot screen over the whole frame**, including the photographs. Photographic cutouts are desaturated and slightly crushed.
9. **Grain.** Light, moving grain on top of the halftone. Readability of the type is never affected.
10. **Accent colours.** One dominant accent (deep red, around `#A8121A` to `#8E1116`). A complementary teal appears only in the three-frame inversion flash. Everything else is near-black and paper.
11. **Cutout treatment.** Photographic objects are cut cleanly with no white border, desaturated, contrast pushed. Graphic objects (cards, tiles) have thick rounded rims.
12. **Collage construction.** Photography and flat graphics mix freely in one frame: a real concrete plinth holds flat red product cards; a flat red beam comes out of a photographic torch. That mix is the style.
13. **Depth.** 2.5D only. Layers at different scales with shadows, slight parallax during camera moves, defocus on the nearest and farthest layers. No real 3D camera.
14. **Camera movement.** Mostly locked off with small push-ins. The one big move is the long travel along the drawn line (12 to 21 s), which is the backbone of the film's middle.
15. **Scene duration.** 1.2 to 4 s per idea, except the 9-second line travel. Nothing is equal length.
16. **Transition families.** (a) Inversion flash, (b) a moving object carrying the eye (torch, cursor), (c) colour field wipe (red beam fills frame), (d) camera travel along a path, (e) plain hard cut on a VO sentence boundary.
17. **Metaphors.** Literal and quick: torch = searching, handshake = partner, magnifier = reading results, folder = report. The film never explains a metaphor twice.
18. **How often text appears.** Nearly always, but in short fragments.
19. **How much of the sentence is on screen.** About 40 to 60 % of the words. Key clauses only, never the whole sentence as a caption.
20. **Hand-drawn marks.** A single black wobbly line linking the tiles, small black starbursts (8 to 10 points) that pop on arrival, dotted connector lines to pins, a mouse cursor.
21. **Photographic versus graphic.** Roughly half and half. Photographs carry the objects; flat graphics carry the ideas (bursts, beams, tiles).
22. **Pacing changes.** Fast and dense for the first 4 s, then slower. The middle (line travel) is continuous and calm. The last 6 s are almost pure typography.
23. **Handing objects between scenes.** The cursor persists across three shots. The red beam becomes the red field. The drawn line is one object for nine seconds. This is the part of the grammar most worth borrowing.

## What to borrow for Four Steps

- Warm paper, full-frame halftone, one accent, near-black type.
- Kashida as rhythm, used on a few chosen words only.
- Words land one at a time with a short blur and a lifted shadow.
- Photo cutout + flat graphic in the same frame.
- One continuous drawn path that the camera follows through the "how we work" section.
- Small black starbursts as punctuation when something arrives.
- Dense, quiet, dense.

## What not to carry over

- The red accent and teal flash (ROAR's palette). Four Steps has its own blue.
- The e-commerce props (bags, bottles, receipts, carts).
- The red app-icon tiles. They read as an icon explainer, which this brief rules out.
- Its layouts and copy.

## Where Four Steps can go further than the reference

- The reference keeps type small. Thmanyah can carry whole frames at 300 to 500 px.
- The reference uses its brand mark only at the end. The Four Steps mark is four stepped shapes, which can be the path itself.
- The reference cuts hard between most ideas. Four Steps can hand objects between more of its scenes.

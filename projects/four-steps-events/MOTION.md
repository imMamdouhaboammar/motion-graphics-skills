# MOTION.md: Four Steps, events film (campaign art direction)

Read this before animating anything for this film. The file sets the look, not the ambition.

This is **campaign art direction** for one film. It borrows the editorial paper-collage grammar of the reference reel and dresses it in Four Steps' own colours. The paper ground and print texture belong to this campaign, not to the permanent brand identity, which is navy and volt on the web (`DESIGN.md`).

## 1. Colour

| Token | Hex | Job |
|---|---|---|
| `paper` | `#F3EEE5` | Ground for most shots. Printed paper, clean and bright, never aged |
| `paper-2` | `#E6DED2` | Secondary paper: walls, photo mats, card backs |
| `card` | `#FBF7F0` | Printed cards, passes, sheets, and the clear ground behind the official event logos |
| `ink` | `#11110F` | Type, drawn lines, the ink plate of printed bursts |
| `ink-2` | `#777168` | Muted ink: small print, labels, support lines |
| `blue` | `#192EE8` | Four Steps blue. **Signal, never wallpaper**: the path, the marker correction, the underline, the steps, the mark. 5 to 15 % of a frame. One full-blue brand beat (B4), and it is earned: the correction stroke floods the frame |
| `navy` | `#000032` | Dark shots: lights off. No blue in the dark section (B7): navy and paper only |
| `volt` | `#CAF222` | Two frames only, when the lamp strikes. Never on paper, never for type |

Official event logos keep their exact colours (gold, teal, slate) and always sit on `card` with clear space around them; no Four Steps blue touches them.

## 2. Type

All type is Thmanyah, loaded locally with `@font-face`. `direction: rtl` on every Arabic block.

| Level | Face | Size at 1080 × 1920 | Used for |
|---|---|---|---|
| Hero word | thmanyah serif display Black | 140 to 290 px (to 450 when the crop is the composition) | آخر, علق في بالك؟, التنظيم, تخطيط, كل دقيقة, الفكرة, آخر ضيف, شهور, باسمك, خطوة بخطوة, تشوفه |
| Main statement | thmanyah sans Black/Bold | 85 to 150 px (to 370 in the opening) | لأكبر الجهات, هذا شغلنا, نخطط, أصغر غلطة, آلاف الضيوف |
| Question / human voice | thmanyah serif display Bold | 75 to 150 px | المسرح؟, عندك فعالية جاية؟, خلّها تنذكر, نمشي معك |
| Support | thmanyah sans Medium or serif display Medium | 42 to 104 px | تذكر وش اللي, ولا, ليالي, قدام, نبدأ معك من, في المملكة |
| Small print | thmanyah sans Regular/Medium | 26 to 34 px | Cards, passes, cue sheets. Never below 26 px |

Rules: never three levels in Black at once; one oversized word per frame; the VO is designed, not transcribed (most frames carry 1 to 5 words, and a phrase the VO carries can stay off screen, as «شيء الناس» does).

OpenType features available in both families: `swsh`, `salt`, `ss01` and `ss03` to `ss07` (sans adds `ss08`, `case`, `frac`; serif display adds `lnum`, `onum`), plus `dlig`. Swashes are off everywhere in this film: on «باسمك» and «وتتذكره» they read as a font demo. Glyphs are never scaled on one axis, and kashida is not used.

## 3. Timing

- The WAV is the clock. Every entrance is keyed to a word time in `beat-map.md`.
- A word lands 0 to 60 ms before it is spoken, never after.
- Entrances: 0.25 to 0.45 s. Exits: 0.2 to 0.35 s. Holds: until the next VO idea, minimum 0.9 s for any line of text.
- Staggers: 70 to 120 ms between siblings.
- Rhythm across the film: dense (B1) → quieter (B2) → dense (B3) → quiet (B4) → dense (B5, B6) → dark and sparse (B7) → empty (B8) → assembled (B9).

## 4. How things move

- 30 fps output. Camera moves, depth and object travel are smooth (every frame).
- Hand-made elements (marker lines, starbursts, doodles, grain, paper snaps) update **on twos** (15 fps), so they feel drawn.
- Easing: `outExpo` for arrivals, `inOutCubic` for camera, `outBack(1.2)` only for paper snaps and starbursts. No elastic.
- Words arrive with a short horizontal motion blur and settle with a lifted shadow, like printed type laid on paper.
- Objects hand over: an object that ends one beat becomes the start of the next (see `beat-map.md`, transition column).
- Deterministic: everything is a function of `t`. Seeded random only (mulberry32). `window.seek(t)` draws the same frame every time.

## 5. Texture and finish

- Paper tooth: fine seeded noise and a few fibres, multiply at 50 %. No stains, no ageing.
- Halftone screen over the frame at 22 %, 4 px pitch.
- Grain: 4 seeded tiles, cycled on twos, overlay at 7.5 %: visible when you look for it.
- Vignette: 6 % at the corners only.
- **One print treatment for every photographic prop** (`.cut`): saturate .45, sepia .12, contrast .9. Chrome props (stopwatch) get the flatter `.cut.flat`.
- **Three elevations only**: low (cards, 4 to 6 px), medium (props, posters, 8 to 14 px), high (hero objects: the pass, the lever, the ticket, 14 to 24 px). Light always comes from the top left.
- Bursts are printed, hand-cut shapes with a second plate slightly off register (`printBurst`). No vector starbursts. The end of the film uses a torn label and a stamp instead.

## 6. Never

1. Glow, neon, gradients on type, glassmorphism, purple-blue gradients.
2. Typewriter headlines, bouncing, perpetual floating, elastic overshoot everywhere.
3. Icon tiles or icon explainers. Props are photographic or printed artifacts.
4. Invented logos, photos or figures.
5. The full VO as subtitles.

## 7. One example done right (beat 2, 5.5 to 9.4 s)

1. 5.50: «المسرح؟» in serif display lands above a flat printed stage plan; the plan's front edge folds up into a stage with a truss.
2. 6.04: the frame drops to navy; a spotlight cutout swings in and throws a flat paper-coloured cone that reveals «الإضاءة؟». Volt flashes for two frames on the lamp as it strikes.
3. 7.08: the cone keeps rotating around the lamp; the lamp pulls back and becomes the centre of a stopwatch, the cone becomes its hand. «ولا التنظيم» sits on the dial.
4. 8.90: on «ساعة» the hand ticks past each minute mark; the marks peel off the dial and become the ruled lines of a sheet, and the first planning card prints down over them (beat 3).

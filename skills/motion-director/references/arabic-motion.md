# Arabic motion

Arabic typography needs motion decisions that respect joining, direction, and mixed-script layout.

Use browser DOM or SVG text when shaping must remain reliable.

## Direction

Build the composition natively for Arabic. Never mirror an English layout mechanically.

A top-right entry that moves toward the visual center and resolves toward the lower-left is a useful RTL pattern when it fits, not a mandatory template.

For Arabic blocks:

- use RTL direction
- verify alignment visually
- verify punctuation
- verify numerals
- verify mixed Arabic and Latin content

For Latin brand names inside Arabic layouts, isolate their direction so the browser does not reorder the phrase unexpectedly.

## Joining

Arabic letters join.

Character-by-character animation can break the word visually or change joining behavior.

Default to:

- phrase
- line
- word
- full shaped glyph run

Move to individual glyph outlines only when the effect truly needs it and the final shaping has been verified.

## Tracking

Do not apply Latin-style letter spacing to Arabic simply to create air.

Use:

- font size
- line height
- word spacing
- container width
- weight
- alternate cuts
- layout

to create hierarchy.

## Cropping

Arabic has ascenders, descenders, dots, and optional diacritics.

Intentional hero crops can work.

Never accidentally clip:

- dots
- hamza
- diacritics
- descenders
- final letter forms

Inspect every hero crop at the actual final resolution.

The dots carry letter identity. When a sheet, card, or mask edge overlaps the foot of a word, it removes the dots below the baseline first, and ي without its dots reads as another letter. Keep any overlap above the dot and descender zone of a word meant to be read.

Widths differ between faces. Moving a word from a sans to a serif display at the same size changes its width, so recompute any layout that depended on it. With white-space nowrap, an overlong line never wraps and overflows silently.

A text box revealed inside a polygon (a light cone, a torn edge) must sit inside the polygon at its widest reading frame.

Measure instead of guessing. For HTML compositions, scripts/clip-audit.js measures every visible text run against the frame and every clipping container across the timeline. Mark designed crops with data-crop="intentional" so the decision is visible in code.

## Font loading

Do not assume the browser used the intended font because CSS named it.

When the production stack allows it, verify the platform font used to paint Arabic glyphs.

Wait for fonts before the first proof snapshot or render frame.

## Mixed script

Examples:

- Four Steps
- AI
- 2026
- URL
- product name

Treat mixed-script runs as deliberate units.

Use separate spans or bidi isolation when necessary. Balance the Latin word optically against the Arabic mass so it does not overpower the sentence.

Do not let Latin text reverse, jump, or adopt Arabic shaping rules.

## Line breaks

Break Arabic by meaning.

A line break should support:

- emphasis
- rhythm
- visual balance
- reading order

Do not split a fixed phrase only because a container is too narrow.

Fix the composition first.

## Kinetic typography

Good Arabic kinetic patterns:

- masked line rise
- word-by-word arrival
- baseline shift
- large display crop
- word-to-layout transformation
- paper or stamp reveal
- calligraphic path interaction when the font supports it
- weight or width change when a real variable axis exists
- phrase compression and expansion

Avoid default typewriter animation.

Arabic typed character by character often looks mechanically wrong because the visible joining changes with every new character.

## Display alternates

If the font contains stylistic alternates, swashes, or display cuts, inspect them.

Use them as part of composition, not as decoration for every headline.

A swash is useful when it:

- frames another element
- creates a transition path
- anchors the baseline
- balances negative space

Remove it when it only proves the font has a swash.

## Arabic and motion blur

Motion blur can hurt small Arabic text.

Use stronger blur on large hero words and physical objects.

Keep support copy crisp enough to read on a phone.

## Review

Hard-fail if:

- letters disconnect unexpectedly
- font fallback appears
- punctuation reverses
- Latin brand names reorder
- crop removes meaning
- multiple weights collapse into one visual voice
- text is too small at phone scale

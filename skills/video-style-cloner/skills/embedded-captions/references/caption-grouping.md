# Caption Grouping

How to turn the Whisper word-level transcript into the `groups[]` array of plan.json.

## Goal

**Each group is one visual phrase**: enters, reveals word-by-word, exits. Rule of thumb: 1 group ≈ 1 comma-to-comma clause or 1 breath of speech.

## Input

`transcript.json` from `transcribe.cjs`:

```json
{
  "words": [
    { "text": "Some", "start": 0.24, "end": 0.44, "type": "word" },
    { "text": " ", "start": 0.44, "end": 0.48, "type": "spacing" },
    { "text": "memories", "start": 0.48, "end": 0.82, "type": "word" }
  ]
}
```

Drop `type: "spacing"` entries; you only need words.

## Break boundaries

Cut a new group at ANY of:

1. **Pause ≥ 500ms** (gap between word.end[i] and word.start[i+1]) — speaker took a breath.
2. **Sentence terminator** — word ends with `.`, `?`, `!`, or an em-dash-like pause.
3. **Strong comma** — `,` followed by pause ≥ 250ms.
4. **Discourse reset** — words like "but", "so", "and then", "you know" starting a clause often merit their own or new group.
5. **Group reaches 6 words OR 2.5 seconds** — whichever first. Long groups feel like subtitles, not embedded typography.

Hard constraints:

- Minimum 2 words per group (1-word exceptions: interjections like "Wait." or the crown line).
- Minimum 0.5s on screen. If a group is less, merge into neighbor.
- Groups may overlap in time when they occupy separate screen regions (cascade and accumulation). Avoid collisions in both time and screen region. Rail captions share one region, so only one rail group is visible at a time.

## Timing the group

For a group with words `w[0]..w[n-1]`:

- `in` = `max(0, w[0].start - 0.08)` (enter slightly before first word).
- Start with `out` = `w[n-1].end + 0.6` (linger after the final word).
- For the next group in the **same screen region**, shorten that linger to
  `min(next_group.in - 0.05, w[n-1].end + 0.6)` only if the result is at least
  `w[n-1].end`. Always preserve `out ≥ w[n-1].end` and `in ≤ w[0].start`.
- If a 50ms gap and pre-entry would clip a word, reduce those optional margins first.
  If the groups still collide or cannot each hold for 0.5s, merge or repartition them,
  or place embedded groups in separate screen regions. Never trim word timings to fit.
  Spatially separated groups may keep their linger while the next group enters.

The last group may extend to the video end; the video must cover its final word.

## Style & tone (cross-reference)

See `typography-presets.md` for how to pick `style` and `tone` per group. Work left-to-right through the groups and:

1. First group: default `intro` + `soft`.
2. Watch for emphasis signals (ALL CAPS in transcript is rare but possible; more often it's semantic — superlatives, proper nouns).
3. Escalate tone into `present` once the monologue shifts from setup to statement.
4. Reserve `crown` for at most ONE group, typically the final line.

## Editorial surgery is allowed

You do NOT have to caption every word. It's fine to:

- **Drop filler** like extra "you know"s, "um"s, "I mean"s if they bloat the visual pace.
- **Condense** a 6-word run into 4 by cutting function words, as long as the meaning and timing remain truthful.
- **Skip the whole thing** during obvious silence or non-speech (laugh, music interlude).

Editorial rule: you are writing typography to support the speech, not a court transcript. Keep meaning, trim noise.

## Example (champion)

Transcript: "You know, for me I've had this kind of upbringing, had the great foundation and, you know, I've achieved incredible things. I was dreaming of becoming number one in the world and becoming a Wimbledon champion"

Groups after editorial pass (illustrative timestamps; use the actual transcript times in your project):

```json
[
  {
    "id": "cg-0",
    "style": "intro",
    "tone": "soft",
    "words": [{"text": "You", "start": 0.18, "end": 0.427}, {"text": "know", "start": 0.448, "end": 0.695}, {"text": "for", "start": 0.715, "end": 0.962}, {"text": "me", "start": 0.982, "end": 1.23}],
    "in": 0.1,
    "out": 1.35
  },
  {
    "id": "cg-1",
    "style": "phrase",
    "tone": "soft",
    "words": [{"text": "I've", "start": 1.48, "end": 1.73}, {"text": "had", "start": 1.75, "end": 2.0}, {"text": "this", "start": 2.02, "end": 2.27}, {"text": "kind", "start": 2.29, "end": 2.54}, {"text": "of", "start": 2.56, "end": 2.81}, {"text": "upbringing", "start": 2.83, "end": 3.08}],
    "in": 1.4,
    "out": 3.35
  },
  {
    "id": "cg-2",
    "style": "phrase",
    "tone": "soft",
    "words": [{"text": "the", "start": 3.58, "end": 4.067}, {"text": "great", "start": 4.087, "end": 4.573}, {"text": "foundation", "start": 4.593, "end": 5.08}],
    "in": 3.5,
    "out": 5.35
  },
  {
    "id": "cg-3",
    "style": "emph",
    "tone": "present",
    "words": [{"text": "I've", "start": 6.13, "end": 6.59}, {"text": "achieved", "start": 6.61, "end": 7.07}, {"text": "incredible", "start": 7.09, "end": 7.55}, {"text": "things", "start": 7.57, "end": 8.03}],
    "in": 6.05,
    "out": 8.3
  },
  {
    "id": "cg-4",
    "style": "dream",
    "tone": "present",
    "words": [{"text": "dreaming", "start": 8.58, "end": 8.874}, {"text": "of", "start": 8.894, "end": 9.188}, {"text": "becoming", "start": 9.208, "end": 9.502}, {"text": "number", "start": 9.522, "end": 9.816}, {"text": "one", "start": 9.836, "end": 10.13}],
    "in": 8.5,
    "out": 10.4
  }
]
```

Plus the crown:

```json
{ "id": "cg-crown", "style": "crown", "words": [{"text": "Wimbledon", "start": 10.88, "end": 11.345}, {"text": "Champion", "start": 11.365, "end": 11.83}], "in": 10.8, "out": 12.08 }
```

Notice "had" was dropped from cg-2 ("had the great foundation" → "the great foundation"), "I was" was dropped from cg-4, and "a" was dropped from crown — all for visual cadence.

## word.start/end inside groups

Pass through the original timestamps from the transcript. Don't retime individual words — only the group `in`/`out`. The word-level karaoke reveal inside each group uses the original w.start.

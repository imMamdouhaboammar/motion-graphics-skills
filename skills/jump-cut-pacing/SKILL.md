---
name: jump-cut-pacing
description: Tighten raw talking-head footage with silence trimming and intentional face-safe jump cuts. Detects pauses with FFmpeg, preserves breath padding, alternates subtle reframing only when it helps continuity, and keeps the speaker face safe. Use for talking-head edits, voice pause cleanup, jump-cut pacing, or requests such as "cut the silences", "tighten this video", and "smooth talking head zooms".
---

# Jump Cut and Pacing

Treat pacing as editorial direction, not automatic silence deletion.

The goal is to remove dead air while preserving breath, thought, emphasis, and the speaker's physical continuity. A fast cut is not automatically a better cut.

## Decision gate

Use this skill when the source is mainly a presenter or interview and the editing problem is cadence.

Do not use it as the main solution when:

- pauses are intentional dramatic beats
- the source depends on performance timing, comedy, or music sync
- a cut would remove a breath needed for intelligibility
- the reference uses continuous camera movement rather than editorial punch-ins
- the speaker already changes framing naturally between cameras

When uncertain, preserve the pause and flag it for review.

## Editorial rules before automation

1. Keep micro-pauses that make speech human.
2. Cut retakes, abandoned starts, and dead air more aggressively than sentence breathing.
3. Place cuts at phrase boundaries when possible.
4. Avoid two hard cuts inside one short clause.
5. Use a punch-in to clarify a cut, not on every sentence by habit.
6. If the speaker moves strongly across a cut, prefer a wider frame or b-roll bridge instead of a tighter crop.

Read references/pacing-rules.md before changing the default thresholds.

## Workflow

### Step 1: Build the cut plan

Use the bundled planner:

~~~bash
python3 scripts/cut_plan.py "$WORK/src.mov" --min-silence 0.45 -o "$WORK/cut_plan.json"
~~~

The planner probes the source duration with ffprobe when total duration is omitted. FFmpeg or ffprobe failure is a hard failure and must not produce a successful empty plan.

The plan contains:

- source start and end for every kept speech segment
- preserved lead padding before speech
- preserved tail padding after speech
- alternating zoom values
- zoom_anchor_y for face-safe vertical framing

### Step 2: Review the plan as an editor

Before rendering, inspect:

- whether a meaningful pause was classified as dead air
- whether any kept segment is too short to read naturally
- whether two cuts happen too close together
- whether zoom alternation matches emphasis rather than becoming a metronome

If a section feels rushed, restore time. Do not lower the silence threshold globally just to fix one sentence.

### Step 3: Render each segment with its planned framing

A cut plan is not complete until the zoom fields affect the pixels.

For every segment with source interval S to E, zoom Z, and anchor A, build a video branch using this pattern:

~~~text
[0:v]
trim=start=S:end=E,
setpts=PTS-STARTPTS,
scale=iw*Z:ih*Z,
crop=iw/Z:ih/Z:(iw-ow)/2:(ih-oh)*A
[vN]

[0:a]
atrim=start=S:end=E,
asetpts=PTS-STARTPTS
[aN]
~~~

Then concatenate the matching video and audio branches in plan order:

~~~text
[v0][a0][v1][a1]...[vN][aN]concat=n=SEGMENT_COUNT:v=1:a=1[outv][outa]
~~~

For Z equal to 1.0, this resolves to the original framing. For a punch-in, the scaled frame is cropped back to delivery size with the vertical crop controlled by zoom_anchor_y.

If the active project already uses HyperFrames or another deterministic timeline, translate the same segment plan into that runtime instead of building a second renderer.

### Step 4: Protect the face

Verify at least:

- crown and hair are not clipped
- eyes stay comfortably above center
- chin is not trapped against captions
- hand gestures are not removed by a punch-in
- the crop still works if the presenter leans during the segment

### Step 5: Protect audio continuity

Use the camera or production master audio. Do not reintroduce transcription audio into the final edit.

Check the assembled output for:

- clipped consonants
- missing word tails
- clicks at cuts
- sudden room-tone changes
- accidental loudness pumping

## Rhythm patterns

A useful sequence can be:

wide -> punch -> wide -> hold -> punch

A weak sequence is:

wide -> punch -> wide -> punch -> wide -> punch

The second pattern exposes the automation. Break the pattern when the meaning changes.

## Creative QA

Hard-fail the edit if:

- the speaker sounds unnaturally breathless
- zooms happen with no semantic reason
- face framing becomes less stable after the edit
- the same two zoom states repeat for the whole video
- a cut lands inside a meaningful word or gesture
- the output is shorter but less comprehensible

## What I learned the hard way

- Centered crops often clip foreheads in vertical talking-head footage.
- Removing every pause makes natural speech feel synthetic.
- Alternating zoom is useful camouflage, but visible repetition becomes its own defect.
- The rendered video is the evidence. A correct JSON plan is not proof that pacing works.

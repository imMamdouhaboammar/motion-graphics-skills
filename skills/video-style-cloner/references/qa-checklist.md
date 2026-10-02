# Visual QA Checklist: Full Expanded Version

Use this checklist at EVERY gate. No gate passes without running it.
Use the Read tool to open frame crops at full resolution. If unclear → crop and zoom.

## Character Integrity
- [ ] All limbs attached to body: no floating arms, legs, or hands
- [ ] Neck present and proportionally natural
- [ ] Head connected to neck without gap or seam
- [ ] Fingers/hands: correct count, not fused or missing
- [ ] Feet touching ground correctly when standing
- [ ] No body parts mirrored incorrectly

## Line & Stroke Quality
- [ ] No double-stroke outlines (no ghosting)
- [ ] Consistent line weight throughout frame
- [ ] No seams where separate elements join
- [ ] Outlines close completely: no open paths

## Character Consistency
- [ ] Design matches approved character sheets
- [ ] Expression set matches brief
- [ ] Clothing/accessories consistent with previous shots
- [ ] Hair style consistent across frames

## Composition & Framing
- [ ] Subject fills frame at appropriate ratio (plan.json `fill` value ±15%)
- [ ] No critical content clipped at frame edges
- [ ] Horizon/ground line consistent with context
- [ ] Negative space intentional, not accidental

## Text & Typography
- [ ] All text legible at final export resolution
- [ ] No text clipped by frame edge
- [ ] Caption timing matches lyrics/script (if applicable)
- [ ] Font consistent with style spec

## Technical
- [ ] No colour banding
- [ ] No frame flicker or brightness pop between shots
- [ ] No compression artefacts on exported frame
- [ ] No mesh intersection / model clipping (for 3D-derived assets)

## Motion
- [ ] Motion has anticipation (wind-up before fast move)
- [ ] Motion has follow-through (settle after move completes)
- [ ] Camera move speed matches plan.json `camera.speed`
- [ ] No teleport cuts: subject positions make continuity sense

## Audio Sync (final assembly gate only)
- [ ] Beat cuts align within ±1 frame of plan.json beat markers
- [ ] Audio fade-in/out smooth (no click)
- [ ] No audio-video desync at segment joins

---

## Scoring

Each item is binary. Count failures:
- **0 failures** → PASS → proceed
- **1-2 minor failures** → CONDITIONAL PASS → fix in next segment, log to fixes.json
- **3+ failures or any character-integrity failure** → FAIL → return to producer

Never mark PASS on a character-integrity failure regardless of score.

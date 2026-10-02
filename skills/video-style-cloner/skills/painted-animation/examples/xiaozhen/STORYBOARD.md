# Example · 小镇姑娘 (David Tao), a 31 s lyric video

Made with this skill by Claude Opus 5.5 in Claude Code. The prompt was the lyrics of one verse plus three notes: read the song's context so the visuals aren't abrupt; fans joke that "大经理" (big manager) is "大锦鲤" (big lucky koi), so show that; and later, the song file and the LRC timings. The scene code is in [xz_set.js](xz_set.js) (the world, cast and props) and [xz_shots.js](xz_shots.js) (the shots). To run it, scaffold a project, copy both files into `src/scenes/`, add `src/karaoke.js` with the song's `LY` table, and put your own copy of the song in `assets/`. The song isn't included.

![contact sheet](../../docs/xiaozhen-sheet.jpg)

**Logline:** A year ago the small-town girl left on the train, crying at the window. Now I hear she's a "big manager" (a big lucky koi). Seeing her shine like a star and happy, I can finally stop worrying, and I take the train myself.

**Song grid:** 154 BPM (half-time 77.125), one lyric line = 8 beats ≈ 3.1 s. The clip is 146.887–177.987 s of the song: one bar before the first line, room after the last line for the ending, and a 2 s fade.

**One world:** a small-town railway station in three lights: dusk now → the sepia memory (old-film scratches) → night now. **Motif:** her flower. It's on her head, then on the koi, then on the star, so you always know it's her. **Rhyme:** she left by train at the start; I leave by the same kind of train at the end.

| Clip time | Line | Shot | In |
|---|---|---|---|
| 0–3.02 | (intro bar) | Dusk. I sit on the bench with my suitcase, staring down the empty line, and sigh. | iris from dark |
| 3.02 | 还记得一年前站在火车站 | Sepia memory. She turns, walks to the train, and hops into the doorway; I step after her with a hand out. | sepia brush wipe |
| 6.07 | 看着自己的悲剧演完 | The door shuts. The platform becomes a stage: a spotlight on me, a rain cloud, and the red curtain falls. | cut on action |
| 9.08 | 透过玻璃窗看见你的泪满面 | The curtain opens on the train window (my POV): she cries and presses her paw to the glass, and the window slides away. | curtain |
| 12.38 | 那车头依然吐着烟 | The engine puffs a cloud on every beat as it pulls out; I run, stop and wave; the smoke swallows the frame. | cut on action |
| 15.39 | 听说现在的你成了大经理 | Night, the waiting-room TV: she's on an award stage in a tie. **On "经理" (≈17.6):** poof, she's a big golden koi (with the flower and tie), the crowd bows to it, and the lyric is struck through and becomes **锦鲤**. That line is then held above the next one for 1.4 s. | smoke clears |
| 18.64 | 前途好比闪亮的星星 | The koi leaps out of the TV, out of the window, swims up the night sky, and **becomes a star** on "星星". | cut on action |
| 21.54 | 我只希望这所有能够让你欢喜 | Tilt down to me. Her star smiles and winks; I clasp my hands, a little heart floats up to her, and the star glows. | camera carries through |
| 25.01 | 我才能放心走 | The night train pulls in; I pick up my case, wave up at her star, and hop aboard; the door shuts and it pulls out. Tilt up to her star, it winks, iris. | — |

**Lessons it taught the skill:** get the LRC and measure the tempo before storyboarding (the first draft, timed by feel, was twice too slow); carry a gag across a line boundary instead of slowing the song; paint a doorway's jambs back over whoever stands in it; don't name globals after p5's (`line`).

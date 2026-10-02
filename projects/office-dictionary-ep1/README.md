# قاموس المكتب، الحلقة 1: «مين عنده سؤال؟»

A 41.5 s vertical reel (1080 × 1920, 30 fps) in Egyptian Arabic about psychological safety at work,
cut to the owner's recorded voice over. First episode of the «قاموس المكتب» series.

The voice and the screen play ping pong: the voice throws a line, the screen answers it or finishes it
(«عشان السؤال ده...» → the stamp «هيبان غبي»).

## The film

| Time | Beat | On screen |
|---|---|---|
| 0.0 | Hook | «مين عنده سؤال؟» written on a chalkboard, six silent team members, every glass dome lights a question |
| 4.6 | Inside one head | zoom into a dome, red spiral world: stamp «هيبان غبي», the boss's reply mail, the boss's eye and clock |
| 11.0 | Out | everyone nods, the door shuts, the side chat «جروب الفريق، من غير المدير» |
| 15.8 | The name | the world turns lavender, dictionary card «أمان نفسي (اسم)», three ticks, the team relaxes |
| 22.2 | Proof | Google's Project Aristotle: 180 teams, five team dynamics, #1 psychological safety |
| 31.0 | Payoff | the question gets swallowed, the project bar shows what it could have reached |
| 35.6 | CTA | «ابعته لمديرك»; spotlight on «ولو خايف تبعته...»; «يبقى فهمت الحلقة ✓» |
| 40.0 | End card | series title and the next episode «معلش، حاجة سريعة» |

Direction is in `mix-brief.md`: three supplied references, mixed with `mix-and-match`.

## Files

| Path | What it is |
|---|---|
| `index.html` | the composition, one seek-safe GSAP timeline |
| `assets/audio/vo.wav` | the supplied voice over, untouched (40.2 s) |
| `assets/audio/vo-words.json` | word timings from faster-whisper `medium` (Arabic) |
| `tools/cues.py` | writes every sound cue from the word timings |
| `ASSET_SOURCES.md` | where every asset came from |
| `renders/office-dictionary-ep1.mp4` | the delivered reel |

## Commands

```bash
python3 tools/cues.py
npx hyperframes@0.8.92 lint
npx hyperframes@0.8.92 render -f 30 -q delivery -o renders/out.mp4
ffmpeg -i renders/out.mp4 -c:v copy -af "alimiter=limit=0.82:level=false" -c:a aac -b:a 192k -movflags +faststart renders/office-dictionary-ep1.mp4
```

## Delivery check

- **Encoding:** H.264, yuv420p, bt709, 1245 frames (41.5 s), AAC.
- **Loudness:** -14.4 LUFS integrated, -1.4 dBTP peak.
- **Review:** `video-review-loop` reported 0 hard findings. The warnings are short reading holds; the longest (1.2 s at 28.6 s) is the pause before #1 is revealed.

# Beat map

Master timeline: `assets/audio/vo-master.wav` (48 kHz mono PCM, 26.122 s, md5 `ab45442336d95b74c19cf296da9ec5e3`), untouched.
Word times: whisper large-v3 (`assets/audio/transcript.json`), cross-checked against `silencedetect -40 dB`.
Film: 30 fps. Last spoken word ends 25.89 s, WAV ends 26.12 s. The WAV already exceeds the 25 s target, so the film is WAV length plus a 0.48 s silent CTA hold = **26.60 s (798 frames)**. The VO is not trimmed, stretched or sped up.

Pauses (> 120 ms): 1.24 to 1.50, 4.39 to 4.55, 9.68 to 9.90, 11.69 to 11.82, 13.62 to 13.91, 15.18 to 15.46, 17.90 to 18.14, 22.38 to 22.59, 23.26 to 23.51, 25.30 to 25.45.

| # | Start | End | Spoken | Visual idea | Visible text | Assets | In | Out | Intensity |
|---|---|---|---|---|---|---|---|---|---|
| B1 | 0.00 | 1.50 | شايف الموشن هذا؟ | Hook. See `openings.md` for the chosen study | الموشن هذا؟ | type | first frame already moving | hard flip to paper at 1.50 (pause) | high |
| B2 | 1.50 | 4.33 | تقدر تسوي زيه بدون ما تفتح After Effects | A purple "Ae" tile taped to paper. «بدون» lands at 2.33. Scissors cut the tape at 3.20 and the tile drops out of frame on "Effects" (3.56 to 4.20), leaving its pale ghost | بدون · After Effects | Ae tile (drawn), tape, scissors cutout | hard flip | T1 cursor cut R→L at 4.30 | medium, one impact |
| B3 | 4.33 | 7.95 | جهزت لك Skill تخلي Claude Code يبني الموشن معك | Night. The real install command types in mono (4.40 to 5.25), Enter at 5.35, one output line. «Claude Code» rises at 5.88. On «يبني الموشن» (6.74) the command line becomes a timeline: ticks, six frames stamping in, a clay playhead | the command · Claude Code | JetBrains Mono, drawn timeline | T1 | T2 push into the frame under the playhead at 7.85 | building |
| B4 | 7.95 | 9.72 | من الفكرة لين الرندر | The pushed frame is now a paper canvas. A pencil sketch (8.19 «الفكرة») straightens into a wireframe (8.6 to 9.0) and fills into a rendered frame with a full progress bar on «الرندر» (9.06) | الفكرة · الرندر | drawn SVG | T2 | T3: the canvas becomes the script sheet | medium |
| B5 | 9.72 | 13.62 | ومعها Skill تكتب لك السكربت / وSkill تسوي لك الـVoice Over | A script sheet carrying this film's real script lines. «السكربت» at 10.85. On the second Skill (11.64) every line collapses into a waveform bar built from this VO's own envelope; the mic cutout rises; «Voice Over» at 12.56 | السكربت · Voice Over | script text, VO envelope, mic cutout | T3 | T3: waveform flattens into one clay line at 13.45 | fast pair |
| B6 | 13.62 | 15.20 | ولسه فيه أكثر | Pattern interrupt. Night, one clay line across the frame. «ولسه فيه» small at 13.72, «أكثر» rises out of the line at 14.56 and holds | ولسه فيه أكثر | none | T3 | the line splits open vertically at 15.18 (pause) | quiet |
| B7 | 15.20 | 18.14 | جايب لك عرض قوي على Claude Code نفسه | Paper. A clay-ink stamp «عرض قوي» hits on «عرض» (15.80). «على Claude Code» prints below at 16.68. No price, no percentage, no timer | عرض قوي · Claude Code | stamp (drawn + halftone ink) | line split | T2 pull-out at 18.14 (pause) | impact then hold |
| B8 | 18.14 | 22.45 | يعني الأدوات كلها صارت عندك / وتقدر تفتح Studio وأنت في بيتك | The stamped sheet shrinks onto a desk. Tools arrive and settle around it on «الأدوات» (18.44 to 19.65): keyboard, mic, headphones, scissors, the timeline strip. «Studio» with a clay rec dot at 20.85, «في بيتك» at 21.94 | Studio · في بيتك | keyboard, mic, headphones, scissors cutouts | T2 | T1 cursor cut at 22.40 | densest |
| B9 | 22.45 | 26.60 | عليك تبدأ بس / اترك لي تعليق وراح أرسل لك كل شيء | Night. «عليك تبدأ بس» small at 22.51. «اترك تعليق» lands at 23.66 with the clay cursor blinking at its end. Nothing new after 24.7. Clean hold | عليك تبدأ بس · اترك تعليق | none | T1 | hold, 0.48 s silent tail | resolve |

## Sound

VO dominant at unity. Three structural SFX from the HyperFrames bundled library, each at least 14 dB under the VO:
- 3.22 s `click` — the scissors cut the tape.
- 5.35 s `key-press` — Enter on the command.
- 15.78 s `impact-bass-1` — the stamp.
No music bed. No whoosh per transition.

## End hold

Last key word «تعليق» 24.16 to 24.66 s. The CTA is fully composed by 24.1 s and nothing new enters after 24.7 s, so the CTA holds 2.5 s, including the 0.48 s silent tail.

# Beat map

Word times from `assets/transcript.json`. Every word cue in `index.html` fires 0.1 s before the spoken word (`LEAD`). Scene boundaries sit in the pauses between phrases.

| Scene | Time (s) | VO | Visual |
|---|---|---|---|
| S1 | 0.00 to 1.32 | بسألك سؤال | «سؤال» at 330 px, ghost «؟», green bar rises |
| S2 | 1.32 to 3.32 | شركة كل شغلها سري | Case file, redaction bars, «سري» stamp lands at 2.48 |
| S3 | 3.32 to 5.62 | وعملاؤها ما أحد يعرف أسماءهم | Five figures, eye bars and name tags draw on |
| S4 | 5.62 to 7.50 | ليش تعطيك تقييم مجاني؟ | Hang tag «تقييم» drops at 6.2, green panel, «مجاني؟» |
| S5 | 7.50 to 9.36 | خلني أقول لك السبب بصراحة | Green field, «السبب» with a drawn rule |
| S6 | 9.36 to 12.92 | أغلب الناس يدورون على جدار بعد ما يجي السيل | Figure searching among small walls; water rises from 11.5 and fills the frame |
| S7a | 12.92 to 14.02 | الخبر انتشر | One front page multiplies into eight |
| S7b | 14.02 to 15.26 | الهاشتاق شغال | Huge «#», illustrative counter, three pop-ups |
| S7c | 15.26 to 17.26 | والوقت ضيق على أي قرار | Clock wedge fills, time bar shrinks |
| S8 | 17.26 to 19.62 | والشغل وقتها أصعب... وأغلى | Bars rise to 35 %, then jump at «وأغلى» with a shake |
| S9 | 19.62 to 24.45 | عشان كذا جدار، أول شركة سعودية متخصصة في إدارة الأزمات الإعلامية | Wall builds bottom-up; wordmark at 20.16; two chips |
| S10 | 24.45 to 26.60 | تفتح الباب قبل الأزمة | Door bricks fade, door opens at 25.2, light; camera ×7 into the door from 26.0 |
| S11 | 26.60 to 28.34 | تقييم جاهزية مجاني | Pinned note on a green grid, check mark draws at 27.75 |
| S12 | 28.34 to 29.85 | يراجعون حضورك الإعلامي | Nine post cards, magnifier sweeps |
| S13 | 29.85 to 31.78 | يحددون وين أنت مكشوف | Same grid; other cards dim, brackets lock on one, «مكشوف» |
| S14 | 31.78 to 35.00 | ويقولون لك وش الشرارة اللي ممكن تشعل أزمة | Match rises; flame and sparks at 33.9; «أزمة» with a shake |
| S15 | 35.00 to 37.36 | بعد التقييم بتعرف ثلاث أشياء | «٣» extruded; panel with «أشياء» |
| S16 | 37.36 to 44.22 | مين أول شخص تتصل فيه / وش البيان / ووين الثغرة اللي غيرك شايفها قبلك | Numbered rows arrive on each question; earlier rows dim; crack draws in the wall icon |
| S17 | 44.22 to 49.62 | والمصلحة واضحة للطرفين. أنت تعرف وضعك. وهم يعرفونك قبل ما تحتاجهم | Seesaw levels at 45.2; «أنت» then «جدار» blocks highlight |
| S18 | 49.62 to 53.38 | إذا اسمك أو شركتك صار لها حضور وما تدري وين مكشوف | Browser window types three lines in sync |
| S19 | 53.38 to 59.00 | أرسل كلمة (جاهز) على واتساب جدار. الرقم في التعليق المثبت | Chat: «جاهز» typed, sent at 54.62, stays on screen to the end; pinned-comment card at 55.9; positioning line at 57.1 |

## End hold

The last word ends at about 57.5 s and the WAV at 57.81 s, so there is no room for a hold inside the audio. The film adds 1.2 s: `window.seek` clamps time to `VO_END`, the render range is 0 to 59 s, and the mux pads the audio with `apad=pad_dur=1.2` without `-shortest`. Following [Plan the end hold in the beat map](../../Failure-lessons/render-pipeline.md#plan-the-end-hold-in-the-beat-map).

## Script requirement checks

- «جاهز» is on screen from 54.1 s to 59.0 s (4.9 s, in the input field and then the sent bubble). The script asks for the last 5 seconds.
- No music in the first 3 seconds: the film has no music.

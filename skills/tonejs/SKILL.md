---
name: tonejs
description: Use when adding audio, sound design, music sequencing, or audio-reactive animation to a project. Use when syncing Tone.js with GSAP timelines, creating beat-locked animations, playing sound effects on motion events, generating oscillator tones, or building audio visualizers with waveform/frequency data driving DOM elements.
license: MIT
---

# Tone.js

## When to Use This Skill

Apply when any of the following are needed:

- Playing audio files (SFX, VO, music) alongside GSAP animations
- Beat-synchronized or BPM-locked animation (e.g. scene cuts on the beat)
- Audio-reactive visuals — DOM/SVG elements animated by waveform or frequency data
- Programmatic sound generation (synths, oscillators, UI sounds)
- Adding audio effects (reverb, delay, distortion) to any source

**Related skills:** For timeline sequencing use **gsap-timeline**; for performance use **gsap-performance**; for scroll-sync use **gsap-scrolltrigger**.

> ⚠️ **Browser Autoplay Policy** — `Tone.start()` MUST be called inside a user-gesture handler (click, keydown, etc.). Audio context will not resume otherwise. Always gate initialization behind an interaction.

---

## Setup

**CDN (vanilla HTML projects):**
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
```

**npm / bun:**
```bash
bun add tone
```
```js
import * as Tone from 'tone';
```

**Required initialization (always wrap in user gesture):**
```js
document.getElementById('start-btn').addEventListener('click', async () => {
  await Tone.start();           // Resume AudioContext
  Tone.getTransport().start();  // Start master clock
}, { once: true });
```

---

## Core Architecture

```
Tone.js signal graph
  Source  →  Effect(s)  →  Destination
  Synth       Reverb        toDestination()
  Player      Delay
  Analyser    Distortion
```

All nodes connect via `.connect()` or `.toDestination()` shorthand.

---

## Quick Reference

| Task | API |
|---|---|
| Play a tone | `new Tone.Synth().toDestination().triggerAttackRelease("C4", "8n")` |
| Load + play file | `new Tone.Player(url).toDestination(); player.start()` |
| Add reverb | `const rev = new Tone.Reverb(2).toDestination(); synth.connect(rev)` |
| Schedule on beat | `Tone.getTransport().scheduleRepeat(cb, "4n")` |
| Read waveform | `new Tone.Analyser("waveform", 64).getValue()` |
| Read frequency | `new Tone.Analyser("fft", 32).getValue()` |
| Set BPM | `Tone.getTransport().bpm.value = 120` |
| Sync visual to audio | `Tone.getDraw().schedule(() => { /* gsap here */ }, time)` |
| Stop everything | `Tone.getTransport().stop(); Tone.getTransport().cancel()` |

---

## GSAP Sync — The Right Way

**Problem:** Tone callbacks run on the audio thread. Calling `gsap.to()` directly inside them causes jitter.

**Solution:** Always use `Tone.getDraw().schedule()` to bridge audio events to the visual frame.

```js
// ✅ Correct — no jitter
Tone.getTransport().scheduleRepeat((time) => {
  Tone.getDraw().schedule(() => {
    gsap.fromTo('#element', { scale: 1 }, { scale: 1.2, duration: 0.1 });
  }, time);
}, '4n');

// ❌ Wrong — triggers on audio thread, causes jitter
Tone.getTransport().scheduleRepeat((time) => {
  gsap.to('#element', { scale: 1.2 }); // DO NOT do this
}, '4n');
```

---

## Audio-Reactive Animation

Wire a `Tone.Analyser` into the GSAP ticker to drive DOM elements in real time:

```js
const analyser = new Tone.Analyser('waveform', 64);
const synth    = new Tone.Synth().connect(analyser).toDestination();

// Pull audio data every animation frame via GSAP ticker
gsap.ticker.add(() => {
  const waveform = analyser.getValue(); // Float32Array, values in [-1, 1]
  const bars = document.querySelectorAll('.bar');

  bars.forEach((bar, i) => {
    const amp = Math.abs(waveform[i] ?? 0);
    gsap.set(bar, { scaleY: 1 + amp * 15 }); // gsap.set — no tween overhead
  });
});

synth.triggerAttackRelease('C3', '1n');
```

> Use `gsap.set()` (not `gsap.to()`) inside `ticker.add()` — creating new tweens every frame is expensive.

---

## BPM-Locked Scene Cuts

```js
Tone.getTransport().bpm.value = 120;

// Fire visual on every measure
Tone.getTransport().scheduleRepeat((time) => {
  Tone.getDraw().schedule(() => {
    gsap.fromTo('#scene', { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 });
  }, time);
}, '1m'); // 1m = 1 measure

Tone.getTransport().start();
```

---

## Playing Audio Files (SFX / VO)

```js
const player = new Tone.Player({
  url:       'assets/audio/whoosh.mp3',
  autostart: false,
}).toDestination();

// Trigger on a GSAP event
gsap.to('#card', {
  y: -200,
  onStart: () => player.start(),
});
```

---

## Effects Chain

```js
const reverb = new Tone.Reverb({ decay: 3, wet: 0.4 }).toDestination();
const delay  = new Tone.FeedbackDelay('8n', 0.3).connect(reverb);
const synth  = new Tone.Synth().connect(delay);

synth.triggerAttackRelease('A3', '4n');
```

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Audio doesn't start | Call `await Tone.start()` inside a click/keydown handler first |
| Jittery visuals | Never call `gsap.to()` directly in Tone callbacks — use `Tone.getDraw().schedule()` |
| `gsap.to()` inside ticker | Use `gsap.set()` inside `gsap.ticker.add()` — never create tweens per frame |
| Transport events fire twice | Call `Tone.getTransport().cancel()` before re-scheduling |
| Player not ready | Wrap `player.start()` in the `player.load()` promise or use `onsuccess` |
| High CPU from analyser | Use a small buffer size (32–64) and avoid FFT when waveform is enough |

---

## Minimal Working Example (vanilla HTML)

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
<script src="assets/vendor/gsap.min.js"></script>
<script>
  document.body.addEventListener('click', async () => {
    await Tone.start();

    const analyser = new Tone.Analyser('waveform', 32);
    const synth    = new Tone.Synth().connect(analyser).toDestination();

    gsap.ticker.add(() => {
      const data = analyser.getValue();
      document.querySelectorAll('.bar').forEach((bar, i) => {
        gsap.set(bar, { scaleY: 1 + Math.abs(data[i] ?? 0) * 10 });
      });
    });

    synth.triggerAttackRelease('C2', '2n');
  }, { once: true });
</script>
```

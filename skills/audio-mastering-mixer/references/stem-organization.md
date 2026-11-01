# Audio Stem Organization and Mixing Hierarchy

Architecture for organizing audio assets across motion graphics productions.

## Three Stem Separation

1. `VOICE.wav`: Raw narrated speech, leveled and gated.
2. `MUSIC.wav`: Instrumental bed with designated drop points.
3. `SFX.wav`: Frame-synchronized tactile foley events.

## Ducking Automation Strategy

Duck music track volume dynamically whenever the voice track amplitude exceeds -36 dB. Ensure attack is set to 20ms and release is set to 250ms to prevent unnatural pumping artifacts.

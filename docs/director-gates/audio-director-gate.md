# Gate 4: Audio Director Quality Gate

Sign-off criteria for Phase 4 (Sound Design and Loudness).

## Mandatory Sign-Off Criteria

1. **Audio-First Synchronization**:
   - Spoken words aligned with frame-exact visual events.
   - Scene transitions occur on musical downbeats or bar boundaries.
2. **Tactile Foley and Whoosh Prohibition**:
   - Subtle clicks and ticks attached to meaningful UI interactions (counters, checklist marks, button taps).
   - Zero gratuitous whooshes on basic card entries or exits.
   - Climax impact receives 60ms of acoustic silence prior to hit.
3. **Broadcast Loudness Standards**:
   - Integrated master loudness measured between -13.5 and -14.5 LUFS.
   - Maximum true peak below -1.25 dBTP.
   - Music ducked by at least 12.0 dB beneath spoken dialogue.

## Verdict Contract

- **PASS**: FFmpeg loudnorm scan confirms -14.0 LUFS and true peak under -1.25 dBTP.
- **BLOCK**: Audio clipping, un-ducked music masking speech, or missing tactile foley cues.

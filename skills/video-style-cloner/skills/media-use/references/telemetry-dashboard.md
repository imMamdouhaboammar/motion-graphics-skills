# media-use usage dashboard

Dashboard definitions for the standalone audio scripts shipped here. The resolve wrapper delegates to an installed HyperFrames CLI; this package does not emit resolve, candidates, doctor, or compare events. Its resolver statistics and any CLI telemetry depend on that installation.

## Identity (see `scripts/lib/telemetry.mjs`)

Events attribute to the **same person as the hyperframes CLI and studio**
— the shared install id in `~/.hyperframes/config.json` (`anonymousId`), stitched
to the HeyGen account (`$identify`, `distinct_id` = email/username) on sign-in.
Not fully anonymous by design; pseudonymous before sign-in, account-linked after.
`$ip:null`. Opt-out: `HYPERFRAMES_NO_TELEMETRY=1` / `DO_NOT_TRACK=1` (also CI, dev).

## Event catalog (verified present in-project)

Every event carries `surface: "media-use"`. Event **properties are coarse** —
never intent text, file names, or paths.

| Event | Fires after | Properties |
| --- | --- | --- |
| `media_use_transcribe` | successful transcription | `engine` |
| `media_use_duck` | successful ducking output | `sequential` |
| `media_use_transcript_cut` | successful cut plan or encode | `mode`, `remove_fillers`, `cut_silence`, `ranges`, `keep` |

## Dashboard tiles

1. **Audio operation volume** — count the three events over time, broken down by event.
2. **Transcription engine mix** — break down `media_use_transcribe` by `engine`.
3. **Ducking placement** — break down `media_use_duck` by `sequential`.
4. **Transcript cut modes** — break down `media_use_transcript_cut` by `mode`; optional breakdowns use its boolean properties.

These events count successful script outputs, not failures, synthesized voice lines, BGM jobs, or SFX cues. They cannot measure resolver hit rates, doctor health, or compare cost. Validate received event schemas in your authorized analytics project before creating tiles; keep names prefixed `media-use:`.

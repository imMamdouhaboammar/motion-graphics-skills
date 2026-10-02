# Sound effects (SFX)

Named sound effects, produced by the shared audio engine (`scripts/audio.mjs` → `scripts/lib/sfx.mjs`). **Provider-gated** by the engine's one switch — whether a HeyGen credential is present, decided once (not per cue):

- **HeyGen credential present → retrieve every cue** from HeyGen's audio library (`/v3/audio/sounds`, `type=sound_effects`, `min_score=0.4`). Search-and-download, **not** generation. The local manifest is not consulted.
- **No credential → a user-supplied local library** (`assets/sfx/` + `manifest.json`): match each cue name and copy the matched file into the project. This package ships an empty manifest and no audio files, so offline cues are skipped until you supply assets.

There is no `npx hyperframes sfx` command. SFX is never generated — it is retrieved (online) or copied from user-supplied assets (offline).

## Cues — request → meta

Each line names the effects it wants: `lines[].sfx: ["whoosh", "click"]`. The engine flattens these into cues, resolves them per the switch, dedupes identical `(id, name)` pairs (the same effect named twice downloads/copies once), and writes `audio_meta.sfx[]`:

```jsonc
{
  "id": "3",                       // joins the cue to the caller's model (frame / scene / segment)
  "name": "whoosh",
  "file": "assets/sfx/whoosh.mp3", // downloaded or copied, relative to project root
  "source": "heygen" | "local",    // which route resolved it
  "offset_s": 0,                   // delay from the line's start
  "duration_s": 0.57,
  "volume": 0.35                   // SFX sit UNDER voice + BGM
}
```

A cue that matches nothing is **skipped** (recorded as an anomaly); SFX never blocks a render.

## HeyGen retrieval (credentialed)

`searchSounds(name, "sound_effects", headers, { limit: 3, minScore: 0.4 })` → top hit → `assets/sfx/<slug>.mp3`. Results are ranked by `score` (each carries a presigned `audio_url`, `duration`, `description`). The floor is **0.4** because good SFX hits score ~0.5–0.67 — below the API's default `0.7`, which would silently drop most named cues (only whoosh/swoosh-family clears 0.7). `duration_s` comes from the result (else 1.0). Name effects concretely (`glass shatter`, not `dramatic sound`); a vague query returns a poor match.

## Local library (no credential)

The shipped `assets/sfx/manifest.json` is empty. Add your own permitted audio files alongside it and entries such as:

```json
{ "click": { "file": "click.mp3", "duration": 0.2, "description": "UI confirmation" } }
```

A cue resolves by manifest key, file basename, or the slug of either. With that entry and file present, `click` and `click.mp3` match; `"ui click"` becomes `ui-click` and requires its own manifest key. Matched files are copied into the project's `assets/sfx/`; `duration_s` comes from the manifest. Missing files or unknown names are skipped with an anomaly. Record sources and licenses in `assets/sfx/CREDITS.md`.

## Rules

- **Volume ~0.35.** SFX must sit under narration and BGM, not fight them.
- **No match → skip, don't fail.** A missing effect logs an anomaly and moves on; never a render blocker.
- **Retrieval (credentialed) or local assets (offline) — never generation.** You search HeyGen by text or match a name against your local manifest.
- **One asset per distinct name.** Reuse across lines is deduped to a single download/copy, many cues.
- **The switch is global, not per cue.** With a credential, retrieval handles every cue; without one, only names backed by your local manifest and files resolve.

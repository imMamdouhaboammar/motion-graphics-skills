# Asset Licensing Reference

## Asset sources

Run commands from the repository root, or set `$SKILL_DIR` to this suite's absolute path.
The search command always queries Openverse. It also queries Pixabay for images
when `PIXABAY_KEY` is set, or Freesound for audio when `FREESOUND_KEY` is set.
There is no `--sources` option. Check each returned asset's license before use.

| Source | Search type | Licences returned | CLI |
|---|---|---|---|
| [Openverse](https://openverse.org) | Images, audio | CC0, CC BY, CC BY-SA | `python "$SKILL_DIR/skills/video-clone/scripts/fetch_assets.py" search --kind image --q "paper texture" --cc0` |
| [Pixabay](https://pixabay.com) | Images | Pixabay Content License | `python "$SKILL_DIR/skills/video-clone/scripts/fetch_assets.py" search --kind image --q "forest"` |
| [Freesound](https://freesound.org) | Audio/SFX | CC0, CC BY | `python "$SKILL_DIR/skills/video-clone/scripts/fetch_assets.py" search --kind audio --q "whoosh"` |
| [Unsplash](https://unsplash.com) | Photos | Unsplash licence | Manual download |
| [SVGrepo](https://svgrepo.com) | SVG icons | Check each asset's licence | Manual download |

Openverse's default commercial/modification search can return CC BY-SA assets.
Attribute the author, link the applicable license and record changes. Adaptations
must use the same or a compatible license, and must not impose additional restrictions.
Read the [CC BY-SA 4.0 terms](https://creativecommons.org/licenses/by-sa/4.0/)
and the specific version attached to the asset. Use `--cc0` or choose another asset
when the project's distribution terms cannot satisfy ShareAlike.

## Licence Grades

| Grade | Examples | Commercial use | Attribution |
|---|---|---|---|
| **CC0** | Most Openverse, Freesound CC0 | ✅ Yes | Not required (still log it) |
| **CC-BY** | Some Openverse | ✅ Yes | Required in credits |
| **CC-BY-SA** | Openverse adaptations | Yes, subject to ShareAlike | Required, with license and changes. Share adaptations under the same or a compatible license |
| **CC-BY-NC** | Some Freesound | ❌ Personal only | Required |
| **Royalty-free** | Pixabay, Unsplash | ✅ Yes | Check per-source TOS |
| **Unknown** | Random web search | ❌ Assume no |. |

## ASSETS.md Format

Every fetched or user-provided asset goes here:

```markdown
# Asset Log. <project slug>

| Filename | Source | Author | Licence | URL | Notes |
|---|---|---|---|---|---|
| background_forest.jpg | Openverse | Jane Smith | CC0 | https://... |. |
| sfx_whoosh.wav | Freesound | sounduser42 | CC-BY | https://... | Attribute in credits |
| logo_client.png | User-provided | Client | Proprietary |. | Client IP |
| mystery_icon.svg | Google Images search | Unknown | Licence unconfirmed | https://... | ⚠️ Confirm before release |
```

## Forbidden Assets

- Commercial music not provided by user (Spotify, Apple Music, YouTube rips)
- Getty Images, Shutterstock, Adobe Stock (require paid licence)
- Brand logos of third parties (not user's own brand)
- Real human faces (no deepfakes, no public figure likenesses)
- User's competitors' assets

## When Licence is Unknown

1. Tag as "Licence unconfirmed" in ASSETS.md
2. Tell the user explicitly: "I used [asset] from [source]. licence is unclear. Confirm before commercial release or replace with CC0 alternative."
3. Never silently use a licence-unknown asset without disclosure

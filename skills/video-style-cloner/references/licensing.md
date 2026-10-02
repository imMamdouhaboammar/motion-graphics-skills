# Asset Licensing Reference

## Safe Sources (CC0 / CC-BY)

| Source | Type | Licence | CLI |
|---|---|---|---|
| [Openverse](https://openverse.org) | Images, video clips | CC0, CC-BY | `fetch_assets.py search "kw" --sources openverse` |
| [Pixabay](https://pixabay.com) | Images, video, audio | Pixabay (free commercial) | `fetch_assets.py search "kw" --sources pixabay` |
| [Freesound](https://freesound.org) | Audio/SFX | CC0, CC-BY, CC-BY-NC | `fetch_assets.py search "kw" --sources freesound` |
| [Unsplash](https://unsplash.com) | Photos | Unsplash (free commercial) | Manual download |
| [SVGrepo](https://svgrepo.com) | SVG icons/graphics | CC0 | Manual download |

## Licence Grades

| Grade | Examples | Commercial use | Attribution |
|---|---|---|---|
| **CC0** | Most Openverse, Freesound CC0 | ✅ Yes | Not required (still log it) |
| **CC-BY** | Some Openverse | ✅ Yes | Required in credits |
| **CC-BY-NC** | Some Freesound | ❌ Personal only | Required |
| **Royalty-free** | Pixabay, Unsplash | ✅ Yes | Check per-source TOS |
| **Unknown** | Random web search | ❌ Assume no | — |

## ASSETS.md Format

Every fetched or user-provided asset goes here:

```markdown
# Asset Log — <project slug>

| Filename | Source | Author | Licence | URL | Notes |
|---|---|---|---|---|---|
| background_forest.jpg | Openverse | Jane Smith | CC0 | https://... | — |
| sfx_whoosh.wav | Freesound | sounduser42 | CC-BY | https://... | Attribute in credits |
| logo_client.png | User-provided | Client | Proprietary | — | Client IP |
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
2. Tell the user explicitly: "I used [asset] from [source] — licence is unclear. Confirm before commercial release or replace with CC0 alternative."
3. Never silently use a licence-unknown asset without disclosure

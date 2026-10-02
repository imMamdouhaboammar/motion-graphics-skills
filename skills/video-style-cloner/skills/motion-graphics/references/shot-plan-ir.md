# shot-plan IR

The single contract between Director and Builder. One file: `PROJECT_DIR/shot-plan.json`.

```jsonc
{
  // ── envelope (every category) ──
  "category": "kinetic-type | stat | charts | logo-reveal | lower-thirds | webpage | news | tweet | asset-fusion | maps",
  "duration_s": 6,
  "fps": 30,
  "canvas": { "w": 1080, "h": 1920, "aspect": "9:16" },
  "style": "free-form visual direction (mood / energy / reference)",
  "palette": ["#…"], // or "derive-from-asset"
  "font": "<HF embed-list font>",
  "beats": [12, 37], // optional accent frames/seconds
  "export": "mp4", // or "alpha-overlay" (transparent webm/mov)

  // ── sourcing seam (Director Part 1) — [] means skip the source phase ──
  "asset_needs": [
    {
      "role": "hero",
      "kind": "image|icon|logo|svg|news|web|tweet",
      "query": "…",
      "source": "…", // user-supplied path or source URL, instead of query
      "entity": "…", // known brand name when kind is logo
      "treatment": "cutout|recolor|vectorize|none",
    },
    // Maps basemap lane uses this alternative need shape (not a media-use type):
    {
      "role": "basemap",
      "type": "map-bake",
      "env": { "NAME": "basemap", "STYLE": "satellite", "CENTER": "2.6,46.6",
               "ZSTART": "4.2", "ZEND": "5.4", "COUNTRIES": "France:#38bdf8",
               "FPS": "30", "DUR": "6" },
    },
  ],

  // ── category-specific content + build directive (Director Part 2) ──
  "content": {
    "block": "<catalog block id, e.g. data-chart | caption-kinetic-slam>", // optional
    "customize": { /* data, text, palette, positions to change on the block */ },
    /* remaining shape varies by category, below */
  },
}
```

**Per-category `content` shapes** (alongside optional `block` and `customize`):

- `kinetic-type` → `scenes[]` `{ id, start, end, text, emphasis_words[], emotion, motion, beats[] }`
- `stat` → `{ value, prefix, suffix, label, ring: bool }`
- `charts` → `{ type: bar|line|pie|race|pct, data[], labels[], headline, axes: bool }`
- `logo-reveal` → `{ logo: <asset path>, tagline, url }`
- `lower-thirds` → `{ name, role, position, brand_colors[] }`
- `webpage` → `{ url, capture, highlights: [ { selector|region, label } ] }` (step-highlight a real captured page)
- `news` → `{ outlet, headline, body, keyword, layout: A|B, logo?, date?, subject? }` (article-highlight: lay text out readable — **no zoom** — then sweep a marker band over the keyword in place. Layout **A** = centered-emphasis 9:16 text-only; **B** = full article 16:9 with `logo` + `date` + `subject` (a person photo → `remove-background` cutout))
- `tweet` → `{ author, handle, avatar, text, metrics }`
- `maps` → `{ lane: vector|basemap, shot: highlight|flow|choropleth|labels|flag|pin-rollout|zoom-to, regions[], points[], basemap: satellite|dark, palette, headline, overlays: [label|pin|callout-card] }` (vector: no asset need; basemap: `type: "map-bake"` need, frozen video + projected coordinates from Source; see `categories/maps/module.md`)
- `asset-fusion` → `{ data_type, asset: <path>, affordance, element_positions: {center, extent, safe[], avoid[]}, derived_palette[], connectors[] }`

**Invariants:** `scenes` (if present) partition `[0, duration_s]` with no gaps/overlaps · empty `asset_needs` ⇒ Step 2 (source) is skipped · a named `content.block` ⇒ the Builder reuses + customizes it rather than hand-authoring.

**Asset need variants:** ordinary source needs use `kind` plus `query` or `source` (and optional `entity` / `treatment`); basemap needs use `type: "map-bake"` plus `env`. `env` contains the helper's uppercase parameters; optional `PITCH`, `BEARING`, `HOLD`, and `KEEPMARGIN` are documented in the maps module/helper. Source supplies `OUT` as a project-local assets directory. Keep `FPS` / `DUR` aligned with the envelope. For basemap shots, `content.basemap` must equal the map-bake need's `env.STYLE`; Source rejects mismatches before baking. The example array illustrates alternatives; emit only the needs required by the shot.

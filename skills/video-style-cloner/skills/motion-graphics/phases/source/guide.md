# source phase — asset sourcing (asset-first)

Runs **only when `shot-plan.json.asset_needs` is non-empty** (including logo and maps basemap needs). Sources each needed asset → a **frozen project-local path** + a ledger (`assets/index.md`). Uses `/media-use` for its supported media types, an available RWA/web-search capability for real-source discovery, and the maps bake helper for basemaps. If no such search capability is available, it **degrades to asset-free** (see below).

## Per asset_need

- `kind: image / icon / logo` → media-use `resolve` with `--type <kind> --intent "<query>" --project "$PROJECT_DIR"`. A known-brand logo also passes `--entity "<entity>"`; use official marks, never regenerate them. A supplied file/direct asset URL uses `--from "<source>"`. Optional `treatment`: cutout (remove-background) / recolor / vectorize through an available prep capability.
- `kind: svg` → freeze a supplied SVG or use an available asset-search capability for a real SVG; `svg` is not a media-use resolve type. If recording it through media-use, ingest with a supported semantic type (`icon` or `logo`).
- `kind: news / web / tweet` → use an installed RWA/web-search capability for source discovery; for a supplied page URL, use `hyperframes capture` when available. Preserve the real source URL and article/tweet text in the ledger, and freeze any capture and supporting media locally. These are not media-use resolve types. Two-pole queries: **atomic** (1–3 words, composable) or **specific** (5–15 words: a news event / tweet); never the middle. A failed specific query is dropped, not broadened.
- `type: map-bake` → run `node "$SKILL_DIR/categories/maps/bake-basemap.mjs"` with the need's `env` parameters and `OUT="$PROJECT_DIR/assets"`; map `FPS` / `DUR` to the envelope. See the maps module for Chrome, puppeteer-core, and ffmpeg requirements. Record both `assets/<NAME>.mp4` and `assets/<NAME>-coords.json` in the ledger. This lane does not call media-use resolve.

## Steps

1. Read `asset_needs` from `shot-plan.json`.
2. For each: **analyze → search → review (use/maybe/reject — selection is the hard part; do NOT take the first/generated result) → freeze** the kept asset into `assets/` (rehost remote URLs).
3. Write `assets/index.md` — agent-readable ledger: `role → frozen path + provenance`.
4. For `asset-fusion`: also capture the asset's measurable geometry (so Director Part 2 can set `element_positions`) + an eyedropper palette.

## Degrade gracefully

If a provider / search is unavailable, mark the need unmet in `context.log`; the category falls back to asset-free where possible (e.g. `news` → typographic headline without the sourced image).

Drive the documented resolver/search/bake capability directly; this skill has no `phases/source/resolve.mjs` wrapper.

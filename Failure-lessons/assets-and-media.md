# Assets and media

Lessons about sourcing, generating and preparing the images, audio and text that go into a film. Rendering them is covered in [render-pipeline.md](render-pipeline.md).

Related code: `projects/mgs-promo/tools/prep_cutouts.py`, `projects/mgs-promo/tools/prep_textures.py`, `projects/mgs-promo/ASSET_SOURCES.md`.

---

## A generation service that is connected is not a service that can generate

### What happened

The brief asked to use Higgsfield for custom cutout assets only if it had credit. The connector was present and authenticated. Its read-only `balance` call returned 0 credits on a free plan. The HyperFrames `media-use resolve --type image` path was also unavailable: it needs the HeyGen CLI or Codex, and neither was installed in the sandbox.

### Fix

Balance first, before any generation call, then fall back to openly licensed stock through the Openverse API (Wikimedia Commons and rawpixel), with every source URL and licence written to `ASSET_SOURCES.md` at the time of download.

### Prevention rule

Check a paid generator's balance with a read-only call and record the number before planning around it. Never infer credit from a working connection. Keep a documented offline route (licensed stock plus local processing) that does not block the film.

### Status

Resolved as practice.

---

## The ML background remover failed on product shots

### What happened

`npx hyperframes remove-background` (a local model) was run on a microphone, a keyboard, headphones, scissors and a camera, all photographed on white. It kept only fragments of most of them, such as part of one headphone cup and half a camera, and left rectangular bands on others. A simple key produced clean cutouts: near-white regions touching the border are background, plus enclosed near-white holes over a size threshold (headphone band, scissor handles), plus a row cutoff for floor shadows.

### Root cause

**Strongly indicated**: the remover is built for video and people, and these were isolated products on white. Not investigated further.

### What still failed

The camera's chrome top was as bright as the backdrop and keyed away at any threshold that removed its shadow. The camera was dropped rather than shipped damaged. A "transparent PNG" from a stock site had the checkerboard baked into a JPEG and was rejected.

### Fix

`projects/mgs-promo/tools/prep_cutouts.py`: a key with hole removal and an optional shadow cutoff, followed by one shared print treatment for every cutout (duotone ink to paper, S-curve, seeded midtone grain, 1 px die-cut edge).

### Verification

Each cutout was checked on both the paper and the night background, because a white fringe is invisible on paper and obvious on night.

### Prevention rule

Choose stock with the key in mind: a clean white or flat backdrop and no bright parts that match it. Check every cutout on the darkest and the lightest background it will sit on. One treatment for all photographic cutouts is what makes mixed stock read as one world.

### Implementation trap

`PIL.ImageDraw.floodfill` did nothing on an image made by `Image.fromarray(...)` until the image was `.copy()`'d. There was no error, just an unchanged mask. The cause is **strongly indicated** to be the read-only buffer that `fromarray` shares with numpy. The current script uses `scipy.ndimage.label` instead.

### Status

Resolved for this film. Keying bright metal on white is unsolved.

---

## Speech recognition text is timing data, not caption text

### What happened

Whisper large-v3 on the Arabic VO gave word times that matched `silencedetect` pauses closely, and the beat map was built on them. Several words, however, were misrecognized: «جهست» for «جهزت», "Cloud Code" for "Claude Code", «عظ» for «عرض», «ترك» for «اترك», «أرسلك» for «أرسل لك».

### Fix

`renders/mgs-promo-final.ar.vtt` takes its text from the approved script and only its timings from the recognizer. Latin names inside Arabic lines are wrapped in right-to-left marks so they keep their order.

### Prevention rule

Use ASR for timings. Take caption and on-screen text from the approved script. Never ship ASR text for a brand name or for Arabic without comparing it to the script.

### Status

Resolved.

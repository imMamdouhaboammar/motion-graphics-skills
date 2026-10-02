---
name: blender-product-film
description: Premium 3D product films rendered in Blender (headless, GPU) — dark studio, rim light, light sweeps, glass/liquid/metal materials, condensation and bubbles, macro and orbit camera moves, shallow depth of field, then crisp 2D titles, transitions, music and SFX in the edit. Builds a round product (bottle, can, jar) directly from a user's product photo (real silhouette + projected label), or a procedural one. Use for product launch / hero / commercial films whose reference is 3D or photoreal CG (Apple-style "black stage + a line of light" films), for any request to make a product look expensive, and whenever the video-clone router picks the premium-product-3d style.
---

# Blender product film

Everything is driven by JSON shot specs → `scripts/pfilm.py` (runs inside Blender) → PNG frames → `scripts/finish.py` (edit, titles, audio).
Blender 4.2+（`BLENDER` 環境變數或在 PATH 上；建議有 OptiX/CUDA 的 GPU）。選配 Real-ESRGAN（`REALESRGAN` 環境變數指到 realesrgan-ncnn-vulkan）。

## Pipeline

```
build/
  product/        prep_product.py output (from the user's photo)
  shots/S1.json   one spec per shot (format: top of scripts/pfilm.py)
  renders/…       frames
  edit.json       the cut: order, transitions, titles, music, SFX (format: top of scripts/finish.py)
```

1. **Product.** User photo (front view, plain background) →
   `python scripts/prep_product.py <photo> --out build/product --height <real height m>`
   Small images are AI-upscaled 4× first. **Open `build/product/check.png`** and confirm the green silhouette hugs the product and the
   magenta print mask covers the label/cap and not the clear body. No photo → procedural `"type": "bottle"` (see pfilm.py).
2. **Shot specs.** One JSON per shot in `build/shots/`, written from the plan's shot table (camera language below).
3. **Look-dev stills** (fast, do this first, iterate here):
   `python scripts/render_shots.py build --quality final --stills auto` (start/middle/end of each shot) → `out/check/<id>_stills.jpg`
4. **Motion preview** of every shot + a rough cut compared to the reference:
   `python scripts/render_shots.py build --quality preview --cut` → `out/check/<id>_preview.jpg`, `out/preview_cut.mp4`, compare sheets
5. **Compare with the reference** (see Review) and fix; repeat 3–5 until every shot passes.
6. **Final:** `python scripts/render_shots.py build --quality final` (≈1.5–4 s/frame at 1080p) → `python scripts/finish.py build/edit.json`.

## Camera language (use these; name them in the plan)

Every shot has a **move**, a **subject**, a **fill** and a **motivation**.
**Speed: match the reference, measured.** Premium films move slowly — the reference's `shot_details[].camera.pace` is usually slow/medium.
The ranges below are the *total* travel for a ~3 s shot at a *slow* pace; macro shots need far less travel than full-product shots
(on a small `region`, fill 0.95→0.85 already reads as a 50% zoom). Always: preview → `--cut` compare → scale with `camera.speed_scale`
(ratio reference speed ÷ our speed, floor ≈ 0.2 so nothing goes dead) → re-preview, before the final render.

| Move | Spec | When | Typical |
|---|---|---|---|
| Hero reveal (push_reveal / dolly_in from dark) | `dolly_in`, fill 0.7→0.8, lens 85, light sweep across | opening, closing | 3–4 s |
| Macro slide | `macro_slide`, lens 60–100, `region` = the detail, fill 0.9→0.92, angle −3→+3 | material / detail proof | 2–3 s |
| Orbit | `orbit`, angle −25→+10, fill 0.7→0.75, height rising a little | reveal the form, turn the label into view | 3–4 s |
| Crane | `dolly_out` + target moving up (pure crane reads backwards in compare), height ±0.03 | scale, cap-to-base travel | 2–3 s |
| Rack focus | `rack_focus`, focus_from/focus_to (m), lens 100, fstop 2.8 | droplets → label, foreground → product | 2 s |
| Static + light sweep | `static` + `lights.sweep` | text beat with product still alive | 2–3 s |
| Product spin | `product.rotate` [a, b] with a slow camera | turntable feel without moving the camera | any |

Rules of the look (what makes it read "premium"):
- **Black stage, low key.** `set.backglow` gives a soft coloured pool on a dark backdrop; key light low (≈5), rim strips do the modelling,
  one moving **sweep** light per hero shot. Never a flat bright background.
- **The product fills the frame.** Hero ≥ 0.7 of frame height; details via `region` + fill ≥ 0.8. A small product in a big black frame is the #1 failure.
- **Every shot moves** (camera or product or light), slow and eased — no cut to a dead still.
- **Open with a reveal**: shot 1 starts dark and the light finds the product (`lights.reveal: [0, 1.5]`), centred or on a third with
  purpose. It is the most striking image of the film — never a static, half-empty frame.
- **Empty frame has a job.** More than half the frame black and empty is only allowed when a title lives there. Tall thin products
  (bottles) cover little area even at full height: crop tighter (cap-to-label), go lower and closer, or put the title in the empty side.
  pfilm prints `PFILM_WARN` (and `meta.json`) when the product is small or its texture too soft for the close-up — treat warnings as defects.
- **Close-up rims**: pfilm switches to a 4 mm strip at equal radiance on close-ups (a fine edge line). Don't force `closeup_rim` up:
  a thick continuous white outline reads as a cut-out sticker.
- **Titles**: headline cards 0.06–0.09 of frame height, supers next to the product 0.04–0.05, closing brand line ≥ 0.05.
  Never three text beats in a row without a product image between them unless the reference does exactly that.
- **Depth of field by depth, not f-number**: `"dof": "shallow|medium|deep"` computes the f-stop for the camera distance
  (macro at f/3.5 leaves ~2 mm sharp — unusable). Focus sits on the product's front surface automatically.
- **Titles are 2D, in negative space**, never over the product: short (3–8 characters/words), grey + white two-tone, `light_up` or `rise` reveal.
  Title-only frames (black + text) ≤ 15% of runtime — a product film is pictures first.
- **Macro on bubbles / droplets needs a bright area behind the product** (clear things only show what they refract): bring the backdrop
  close (`set.backdrop_dist` ≈ 0.55) and make the back spot small and bright (`backglow_spread` ≈ 30, strength 9–16, `backglow_height` ≈ 0.25).
- **Light sweep energy ≈ 6–10.** A bright strip passing between lens and product washes the label and cap to white.
- **Atmosphere** (pfilm `set`): `ground_fog` = low rolling haze at the base only (density ≈ 0.3, height ≈ 0.08 m) for "mist / cool" beats —
  never a whole-frame grey wash. `caustics` = moving water-light lines on the backdrop for "ocean / water" beats; best on a mid-blue
  backdrop (`backdrop_color`), keep it subtle (default strength 0.35) and let depth of field soften it.
- **Rising bubbles** are `product.bubbles` (inside the water); condensation is `product.droplets` (outside). A shot that promises bubbles must show bubbles.
- **Clear liquids need light BEHIND them.** In a dark field, water reads as black ink unless something bright sits behind it:
  keep a soft bright zone behind the product in every dark shot (`set.backglow` strong and low behind the body, or a glow card),
  so the liquid refracts light and reads clear. "Is the water clear?" is the first question for any drink film.
- **Titles say something.** Repeating the product name is not a message: each text beat is one claim (taken from the pack or the
  user) followed by the picture that proves it. The name appears at the open and the close.
- **Don't repeat a detail**: the same close-up subject (e.g. the cap) at most twice per film; vary subject, scale and angle between
  neighbouring shots. Keep the product's colours identical across shots — change light level, not hue.
- **The last shot is a hero**: full product or shoulder-and-label, fill ≥ 0.7, a final light sweep across the name, and ≥ 1 s of stable
  frame before the fade.
- **Proof shots**: turn each claim into a picture of the product (droplets = cold, bubbles rising = fresh, macro label = the name, orbit = the shape).
  Only claims that are printed on the product or given by the user; never invent specs for a real brand.
- **Cuts on motion**: the next shot continues the direction of the last (orbit right → next move right), or dips through black at section breaks.

## Review (mandatory before the final render)

For every shot, put the reference shot it maps to next to ours (video-clone `scripts/compare.py`), open it, and score 1–5:
lighting (low key, rim, highlights) · material realism · camera motion (type and speed match the reference) · composition / fill ·
typography · pacing. Any score < 4 → fix the spec and re-render stills/preview. Write the scores to `out/check/review.md`.
Also open one full-res still per shot and look for: blown highlights, washed-out label, visible light panels, clipping into the product,
text over the product, flat black frames.

## Known pitfalls
- EEVEE's screen-space refraction breaks clear bottles (black bands) → preview and final both use Cycles (default).
- Big emissive cards behind the product flood the frame → use `set.backglow` (backdrop + spot), not an emissive wall.
- Glossy floors mirror the softboxes → lights are light-linked to the product (automatic).
- Blender renders CJK blank from Noto *variable* fonts → 3D text uses Microsoft JhengHei; but titles belong in finish.py anyway.
- Web product photos are tiny (≈400 px) → prep upscales with Real-ESRGAN; still, avoid extreme label macros (fill > 0.95 on text).
- Baked highlights in the product photo are removed from the print mask (thin white outlines are kept, semi-opaque).
- **Ghost / doubled label text → check `print.png`'s alpha first, not the lights.** Upscaled small CJK text leaves speckles between strokes.
  Best fix for a user's own product: clear the name area in `print.png` and re-typeset the printed name in place (same text, colour,
  position; 2× resolution), then update `product.json` (`m_per_px`, `bottom_px`) — see a project's `build/relabel.py` for a worked example.
- Photo relief (bump from the photo) is off by default: it turns JPEG noise into embossed grain.
- Hue-matched print (a blue stripe on a blue-tinted bottle) gets cut out as "clear body" → patch those holes in `print.png`.

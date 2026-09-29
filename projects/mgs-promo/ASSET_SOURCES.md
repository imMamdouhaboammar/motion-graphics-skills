# Asset sources

Every asset is local. Nothing is fetched at render time.

## Generation service

Higgsfield was connected. `balance` returned `{"credits": 0, "subscription_plan_type": "free"}` on 2026-09-29, so no images were generated. HyperFrames `media-use resolve --type image` had no reachable provider in this sandbox (no HeyGen CLI, no Codex), so photography came from openly licensed stock found through the Openverse API.

## Photography (cutouts)

All four were keyed in this project (`border flood-fill + enclosed-hole removal`, scripts in the session notes), then given one shared print treatment: duotone ink `#161412` to paper `#F6F2EA`, S-curve contrast, seeded midtone grain, 1 px die-cut edge. The HyperFrames ML background remover was tried first and rejected for these product shots (it removed most of the objects).

| File | Subject | Source | Licence | Changes |
|---|---|---|---|---|
| `assets/cutouts/mic_akg.png` | AKG C214 condenser microphone | https://commons.wikimedia.org/wiki/File:AKG_C214_Condenser_microphone.jpg | CC BY-SA 3.0 (author credited on the file page) | cutout, duotone, resize |
| `assets/cutouts/kb_wm.png` | Wireless computer keyboard | https://commons.wikimedia.org/wiki/File:Wireless_Computer_Keyboard.jpg | CC BY-SA 4.0 (author credited on the file page) | cutout, duotone, resize |
| `assets/cutouts/scissors.png` | Pair of scissors with black handle | https://commons.wikimedia.org/wiki/File:Pair_of_scissors_with_black_handle,_2015-06-07.jpg | CC BY-SA 4.0 (author credited on the file page) | cutout, duotone, resize, mirrored in the film |
| `assets/cutouts/hp_iso.png` | Isolated headphones | rawpixel via Openverse (id d6c09406…), https://www.rawpixel.com | CC0 1.0 | cutout, duotone, resize |

Rejected candidates: Zenit camera (chrome keyed badly), "vintage microphone png" (fake checkerboard baked into a JPEG), potted-succulent line art (wrong material).

CC BY-SA assets require attribution and share-alike on the adapted images. Put a credit line in the post caption or description, for example: "Photos: AKG C214, Wireless keyboard, Scissors via Wikimedia Commons (CC BY-SA)".

## Drawn in code

After Effects–style tile (a reference to the product, no Adobe artwork used), tape, timeline, pencil sketch, wireframe, render card, script sheet, waveform, stamp, cursor, block caret. The waveform bar heights are the RMS envelope of `vo-master.wav` (0 to 13.6 s, 36 windows). The script sheet lines are the film's own approved script.

## Textures (generated here, seeded)

- `assets/tex/paper-fibre.png`: seeded noise + fibre strokes (seed 11).
- `assets/tex/grain-0..2.png`: seeded Gaussian grain (seed 11), swapped on twos.
- `assets/tex/stamp-ink.png`: seeded pressure and speckle mask (seed 5).

## Fonts

| Files | Family (from the name table) | Source | Licence |
|---|---|---|---|
| `thmanyahsans-{Light,Regular,Medium,Bold,Black}.woff2` | thmanyah sans | github.com/imMamdouhaboammar/4steps-web @ `codex/4steps-build`, `/thmanyahsans/woff2` | use authorised by the user for this project |
| `thmanyahserifdisplay-{Regular,Bold,Black}.woff2` | thmanyah serif display | same repo, `/thmanyahserifdisplay/woff2` | same |
| `jetbrains-mono-latin-{500,700}-normal.woff2` | JetBrains Mono | npm `@fontsource/jetbrains-mono@5.3.0` | SIL OFL 1.1 |

Thmanyah Serif Text was checked and not needed.

## Audio

| File | Source | Licence |
|---|---|---|
| `assets/audio/vo-master.wav` | supplied by the user (ElevenLabs export), untouched, md5 `ab45442336d95b74c19cf296da9ec5e3` | user's |
| `assets/audio/sfx/click.mp3`, `key-press.mp3`, `impact-bass-1.mp3` | HyperFrames bundled SFX library (`hyperframes@0.8.92`, `skills/media-use/audio/assets/sfx`) | shipped with HyperFrames for use in compositions |

## Runtime

- `assets/vendor/gsap.min.js`: GSAP 3.14.2 from npm, vendored so the render needs no CDN.
- `compositions/components/grain-overlay.html`: HyperFrames registry component, used as the donor for the grain layer (its CSS keyframe loop was replaced by a timeline-driven, on-twos swap so it is seek-safe).

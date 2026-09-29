<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/readme/hero-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="assets/readme/hero-light.png">
    <img alt="Motion Graphics Skill Pack by Mamdouh Aboammar" src="assets/readme/hero-light.png" width="100%">
  </picture>
</p>

<h1 align="center">Motion Graphics Skill Pack</h1>

<p align="center">
  <strong>14 skills for directing and building professional motion graphics with Claude Code. Every frame is code.</strong>
</p>

<p align="center">
  <a href="https://github.com/imMamdouhaboammar/motion-graphics-skills/stargazers"><img src="https://img.shields.io/github/stars/imMamdouhaboammar/motion-graphics-skills?style=flat-square&color=D97557&labelColor=00132F&label=stars" alt="GitHub stars"></a>
  <img src="https://img.shields.io/badge/skills-14-D97557?style=flat-square&labelColor=00132F" alt="14 skills">
  <img src="https://img.shields.io/badge/runs_in-Claude_Code_%C2%B7_Codex-58B6FF?style=flat-square&labelColor=00132F" alt="Runs in Claude Code and Codex">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red?style=flat-square&labelColor=00132F" alt="Licence"></a>
  <a href="https://github.com/imMamdouhaboammar"><img src="https://img.shields.io/badge/creator-Mamdouh_Aboammar-FFD11A?style=flat-square&labelColor=00132F" alt="Creator"></a>
</p>

<p align="center">
  <a href="#install">Install</a> &nbsp;·&nbsp;
  <a href="#see-it-work">See it work</a> &nbsp;·&nbsp;
  <a href="#the-skills">The skills</a> &nbsp;·&nbsp;
  <a href="#how-they-fit-together">How they fit</a> &nbsp;·&nbsp;
  <a href="#prompts">Prompts</a> &nbsp;·&nbsp;
  <a href="https://github.com/imMamdouhaboammar">Author</a>
</p>

---

This pack directs and builds code-driven motion graphics without requiring After Effects. It covers brand films, event promos, explainers, kinetic typography, editorial collage, charts, title sequences, product launches, 2D, 2.5D and true 3D. Claude Code or Codex can author the composition, while HyperFrames can provide the reusable runtime, validation, preview, audio and rendering layers instead of rebuilding them.

## Install

One line, about 30 seconds:

```bash
npx skills add imMamdouhaboammar/motion-graphics-skills
```

Then open Claude Code, pick Opus 5.5 with `/model`, and run `brand-intake` first.

<details>
<summary><strong>Manual copy into Claude Code</strong></summary>

Download this repo (green **Code** button, then **Download ZIP**) and unzip it, or clone it:

```bash
git clone https://github.com/imMamdouhaboammar/motion-graphics-skills.git
```

Copy the 14 folders inside `skills/` into `~/.claude/skills/` (every project) or your project's `.claude/skills/` (one project). This loop keeps any skill folder you already have:

```bash
mkdir -p ~/.claude/skills
for skill in motion-graphics-skills/skills/*; do
  [ -f "$skill/SKILL.md" ] || continue
  destination="$HOME/.claude/skills/$(basename "$skill")"
  if [ -e "$destination" ]; then
    printf 'Preserved existing skill: %s\n' "$destination"
  else
    cp -R "$skill" "$destination"
  fi
done
```

</details>

<details>
<summary><strong>Claude Desktop (upload one skill)</strong></summary>

Zip one skill folder and upload it in Customise, then Skills. From `motion-graphics-skills/skills`:

```bash
zip -r brand-intake.skill brand-intake
```

Start with `brand-intake`, then add the skills you need.

</details>

<details>
<summary><strong>Codex</strong></summary>

From your project's root, after cloning this repo into it:

```bash
test -d motion-graphics-skills/skills || { printf 'Missing source skills folder\n'; exit 1; }
mkdir -p .agents/skills || exit 1
for skill in motion-graphics-skills/skills/*; do
  [ -f "$skill/SKILL.md" ] || continue
  name="$(basename "$skill")"
  destination=".agents/skills/$name"
  if [ -e "$destination" ] || [ -L "$destination" ]; then
    printf 'Preserved existing skill: %s\n' "$destination"
  else
    cp -R "$skill" "$destination" || exit 1
  fi
done
```

Open a fresh Codex task and check the skills load from `.agents/skills/<name>/SKILL.md`.

</details>

<details>
<summary><strong>Export to MP4</strong></summary>

Add HyperFrames once (free, open source): `npx skills add heygen-com/hyperframes`. No export tools at all? [My export kit (Mac and Windows)](https://drive.google.com/file/d/18ugNPOOHqLTbkekSYPzvC1wJStMjWg8y/view?usp=drivesdk) turns any of these HTML files into an MP4.

</details>

## See it work

<table>
  <tr>
    <td width="64%" valign="top"><img src="assets/readme/demo-launch.gif" alt="A 20-second product launch film built entirely in code" width="100%"></td>
    <td width="36%" valign="top"><img src="assets/readme/demo-milestone.gif" alt="A 12-second milestone loop that resolves into 250,000 LinkedIn followers" width="100%"></td>
  </tr>
  <tr>
    <td valign="top"><sub>A 20-second launch film. Deep blue glass, one glow, every word from a fact list I approved. No screen recording.</sub></td>
    <td valign="top"><sub>A 12-second milestone loop. A night sky of points pulls into my real number.</sub></td>
  </tr>
</table>

### Start here: one line, 60 seconds

Before any skill, paste this into Claude Code on Opus 5.5:

```
Make a dynamic 15-second motion graphics video that shows what an incredible motion designer you are. Go all out.
```

Then change it by describing the edit:

- "Slow down the second scene."
- "Swap the text for mine: [your words]."
- "Use my brand colours: [hex codes]."
- "Make it 1080 x 1350 for LinkedIn."

When you want a specific job done properly, pick a skill below.

## The skills

Fourteen skills, with motion-director as the broad creative front door. Type the line on the right into Claude Code and the right skill picks it up.

| Stage | Skill | What you get | Say this |
|---|---|---|---|
| Direct | [**motion-director**](skills/motion-director/) | Master creative direction, concept, craft, HyperFrames routing, review, and production for broad motion work. | "Direct this motion film from reference to final render." |\n| Set up | [**brand-intake**](skills/brand-intake/) | Builds brand.md and MOTION.md. Every other skill reads them first. | "Set up my brand for motion. Here are five frames I like." |
| Plan | [**motion-brief-writer**](skills/motion-brief-writer/) | Turns a rough idea into a precise build brief in your brand. | "Write me a motion brief for my next milestone post." |
| Launch | [**launch-video**](skills/launch-video/) | A 30 to 45 second launch for a product, offer or cohort. | "Make a launch video for my new cohort." |
| Launch | [**apple-launch-film**](skills/apple-launch-film/) | A Mac-style launch film. Menu bar, notch and widgets, all code. | "Make it look like an Apple keynote launch." |
| Explain | [**vox-explainer**](skills/vox-explainer/) | A 30 to 60 second documentary explainer. | "Make a Vox-style video: why do we dream?" |
| Explain | [**animated-chart**](skills/animated-chart/) | A looping chart. Every value stays exactly as you give it. | "Animate my chart. Here are my numbers." |
| Explain | [**milestone-reveal**](skills/milestone-reveal/) | A night sky of points that pulls into your real number. | "Make a milestone video for my follower count." |
| Explain | [**motion-effects**](skills/motion-effects/) | 16 premium effects in your brand, as 8-second loops. | "Build the search-to-results effect in my brand." |
| Open | [**title-sequence-3d**](skills/title-sequence-3d/) | An 8 to 15 second 3D opener that stops the scroll. | "Make a cinematic 3D intro for my next video." |
| Compare | [**model-showdown**](skills/model-showdown/) | One brief, three AI models, stacked into one video. | "Same prompt, three AIs. Make a model showdown." |
| Promote | [**newsletter-promo**](skills/newsletter-promo/) | A 12 to 20 second promo that sends people to an edition. | "Make a promo for this week’s newsletter." |
| Promote | [**loop-cover**](skills/loop-cover/) | Your newsletter cover as a seamless looping GIF. | "Make my newsletter cover a looping GIF." |
| Promote | [**reel-export**](skills/reel-export/) | Any video as a clean 1080 x 1920 Reel or TikTok. | "Make this a reel for Instagram." |

See each skill's `SKILL.md` for its trigger phrases, the inputs it asks for and what it learned the hard way.

## How they fit together

Use `motion-director` for broad motion work and `brand-intake` once per brand. `brand-intake` writes `brand.md` (who you are, what you sell, your assets) and `MOTION.md` (your colours, type, timing and motion rules), and adds a rule to CLAUDE.md so Claude reads both before it animates anything. Every other skill reads those two files first. Without them, a skill asks for your hex codes, font and logo, and never calls its result on-brand.

```mermaid
flowchart TD
  D["motion-director<br/>concept · art direction · runtime routing · QA"]
  B["brand-intake<br/>brand.md + MOTION.md"]
  P["motion-brief-writer"]
  L["launch-video · apple-launch-film"]
  E["vox-explainer · animated-chart · milestone-reveal · motion-effects"]
  O["title-sequence-3d"]
  X["model-showdown"]
  R["newsletter-promo · loop-cover · reel-export"]

  D --> B
  D --> P
  D --> L
  D --> E
  D --> O
  D --> X
  D --> R
  B --> P
```

## Use it

For broad motion work, start with `motion-director`. Run `brand-intake` once per brand when brand.md and MOTION.md do not already exist. Narrow requests can route directly to a specialist:

```
"Direct this motion film" → motion-director\n"Review this motion cut by timecode" → motion-director\n"Set up my brand" → brand-intake
"Brief this animation" → motion-brief-writer
"Make a launch video for my coaching programme" → launch-video
"Make an Apple-style launch for my app" → apple-launch-film
"Why does every logo look the same now?" → vox-explainer
"Animate my Q3 chart" → animated-chart
"Celebrate 10,000 subscribers" → milestone-reveal
"Build the chart morph with my numbers" → motion-effects
"Make a button that turns into a video player" → motion-effects
"Give me a cinematic opener" → title-sequence-3d
"Same prompt, three AIs" → model-showdown
"Promo for this edition" → newsletter-promo
"Make my cover move" → loop-cover
"Make this a reel" → reel-export
```

<details>
<summary><strong>The brief behind my "Why do we dream?" film</strong></summary>

One line gets you close. A proper brief gets you something people share. This is exactly what I typed (with `vox-explainer` installed):

```
Why do we dream? And then someone suddenly wakes up, zooms out of the eye, and goes into outer space. There are neural networks of interconnectivity to convey the brain.
```

It found a source for every fact before it drew anything, wrote the script, added a voice and rendered it. Then give it notes like you would a designer.

</details>

## Prompts

Every prompt from the edition, ready to paste, one file per job. Each one says when to use it.

| File | What is in it |
|---|---|
| [start-here.md](prompts/start-here.md) | The one-line starter, the edit-by-describing lines and what to do tonight |
| [brand-design-system.md](prompts/brand-design-system.md) | The MOTION.md prompt and the CLAUDE.md read-first block |
| [briefs.md](prompts/briefs.md) | The "Why do we dream?" brief and the real designer notes I gave |
| [polish.md](prompts/polish.md) | The Apple motion audit, the real-components rule and the fix-one-thing prompt |
| [effects.md](prompts/effects.md) | 16 prompts, one per effect, each built from scratch in your brand |

<details>
<summary><strong>What each skill needs to run</strong></summary>

Only install what the job needs. Nothing here needs an API key.

| Workflow | Needs | If it is missing |
|---|---|---|
| Any skill, on-brand | `brand.md` and `MOTION.md` from `brand-intake` | The skill asks for hex codes, font and logo, and does not call the result on-brand |
| Build any animation | Claude Code on Opus 5.5 | Nothing to build with |
| MP4 export | HyperFrames, or ffmpeg plus Chrome | You get the HTML with `window.seek()`, export pending |
| `loop-cover` measuring | ffmpeg and Python 3 | GIF made, seam and motion unmeasured, so not called done |
| `reel-export` and `model-showdown` stacking | ffmpeg and ffprobe | Stacked layout as HTML, final encode and checks pending |
| `model-showdown` | Access to each model through your own accounts | Compare the models you can reach, and say which were left out |
| `apple-launch-film` motion check | The free `apple-design` skill | Builds without it, motion unchecked against Apple's rules |
| Logos and screenshots | Your own files | The skill asks. It never redraws a logo from memory |

</details>

<details>
<summary><strong>House rules every skill follows</strong></summary>

1. **Reuse first.** Use the current project, specialist skills and HyperFrames capabilities before building new infrastructure.\n2. **Facts first.** Every name, date and number on screen comes from a list you approve. Nothing invented.
3. **Your brand, not the average.** Colours and fonts come from `brand-intake` or from you. With nothing given, it asks.
4. **Banned defaults:** typewriter text, glow, bounce, gradients on text, purple-to-blue backgrounds.
5. **Motion on twos** for anything hand-made in feel (hold each pose for 2 frames at 24fps).
6. **First 3 seconds carry the hook.** If the first frame is empty, it's cut.
7. **Check before export.** One frame from the middle of every shot, checked for cut-off text, overlaps and wrong facts.
8. **Real assets only.** Logos and screenshots come from your files, never redrawn from memory.

</details>

<details>
<summary><strong>Pairs well with: Apple's motion rules</strong></summary>

A free skill (not mine) that turns Apple's design guidelines into rules Claude follows:

```
npx skills add emilkowalski/skills --skill apple-design
```

Then ask: "Use the apple-design skill to audit this animation. Give me a ranked list of everything that feels off, worst first." Paste the fixes back as notes.

</details>

<details>
<summary><strong>Pairs well with: real UI components</strong></summary>

If your video shows a product, don't let Claude draw the buttons and cards from scratch. It guesses the spacing and the UI looks fake. [21st.dev](https://21st.dev) publishes real components with a prompt under each one. Paste this once, then paste any component prompt straight in:

```
Add this rule to CLAUDE.md: whenever I paste a component prompt or third-party component code, treat it as a structural donor only. Keep its engineering. Replace its demo copy with my real copy, and translate every colour, border, shadow, font and timing to MOTION.md.
```

</details>

> [!NOTE]
> **One honest limit:** a photoreal human face. Code draws motion, type and UI brilliantly, but a lifelike person still needs an image model (for now).

## Runtime philosophy

The pack uses a reuse-first ladder:

1. Current project primitives
2. A specialist skill already in this pack
3. HyperFrames workflow, registry block, adapter, CLI, media, or audio capability
4. Native HTML, CSS, SVG, Canvas, Web Audio, or WebGL
5. GSAP for complex seekable choreography
6. Three.js when the shot truly needs 3D geometry, occlusion, lighting, or camera depth
7. Custom infrastructure only when the earlier layers do not solve the problem

For a fresh HyperFrames project, install its current skills with:

```bash
npx skills add heygen-com/hyperframes
```

The master skill adds creative direction, narrative, typography, composition, motion craft, Arabic RTL guidance, reference analysis, and visual QA. It does not copy HyperFrames' renderer or rebuild its engine.

## Contributing

Found a way to improve a skill? [Open an issue](https://github.com/imMamdouhaboammar/motion-graphics-skills/issues).

Before debugging a render, a clipped word or a broken transition, check [Failure-lessons](Failure-lessons/lessons-index.md). It records what already went wrong on real films, how it was proven, and the rule that now prevents it.

Run `bash validate-skills.sh` before you submit. It checks every skill's frontmatter, that the name matches the folder, the description length, and the house style across every skill, its reference files and the prompts folder.

## Author and Ownership

<table>
  <tr>
    <td valign="top">
      <strong>Mamdouh Aboammar</strong><br>
      <sub>AI Engineer and Creative Technologist</sub><br>
      <a href="https://github.com/imMamdouhaboammar">GitHub Profile</a>
    </td>
  </tr>
</table>

## Licence

[Proprietary (All Rights Reserved)](LICENSE). Copyright (c) 2026 Mamdouh Aboammar. All rights reserved. Strictly prohibited to copy, distribute, modify, reverse engineer, or commercially exploit without explicit written permission.

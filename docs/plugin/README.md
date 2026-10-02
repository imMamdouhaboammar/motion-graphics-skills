# Motion Graphics Skills plugin

This is a skills-only plugin for ChatGPT and Codex, built from the canonical `skills/` directory. It preserves all 50 domain specialist skills and adds `motion-studio`, `host-workspace-operator` and `sandbox-python-executor`.

Version **1.2.0** includes 53 top-level skills and 36 nested Video Style Cloner workflow modules. Read the [complete catalog](CATALOG.md) and [engine/runtime requirements](RUNTIMES.md). Nested modules are loaded by their named entry files, not imported as independent plugin skills.

## Start here

Invoke Motion Graphics Skills and ask:

- Plan a 30-second Arabic brand film from my script and visual reference
- Build a code-driven motion sequence from my approved storyboard
- Review my video and give me timecoded fixes for typography, pacing and transitions

`motion-studio` checks the host capabilities and routes the task. `motion-director` directs larger films. Use narrow specialists for small animation jobs.

## Installation and execution

The saved private plugin is installed through its returned ChatGPT plugin page. Select it in a new conversation to test discovery and execution. Importing a package does not itself test the installed runtime.

For standalone skills in coding agents, the existing command remains:

```bash
npx skills add imMamdouhaboammar/motion-graphics-skills
```

This command installs agent skills. It does not register a private ChatGPT plugin.

Portable clients discover root `plugin.json` and `skills/`. Older Codex clients can use `.codex-plugin/plugin.json`. Both manifests carry the same identity, version and presentation.

Rendering needs an execution-capable host and a working renderer. New production projects use HyperFrames under the existing source workflow. Browser dependencies, FFmpeg and optional providers are external requirements. The package contains no hosted renderer, MCP server, service connection or credentials. Planning and review can run without media-provider authentication.

## Rebuild

Run from a checkout, choosing a new output path:

```bash
python3 tools/build_plugin.py /absolute/path/motion-graphics-skills-1.2.0.zip
```

The builder includes only manifests, canonical skills, plugin branding, plugin documentation and the original license. It excludes `.git`, `.agents` duplicates, project source, rendered client videos, dependency trees and transient Python files. It refuses an existing output path. A rebuild requires package validation and a clean extraction check before upload.

## Review scope

Package validity and deterministic archive checks are distinct from model behavior, rendered video quality and public directory approval. The initial static Plugin Eval report flags large existing skills and aggregate context estimates. Its required legal-URL checks are stricter than the current official rules for private skills-only packages. No legal URLs or verified publisher identity are invented to improve a score.

This release updates the existing private account plugin. It is not a public directory submission. The repository's proprietary license remains in force. The two host operation skills are adapted from Plugin Autopilot under the MIT notice in `AUTOPILOT-LICENSE.txt`.

## Release verification

Run `python3 -m unittest discover -s tests -p test_build_plugin.py -v` and `python3 -m unittest discover -s tests -p test_plugin_catalog.py -v`. Build two archives into different new output paths, compare their hashes, extract a clean copy and validate it. Catalog tests reject missing skills/modules, stale counts and inconsistent manifest presentation. A saved plugin update is separate from an executed fresh-host rendering smoke test.

#!/usr/bin/env bash
# Scaffolds a project from this engine's template, installs deps and checks the toolchain.
#   bash .claude/skills/<engine>/scripts/new_project.sh <project-dir> [--keep-demo]
set -e
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:?usage: new_project.sh <project-dir> [--keep-demo]}"
if [ -e "$TARGET/studio.html" ]; then echo "error: $TARGET already has a studio.html; not overwriting" >&2; exit 1; fi
mkdir -p "$TARGET"
if command -v rsync >/dev/null; then rsync -a --exclude node_modules --exclude out "$SKILL_DIR/template/" "$TARGET/"; else cp -R "$SKILL_DIR/template/." "$TARGET/"; rm -rf "$TARGET/node_modules" "$TARGET/out"; fi   # Git Bash on Windows has no rsync
mkdir -p "$TARGET/assets" "$TARGET/out/check"
# The demo is an example, not a template: unless asked, unhook it so the new video starts clean.
if [ "${2:-}" != "--keep-demo" ]; then sed -i.bak 's#<script src="src/scenes/demo.js"></script>##' "$TARGET/studio.html" && rm -f "$TARGET/studio.html.bak"; fi
( cd "$TARGET" && npm install --silent --no-audit --no-fund )
echo "node   $(node -v)"
command -v ffmpeg >/dev/null && echo "ffmpeg ok" || echo "MISSING: ffmpeg"
FOUND=
for c in "${CHROME_PATH:-}" "/c/Program Files/Google/Chrome/Application/chrome.exe" "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" /usr/bin/google-chrome /usr/bin/chromium /usr/bin/chromium-browser; do
  [ -n "$c" ] && [ -x "$c" ] && { echo "chrome $c"; FOUND=1; break; }
done
[ "${FOUND:-}" = 1 ] || echo "MISSING: Chrome (install it, or pass --chrome=<path> to render.mjs)"
echo "== ready: $TARGET"

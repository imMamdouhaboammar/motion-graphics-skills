#!/usr/bin/env bash
# new_project.sh <target-dir> [--keep-demo]
# Scaffolds a crayon-storybook project from the skill's template, installs deps (npm install also writes the patched
# p5.brush build, see template/patch_brush.mjs) and checks the toolchain.
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:?usage: new_project.sh <target-dir> [--keep-demo]}"
KEEP_DEMO="${2:-}"

if [ -e "$TARGET/studio.html" ]; then echo "error: $TARGET already has a studio.html; not overwriting" >&2; exit 1; fi
mkdir -p "$TARGET"
if command -v rsync >/dev/null; then rsync -a --exclude node_modules --exclude out "$SKILL_DIR/template/" "$TARGET/"
else (cd "$SKILL_DIR/template" && for f in * .gitignore; do case "$f" in node_modules|out) ;; *) cp -R "$f" "$TARGET/";; esac; done); fi   # Git Bash on Windows has no rsync
mkdir -p "$TARGET/assets" "$TARGET/out/check"

# The demo is an example, not a template: unless asked, unhook it so the new video starts clean.
if [ "$KEEP_DEMO" != "--keep-demo" ]; then
  sed -i.bak 's|<script src="src/scenes/demo.js"></script>|<!-- <script src="src/scenes/demo.js"></script>  (example only) -->|' "$TARGET/studio.html" && rm -f "$TARGET/studio.html.bak"
fi

cd "$TARGET"
echo "== installing p5, p5.brush, puppeteer-core (+ patched p5.brush build)"
npm install --silent
[ -f node_modules/p5.brush/dist/p5.brush.crayon.js ] || node patch_brush.mjs

echo "== toolchain"
command -v node   >/dev/null && echo "node   $(node -v)"   || echo "MISSING: node"
if command -v ffmpeg >/dev/null; then echo "ffmpeg ok"; elif [ -n "${FFMPEG_DIR:-}" ] && [ -x "$FFMPEG_DIR/ffmpeg" -o -x "$FFMPEG_DIR/ffmpeg.exe" ]; then echo "ffmpeg in FFMPEG_DIR (add it to PATH before --encode)"; else echo "MISSING: ffmpeg"; fi
for c in "${CHROME_PATH:-}" "/c/Program Files/Google/Chrome/Application/chrome.exe" "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" /usr/bin/google-chrome /usr/bin/chromium /usr/bin/chromium-browser; do
  [ -n "$c" ] && [ -x "$c" ] && { echo "chrome $c"; FOUND=1; break; }
done
[ "${FOUND:-}" = 1 ] || echo "MISSING: Chrome (install it, or pass --chrome=<path> to render.mjs)"
echo "== ready: $TARGET   (read GUIDE.md in the skill folder before drawing)"

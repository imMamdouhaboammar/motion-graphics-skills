#!/usr/bin/env bash
# Asset Scan and Dependency Auditor
# Checks fonts, audio stems, vector files, and render artifacts

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "=== MOTION STUDIOS ASSET SCAN ==="

MISSING=0

# Check font dependencies
echo "Checking Typography Assets:"
if [ -d "fonts" ] && [ "$(ls -A fonts 2>/dev/null)" ]; then
  find fonts -type f \( -name "*.woff2" -o -name "*.ttf" -o -name "*.otf" \) | while read -r f; do
    echo "  [FOUND] $f"
  done
else
  echo "  [WARN] No local fonts directory found in project root."
  echo "         (Copy required fonts to fonts/ before final rendering)"
fi

# Check audio stems
echo "Checking Audio Assets:"
if [ -d "sfx" ] && [ "$(ls -A sfx 2>/dev/null)" ]; then
  sfx_count=$(find sfx -type f \( -name "*.wav" -o -name "*.mp3" \) | wc -l | tr -d ' ')
  echo "  [FOUND] sfx/ contains $sfx_count sound effects."
else
  echo "  [INFO] sfx/ directory is empty or not yet initialized."
fi

# Check outputs
if [ -d "renders" ]; then
  render_count=$(find renders -type f \( -name "*.mp4" -o -name "*.mov" \) | wc -l | tr -d ' ')
  echo "  [FOUND] renders/ contains $render_count video files."
else
  echo "  [INFO] renders/ directory not yet initialized."
fi

echo "=== ASSET SCAN COMPLETE ==="

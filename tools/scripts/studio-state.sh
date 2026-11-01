#!/usr/bin/env bash
# Studio State Inspector
# Reports active stage, rigor mode, and production readiness

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

STAGE="concept"
RIGOR="standard"

if [ -f "studio.yaml" ]; then
  parsed_stage=$(grep "^stage:" studio.yaml 2>/dev/null | head -n 1 | awk '{print $2}' | tr -d '"' || true)
  [ -n "$parsed_stage" ] && STAGE="$parsed_stage"
  parsed_rigor=$(grep "rigor:" studio.yaml 2>/dev/null | head -n 1 | awk '{print $2}' | tr -d '"' || true)
  [ -n "$parsed_rigor" ] && RIGOR="$parsed_rigor"
fi

echo "=========================================="
echo " CLAUDE CODE MOTION STUDIOS: STATUS"
echo "=========================================="
echo "Active Stage  : $STAGE"
echo "Rigor Mode    : $RIGOR"
echo "Root Path     : $ROOT_DIR"
echo "------------------------------------------"

# Check core files
echo "Project Manifests:"
[ -f "studio.yaml" ] && echo "  [x] studio.yaml" || echo "  [ ] studio.yaml"
[ -f "motion-bible.md" ] && echo "  [x] motion-bible.md" || echo "  [ ] motion-bible.md"
[ -f "beat-sheet.md" ] && echo "  [x] beat-sheet.md" || echo "  [ ] beat-sheet.md"

echo "------------------------------------------"
echo "Asset Directories:"
for dir in fonts sfx assets renders; do
  if [ -d "$dir" ]; then
    count=$(find "$dir" -type f | wc -l | tr -d ' ')
    echo "  [x] $dir/ ($count files)"
  else
    echo "  [ ] $dir/ (missing)"
  fi
done
echo "=========================================="

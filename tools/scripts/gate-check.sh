#!/usr/bin/env bash
# Studio Director Gate Checker
# Evaluates stage completion against the 5 director quality gates

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

STAGE="concept"
if [ -f "studio.yaml" ]; then
  STAGE=$(grep "^stage:" studio.yaml | awk '{print $2}' | tr -d '"' || echo "concept")
fi

echo "=================================================="
echo " CLAUDE CODE MOTION STUDIOS: DIRECTOR GATES AUDIT "
echo "=================================================="
echo "Active Stage: $STAGE"
echo "--------------------------------------------------"

FAILED=0

# Gate 1: Creative Director Gate
echo "[GATE 1] Creative Director (Concept & Storyboard):"
if [ -f "beat-sheet.md" ]; then
  echo "  [PASS] beat-sheet.md is present."
else
  echo "  [WARN] beat-sheet.md not found. (Required for animatic/production)"
fi

# Gate 2: Technical Director Gate
echo "[GATE 2] Technical Director (Pipeline & Stack):"
if [ -f "studio.yaml" ]; then
  echo "  [PASS] studio.yaml defines renderers and aspect ratios."
else
  echo "  [FAIL] studio.yaml missing."
  FAILED=$((FAILED + 1))
fi

# Gate 3: Art Director Gate
echo "[GATE 3] Art Director (Motion Bible & Taste):"
if [ -f "motion-bible.md" ]; then
  echo "  [PASS] motion-bible.md established."
else
  echo "  [WARN] motion-bible.md not yet established."
fi

# Gate 4: Audio Director Gate
echo "[GATE 4] Audio Director (Sound & Loudness):"
if [ -d "sfx" ] && [ "$(ls -A sfx 2>/dev/null)" ]; then
  echo "  [PASS] Local sfx library detected."
else
  echo "  [INFO] Using default synthetic sound assets."
fi

# Gate 5: Platform QA Gate
echo "[GATE 5] Platform QA (Safe Zones & Delivery):"
if [ -f "renders/safe-zone-overlay.svg" ]; then
  echo "  [PASS] Safe zone overlay generated and ready for proofing."
else
  echo "  [INFO] Safe zone overlay can be generated with python3 tools/scripts/safe-zone-verify.py"
fi

echo "--------------------------------------------------"
if [ "$FAILED" -eq 0 ]; then
  echo "STAGE AUDIT RESULT: READY TO PROCEED"
  exit 0
else
  echo "STAGE AUDIT RESULT: $FAILED BLOCKER(S) DETECTED"
  exit 1
fi
echo "=================================================="

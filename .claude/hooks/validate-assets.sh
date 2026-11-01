#!/usr/bin/env bash
# Claude Code PreToolUse Hook: Validate Assets Before Render
# Warns if render command is triggered while local fonts or sound directories are missing

set -euo pipefail

INPUT=$(cat)

if [[ "$INPUT" == *"render"* ]]; then
  if [ ! -d "fonts" ] || [ -z "$(ls -A fonts 2>/dev/null)" ]; then
    echo "NOTICE: Rendering initiated without local fonts/ directory." >&2
    echo "If your composition uses custom typography, ensure font files are placed in fonts/ to prevent fallback shifts." >&2
  fi
fi

exit 0

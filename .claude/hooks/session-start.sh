#!/usr/bin/env bash
# Claude Code Session Start Hook for Motion Studios
# Initializes studio environment and reports project stage

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [ -f "tools/scripts/studio-state.sh" ]; then
  bash tools/scripts/studio-state.sh
fi

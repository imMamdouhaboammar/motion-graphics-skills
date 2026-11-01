#!/usr/bin/env bash
# Claude Code PreToolUse Hook: Validate Git Commit
# Enforces clean commit standards and prevents accidental large media file commits

set -euo pipefail

INPUT=$(cat)

# Only process if this is a git commit invocation
if [[ "$INPUT" =~ "git commit" ]]; then
  # Check if large binary files or video renders are staged
  STAGED_MEDIA=$(git diff --cached --name-only | grep -E '\.(mp4|mov|wav|avi|mkv|zip)$' || true)
  if [ -n "$STAGED_MEDIA" ]; then
    echo "ERROR: Attempting to commit large binary media files directly to git:" >&2
    echo "$STAGED_MEDIA" >&2
    echo "Studio Rule: Media renders belong in local renders/ or storage buckets, not in repository commits." >&2
    exit 2
  fi
fi

exit 0

#!/usr/bin/env bash
# Universal Multi-Agent Installer for motion-graphics-skills
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/skills"

echo "🎨 Installing motion-graphics-skills (15 skills) across AI agent environments..."

if [ ! -d "$SKILLS_SRC" ]; then
  echo "❌ Error: skills directory not found at $SKILLS_SRC"
  exit 1
fi

install_skills() {
  local target_dir="$1"
  local agent_name="$2"
  mkdir -p "$target_dir"
  for skill in "$SKILLS_SRC"/*; do
    [ -d "$skill" ] || continue
    local sname
    sname="$(basename "$skill")"
    rm -rf "$target_dir/$sname"
    cp -R "$skill" "$target_dir/$sname"
  done
  echo "  ✅ Installed 15 skills for $agent_name -> $target_dir"
}

# 1. Claude Code (~/.claude/skills)
if [ -d "$HOME/.claude" ] || command -v claude >/dev/null 2>&1; then
  install_skills "$HOME/.claude/skills" "Claude Code"
fi

# 2. Antigravity / Gemini CLI (~/.gemini/config/skills)
if [ -d "$HOME/.gemini" ]; then
  install_skills "$HOME/.gemini/config/skills" "Antigravity / Gemini CLI"
fi

# 3. Codex / OpenCode (~/.codex/skills)
if [ -d "$HOME/.codex" ]; then
  install_skills "$HOME/.codex/skills" "Codex / OpenCode"
fi

# 4. Universal Agent Kernel (~/.agents/skills)
mkdir -p "$HOME/.agents/skills"
install_skills "$HOME/.agents/skills" "Universal Agent Kernel"

echo "🎉 All 14 motion graphics skills successfully installed!"

#!/usr/bin/env bash
# Validate every skill in skills/ against the Agent Skills spec.
# Checks: YAML frontmatter, required fields, name matches folder, description length,
# file size, standard folder structure, and the pack's house style: no em dashes or
# semicolons in prose (code blocks are skipped), no local /Users/ paths, no "steal".
# Also checks every skill's references/*.md and every prompts/*.md file for the same house style.

set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$ROOT_DIR/skills"
PROMPTS_DIR="$ROOT_DIR/prompts"
PASS=0
WARN=0
FAIL=0
SKILL_COUNT=0
PROMPT_COUNT=0

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

err()  { printf "  ${RED}x${NC} %s\n" "$1"; FAIL=$((FAIL+1)); }
warn() { printf "  ${YELLOW}!${NC} %s\n" "$1"; WARN=$((WARN+1)); }
ok()   { printf "  ${GREEN}v${NC} %s\n" "$1"; PASS=$((PASS+1)); }

# House style for any markdown file: prose outside fenced code blocks, inline code stripped.
check_style() {
  local file="$1" label="$2"
  local em_matches
  em_matches="$(awk '/^```/{f=!f; next} !f && /\xe2\x80\x94/{print "    line " NR ": " $0}' "$file")"
  if [[ -n "$em_matches" ]]; then
    err "$label: em dash found in prose"
    printf "%s\n" "$em_matches"
  else
    ok "$label: no em dashes in prose"
  fi

  local semi_matches
  semi_matches="$(awk '/^```/{f=!f; next} !f {line=$0; gsub(/`[^`]*`/, "", line); if (line ~ /;/) print "    line " NR ": " $0}' "$file")"
  if [[ -n "$semi_matches" ]]; then
    err "$label: semicolon found in prose"
    printf "%s\n" "$semi_matches"
  else
    ok "$label: no semicolons in prose"
  fi

  local user_matches
  user_matches="$(grep -n '/Users/' "$file" 2>/dev/null | sed 's/^/    line /' || true)"
  if [[ -n "$user_matches" ]]; then
    err "$label: local /Users/ path found"
    printf "%s\n" "$user_matches"
  else
    ok "$label: no local paths"
  fi

  local steal_matches
  steal_matches="$(grep -niw 'steal' "$file" 2>/dev/null | sed 's/^/    line /' || true)"
  if [[ -n "$steal_matches" ]]; then
    err "$label: banned word 'steal' found"
    printf "%s\n" "$steal_matches"
  fi
}

printf "${CYAN}Validating skills in %s${NC}\n\n" "$SKILLS_DIR"

if [[ ! -d "$SKILLS_DIR" ]]; then
  printf "${RED}skills/ folder not found.${NC}\n"
  exit 1
fi

validate_skill() {
  local skill_dir="$1"
  SKILL_COUNT=$((SKILL_COUNT+1))
  local skill_name
  skill_name="$(basename "$skill_dir")"
  local skill_md="${skill_dir}SKILL.md"

  printf "${CYAN}%s${NC}\n" "$skill_name"

  # SKILL.md exists
  if [[ ! -f "$skill_md" ]]; then
    err "SKILL.md missing: $skill_md"
    return
  fi

  # Folder name format
  if [[ ! "$skill_name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    err "folder name must be lowercase alphanumeric with hyphens"
  else
    ok "folder name valid"
  fi

  # Frontmatter present
  local first_line
  first_line="$(head -n1 "$skill_md")"
  if [[ "$first_line" != "---" ]]; then
    err "SKILL.md must start with YAML frontmatter (---) in $skill_md"
    return
  fi

  # Extract frontmatter (between the first two --- delimiters)
  local frontmatter
  frontmatter="$(awk '/^---[[:space:]]*$/{n++; next} n==1{print} n==2{exit}' "$skill_md")"

  # name field
  local yaml_name
  yaml_name="$(printf "%s" "$frontmatter" | awk -F': ' '/^name:/{print $2; exit}' | tr -d '"' | tr -d "'" | tr -d '[:space:]')"
  if [[ -z "$yaml_name" ]]; then
    err "name field missing from frontmatter in $skill_md"
  elif [[ "$yaml_name" != "$skill_name" ]]; then
    err "name '$yaml_name' does not match folder '$skill_name' in $skill_md"
  else
    ok "name matches folder"
  fi

  if [[ ${#yaml_name} -gt 64 ]]; then
    err "name exceeds 64 characters: '$yaml_name' in $skill_md"
  fi

  # description field — parse only the frontmatter we already extracted (not the body)
  local desc_block
  desc_block="$(printf "%s\n" "$frontmatter" | awk '
    BEGIN{in_desc=0}
    /^description:/{
      sub(/^description:[ \t]*/, "")
      if ($0 ~ /^>/ || $0 ~ /^\|/) { in_desc=1; next }
      print; exit
    }
    in_desc==1 {
      if ($0 ~ /^[a-zA-Z_-]+:/) exit
      sub(/^[ \t]+/, "")
      printf "%s ", $0
    }
  ')"

  local desc_len=${#desc_block}
  if [[ $desc_len -eq 0 ]]; then
    err "description field missing or empty in $skill_md"
  elif [[ $desc_len -gt 1024 ]]; then
    err "description is $desc_len chars, must be 1024 or fewer in $skill_md"
  else
    ok "description present ($desc_len chars)"
  fi

  # Trigger phrase hint
  if [[ "$desc_block" == *"when"* || "$desc_block" == *"Use"* || "$desc_block" == *"use"* ]]; then
    ok "description has trigger phrasing"
  else
    warn "description should include 'use' or 'when' trigger phrasing in $skill_md"
  fi

  # File size
  local line_count
  line_count=$(wc -l < "$skill_md" | tr -d '[:space:]')
  if [[ $line_count -gt 500 ]]; then
    warn "SKILL.md is $line_count lines, consider moving detail to references/ in $skill_md"
  else
    ok "SKILL.md size OK ($line_count lines)"
  fi

  # House style: prose outside fenced code blocks
  local em_matches
  em_matches="$(awk '/^```/{f=!f; next} !f && /\xe2\x80\x94/{print "    line " NR ": " $0}' "$skill_md")"
  if [[ -n "$em_matches" ]]; then
    err "em dash found in prose"
    printf "%s\n" "$em_matches"
  else
    ok "no em dashes in prose"
  fi

  local semi_matches
  semi_matches="$(awk '/^```/{f=!f; next} !f {line=$0; gsub(/`[^`]*`/, "", line); if (line ~ /;/) print "    line " NR ": " $0}' "$skill_md")"
  if [[ -n "$semi_matches" ]]; then
    err "semicolon found in prose"
    printf "%s\n" "$semi_matches"
  else
    ok "no semicolons in prose"
  fi

  local user_paths
  user_paths="$(grep -rn '/Users/' "$skill_dir" 2>/dev/null | sed 's/^/    /' || true)"
  if [[ -n "$user_paths" ]]; then
    err "local /Users/ path found:"
    printf "%s\n" "$user_paths"
  else
    ok "no local paths"
  fi

  local steal_found
  steal_found="$(grep -rniw 'steal' "$skill_dir" 2>/dev/null | sed 's/^/    /' || true)"
  if [[ -n "$steal_found" ]]; then
    err "banned word 'steal' found:"
    printf "%s\n" "$steal_found"
  fi

  # House style in reference and eval files
  if [[ -d "${skill_dir}references" ]]; then
    for ref in "${skill_dir}references"/*.md; do
      [[ -f "$ref" ]] || continue
      check_style "$ref" "references/$(basename "$ref")"
    done
  fi
  if [[ -d "${skill_dir}evals" ]]; then
    for eval_file in "${skill_dir}evals"/*.md; do
      [[ -f "$eval_file" ]] || continue
      check_style "$eval_file" "evals/$(basename "$eval_file")"
    done
  fi

  # Optional standard folders
  for sub in references scripts assets evals; do
    if [[ -d "${skill_dir}${sub}" ]]; then
      ok "has ${sub}/ folder"
    fi
  done

  printf "\n"
}

for skill_dir in "$SKILLS_DIR"/*/; do
  [[ -d "$skill_dir" ]] || continue
  validate_skill "$skill_dir"
done

if [[ -d "$PROMPTS_DIR" ]]; then
  printf "${CYAN}prompts${NC}\n"
  for prompt_md in "$PROMPTS_DIR"/*.md; do
    [[ -f "$prompt_md" ]] || continue
    PROMPT_COUNT=$((PROMPT_COUNT+1))
    check_style "$prompt_md" "$(basename "$prompt_md")"
    # Every fenced block must be closed
    fences=$(grep -c '^```' "$prompt_md")
    if (( fences % 2 != 0 )); then
      err "$(basename "$prompt_md"): unclosed code block"
    fi
  done
  printf "\n"
fi

printf "${CYAN}Summary${NC}\n"
printf "  Skills checked: %d\n" "$SKILL_COUNT"
printf "  Prompt files checked: %d\n" "$PROMPT_COUNT"
printf "  ${GREEN}Passed:${NC}   %d\n" "$PASS"
printf "  ${YELLOW}Warnings:${NC} %d\n" "$WARN"
printf "  ${RED}Failed:${NC}   %d\n" "$FAIL"

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
exit 0

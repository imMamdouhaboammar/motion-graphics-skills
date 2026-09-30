#!/usr/bin/env python3
"""Scan .agents/skills/ and emit a runtime agent-skills-index.json.

The index is consumed by route_motion.py and motion-director during session
startup so every installed utility skill is automatically discoverable
without manual registration in skill-network.json.

Usage:
    python discover_agent_skills.py
    python discover_agent_skills.py --skills-dir .agents/skills --out skills/motion-director/router/agent-skills-index.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# YAML frontmatter parser (no external deps)
# ---------------------------------------------------------------------------

_FM_DELIMITER = re.compile(r"^---\s*$", re.MULTILINE)

# Multiline / quoted value patterns
_SCALAR_QUOTED  = re.compile(r'^"(.*)"$', re.DOTALL)
_SCALAR_LITERAL = re.compile(r"^'(.*)'$", re.DOTALL)


def _parse_frontmatter(text: str) -> dict[str, str]:
    """Return the YAML frontmatter fields as a flat string dict.

    Handles:
    - Simple key: value
    - Double-quoted  key: "value"
    - Single-quoted  key: 'value'
    - Block scalars  description: >
    """
    parts = _FM_DELIMITER.split(text, maxsplit=2)
    if len(parts) < 3:
        return {}

    fm_block = parts[1]
    result: dict[str, str] = {}

    lines = fm_block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" not in line:
            i += 1
            continue

        key, _, raw_val = line.partition(":")
        key = key.strip()
        raw_val = raw_val.strip()

        # Block scalar (> or |)
        if raw_val in (">", "|", ">-", "|-"):
            collected: list[str] = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                # Block ends at a non-indented key: value line
                if next_line and not next_line.startswith((" ", "\t")):
                    break
                collected.append(next_line.strip())
                i += 1
            result[key] = " ".join(collected).strip()
            continue

        # Strip surrounding quotes
        m = _SCALAR_QUOTED.match(raw_val) or _SCALAR_LITERAL.match(raw_val)
        if m:
            result[key] = m.group(1)
        else:
            result[key] = raw_val

        i += 1

    return result


# ---------------------------------------------------------------------------
# Skill classification helpers
# ---------------------------------------------------------------------------

_GSAP_PATTERN      = re.compile(r"\bgsap\b", re.IGNORECASE)
_AUDIO_PATTERN     = re.compile(r"\b(audio|speech|transcri|whisper|voice)\b", re.IGNORECASE)
_DESIGN_PATTERN    = re.compile(r"\b(design|ui|ux|visual|layout|branding)\b", re.IGNORECASE)
_MEDIA_PATTERN     = re.compile(r"\b(image|video|media|lottie|export|render)\b", re.IGNORECASE)
_MOTION_PATTERN    = re.compile(r"\b(motion|animation|timeline|scroll)\b", re.IGNORECASE)
_UTILITY_PATTERN   = re.compile(r"\b(output|enforcement|performance|util|helper)\b", re.IGNORECASE)


def _classify(name: str, description: str) -> str:
    text = f"{name} {description}"
    if _GSAP_PATTERN.search(text):
        return "gsap-utility"
    if _AUDIO_PATTERN.search(text):
        return "audio-utility"
    if _DESIGN_PATTERN.search(text):
        return "design-utility"
    if _MEDIA_PATTERN.search(text):
        return "media-utility"
    if _MOTION_PATTERN.search(text):
        return "motion-utility"
    return "utility"


# ---------------------------------------------------------------------------
# Main scanner
# ---------------------------------------------------------------------------

def scan(skills_dir: Path) -> list[dict[str, Any]]:
    """Walk *skills_dir* and return one entry per valid skill found."""
    entries: list[dict[str, Any]] = []

    if not skills_dir.is_dir():
        return entries

    for skill_path in sorted(skills_dir.iterdir()):
        if not skill_path.is_dir():
            continue

        skill_md = skill_path / "SKILL.md"
        if not skill_md.is_file():
            continue

        try:
            text = skill_md.read_text(encoding="utf-8")
        except OSError:
            continue

        fm = _parse_frontmatter(text)
        name        = fm.get("name", skill_path.name).strip()
        description = fm.get("description", "").strip()
        license_    = fm.get("license", "").strip()
        category    = _classify(name, description)

        entries.append({
            "name":        name,
            "kind":        "agent-skill",
            "category":    category,
            "path":        str(skill_md.relative_to(skills_dir.parents[1])),
            "description": description,
            "license":     license_ or None,
            "optional":    True,
        })

    return entries


def build_index(skills_dir: Path) -> dict[str, Any]:
    entries = scan(skills_dir)

    # Group by category for quick lookup
    by_category: dict[str, list[str]] = {}
    for entry in entries:
        cat = entry["category"]
        by_category.setdefault(cat, []).append(entry["name"])

    return {
        "version":     2,
        "source":      str(skills_dir),
        "total":       len(entries),
        "skills":      entries,
        "by_category": by_category,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    repo_root       = Path(__file__).resolve().parents[3]
    default_skills  = repo_root / ".agents" / "skills"
    default_out     = Path(__file__).resolve().parent.parent / "router" / "agent-skills-index.json"

    p = argparse.ArgumentParser(
        description="Scan .agents/skills/ and emit agent-skills-index.json"
    )
    p.add_argument(
        "--skills-dir", type=Path, default=default_skills,
        help=f"Path to .agents/skills/ (default: {default_skills})",
    )
    p.add_argument(
        "--out", type=Path, default=default_out,
        help=f"Output JSON path (default: {default_out})",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Print the index to stdout without writing to disk",
    )
    return p


def main() -> int:
    args = build_parser().parse_args()

    index = build_index(args.skills_dir)
    payload = json.dumps(index, ensure_ascii=False, indent=2)

    if args.dry_run:
        print(payload)
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(payload + "\n", encoding="utf-8")
    print(
        f"[discover_agent_skills] wrote {index['total']} skills "
        f"({len(index['by_category'])} categories) -> {args.out}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

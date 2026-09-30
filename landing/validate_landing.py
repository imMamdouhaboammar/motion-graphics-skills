#!/usr/bin/env python3
"""Keep the GitHub Pages landing page synchronized with the repository catalog."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "landing"
INDEX = LANDING / "index.html"
LLMS = LANDING / "llms.txt"
MARKETPLACE = ROOT / "marketplace.json"
SKILLS_DIR = ROOT / "skills"


def fail(message: str) -> None:
    print(f"LANDING SYNC ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    repo_skills = sorted(
        path.name
        for path in SKILLS_DIR.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    )

    index = INDEX.read_text(encoding="utf-8")
    llms = LLMS.read_text(encoding="utf-8")
    marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    version = str(marketplace["version"])

    page_skills = sorted(set(re.findall(r'data-skill="([a-z0-9-]+)"', index)))

    missing = sorted(set(repo_skills) - set(page_skills))
    extra = sorted(set(page_skills) - set(repo_skills))
    if missing or extra:
        fail(f"skill catalog mismatch. missing={missing}, extra={extra}")

    expected_count = len(repo_skills)
    if f'data-skill-count="{expected_count}"' not in index:
        fail(f"index.html must expose data-skill-count=\"{expected_count}\"")

    if f'data-pack-version="{version}"' not in index:
        fail(f"index.html must expose data-pack-version=\"{version}\"")

    if f"{expected_count} skills" not in llms.lower():
        fail(f"llms.txt must describe the current {expected_count} skills")

    for skill in repo_skills:
        expected_href = (
            "https://github.com/imMamdouhaboammar/"
            f"motion-graphics-skills/tree/main/skills/{skill}"
        )
        if expected_href not in index:
            fail(f"landing page is missing the canonical link for {skill}")

    print(
        f"Landing catalog is synchronized: {expected_count} skills, version {version}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

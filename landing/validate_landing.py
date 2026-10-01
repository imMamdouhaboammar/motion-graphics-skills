#!/usr/bin/env python3
"""Keep the GitHub Pages landing page synchronized and structurally valid."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
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


class LandingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.controls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if data.get("id"):
            self.ids.append(str(data["id"]))
        if data.get("aria-controls"):
            self.controls.append(str(data["aria-controls"]))


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

    parser = LandingParser()
    parser.feed(index)

    duplicate_ids = sorted(
        identifier for identifier, count in Counter(parser.ids).items() if count > 1
    )
    if duplicate_ids:
        fail(f"duplicate HTML ids: {duplicate_ids}")

    missing_tab_targets = sorted(set(parser.controls) - set(parser.ids))
    if missing_tab_targets:
        fail(f"aria-controls targets are missing: {missing_tab_targets}")

    jsonld_match = re.search(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
        index,
        flags=re.DOTALL,
    )
    if not jsonld_match:
        fail("missing JSON-LD metadata block")
    try:
        json.loads(jsonld_match.group(1))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON-LD metadata: {exc}")

    page_skills = sorted(set(re.findall(r'data-skill="([a-z0-9-]+)"', index)))
    missing = sorted(set(repo_skills) - set(page_skills))
    extra = sorted(set(page_skills) - set(repo_skills))
    if missing or extra:
        fail(f"skill catalog mismatch. missing={missing}, extra={extra}")

    expected_count = len(repo_skills)
    if f'data-skill-count="{expected_count}"' not in index:
        fail(f'index.html must expose data-skill-count="{expected_count}"')

    if f'data-pack-version="{version}"' not in index:
        fail(f'index.html must expose data-pack-version="{version}"')

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
        f"Landing is synchronized and structurally valid: "
        f"{expected_count} skills, version {version}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

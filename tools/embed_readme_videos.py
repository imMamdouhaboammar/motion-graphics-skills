#!/usr/bin/env python3
"""Replace README thumbnail slots with GitHub-native full-video player embeds.

GitHub only supports reliable inline MP4 player URLs when assets have been
uploaded through the GitHub Markdown editor (user-attachments). Repository
blob/raw URLs are intentionally rejected.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FILMS = ("arabic", "curve", "countdown", "teola", "four-steps", "jedar")
ATTACHMENT = re.compile(r"^/user-attachments/assets/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def validate_manifest(manifest: object) -> dict[str, str]:
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError("Manifest must be a nonempty JSON object of film ID to attachment URL")
    unknown = set(manifest) - set(FILMS)
    if unknown:
        raise ValueError(f"Unknown film IDs: {', '.join(sorted(unknown))}")
    validated = {}
    for film, value in manifest.items():
        if not isinstance(value, str) or value.strip() != value:
            raise ValueError(f"Invalid URL for {film}")
        u = urlsplit(value)
        if (u.scheme != "https" or u.netloc != "github.com"
                or not ATTACHMENT.fullmatch(u.path) or u.query or u.fragment
                or u.username or u.password):
            raise ValueError(f"{film}: upload MP4 via GitHub Markdown editor and paste a github.com/user-attachments/assets/UUID URL")
        validated[film] = value
    if len(set(validated.values())) != len(validated):
        raise ValueError("Each film must have its own uploaded video asset")
    return validated


def render(readme: str, urls: dict[str, str]) -> str:
    for film, url in validate_manifest(urls).items():
        begin = f"<!-- readme-video:{film}:start -->"
        end = f"<!-- readme-video:{film}:end -->"
        if readme.count(begin) != 1 or readme.count(end) != 1:
            raise ValueError(f"Expected exactly one marker pair for {film}")
        slot = re.compile(re.escape(begin) + r"[\s\S]*?" + re.escape(end))
        # GitHub recognizes an attachment URL on its own Markdown line and
        # renders its native player. Embedding this inside an HTML table or
        # image-link Markdown prevents reliable video recognition.
        player = f"{begin}\n\n{url}\n\n{end}"
        readme, count = slot.subn(lambda _match: player, readme)
        if count != 1:
            raise ValueError(f"Failed to replace slot for {film}")
    return readme



def check_readme_video_ready(readme: str) -> int:
    """Enforce six real, distinct standalone attachment URLs before merging.

    This is a structural release check, not proof of playback in a browser.
    """
    urls: dict[str, str] = {}
    for film in FILMS:
        begin = f"<!-- readme-video:{film}:start -->"
        end = f"<!-- readme-video:{film}:end -->"
        if readme.count(begin) != 1 or readme.count(end) != 1:
            raise ValueError(f"{film}: missing or duplicate player slot")
        match = re.search(re.escape(begin) + r"([\\s\\S]*?)" + re.escape(end), readme)
        if match is None:
            raise ValueError(f"{film}: malformed player slot")
        candidate = match.group(1).strip()
        if "\\n" in candidate or not candidate.startswith("https://github.com/user-attachments/assets/"):
            raise ValueError(f"{film}: full video attachment URL has not been published")
        urls[film] = candidate
    try:
        validate_manifest(urls)
    except ValueError as error:
        raise ValueError(f"README has duplicate or invalid video attachment URL: {error}") from error
    return len(urls)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", type=Path, nargs="?", help="JSON file with film ID -> GitHub user-attachment URL")
    p.add_argument("--readme", type=Path, default=ROOT / "README.md")
    p.add_argument("--check", action="store_true", help="Report unsynchronized README without writing")
    p.add_argument("--check-ready", action="store_true",
                   help="Fail until six actual standalone GitHub video attachment links exist")
    args = p.parse_args()
    old = args.readme.read_text(encoding="utf-8")
    if args.check_ready:
        count = check_readme_video_ready(old)
        print(f"README has {count} unique GitHub video attachment URLs; browser playback review still required")
        return 0
    if args.manifest is None:
        p.error("manifest is required unless --check-ready is supplied")
    new = render(old, json.loads(args.manifest.read_text(encoding="utf-8")))
    if args.check:
        if old != new:
            raise SystemExit("README is out of sync with verified GitHub attachment links")
        print("README native video embeds match supplied attachment URLs")
    else:
        args.readme.write_text(new, encoding="utf-8")
        print("Updated README native video players. Verify the rendering on github.com.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

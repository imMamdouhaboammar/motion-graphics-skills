#!/usr/bin/env python3
"""Attach full promo films via authenticated GitHub CLI, then embed them in README.

Requires gh >=2.99 with a personal OAuth/PAT login and ffmpeg/ffprobe for
oversized films. GitHub Actions GITHUB_TOKEN (installation token) is not supported
by the native user-attachments upload endpoint.
"""
from __future__ import annotations

import argparse
import json
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if __package__:
    from .embed_readme_videos import FILMS, ROOT, render
else:
    from embed_readme_videos import FILMS, ROOT, render

REPO = "imMamdouhaboammar/motion-graphics-skills"
MASTER_FILES = {
    "arabic": "projects/mgs-promo/renders/mgs-promo-final.mp4",
    "curve": "projects/skills-promo-curve/renders/skills-promo-curve.mp4",
    "countdown": "projects/skills-countdown-promo/renders/skills-promo-final.mp4",
    "teola": "TEOLA-ad.mp4",
    "four-steps": "projects/four-steps-events/renders/Four-Steps-Events-Motion-Final-v2.mp4",
    "jedar": "projects/jedar-lesh-majani/renders/JEDAR-lesh-majani-final.mp4",
}
ASSET_PATTERN = re.compile(r"https://github\.com/user-attachments/assets/[0-9a-f-]{36}", re.I)


def run(*args: str) -> str:
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(f"Command failed: {args[0]} {args[1] if len(args) > 1 else ''}\n{p.stderr.strip()[:900]}")
    return p.stdout.strip()


def preflight() -> None:
    for binary in ("gh", "ffmpeg", "ffprobe"):
        if shutil.which(binary) is None:
            raise RuntimeError(f"Missing command: {binary}")
    match = re.search(r"gh version (\d+)\.(\d+)", run("gh", "--version"))
    if not match or tuple(map(int, match.groups())) < (2, 99):
        raise RuntimeError("Upgrade GitHub CLI to 2.99.0 or later for --attach")
    run("gh", "auth", "status", "--hostname", "github.com")
    for name in FILMS:
        path = ROOT / MASTER_FILES[name]
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Missing / empty final master: {path}")


def fit_video(path: Path, key: str, directory: Path, max_mb: int) -> Path:
    budget = max_mb * 1024 * 1024
    if path.stat().st_size < int(budget * .97):
        return path
    info = json.loads(run("ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "json", str(path)))
    duration = float(info["format"]["duration"])
    if duration <= 0:
        raise RuntimeError(f"No duration in {path}")
    # Reserve audio, MP4 overhead and a margin for account-specific upload limits.
    audio_bps = 96000
    video_bps = max(200000, int((budget * .88 * 8 / duration) - audio_bps))
    outfile = directory / f"{key}-readme.mp4"
    log = str(directory / f"pass-{key}")
    video_args = ["-map", "0:v:0", "-vf",
                  "scale='min(720,iw)':-2:flags=lanczos,format=yuv420p",
                  "-r", "30", "-c:v", "libx264", "-preset", "slow",
                  "-b:v", str(video_bps), "-passlogfile", log]
    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(path),
        *video_args, "-pass", "1", "-an", "-f", "null", "-")
    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(path),
        *video_args, "-pass", "2", "-map", "0:a:0?", "-c:a", "aac",
        "-b:a", str(audio_bps), "-movflags", "+faststart", str(outfile))
    if outfile.stat().st_size >= budget:
        raise RuntimeError(f"Upload encode of {key} is still too large ({outfile.stat().st_size} bytes); "
                           f"reduce --max-mb or video bitrate manually")
    return outfile


def parse_comment(body: str, marker: str) -> dict[str, str]:
    if marker not in body:
        raise ValueError("Upload comment marker missing")
    result: dict[str, str] = {}
    for i, film in enumerate(FILMS):
        start = body.find(f"### {film}")
        if start < 0:
            raise ValueError(f"No uploaded section for {film}")
        end = body.find("### ", start + 4)
        section = body[start:end if end >= 0 else None]
        links = ASSET_PATTERN.findall(section)
        if len(links) != 1:
            raise ValueError(f"Expected one GitHub video attachment for {film}, got {len(links)}")
        result[film] = links[0]
    return result



def locate_uploaded_comment(ndjson: str, marker: str) -> str:
    """Locate an exact batch marker across all paginated GitHub comment responses."""
    matches: list[str] = []
    for line in ndjson.splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        # gh --jq output may itself JSON-encode strings depending on the
        # CLI formatter. Accept both plain NDJSON objects and quoted objects.
        if isinstance(entry, str):
            entry = json.loads(entry)
        if not isinstance(entry, dict):
            raise ValueError("Unexpected GitHub comment payload")
        body = entry.get("body")
        if isinstance(body, str) and marker in body:
            matches.append(body)
    if len(matches) != 1:
        raise ValueError(f"Expected one uploaded comment for {marker}, found {len(matches)}")
    return matches[0]

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", type=int, default=33, help="Draft PR to host video attachments")
    parser.add_argument("--max-mb", type=int, choices=(10, 100), default=10,
                        help="Per-video upload limit; use 100 only if your GitHub plan permits it")
    parser.add_argument("--commit", action="store_true",
                        help="Commit the updated README to the current branch (does not push)")
    opts = parser.parse_args()

    preflight()
    marker = "README_VIDEO_BATCH_" + secrets.token_hex(8)
    with tempfile.TemporaryDirectory(prefix="motion-readme-") as tmp:
        directory = Path(tmp)
        videos = {film: fit_video(ROOT / MASTER_FILES[film], film, directory, opts.max_mb)
                  for film in FILMS}
        body = directory / "upload-comment.md"
        body.write_text(
            "Full-length README promo assets: " + marker + "\n\n"
            + "\n".join(f"### {film}\n\n![]({videos[film]})\n" for film in FILMS),
            encoding="utf-8",
        )
        arguments = ["gh", "pr", "comment", str(opts.pr), "--repo", REPO,
                     "--body-file", str(body)]
        for film in FILMS:
            arguments.extend(["--attach", str(videos[film])])
        run(*arguments)
        # PR bots can produce >100 comments. Fetch and parse every page before
        # searching for our upload marker, rather than silently truncating page 1.
        comments_ndjson = run("gh", "api", "--paginate",
                              "--jq", ".[] | @json",
                              f"repos/{REPO}/issues/{opts.pr}/comments?per_page=100")
        urls = parse_comment(locate_uploaded_comment(comments_ndjson, marker), marker)
        readme_path = ROOT / "README.md"
        updated = render(readme_path.read_text(encoding="utf-8"), urls)
        readme_path.write_text(updated, encoding="utf-8")
        if opts.commit:
            run("git", "add", "README.md")
            run("git", "commit", "-m", "docs: embed full-length promos as GitHub native README players")
        print("Six complete GitHub attachment embeds added to README.")
        print("Verify audio/seek/fullscreen in the GitHub rendered view before merging.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

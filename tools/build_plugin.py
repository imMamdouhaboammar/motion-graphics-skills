"""Build a deterministic skills-only ChatGPT/Codex plugin from the canonical pack.

No dependency downloads, renderer invocation or repository mutations.
The output must not already exist, so unrelated local files cannot be replaced.
"""
from pathlib import Path
import argparse
import hashlib
import json
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build(output: Path) -> dict:
    output = output.resolve()
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    roots = (ROOT / "skills", ROOT / "assets/plugin", ROOT / "docs/plugin")
    if any(output.is_relative_to(directory.resolve()) for directory in roots):
        raise ValueError("output must be outside packaged source directories")
    manifest = json.loads((ROOT / "plugin.json").read_text())
    paths = [ROOT / "plugin.json", ROOT / ".codex-plugin/plugin.json", ROOT / "LICENSE"]
    for directory in roots:
        paths.extend(sorted(directory.rglob("*")))
    included = []
    for path in sorted(paths):
        if path.is_symlink():
            raise ValueError(f"symlink excluded: {path}")
        relative = path.relative_to(ROOT)
        if any(part in {"__pycache__", "node_modules", ".git"} for part in relative.parts):
            continue
        if path.suffix == ".pyc" or path.name in {".DS_Store", "Thumbs.db"}:
            continue
        if path.name == ".env" or path.name.startswith(".env.") or path.suffix in {".pem", ".key"}:
            raise ValueError(f"secret-shaped file excluded: {relative}")
        if path.is_file():
            included.append(path)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in included:
            relative = path.relative_to(ROOT)
            info = zipfile.ZipInfo(relative.as_posix(), (2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return {"archive": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "version": manifest["version"], "skills": len(list((ROOT / "skills").glob("*/SKILL.md")))}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))

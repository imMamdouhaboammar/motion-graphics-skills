#!/usr/bin/env python3
"""Tests for discover_agent_skills.py.

Run with:
    python -m pytest skills/motion-director/scripts/test_discover_agent_skills.py -v
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------
import importlib.util, sys

_SCRIPT = Path(__file__).parent / "discover_agent_skills.py"
_spec = importlib.util.spec_from_file_location("discover_agent_skills", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

_parse_frontmatter = _mod._parse_frontmatter
_classify          = _mod._classify
scan               = _mod.scan
build_index        = _mod.build_index


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_skill(tmp_path: Path, name: str, description: str, license_: str = "") -> Path:
    skill_dir = tmp_path / name
    skill_dir.mkdir(parents=True)
    fm_lines = [
        "---",
        f'name: {name}',
        f'description: "{description}"',
    ]
    if license_:
        fm_lines.append(f"license: {license_}")
    fm_lines.append("---")
    fm_lines.append("")
    fm_lines.append(f"# {name}")
    (skill_dir / "SKILL.md").write_text("\n".join(fm_lines), encoding="utf-8")
    return skill_dir


# ---------------------------------------------------------------------------
# _parse_frontmatter
# ---------------------------------------------------------------------------

class TestParseFrontmatter:
    def test_simple_fields(self):
        text = textwrap.dedent("""\
            ---
            name: my-skill
            description: "A short description."
            license: MIT
            ---
            # body
        """)
        fm = _parse_frontmatter(text)
        assert fm["name"] == "my-skill"
        assert fm["description"] == "A short description."
        assert fm["license"] == "MIT"

    def test_no_frontmatter_returns_empty(self):
        fm = _parse_frontmatter("# Just a heading\nno front matter here")
        assert fm == {}

    def test_block_scalar(self):
        text = textwrap.dedent("""\
            ---
            name: block-skill
            description: >
              Line one of description.
              Line two of description.
            ---
        """)
        fm = _parse_frontmatter(text)
        assert "Line one" in fm.get("description", "")
        assert "Line two" in fm.get("description", "")

    def test_single_quoted_value(self):
        text = "---\nname: 'quoted'\ndescription: 'also quoted'\n---\n"
        fm = _parse_frontmatter(text)
        assert fm["name"] == "quoted"


# ---------------------------------------------------------------------------
# _classify
# ---------------------------------------------------------------------------

class TestClassify:
    def test_gsap_skill(self):
        assert _classify("gsap-core", "GSAP tweens and timelines") == "gsap-utility"

    def test_audio_skill(self):
        assert _classify("speech-to-text", "Transcribe audio with faster-whisper") == "audio-utility"

    def test_design_skill(self):
        assert _classify("minimalist-ui", "Clean UI design") == "design-utility"

    def test_media_skill(self):
        assert _classify("remove-background", "Remove image backgrounds") == "media-utility"

    def test_motion_skill(self):
        assert _classify("motion-x", "Scroll-driven animation timeline") == "motion-utility"

    def test_fallback_utility(self):
        assert _classify("misc-helper", "Does something generic") == "utility"


# ---------------------------------------------------------------------------
# scan()
# ---------------------------------------------------------------------------

class TestScan:
    def test_empty_directory(self, tmp_path):
        result = scan(tmp_path)
        assert result == []

    def test_missing_directory(self, tmp_path):
        result = scan(tmp_path / "nonexistent")
        assert result == []

    def test_single_skill(self, tmp_path):
        _make_skill(tmp_path, "gsap-core", "GSAP core tweens and timelines.", "MIT")
        result = scan(tmp_path)
        assert len(result) == 1
        entry = result[0]
        assert entry["name"] == "gsap-core"
        assert entry["license"] == "MIT"
        assert entry["kind"] == "agent-skill"
        assert entry["optional"] is True
        assert "gsap-core/SKILL.md" in entry["path"]

    def test_skips_non_directories(self, tmp_path):
        (tmp_path / "README.md").write_text("not a skill", encoding="utf-8")
        result = scan(tmp_path)
        assert result == []

    def test_skips_folder_without_skill_md(self, tmp_path):
        (tmp_path / "orphan-folder").mkdir()
        result = scan(tmp_path)
        assert result == []

    def test_multiple_skills_sorted(self, tmp_path):
        _make_skill(tmp_path, "zzz-skill", "Last alphabetically")
        _make_skill(tmp_path, "aaa-skill", "First alphabetically")
        result = scan(tmp_path)
        names = [e["name"] for e in result]
        assert names == sorted(names)

    def test_path_is_relative(self, tmp_path):
        _make_skill(tmp_path, "speech-to-text", "Transcribe audio")
        result = scan(tmp_path)
        # Path must not be absolute
        assert not Path(result[0]["path"]).is_absolute()

    def test_category_assigned(self, tmp_path):
        _make_skill(tmp_path, "my-audio", "Use faster-whisper to transcribe voice")
        result = scan(tmp_path)
        assert result[0]["category"] == "audio-utility"

    def test_no_license_returns_none(self, tmp_path):
        _make_skill(tmp_path, "no-lic", "Some skill without a license")
        result = scan(tmp_path)
        assert result[0]["license"] is None


# ---------------------------------------------------------------------------
# build_index()
# ---------------------------------------------------------------------------

class TestBuildIndex:
    def test_structure(self, tmp_path):
        _make_skill(tmp_path, "gsap-utils", "GSAP utility functions")
        _make_skill(tmp_path, "speech-to-text", "Whisper audio transcription", "MIT")

        index = build_index(tmp_path)

        assert index["version"] == 2
        assert index["total"] == 2
        assert len(index["skills"]) == 2
        assert "by_category" in index

    def test_by_category_grouping(self, tmp_path):
        _make_skill(tmp_path, "gsap-core", "GSAP tweens")
        _make_skill(tmp_path, "speech-to-text", "Transcribe audio with whisper")

        index = build_index(tmp_path)
        by_cat = index["by_category"]

        assert "gsap-core" in by_cat.get("gsap-utility", [])
        assert "speech-to-text" in by_cat.get("audio-utility", [])

    def test_empty_dir_total_zero(self, tmp_path):
        index = build_index(tmp_path)
        assert index["total"] == 0
        assert index["skills"] == []
        assert index["by_category"] == {}

    def test_json_serialisable(self, tmp_path):
        _make_skill(tmp_path, "brandkit", "Brand identity generation")
        index = build_index(tmp_path)
        # Must not raise
        payload = json.dumps(index, ensure_ascii=False)
        parsed = json.loads(payload)
        assert parsed["total"] == 1

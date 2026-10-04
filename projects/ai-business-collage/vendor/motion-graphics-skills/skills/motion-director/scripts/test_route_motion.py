#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("route_motion.py")
NETWORK = SCRIPT.parent.parent / "router" / "skill-network.json"


def make_pack(root: Path, skills: list[str], *, work_guard: bool = False) -> None:
    for name in skills:
        path = root / "skills" / name
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text(f"---\nname: {name}\ndescription: test\n---\n", encoding="utf-8")
    scripts = root / "skills" / "motion-director" / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    if work_guard:
        (scripts / "work_guard.py").write_text("# test\n", encoding="utf-8")
    (scripts / "gpu_policy.py").write_text("# test\n", encoding="utf-8")


def route(pack: Path, context: dict) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        context_path = Path(tmp) / "context.json"
        context_path.write_text(json.dumps(context), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--context",
                str(context_path),
                "--pack-root",
                str(pack),
                "--network",
                str(NETWORK),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode not in {0, 3}:
            raise AssertionError(result.stderr or result.stdout)
        data = json.loads(result.stdout)
        expected_code = 3 if data.get("status") == "blocked" else 0
        if result.returncode != expected_code:
            raise AssertionError(
                f"route status {data.get('status')} returned {result.returncode}, "
                f"expected {expected_code}"
            )
        return data


class RouteMotionTests(unittest.TestCase):
    def test_short_launch_builds_brand_specialist_gpu_and_review_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp)
            make_pack(pack, ["motion-director", "brand-intake", "launch-video", "video-review-loop"])
            data = route(pack, {
                "deliverable": "launch",
                "brand_ready": False,
                "final_video": True,
                "heavy_media": True,
                "language": "ar",
            })
            self.assertEqual(data["entry"], "motion-director")
            self.assertEqual(
                [stage["name"] for stage in data["stages"]],
                ["motion-director", "brand-intake", "launch-video", "gpu-policy", "video-review-loop"],
            )
            self.assertIn("skills/motion-director/references/arabic-motion.md", data["required_references"])
            self.assertEqual(len(data["stages"]), len({stage["name"] for stage in data["stages"]}))

    def test_multi_reference_route_uses_mix_and_match_only_when_installed(self) -> None:
        base_context = {
            "deliverable": "broad-film",
            "brand_ready": True,
            "reference_count": 3,
            "mix_references": True,
        }
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp)
            make_pack(pack, ["motion-director", "video-review-loop"])
            without_mix = route(pack, base_context)
            self.assertNotIn("mix-and-match", [stage["name"] for stage in without_mix["stages"]])
            self.assertTrue(any(item["name"] == "mix-and-match" for item in without_mix["skipped_optional"]))

        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp)
            make_pack(pack, ["motion-director", "mix-and-match", "video-review-loop"])
            with_mix = route(pack, base_context)
            self.assertIn("mix-and-match", [stage["name"] for stage in with_mix["stages"]])

    def test_structural_fidelity_adds_reference_gate_before_specialist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp)
            make_pack(pack, ["motion-director", "launch-video", "video-review-loop"])
            fidelity_tool = pack / "skills" / "motion-director" / "scripts" / "reference_fidelity.py"
            fidelity_tool.write_text("# test\n", encoding="utf-8")
            data = route(pack, {
                "deliverable": "launch",
                "brand_ready": True,
                "reference_count": 1,
                "reference_mode": "structural-fidelity",
                "difficulty_mode": "preserve",
            })
            names = [stage["name"] for stage in data["stages"]]
            self.assertIn("reference-fidelity", names)
            self.assertLess(names.index("reference-fidelity"), names.index("launch-video"))
            self.assertTrue(data["constraints"]["difficulty_preservation"])
            self.assertEqual(data["constraints"]["reference_mode"], "structural-fidelity")

    def test_inspiration_mode_does_not_force_fidelity_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp)
            make_pack(pack, ["motion-director", "launch-video", "video-review-loop"])
            fidelity_tool = pack / "skills" / "motion-director" / "scripts" / "reference_fidelity.py"
            fidelity_tool.write_text("# test\n", encoding="utf-8")
            data = route(pack, {
                "deliverable": "launch",
                "brand_ready": True,
                "reference_count": 1,
                "reference_mode": "inspiration",
            })
            self.assertNotIn("reference-fidelity", [stage["name"] for stage in data["stages"]])
            self.assertFalse(data["constraints"]["difficulty_preservation"])

    def test_hang_prone_stage_uses_optional_work_guard_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp)
            make_pack(pack, ["motion-director", "video-review-loop"], work_guard=True)
            data = route(pack, {
                "deliverable": "broad-film",
                "brand_ready": True,
                "hang_prone": True,
            })
            self.assertIn("work-guard", [stage["name"] for stage in data["stages"]])

    def test_review_only_does_not_route_through_unrelated_specialist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp)
            make_pack(pack, ["motion-director", "video-review-loop"])
            data = route(pack, {
                "deliverable": "existing-film-review",
                "review_only": True,
                "final_video": True,
                "brand_ready": True,
            })
            self.assertEqual(
                [stage["name"] for stage in data["stages"]],
                ["motion-director", "video-review-loop"],
            )

    def test_specialist_mapping_is_deterministic(self) -> None:
        mapping = {
            "brief-only": "motion-brief-writer",
            "launch": "launch-video",
            "apple-launch": "apple-launch-film",
            "explainer": "vox-explainer",
            "chart": "animated-chart",
            "milestone": "milestone-reveal",
            "named-effect": "motion-effects",
            "3d-title": "title-sequence-3d",
            "model-showdown": "model-showdown",
            "newsletter": "newsletter-promo",
            "loop-cover": "loop-cover",
            "reel-export": "reel-export",
        }
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp)
            make_pack(pack, ["motion-director", "video-review-loop", *mapping.values()])
            for deliverable, expected in mapping.items():
                data = route(pack, {"deliverable": deliverable, "brand_ready": True})
                self.assertIn(expected, [stage["name"] for stage in data["stages"]])

    def test_every_stage_has_explanation_and_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp)
            make_pack(pack, ["motion-director", "launch-video", "video-review-loop"])
            data = route(pack, {"deliverable": "launch", "brand_ready": True, "final_video": True})
            for stage in data["stages"]:
                self.assertTrue(stage["reason"])
                self.assertIn("handoff", stage)
                self.assertIn("must_return", stage["handoff"])


    def test_missing_required_reference_gate_blocks_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp)
            make_pack(pack, ["motion-director", "launch-video", "video-review-loop"])
            data = route(pack, {
                "deliverable": "launch",
                "brand_ready": True,
                "reference_count": 1,
                "reference_mode": "structural-fidelity",
                "difficulty_mode": "preserve",
            })
            self.assertEqual(data["status"], "blocked")
            self.assertIn(
                "reference-fidelity",
                [item["name"] for item in data["blockers"]],
            )

    def test_ready_route_has_no_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp)
            make_pack(pack, ["motion-director", "launch-video", "video-review-loop"])
            data = route(pack, {
                "deliverable": "launch",
                "brand_ready": True,
            })
            self.assertEqual(data["status"], "ready")
            self.assertEqual(data["blockers"], [])


    def test_invalid_reference_mode_blocks_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp)
            make_pack(pack, ["motion-director", "video-review-loop"])
            data = route(pack, {
                "deliverable": "broad-film",
                "brand_ready": True,
                "reference_count": 1,
                "reference_mode": "structural-ish",
                "difficulty_mode": "normal",
            })
            self.assertEqual(data["status"], "blocked")
            self.assertTrue(any(
                item["name"] == "routing-context"
                for item in data["blockers"]
            ))

    def test_invalid_difficulty_mode_blocks_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp)
            make_pack(pack, ["motion-director", "video-review-loop"])
            data = route(pack, {
                "deliverable": "broad-film",
                "brand_ready": True,
                "reference_count": 1,
                "reference_mode": "inspiration",
                "difficulty_mode": "preserv",
            })
            self.assertEqual(data["status"], "blocked")
            self.assertTrue(any(
                item["name"] == "routing-context"
                for item in data["blockers"]
            ))


if __name__ == "__main__":
    unittest.main()

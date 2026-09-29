#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("reference_fidelity.py")


def run_tool(contract: dict, plan: dict | None = None) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        contract_path = tmp_path / "reference-contract.json"
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        argv = [sys.executable, str(SCRIPT), "validate", str(contract_path)]
        if plan is not None:
            plan_path = tmp_path / "implementation-plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            argv.extend(["--plan", str(plan_path)])
        return subprocess.run(
            argv,
            text=True,
            capture_output=True,
            check=False,
        )


def valid_contract() -> dict:
    return {
        "mode": "structural-fidelity",
        "difficulty_mode": "preserve",
        "reference": {
            "source": "reference.mp4",
            "duration": 17.87,
        },
        "signature": {
            "rhythm": "hard reset every 1.4 to 2 seconds",
            "composition": "one huge cropped focal object with generous negative space",
            "typography": "word-level short blur rise with one accent payoff",
            "transitions": "hard world flips plus circular resets and carried handoffs",
            "density": "middle grows denser, ending becomes the quietest frame",
            "material": "object-led editorial system rather than a text-only layout",
        },
        "dominant_language": "large object-led editorial compositions with hard light-dark resets and causal masks",
        "secondary_motifs": [
            "paper texture",
            "grain",
            "tape",
            "print furniture"
        ],
        "must_preserve": [
            {
                "id": "world-flips",
                "mechanism": "hard light/dark world reset on major cuts",
                "why_hard": "requires scene-level continuity and contrast planning",
                "evidence": "compare major cut frames",
            },
            {
                "id": "object-scale",
                "mechanism": "one oversized intentionally cropped focal object per shot",
                "why_hard": "requires asset treatment and composition, not only typography",
                "evidence": "review contact sheet and full video",
            },
            {
                "id": "transition-causality",
                "mechanism": "resets grow from or are carried by an existing scene element",
                "why_hard": "requires cross-scene choreography",
                "evidence": "inspect transitions frame by frame",
            },
        ],
        "may_translate": [
            "copy",
            "brand accent color",
            "specific objects",
        ],
        "forbidden_shortcuts": [
            "replace object-led scenes with paper cards and text",
            "replace causal transitions with generic wipes",
            "flatten scene variety into one repeated material treatment",
        ],
    }


class ReferenceFidelityTests(unittest.TestCase):
    def test_valid_contract_passes(self) -> None:
        result = run_tool(valid_contract())
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "pass")

    def test_structural_fidelity_requires_signature_dimensions(self) -> None:
        contract = valid_contract()
        del contract["signature"]["transitions"]
        result = run_tool(contract)
        self.assertEqual(result.returncode, 3)
        data = json.loads(result.stdout)
        self.assertIn("signature.transitions", data["missing"])

    def test_difficulty_preserve_requires_hard_mechanisms(self) -> None:
        contract = valid_contract()
        contract["must_preserve"] = []
        result = run_tool(contract)
        self.assertEqual(result.returncode, 3)
        data = json.loads(result.stdout)
        self.assertIn("must_preserve>=2", data["missing"])

    def test_surface_only_contract_is_rejected(self) -> None:
        contract = valid_contract()
        contract["signature"] = {
            "rhythm": "fast",
            "composition": "cool",
            "typography": "bold",
            "transitions": "dynamic",
            "density": "premium",
            "material": "cinematic",
        }
        result = run_tool(contract)
        self.assertEqual(result.returncode, 3)
        data = json.loads(result.stdout)
        self.assertTrue(any("too vague" in issue for issue in data["issues"]))

    def test_plan_must_map_every_preserved_mechanism(self) -> None:
        plan = {
            "visual_direction": {
                "dominant_language": "large cropped object-led scenes alternate between complete light and dark worlds",
                "preserves": [
                    "world-flips",
                    "object-scale",
                    "transition-causality"
                ],
                "promoted_secondary_motifs": [],
                "new_dominant_motifs": [],
                "user_approved_style_expansion": False,
            },
            "implementations": [
                {
                    "contract_id": "world-flips",
                    "implementation": "alternate complete light and dark scene worlds",
                    "verification": "major-cut comparison",
                },
                {
                    "contract_id": "object-scale",
                    "implementation": "large cropped assets dominate each object beat",
                    "verification": "contact sheet",
                },
            ]
        }
        result = run_tool(valid_contract(), plan)
        self.assertEqual(result.returncode, 3)
        data = json.loads(result.stdout)
        self.assertIn("transition-causality", data["unmapped_contract_ids"])

    def test_complete_plan_passes(self) -> None:
        plan = {
            "visual_direction": {
                "dominant_language": "large cropped object-led scenes alternate between complete light and dark worlds",
                "preserves": [
                    "world-flips",
                    "object-scale",
                    "transition-causality"
                ],
                "promoted_secondary_motifs": [],
                "new_dominant_motifs": [],
                "user_approved_style_expansion": False,
            },
            "implementations": [
                {
                    "contract_id": "world-flips",
                    "implementation": "alternate complete light and dark scene worlds",
                    "verification": "major-cut comparison",
                },
                {
                    "contract_id": "object-scale",
                    "implementation": "large cropped assets dominate each object beat",
                    "verification": "contact sheet",
                },
                {
                    "contract_id": "transition-causality",
                    "implementation": "each reset originates from a live scene object",
                    "verification": "transition frame audit",
                },
            ]
        }
        result = run_tool(valid_contract(), plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["mapped_contract_ids"], [
            "object-scale",
            "transition-causality",
            "world-flips",
        ])


    def test_preserve_contract_requires_salience_lock(self) -> None:
        contract = valid_contract()
        del contract["dominant_language"]
        del contract["secondary_motifs"]
        result = run_tool(contract)
        self.assertEqual(result.returncode, 3)
        data = json.loads(result.stdout)
        self.assertIn("dominant_language", data["missing"])
        self.assertIn("secondary_motifs>=1", data["missing"])

    def test_plan_rejects_salience_inversion(self) -> None:
        plan = {
            "visual_direction": {
                "dominant_language": "tactile paper desk with sheets tape and grain across most scenes",
                "preserves": [
                    "world-flips",
                    "object-scale",
                    "transition-causality"
                ],
                "promoted_secondary_motifs": [
                    "paper texture",
                    "grain",
                    "tape"
                ],
                "new_dominant_motifs": [],
                "user_approved_style_expansion": False,
            },
            "implementations": [
                {
                    "contract_id": "world-flips",
                    "implementation": "alternate complete light and dark scene worlds",
                    "verification": "major-cut comparison",
                },
                {
                    "contract_id": "object-scale",
                    "implementation": "large cropped assets dominate each object beat",
                    "verification": "contact sheet",
                },
                {
                    "contract_id": "transition-causality",
                    "implementation": "each reset originates from a live scene object",
                    "verification": "transition frame audit",
                },
            ],
        }
        result = run_tool(valid_contract(), plan)
        self.assertEqual(result.returncode, 3)
        data = json.loads(result.stdout)
        self.assertTrue(data["salience_inversions"])

    def test_plan_rejects_unapproved_new_dominant_style(self) -> None:
        plan = {
            "visual_direction": {
                "dominant_language": "large cropped object-led scenes with a new glass interface world",
                "preserves": [
                    "world-flips",
                    "object-scale",
                    "transition-causality"
                ],
                "promoted_secondary_motifs": [],
                "new_dominant_motifs": ["glass interface system"],
                "user_approved_style_expansion": False,
            },
            "implementations": [
                {
                    "contract_id": "world-flips",
                    "implementation": "alternate complete light and dark scene worlds",
                    "verification": "major-cut comparison",
                },
                {
                    "contract_id": "object-scale",
                    "implementation": "large cropped assets dominate each object beat",
                    "verification": "contact sheet",
                },
                {
                    "contract_id": "transition-causality",
                    "implementation": "each reset originates from a live scene object",
                    "verification": "transition frame audit",
                },
            ],
        }
        result = run_tool(valid_contract(), plan)
        self.assertEqual(result.returncode, 3)
        data = json.loads(result.stdout)
        self.assertTrue(data["unapproved_style_expansions"])


if __name__ == "__main__":
    unittest.main()

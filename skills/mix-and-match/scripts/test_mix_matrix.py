#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("mix_matrix.py")


def run_tool(payload: dict, *args: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "pool.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(path), *args],
            text=True,
            capture_output=True,
            check=False,
        )


class MixMatrixTests(unittest.TestCase):
    def test_requires_two_references(self) -> None:
        result = run_tool(
            {
                "references": [
                    {"id": "A", "genes": {"motion": ["mask reveal"]}}
                ]
            }
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("at least two references", result.stderr)

    def test_rejects_non_object_root(self) -> None:
        result = run_tool(["not", "an", "object"])
        self.assertEqual(result.returncode, 2)
        self.assertIn("root must be an object", result.stderr)

    def test_rejects_non_object_reference(self) -> None:
        result = run_tool(
            {
                "references": [
                    "not-an-object",
                    {"id": "B", "genes": {"motion": ["mask reveal"]}},
                ]
            }
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("reference entries must be objects", result.stderr)

    def test_preserves_feasible_cross_source_pairing(self) -> None:
        payload = {
            "references": [
                {
                    "id": "A",
                    "genes": {
                        "motion": ["a-motion"],
                        "material": ["a-material"],
                    },
                },
                {
                    "id": "B",
                    "genes": {
                        "motion": ["b-motion"],
                    },
                },
            ]
        }
        result = run_tool(payload, "--recipes", "1", "--seed", "0")
        self.assertEqual(result.returncode, 0, result.stderr)
        recipe = json.loads(result.stdout)["recipes"][0]
        self.assertEqual(set(recipe["source_share"]), {"A", "B"})
        self.assertEqual(recipe["warnings"], [])

    def test_generates_three_cross_source_recipes(self) -> None:
        payload = {
            "brief": "Arabic promo",
            "references": [
                {
                    "id": "A",
                    "domain": "motion",
                    "genes": {
                        "rhythm": ["fast-fast-hold"],
                        "motion": ["mask reveal"],
                        "typography": ["one dominant phrase"],
                    },
                },
                {
                    "id": "B",
                    "domain": "print",
                    "genes": {
                        "material": ["rough paper edge"],
                        "composition": ["large crop and negative space"],
                        "transition": ["page edge handoff"],
                    },
                },
                {
                    "id": "W1",
                    "role": "wildcard",
                    "domain": "wayfinding",
                    "genes": {
                        "spatial": ["route organizes attention"],
                        "metaphor": ["one line changes role"],
                    },
                },
            ],
        }
        result = run_tool(payload, "--recipes", "3", "--seed", "5")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["recipe_count"], 3)
        for recipe in data["recipes"]:
            self.assertGreaterEqual(len(recipe["source_share"]), 2)
            self.assertLessEqual(max(recipe["source_share"].values()), 0.40)

    def test_two_source_recipe_avoids_impossible_odd_slot_warning(self) -> None:
        payload = {
            "references": [
                {
                    "id": "A",
                    "genes": {
                        "motion": ["a1"],
                        "rhythm": ["a2"],
                        "typography": ["a3"],
                    },
                },
                {
                    "id": "B",
                    "genes": {
                        "material": ["b1"],
                        "transition": ["b2"],
                    },
                },
            ]
        }
        result = run_tool(payload, "--recipes", "1", "--seed", "7")
        self.assertEqual(result.returncode, 0, result.stderr)
        recipe = json.loads(result.stdout)["recipes"][0]
        self.assertEqual(len(recipe["slots"]) % 2, 0)
        self.assertLessEqual(max(recipe["source_share"].values()), 0.50)
        self.assertEqual(recipe["warnings"], [])

    def test_balances_three_sources_when_even_assignment_is_feasible(self) -> None:
        payload = {
            "references": [
                {
                    "id": "A",
                    "genes": {
                        "c1": ["a1"],
                        "c6": ["a6"],
                    },
                },
                {
                    "id": "B",
                    "genes": {
                        "c1": ["b1"],
                        "c2": ["b2"],
                        "c3": ["b3"],
                        "c5": ["b5"],
                    },
                },
                {
                    "id": "C",
                    "genes": {
                        "c0": ["c0"],
                        "c2": ["c2"],
                        "c3": ["c3"],
                        "c4": ["c4"],
                        "c5": ["c5"],
                        "c6": ["c6"],
                    },
                },
            ]
        }
        result = run_tool(payload, "--recipes", "1", "--seed", "19")
        self.assertEqual(result.returncode, 0, result.stderr)
        recipe = json.loads(result.stdout)["recipes"][0]
        self.assertEqual(recipe["source_share"], {"A": 0.333, "B": 0.333, "C": 0.333})
        self.assertEqual(recipe["warnings"], [])

    def test_small_recipe_uses_achievable_dominance_threshold(self) -> None:
        payload = {
            "references": [
                {"id": "A", "genes": {"c0": ["a0"]}},
                {"id": "B", "genes": {"c1": ["b1"]}},
                {"id": "C", "genes": {"c0": ["c0"]}},
            ]
        }
        result = run_tool(payload, "--recipes", "1", "--seed", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        recipe = json.loads(result.stdout)["recipes"][0]
        self.assertEqual(len(recipe["slots"]), 2)
        self.assertEqual(max(recipe["source_share"].values()), 0.50)
        self.assertEqual(recipe["warnings"], [])

    def test_rejects_non_string_gene_values(self) -> None:
        payload = {
            "references": [
                {
                    "id": "A",
                    "genes": {
                        "motion": [None],
                    },
                },
                {
                    "id": "B",
                    "genes": {
                        "material": [None],
                    },
                },
            ]
        }
        result = run_tool(payload)
        self.assertEqual(result.returncode, 2)
        self.assertIn("at least two usable gene categories", result.stderr)

    def test_warns_on_source_dominance_when_relaxed(self) -> None:
        payload = {
            "references": [
                {
                    "id": "A",
                    "genes": {
                        "metaphor": ["a1"],
                        "structure": ["a2"],
                        "rhythm": ["a3"],
                        "composition": ["a4"],
                        "typography": ["a5"],
                    },
                },
                {
                    "id": "B",
                    "genes": {
                        "motion": ["b1"],
                    },
                },
            ]
        }
        result = run_tool(payload, "--recipes", "1", "--seed", "0")
        self.assertEqual(result.returncode, 0, result.stderr)
        recipe = json.loads(result.stdout)["recipes"][0]
        self.assertEqual(recipe["source_share"]["A"], 0.833)
        self.assertEqual(len(recipe["warnings"]), 1)
        self.assertIn("source dominance 83% exceeds target 50%", recipe["warnings"][0])

    def test_is_deterministic_for_same_seed(self) -> None:
        payload = {
            "references": [
                {
                    "id": "A",
                    "genes": {
                        "motion": ["a1", "a2"],
                        "rhythm": ["a3"],
                    },
                },
                {
                    "id": "B",
                    "genes": {
                        "material": ["b1"],
                        "transition": ["b2", "b3"],
                    },
                },
            ]
        }
        first = run_tool(payload, "--seed", "99")
        second = run_tool(payload, "--seed", "99")
        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)


if __name__ == "__main__":
    unittest.main()


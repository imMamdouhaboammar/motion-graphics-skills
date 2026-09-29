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

#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("review_round.py")


def load_module():
    spec = importlib.util.spec_from_file_location("review_round", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load review_round")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_round(
    root: Path,
    machine_hard: int = 0,
    *,
    reference: bool = False,
    strict_signals: bool = False,
) -> Path:
    root.mkdir(parents=True)
    manifest = {"finding_counts": {"hard": machine_hard, "warning": 0}}
    if reference:
        manifest["reference"] = {"path": "/tmp/reference.mp4"}
    (root / "manifest.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )
    if strict_signals:
        (root / "strict-signals.json").write_text(
            json.dumps({"findings": [], "counts": {}}),
            encoding="utf-8",
        )
    return root


class ReviewRoundTests(unittest.TestCase):
    def test_add_and_resolve_visual_finding(self) -> None:
        mod = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = make_round(Path(tmp) / "round")
            item = mod.add_finding(
                round_dir,
                timestamp="00:04.280",
                severity="hard",
                defect="Arabic headline clips",
                fix="increase safe area",
                evidence="full playback and frame inspection",
            )
            self.assertEqual(item["id"], "V001")
            self.assertEqual(mod.round_status(round_dir)["status"], "blocked-visual-hard-findings")
            mod.resolve_finding(
                round_dir,
                "V001",
                resolution="fixed in next render",
                evidence="round-2 final.mp4 at 00:04.280",
            )
            self.assertEqual(mod.round_status(round_dir)["pending_hard_count"], 0)

    def test_clean_round_still_requires_visual_attestation(self) -> None:
        mod = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = make_round(Path(tmp) / "round")
            status = mod.round_status(round_dir)
            self.assertEqual(status["status"], "agent-review-required")
            self.assertIn("watched_with_audio", status["missing_attestations"])

    def test_all_required_attestations_allow_review_complete(self) -> None:
        mod = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = make_round(Path(tmp) / "round", strict_signals=True)
            mod.attest(
                round_dir,
                watched_with_audio=True,
                watched_muted=True,
                first_second_inspected=True,
                transitions_inspected=True,
                ending_inspected=True,
                reference_compared=True,
                strict_signals_inspected=True,
            )
            self.assertEqual(mod.round_status(round_dir)["status"], "review-complete")

    def test_machine_hard_findings_block_completion_even_after_attestation(self) -> None:
        mod = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = make_round(Path(tmp) / "round", machine_hard=1)
            mod.attest(
                round_dir,
                watched_with_audio=True,
                watched_muted=True,
                first_second_inspected=True,
                transitions_inspected=True,
                ending_inspected=True,
                reference_compared=False,
                strict_signals_inspected=False,
            )
            self.assertEqual(mod.round_status(round_dir)["status"], "blocked-machine-hard-findings")


    def test_reference_round_requires_reference_comparison_attestation(self) -> None:
        mod = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = make_round(
                Path(tmp) / "round",
                reference=True,
                strict_signals=True,
            )
            mod.attest(
                round_dir,
                watched_with_audio=True,
                watched_muted=True,
                first_second_inspected=True,
                transitions_inspected=True,
                ending_inspected=True,
                reference_compared=False,
                strict_signals_inspected=True,
            )
            status = mod.round_status(round_dir)
            self.assertEqual(status["status"], "agent-review-required")
            self.assertIn("reference_compared", status["missing_attestations"])


    def test_round_requires_strict_signal_evidence_before_completion(self) -> None:
        mod = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = make_round(Path(tmp) / "round")
            mod.attest(
                round_dir,
                watched_with_audio=True,
                watched_muted=True,
                first_second_inspected=True,
                transitions_inspected=True,
                ending_inspected=True,
                reference_compared=False,
                strict_signals_inspected=True,
            )
            status = mod.round_status(round_dir)
            self.assertEqual(status["status"], "agent-review-required")
            self.assertIn("strict-signals.json", status["missing_evidence"])

    def test_round_requires_strict_signal_inspection_attestation(self) -> None:
        mod = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = make_round(Path(tmp) / "round", strict_signals=True)
            mod.attest(
                round_dir,
                watched_with_audio=True,
                watched_muted=True,
                first_second_inspected=True,
                transitions_inspected=True,
                ending_inspected=True,
                reference_compared=False,
                strict_signals_inspected=False,
            )
            status = mod.round_status(round_dir)
            self.assertEqual(status["status"], "agent-review-required")
            self.assertIn(
                "strict_signals_inspected",
                status["missing_attestations"],
            )


if __name__ == "__main__":
    unittest.main()

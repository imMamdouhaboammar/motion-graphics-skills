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
    source = root / "source.mp4"
    source.write_bytes(b"video-fixture")
    stat = source.stat()
    source_manifest = {
        "path": str(source.resolve()),
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }
    manifest = {
        "finding_counts": {"hard": machine_hard, "warning": 0},
        "source": source_manifest,
    }
    if reference:
        reference_path = root / "reference.mp4"
        reference_path.write_bytes(b"reference-fixture")
        ref_stat = reference_path.stat()
        manifest["reference"] = {
            "path": str(reference_path.resolve()),
            "size_bytes": ref_stat.st_size,
            "mtime_ns": ref_stat.st_mtime_ns,
        }
    (root / "manifest.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )
    if strict_signals:
        (root / "strict-signals.json").write_text(
            json.dumps({
                "status": "pass",
                "source": str(source.resolve()),
                "source_manifest": source_manifest,
                "frames_analyzed": 10,
                "findings": [],
                "counts": {},
            }),
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
            later_artifact = Path(tmp) / "round-2-final.mp4"
            later_artifact.write_bytes(b"new-rendered-content")
            mod.resolve_finding(
                round_dir,
                "V001",
                resolution="fixed in next render",
                evidence="round-2-final.mp4 at 00:04.280",
                later_artifact=later_artifact,
            )
            self.assertEqual(mod.round_status(round_dir)["pending_hard_count"], 0)

    def test_resolve_hard_finding_without_later_artifact_or_acceptance_fails(self) -> None:
        mod = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = make_round(Path(tmp) / "round")
            mod.add_finding(
                round_dir,
                timestamp="00:04.280",
                severity="hard",
                defect="Arabic headline clips",
                fix="increase safe area",
                evidence="inspection",
            )
            with self.assertRaises(ValueError):
                mod.resolve_finding(
                    round_dir,
                    "V001",
                    resolution="fixed in source code",
                    evidence="git commit 12345",
                )

    def test_resolve_hard_finding_with_unchanged_source_fails(self) -> None:
        mod = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = make_round(Path(tmp) / "round")
            source_file = round_dir / "source.mp4"
            mod.add_finding(
                round_dir,
                timestamp="00:04.280",
                severity="hard",
                defect="Arabic headline clips",
                fix="increase safe area",
                evidence="inspection",
            )
            with self.assertRaises(ValueError):
                mod.resolve_finding(
                    round_dir,
                    "V001",
                    resolution="reviewed again",
                    evidence="source.mp4",
                    later_artifact=source_file,
                )

    def test_resolve_hard_finding_with_user_acceptance_succeeds(self) -> None:
        mod = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = make_round(Path(tmp) / "round")
            mod.add_finding(
                round_dir,
                timestamp="00:04.280",
                severity="hard",
                defect="Arabic headline clips",
                fix="increase safe area",
                evidence="inspection",
            )
            mod.resolve_finding(
                round_dir,
                "V001",
                resolution="user-accepted intentional stylistic crop",
                evidence="client email approval",
                user_accepted=True,
            )
            self.assertEqual(mod.round_status(round_dir)["pending_hard_count"], 0)

    def test_resolve_hard_finding_rejects_free_text_without_flag(self) -> None:
        mod = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = make_round(Path(tmp) / "round")
            mod.add_finding(
                round_dir,
                timestamp="00:04.280",
                severity="hard",
                defect="Arabic headline clips",
                fix="increase safe area",
                evidence="inspection",
            )
            with self.assertRaises(ValueError):
                mod.resolve_finding(
                    round_dir,
                    "V001",
                    resolution="not user-accepted; rerender required",
                    evidence="defect still present in current draft",
                    user_accepted=False,
                )

    def test_round_status_keeps_hard_finding_pending_if_unproven(self) -> None:
        mod = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = make_round(Path(tmp) / "round")
            mod.add_finding(
                round_dir,
                timestamp="00:04.280",
                severity="hard",
                defect="Arabic headline clips",
                fix="increase safe area",
                evidence="inspection",
            )
            findings_file = mod.findings_path(round_dir)
            findings = json.loads(findings_file.read_text(encoding="utf-8"))
            findings[0]["status"] = "resolved"
            findings[0]["resolution"] = "arbitrary text"
            findings_file.write_text(json.dumps(findings), encoding="utf-8")

            status = mod.round_status(round_dir)
            self.assertEqual(status["pending_hard_count"], 1)
            self.assertEqual(status["status"], "blocked-visual-hard-findings")

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


    def test_completed_round_is_invalidated_when_source_changes(self) -> None:
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
                strict_signals_inspected=True,
            )
            source = round_dir / "source.mp4"
            source.write_bytes(b"changed-video-fixture")
            status = mod.round_status(round_dir)
            self.assertEqual(status["status"], "source-artifact-changed")
            self.assertTrue(status["source_changed"])

    def test_malformed_strict_signal_evidence_does_not_satisfy_gate(self) -> None:
        mod = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            round_dir = make_round(Path(tmp) / "round", strict_signals=True)
            (round_dir / "strict-signals.json").write_text(
                json.dumps({"status": "pass", "frames_analyzed": 0}),
                encoding="utf-8",
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
            self.assertIn("strict-signals.json:invalid", status["missing_evidence"])


    def test_completed_round_is_invalidated_when_reference_changes(self) -> None:
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
                reference_compared=True,
                strict_signals_inspected=True,
            )
            reference = round_dir / "reference.mp4"
            reference.write_bytes(b"changed-reference-fixture")
            status = mod.round_status(round_dir)
            self.assertEqual(status["status"], "reference-artifact-changed")
            self.assertTrue(status["reference_changed"])


if __name__ == "__main__":
    unittest.main()

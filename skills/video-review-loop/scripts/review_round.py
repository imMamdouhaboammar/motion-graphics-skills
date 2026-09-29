#!/usr/bin/env python3
"""Manage structured visual-review findings for one motion review round."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FINDINGS_FILE = "visual-findings.json"
STATE_FILE = "review-state.json"
VALID_VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}
REQUIRED_ATTESTATIONS = (
    "watched_with_audio",
    "watched_muted",
    "first_second_inspected",
    "transitions_inspected",
    "ending_inspected",
    "strict_signals_inspected",
)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def ensure_round(round_dir: Path) -> None:
    if not round_dir.is_dir():
        raise ValueError(f"Review round does not exist: {round_dir}")
    if not (round_dir / "manifest.json").exists():
        raise ValueError(f"Not a video-review round: {round_dir}")


def findings_path(round_dir: Path) -> Path:
    return round_dir / FINDINGS_FILE


def state_path(round_dir: Path) -> Path:
    return round_dir / STATE_FILE


def load_findings(round_dir: Path) -> list[dict[str, Any]]:
    data = load_json(findings_path(round_dir), [])
    if not isinstance(data, list):
        raise ValueError("visual-findings.json must contain a list")
    return data


def next_id(findings: list[dict[str, Any]]) -> str:
    highest = 0
    for item in findings:
        raw = str(item.get("id", ""))
        if raw.startswith("V") and raw[1:].isdigit():
            highest = max(highest, int(raw[1:]))
    return f"V{highest + 1:03d}"


def add_finding(
    round_dir: Path,
    *,
    timestamp: str,
    severity: str,
    defect: str,
    fix: str,
    evidence: str,
) -> dict[str, Any]:
    findings = load_findings(round_dir)
    item = {
        "id": next_id(findings),
        "timestamp": timestamp,
        "severity": severity,
        "defect": defect,
        "fix": fix,
        "evidence": evidence,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "resolved_at": None,
        "resolution": None,
        "resolution_evidence": None,
    }
    findings.append(item)
    write_json(findings_path(round_dir), findings)
    return item


def resolve_finding(
    round_dir: Path,
    finding_id: str,
    *,
    resolution: str,
    evidence: str,
    later_artifact: Path | str | None = None,
    later_round: Path | str | None = None,
    user_accepted: bool = False,
) -> dict[str, Any]:
    findings = load_findings(round_dir)
    manifest = load_json(round_dir / "manifest.json", {})
    current_source = manifest.get("source") if isinstance(manifest, dict) else None

    for item in findings:
        if item.get("id") == finding_id:
            resolved_artifact: dict[str, Any] | None = None
            outcome = "user-accepted" if user_accepted else "fixed-in-later-render"

            if later_round is not None:
                lr_path = Path(later_round)
                lr_manifest = load_json(lr_path / "manifest.json", {})
                if not isinstance(lr_manifest, dict) or not lr_manifest.get("source"):
                    raise ValueError(f"Invalid later round manifest at {lr_path}")
                lr_source_path = Path(str(lr_manifest["source"].get("path", "")))
                if lr_source_path.suffix.lower() not in VALID_VIDEO_EXTENSIONS:
                    raise ValueError(f"Later round source must be a video file ({lr_source_path.name})")
                lr_created = lr_manifest.get("created_at")
                manifest_created = manifest.get("created_at")
                if lr_created and manifest_created:
                    try:
                        if datetime.fromisoformat(lr_created) <= datetime.fromisoformat(manifest_created):
                            raise ValueError("Later round must be chronologically after the current review round")
                    except ValueError as val_err:
                        if "chronologically" in str(val_err):
                            raise
                resolved_artifact = dict(lr_manifest["source"])
                outcome = "fixed-in-later-round"
            elif later_artifact is not None:
                art_path = Path(later_artifact).resolve()
                if not art_path.is_file():
                    raise ValueError(f"Later artifact file not found: {art_path}")
                if art_path.suffix.lower() not in VALID_VIDEO_EXTENSIONS:
                    raise ValueError(f"Later artifact must be a video file ({art_path.name})")
                stat = art_path.stat()
                if current_source and isinstance(current_source, dict):
                    source_mtime = current_source.get("mtime_ns")
                    if source_mtime is not None and stat.st_mtime_ns < int(source_mtime):
                        raise ValueError("Later artifact must be modified at or after the reviewed source artifact")
                resolved_artifact = {
                    "path": str(art_path),
                    "size_bytes": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                }
                outcome = "fixed-in-later-artifact"

            if item.get("severity") == "hard":
                if outcome != "user-accepted":
                    if not resolved_artifact:
                        raise ValueError(
                            "Hard visual findings must reference and fingerprint a later round/artifact "
                            "(--later-artifact / --later-round) or record explicit user acceptance (--user-accepted)"
                        )
                    if current_source and (
                        resolved_artifact.get("path") == current_source.get("path")
                        and resolved_artifact.get("size_bytes") == current_source.get("size_bytes")
                        and resolved_artifact.get("mtime_ns") == current_source.get("mtime_ns")
                    ):
                        raise ValueError(
                            "Hard visual finding cannot be resolved while reviewed source artifact is unchanged"
                        )

            item["status"] = "resolved"
            item["resolved_at"] = datetime.now(timezone.utc).isoformat()
            item["resolution"] = resolution
            item["resolution_evidence"] = evidence
            item["resolution_outcome"] = outcome
            item["resolved_artifact"] = resolved_artifact
            write_json(findings_path(round_dir), findings)
            return item
    raise ValueError(f"Unknown finding id: {finding_id}")


def attest(
    round_dir: Path,
    *,
    watched_with_audio: bool,
    watched_muted: bool,
    first_second_inspected: bool,
    transitions_inspected: bool,
    ending_inspected: bool,
    reference_compared: bool,
    strict_signals_inspected: bool,
    machine_findings_inspected: bool = False,
) -> dict[str, Any]:
    state = {
        "watched_with_audio": watched_with_audio,
        "watched_muted": watched_muted,
        "first_second_inspected": first_second_inspected,
        "transitions_inspected": transitions_inspected,
        "ending_inspected": ending_inspected,
        "reference_compared": reference_compared,
        "strict_signals_inspected": strict_signals_inspected,
        "machine_findings_inspected": machine_findings_inspected,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(state_path(round_dir), state)
    return state


def accept_machine_finding(
    round_dir: Path,
    code: str,
    *,
    reason: str,
) -> dict[str, Any]:
    state = load_json(state_path(round_dir), {})
    if not isinstance(state, dict):
        state = {}
    accepted = state.get("accepted_machine_findings")
    if not isinstance(accepted, list):
        accepted = []

    findings_file = round_dir / "findings.json"
    if findings_file.is_file():
        machine_findings = load_json(findings_file, [])
        valid_codes = {
            item.get("code") for item in machine_findings
            if isinstance(item, dict) and item.get("code")
        }
        if valid_codes and code not in valid_codes:
            raise ValueError(f"Unknown machine finding code: {code}")

    if not any(isinstance(e, dict) and e.get("code") == code for e in accepted):
        accepted.append({
            "code": code,
            "reason": reason,
            "accepted_at": datetime.now(timezone.utc).isoformat(),
        })
    state["accepted_machine_findings"] = accepted
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    write_json(state_path(round_dir), state)
    return state


def artifact_matches_manifest(artifact: Any) -> bool:
    if artifact is None:
        return True
    if isinstance(artifact, str):
        raw_path = artifact.strip()
        if not raw_path:
            return True
        return Path(raw_path).is_file()
    if not isinstance(artifact, dict):
        return False

    raw_path = str(artifact.get("path", "")).strip()
    if not raw_path:
        return False

    path = Path(raw_path)
    if not path.is_file():
        return False

    stat = path.stat()
    return (
        stat.st_size == int(artifact.get("size_bytes", -1))
        and stat.st_mtime_ns == int(artifact.get("mtime_ns", -1))
    )


def source_matches_manifest(manifest: dict[str, Any]) -> bool:
    return artifact_matches_manifest(manifest.get("source"))


def reference_matches_manifest(manifest: dict[str, Any]) -> bool:
    return artifact_matches_manifest(manifest.get("reference"))


def reference_contract_matches_manifest(manifest: dict[str, Any]) -> bool:
    return artifact_matches_manifest(manifest.get("reference_contract"))


def strict_signal_evidence_valid(
    round_dir: Path,
    manifest: dict[str, Any],
) -> bool:
    path = round_dir / "strict-signals.json"
    if not path.is_file():
        return False

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    if data.get("status") != "pass":
        return False

    frames_analyzed = data.get("frames_analyzed")
    if not isinstance(frames_analyzed, int) or frames_analyzed <= 0:
        return False

    manifest_source = manifest.get("source")
    signal_source = data.get("source_manifest")
    if not isinstance(manifest_source, dict):
        return False
    if not isinstance(signal_source, dict):
        return False

    for key in ("path", "size_bytes", "mtime_ns"):
        if signal_source.get(key) != manifest_source.get(key):
            return False

    source_path = str(data.get("source", "")).strip()
    return source_path == str(manifest_source.get("path", "")).strip()


def is_finding_resolved(
    item: dict[str, Any],
    current_source: dict[str, Any] | None,
) -> bool:
    if item.get("status") != "resolved":
        return False
    if item.get("severity") != "hard":
        return True
    if item.get("resolution_outcome") == "user-accepted":
        return True
    artifact = item.get("resolved_artifact")
    if not artifact or not isinstance(artifact, dict):
        return False
    if not artifact_matches_manifest(artifact):
        return False
    art_path = Path(str(artifact.get("path", "")))
    if art_path.suffix.lower() not in VALID_VIDEO_EXTENSIONS:
        return False
    if current_source and (
        artifact.get("path") == current_source.get("path")
        and artifact.get("size_bytes") == current_source.get("size_bytes")
        and artifact.get("mtime_ns") == current_source.get("mtime_ns")
    ):
        return False
    if current_source and int(artifact.get("mtime_ns", 0)) < int(current_source.get("mtime_ns", 0)):
        return False
    return True


def round_status(round_dir: Path) -> dict[str, Any]:
    manifest = load_json(round_dir / "manifest.json", {})
    findings = load_findings(round_dir)
    state = load_json(state_path(round_dir), {})
    if not isinstance(state, dict):
        state = {}

    current_source = (
        manifest.get("source") if isinstance(manifest, dict) else None
    )
    pending = [
        item for item in findings
        if not is_finding_resolved(item, current_source)
    ]
    pending_hard = [item for item in pending if item.get("severity") == "hard"]

    finding_counts = manifest.get("finding_counts") if isinstance(manifest, dict) else {}
    warning_count = int((finding_counts or {}).get("warning", 0))
    raw_hard_count = int((finding_counts or {}).get("hard", 0))
    has_machine_findings = warning_count > 0 or raw_hard_count > 0

    findings_file = round_dir / "findings.json"
    if findings_file.is_file():
        m_findings = load_json(findings_file, [])
        if isinstance(m_findings, list) and m_findings:
            has_machine_findings = True

    required_attestations = list(REQUIRED_ATTESTATIONS)
    if isinstance(manifest, dict) and manifest.get("reference"):
        required_attestations.append("reference_compared")
    if has_machine_findings:
        required_attestations.append("machine_findings_inspected")

    missing_attestations = [
        key for key in required_attestations if not bool(state.get(key, False))
    ]

    source_changed = (
        not source_matches_manifest(manifest)
        if isinstance(manifest, dict)
        else True
    )
    reference_changed = (
        not reference_matches_manifest(manifest)
        if isinstance(manifest, dict)
        else True
    )
    contract_changed = (
        not reference_contract_matches_manifest(manifest)
        if isinstance(manifest, dict)
        else True
    )

    strict_signal_path = round_dir / "strict-signals.json"
    missing_evidence: list[str] = []
    if not strict_signal_path.exists():
        missing_evidence.append("strict-signals.json")
    elif not strict_signal_evidence_valid(round_dir, manifest):
        missing_evidence.append("strict-signals.json:invalid")

    accepted_entries = state.get("accepted_machine_findings", [])
    accepted_codes = {
        entry.get("code") for entry in accepted_entries
        if isinstance(entry, dict) and entry.get("code")
    }

    findings_file = round_dir / "findings.json"
    machine_hard = 0
    if findings_file.is_file():
        machine_findings = load_json(findings_file, [])
        if isinstance(machine_findings, list):
            machine_hard = sum(
                1 for item in machine_findings
                if isinstance(item, dict)
                and item.get("severity") == "hard"
                and item.get("code") not in accepted_codes
            )
    else:
        total_manifest_hard = int(
            (manifest.get("finding_counts") or {}).get("hard", 0)
            if isinstance(manifest, dict)
            else 0
        )
        machine_hard = max(0, total_manifest_hard - len(accepted_codes))

    status = "review-complete"
    if source_changed:
        status = "source-artifact-changed"
    elif reference_changed:
        status = "reference-artifact-changed"
    elif contract_changed:
        status = "reference-contract-changed"
    elif machine_hard:
        status = "blocked-machine-hard-findings"
    elif pending_hard:
        status = "blocked-visual-hard-findings"
    elif missing_attestations or missing_evidence:
        status = "agent-review-required"

    return {
        "status": status,
        "pending_count": len(pending),
        "pending_hard_count": len(pending_hard),
        "machine_hard_count": machine_hard,
        "accepted_machine_findings": sorted(accepted_codes),
        "missing_attestations": missing_attestations,
        "missing_evidence": missing_evidence,
        "source_changed": source_changed,
        "reference_changed": reference_changed,
        "reference_contract_changed": contract_changed,
        "reference_compared": bool(state.get("reference_compared", False)),
        "strict_signals_inspected": bool(
            state.get("strict_signals_inspected", False)
        ),
        "machine_findings_inspected": bool(
            state.get("machine_findings_inspected", False)
        ),
        "pending": pending,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage timecoded motion-review findings"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add")
    add.add_argument("round_dir", type=Path)
    add.add_argument("--time", required=True)
    add.add_argument(
        "--severity",
        choices=["hard", "warning", "review"],
        required=True,
    )
    add.add_argument("--defect", required=True)
    add.add_argument("--fix", required=True)
    add.add_argument("--evidence", required=True)

    resolve = sub.add_parser("resolve")
    resolve.add_argument("round_dir", type=Path)
    resolve.add_argument("--id", required=True)
    resolve.add_argument("--resolution", required=True)
    resolve.add_argument("--evidence", required=True)
    resolve.add_argument(
        "--later-artifact",
        type=Path,
        default=None,
        help="path to later rendered video artifact",
    )
    resolve.add_argument(
        "--later-round",
        type=Path,
        default=None,
        help="path to later review round directory",
    )
    resolve.add_argument(
        "--user-accepted",
        action="store_true",
        help="explicitly record user acceptance of the defect",
    )

    pending = sub.add_parser("pending")
    pending.add_argument("round_dir", type=Path)

    attest_parser = sub.add_parser("attest")
    attest_parser.add_argument("round_dir", type=Path)
    attest_parser.add_argument("--watched-with-audio", action="store_true")
    attest_parser.add_argument("--watched-muted", action="store_true")
    attest_parser.add_argument("--first-second-inspected", action="store_true")
    attest_parser.add_argument("--transitions-inspected", action="store_true")
    attest_parser.add_argument("--ending-inspected", action="store_true")
    attest_parser.add_argument("--reference-compared", action="store_true")
    attest_parser.add_argument(
        "--strict-signals-inspected",
        action="store_true",
    )
    attest_parser.add_argument(
        "--machine-findings-inspected",
        action="store_true",
    )

    status = sub.add_parser("status")
    status.add_argument("round_dir", type=Path)

    accept_m = sub.add_parser("accept-machine")
    accept_m.add_argument("round_dir", type=Path)
    accept_m.add_argument("--code", required=True)
    accept_m.add_argument("--reason", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        ensure_round(args.round_dir)
        if args.command == "add":
            result = add_finding(
                args.round_dir,
                timestamp=args.time,
                severity=args.severity,
                defect=args.defect,
                fix=args.fix,
                evidence=args.evidence,
            )
        elif args.command == "resolve":
            result = resolve_finding(
                args.round_dir,
                args.id,
                resolution=args.resolution,
                evidence=args.evidence,
                later_artifact=args.later_artifact,
                later_round=args.later_round,
                user_accepted=args.user_accepted,
            )
        elif args.command == "accept-machine":
            result = accept_machine_finding(
                args.round_dir,
                args.code,
                reason=args.reason,
            )
        elif args.command == "pending":
            manifest = load_json(args.round_dir / "manifest.json", {})
            current_source = (
                manifest.get("source") if isinstance(manifest, dict) else None
            )
            result = {
                "pending": [
                    item for item in load_findings(args.round_dir)
                    if not is_finding_resolved(item, current_source)
                ]
            }
        elif args.command == "attest":
            result = attest(
                args.round_dir,
                watched_with_audio=args.watched_with_audio,
                watched_muted=args.watched_muted,
                first_second_inspected=args.first_second_inspected,
                transitions_inspected=args.transitions_inspected,
                ending_inspected=args.ending_inspected,
                reference_compared=args.reference_compared,
                strict_signals_inspected=args.strict_signals_inspected,
                machine_findings_inspected=args.machine_findings_inspected,
            )
        else:
            result = round_status(args.round_dir)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps(
            {"status": "blocked", "error": str(exc)},
            ensure_ascii=False,
            indent=2,
        ))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == "status" and result.get("status") != "review-complete":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

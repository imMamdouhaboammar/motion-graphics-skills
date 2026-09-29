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
REQUIRED_ATTESTATIONS = (
    "watched_with_audio",
    "watched_muted",
    "first_second_inspected",
    "transitions_inspected",
    "ending_inspected",
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
) -> dict[str, Any]:
    findings = load_findings(round_dir)
    for item in findings:
        if item.get("id") == finding_id:
            item["status"] = "resolved"
            item["resolved_at"] = datetime.now(timezone.utc).isoformat()
            item["resolution"] = resolution
            item["resolution_evidence"] = evidence
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
) -> dict[str, Any]:
    state = {
        "watched_with_audio": watched_with_audio,
        "watched_muted": watched_muted,
        "first_second_inspected": first_second_inspected,
        "transitions_inspected": transitions_inspected,
        "ending_inspected": ending_inspected,
        "reference_compared": reference_compared,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(state_path(round_dir), state)
    return state


def round_status(round_dir: Path) -> dict[str, Any]:
    manifest = load_json(round_dir / "manifest.json", {})
    findings = load_findings(round_dir)
    state = load_json(state_path(round_dir), {})
    if not isinstance(state, dict):
        state = {}

    pending = [item for item in findings if item.get("status") != "resolved"]
    pending_hard = [item for item in pending if item.get("severity") == "hard"]
    missing_attestations = [
        key for key in REQUIRED_ATTESTATIONS if not bool(state.get(key, False))
    ]

    machine_hard = int(
        (manifest.get("finding_counts") or {}).get("hard", 0)
        if isinstance(manifest, dict)
        else 0
    )

    status = "review-complete"
    if machine_hard:
        status = "blocked-machine-hard-findings"
    elif pending_hard:
        status = "blocked-visual-hard-findings"
    elif missing_attestations:
        status = "agent-review-required"

    return {
        "status": status,
        "pending_count": len(pending),
        "pending_hard_count": len(pending_hard),
        "machine_hard_count": machine_hard,
        "missing_attestations": missing_attestations,
        "reference_compared": bool(state.get("reference_compared", False)),
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

    status = sub.add_parser("status")
    status.add_argument("round_dir", type=Path)
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
            )
        elif args.command == "pending":
            result = {
                "pending": [
                    item for item in load_findings(args.round_dir)
                    if item.get("status") != "resolved"
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

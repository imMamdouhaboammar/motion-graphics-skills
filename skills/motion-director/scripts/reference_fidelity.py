#!/usr/bin/env python3
"""Validate structural reference fidelity and difficulty-preservation contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_SIGNATURE = (
    "rhythm",
    "composition",
    "typography",
    "transitions",
    "density",
    "material",
)

VAGUE_TERMS = {
    "fast",
    "cool",
    "bold",
    "dynamic",
    "premium",
    "cinematic",
    "modern",
    "clean",
    "creative",
    "edgy",
}


def load_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def is_specific(value: Any) -> bool:
    text = str(value or "").strip().lower()
    if not text:
        return False
    words = [word.strip(".,:;()[]{}") for word in text.split()]
    if len(words) < 5:
        return False
    if len(words) <= 8 and all(word in VAGUE_TERMS for word in words):
        return False
    if text in VAGUE_TERMS:
        return False
    return True


def validate_contract(contract: dict[str, Any]) -> dict[str, Any]:
    missing: list[str] = []
    issues: list[str] = []

    mode = str(contract.get("mode", "")).strip()
    difficulty_mode = str(contract.get("difficulty_mode", "")).strip()

    if mode not in {"structural-fidelity", "translation", "inspiration", "mix"}:
        missing.append("mode")

    reference = contract.get("reference")
    if not isinstance(reference, dict) or not str(reference.get("source", "")).strip():
        missing.append("reference.source")

    signature = contract.get("signature")
    if not isinstance(signature, dict):
        signature = {}
    for key in REQUIRED_SIGNATURE:
        value = signature.get(key)
        if not value:
            missing.append(f"signature.{key}")
        elif not is_specific(value):
            issues.append(f"signature.{key} is too vague to enforce")

    preserve = contract.get("must_preserve")
    if not isinstance(preserve, list):
        preserve = []
    valid_preserve: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(preserve):
        if not isinstance(item, dict):
            issues.append(f"must_preserve[{index}] must be an object")
            continue
        contract_id = str(item.get("id", "")).strip()
        mechanism = str(item.get("mechanism", "")).strip()
        why_hard = str(item.get("why_hard", "")).strip()
        evidence = str(item.get("evidence", "")).strip()
        if not contract_id:
            issues.append(f"must_preserve[{index}].id is required")
            continue
        if contract_id in seen_ids:
            issues.append(f"duplicate must_preserve id: {contract_id}")
            continue
        seen_ids.add(contract_id)
        if not is_specific(mechanism):
            issues.append(f"must_preserve[{index}].mechanism is too vague")
        if difficulty_mode == "preserve" and not is_specific(why_hard):
            issues.append(f"must_preserve[{index}].why_hard is required in preserve mode")
        if not evidence:
            issues.append(f"must_preserve[{index}].evidence is required")
        valid_preserve.append(item)

    if mode == "structural-fidelity" and len(valid_preserve) < 2:
        missing.append("must_preserve>=2")
    if difficulty_mode == "preserve" and len(valid_preserve) < 2:
        if "must_preserve>=2" not in missing:
            missing.append("must_preserve>=2")

    shortcuts = contract.get("forbidden_shortcuts")
    if difficulty_mode == "preserve":
        if not isinstance(shortcuts, list) or len([x for x in shortcuts if str(x).strip()]) < 1:
            missing.append("forbidden_shortcuts>=1")

    translate = contract.get("may_translate")
    if mode in {"structural-fidelity", "translation"} and not isinstance(translate, list):
        missing.append("may_translate")

    return {
        "status": "pass" if not missing and not issues else "fail",
        "mode": mode,
        "difficulty_mode": difficulty_mode,
        "contract_ids": sorted(seen_ids),
        "missing": missing,
        "issues": issues,
    }


def validate_plan(
    contract_result: dict[str, Any],
    plan: dict[str, Any],
) -> dict[str, Any]:
    implementations = plan.get("implementations")
    if not isinstance(implementations, list):
        implementations = []

    mapped: set[str] = set()
    issues: list[str] = []
    for index, item in enumerate(implementations):
        if not isinstance(item, dict):
            issues.append(f"implementations[{index}] must be an object")
            continue
        contract_id = str(item.get("contract_id", "")).strip()
        implementation = str(item.get("implementation", "")).strip()
        verification = str(item.get("verification", "")).strip()
        if not contract_id:
            issues.append(f"implementations[{index}].contract_id is required")
            continue
        if not is_specific(implementation):
            issues.append(f"implementation for {contract_id} is too vague")
        if not verification:
            issues.append(f"verification for {contract_id} is required")
        mapped.add(contract_id)

    expected = set(contract_result["contract_ids"])
    unmapped = sorted(expected - mapped)
    unknown = sorted(mapped - expected)

    return {
        "mapped_contract_ids": sorted(mapped & expected),
        "unmapped_contract_ids": unmapped,
        "unknown_contract_ids": unknown,
        "plan_issues": issues,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a structural reference fidelity contract",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("contract", type=Path)
    validate.add_argument("--plan", type=Path)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        contract = load_object(args.contract)
        result = validate_contract(contract)
        if args.plan is not None:
            plan = load_object(args.plan)
            plan_result = validate_plan(result, plan)
            result.update(plan_result)
            if (
                plan_result["unmapped_contract_ids"]
                or plan_result["unknown_contract_ids"]
                or plan_result["plan_issues"]
            ):
                result["status"] = "fail"
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 3


if __name__ == "__main__":
    raise SystemExit(main())

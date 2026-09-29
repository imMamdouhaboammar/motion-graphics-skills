#!/usr/bin/env python3
"""Validate structural reference fidelity and difficulty-preservation contracts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


STOP_WORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of", "with",
    "by", "as", "is", "are", "between", "across", "into", "through", "from",
    "each", "all", "both", "neither", "either", "than", "rather", "plus",
    "world", "worlds", "scenes", "scene", "system", "systems", "visual",
    "style", "direction", "most", "every"
}


def extract_keywords(text: str) -> set[str]:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", " ", str(text or "").lower())
    return {t for t in cleaned.split() if len(t) > 2 and t not in STOP_WORDS}


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
    if not difficulty_mode:
        missing.append("difficulty_mode")
    elif difficulty_mode not in {"normal", "preserve"}:
        issues.append(
            f"unsupported difficulty_mode: {difficulty_mode}"
        )

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
        if difficulty_mode == "preserve" and len(why_hard.split()) < 3:
            issues.append(f"must_preserve[{index}].why_hard is required in preserve mode")
        if not evidence:
            issues.append(f"must_preserve[{index}].evidence is required")
        valid_preserve.append(item)

    if mode == "structural-fidelity" and len(valid_preserve) < 2:
        missing.append("must_preserve>=2")
    if difficulty_mode == "preserve" and len(valid_preserve) < 2:
        if "must_preserve>=2" not in missing:
            missing.append("must_preserve>=2")

    dominant_language = str(contract.get("dominant_language", "")).strip()
    secondary_motifs = contract.get("secondary_motifs")
    if not isinstance(secondary_motifs, list):
        secondary_motifs = []
    secondary_motifs = [
        str(item).strip()
        for item in secondary_motifs
        if str(item).strip()
    ]

    shortcuts = contract.get("forbidden_shortcuts")
    if difficulty_mode == "preserve":
        if not isinstance(shortcuts, list) or len([x for x in shortcuts if str(x).strip()]) < 1:
            missing.append("forbidden_shortcuts>=1")
        if not dominant_language:
            missing.append("dominant_language")
        elif not is_specific(dominant_language):
            issues.append("dominant_language is too vague to enforce")
        if not secondary_motifs:
            missing.append("secondary_motifs>=1")

    translate = contract.get("may_translate")
    if mode in {"structural-fidelity", "translation"} and not isinstance(translate, list):
        missing.append("may_translate")

    return {
        "status": "pass" if not missing and not issues else "fail",
        "mode": mode,
        "difficulty_mode": difficulty_mode,
        "contract_ids": sorted(seen_ids),
        "dominant_language": dominant_language,
        "secondary_motifs": secondary_motifs,
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

    direction_unmapped: list[str] = []
    salience_inversions: list[str] = []
    unapproved_style_expansions: list[str] = []

    if contract_result.get("difficulty_mode") == "preserve":
        visual_direction = plan.get("visual_direction")
        if not isinstance(visual_direction, dict):
            issues.append("visual_direction is required in preserve mode")
        else:
            approved_expansion = bool(
                visual_direction.get("user_approved_style_expansion", False)
            )
            direction_language = str(
                visual_direction.get("dominant_language", "")
            ).strip()
            if not is_specific(direction_language):
                issues.append(
                    "visual_direction.dominant_language is too vague"
                )
            else:
                contract_dominant = str(contract_result.get("dominant_language", "")).strip()
                contract_keywords = extract_keywords(contract_dominant)
                direction_keywords = extract_keywords(direction_language)
                token_overlap = contract_keywords & direction_keywords

                if contract_dominant and not approved_expansion and not token_overlap:
                    issues.append(
                        f"visual_direction.dominant_language does not bind to or preserve contract dominant language: '{contract_dominant}'"
                    )

                secondary_tokens: set[str] = set()
                for motif in contract_result.get("secondary_motifs", []):
                    for tok in extract_keywords(str(motif)):
                        if tok not in contract_keywords:
                            secondary_tokens.add(tok)

                if not approved_expansion:
                    for tok in secondary_tokens:
                        if tok in direction_keywords:
                            salience_inversions.append(
                                f"dominant_language incorporates secondary motif '{tok}'"
                            )

            preserves = visual_direction.get("preserves")
            if not isinstance(preserves, list):
                preserves = []
            preserves_set = {
                str(item).strip()
                for item in preserves
                if str(item).strip()
            }
            direction_unmapped = sorted(expected - preserves_set)

            promoted = visual_direction.get("promoted_secondary_motifs")
            if not isinstance(promoted, list):
                issues.append(
                    "visual_direction.promoted_secondary_motifs must be a list"
                )
                promoted = []
            promoted_clean = [
                str(item).strip()
                for item in promoted
                if str(item).strip()
            ]

            secondary = {
                str(item).strip().lower()
                for item in contract_result.get("secondary_motifs", [])
                if str(item).strip()
            }
            for item in promoted_clean:
                if item.lower() in secondary:
                    salience_inversions.append(item)
                else:
                    salience_inversions.append(item)

            new_dominant = visual_direction.get("new_dominant_motifs")
            if not isinstance(new_dominant, list):
                issues.append(
                    "visual_direction.new_dominant_motifs must be a list"
                )
                new_dominant = []
            new_dominant_clean = [
                str(item).strip()
                for item in new_dominant
                if str(item).strip()
            ]
            if new_dominant_clean and not approved_expansion:
                unapproved_style_expansions.extend(new_dominant_clean)

    return {
        "mapped_contract_ids": sorted(mapped & expected),
        "unmapped_contract_ids": unmapped,
        "unknown_contract_ids": unknown,
        "direction_unmapped_contract_ids": direction_unmapped,
        "salience_inversions": salience_inversions,
        "unapproved_style_expansions": unapproved_style_expansions,
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
                or plan_result["direction_unmapped_contract_ids"]
                or plan_result["salience_inversions"]
                or plan_result["unapproved_style_expansions"]
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

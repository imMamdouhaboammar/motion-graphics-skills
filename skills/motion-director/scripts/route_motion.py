#!/usr/bin/env python3
"""Compose an inspectable motion-production route from task context.

The router is deterministic. Claude supplies semantic task classification,
the router validates installed capabilities and returns ordered handoffs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SPECIALISTS = {
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


RETURN_CONTRACTS = {
    "motion-director": [
        "shared truth",
        "route state",
        "approved constraints",
    ],
    "reference-fidelity": [
        "validated reference contract",
        "difficulty-preservation requirements",
        "forbidden substitutions",
    ],
    "brand-intake": [
        "brand.md",
        "MOTION.md",
        "verified identity constraints",
    ],
    "mix-and-match": [
        "selected concept direction",
        "creative distance audit",
        "mix-brief.md",
    ],
    "motion-brief-writer": [
        "approved motion brief",
        "production constraints",
        "open risks",
    ],
    "gpu-policy": [
        "selected hardware backend",
        "backend evidence",
        "execution hints",
    ],
    "work-guard": [
        "run evidence",
        "failure classification",
        "recovery result",
    ],
    "video-review-loop": [
        "timecoded findings",
        "machine evidence",
        "review status",
    ],
}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def discover_nodes(pack_root: Path, network: dict[str, Any]) -> dict[str, bool]:
    availability: dict[str, bool] = {}
    for node in network.get("nodes", []):
        if not isinstance(node, dict) or not node.get("name") or not node.get("path"):
            continue
        availability[str(node["name"])] = (pack_root / str(node["path"])).exists()
    return availability


def edge_map(network: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for edge in network.get("edges", []):
        if not isinstance(edge, dict):
            continue
        source = str(edge.get("from", ""))
        target = str(edge.get("to", ""))
        if source and target:
            result[(source, target)] = edge
    return result


def specialist_returns(name: str) -> list[str]:
    if name in RETURN_CONTRACTS:
        return RETURN_CONTRACTS[name]
    return [
        "specialist decisions",
        "created or updated artifacts",
        "risks and unresolved constraints",
    ]


def handoff_for(
    name: str,
    *,
    reason: str,
    edges: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any]:
    if name == "motion-director":
        return {
            "from": "user",
            "to": "motion-director",
            "purpose": reason,
            "inherits": ["user brief", "supplied assets", "known project truth"],
            "must_return": specialist_returns(name),
            "return_to": None,
        }

    edge = edges.get(("motion-director", name), {})
    return {
        "from": "motion-director",
        "to": name,
        "purpose": reason,
        "inherits": list(edge.get("passes", ["shared truth", "approved constraints"])),
        "must_return": specialist_returns(name),
        "return_to": edge.get("returns", "motion-director"),
    }


def build_route(
    context: dict[str, Any],
    network: dict[str, Any],
    availability: dict[str, bool],
) -> dict[str, Any]:
    edges = edge_map(network)
    stages: list[dict[str, Any]] = []
    skipped_optional: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[dict[str, str]] = []
    required_references: list[str] = []

    def add_stage(name: str, reason: str, *, required: bool = True) -> None:
        if any(stage["name"] == name for stage in stages):
            return
        available = availability.get(name, False)
        if not available:
            node = next(
                (item for item in network.get("nodes", []) if item.get("name") == name),
                {},
            )
            optional = bool(node.get("optional", False))
            if optional or not required:
                skipped_optional.append({
                    "name": name,
                    "reason": f"{reason}. Capability is not installed",
                })
                return
            blockers.append({
                "name": name,
                "reason": f"{reason}. Required capability is not installed",
            })
            warnings.append(
                f"{name} is required for this route and is not installed; production must stop or the task must be reclassified"
            )
            return
        stages.append({
            "name": name,
            "reason": reason,
            "handoff": handoff_for(name, reason=reason, edges=edges),
        })

    add_stage(
        "motion-director",
        "Own the shared brief, route, creative direction, production state, and final decision gates",
    )

    brand_ready = bool(context.get("brand_ready", True))
    if not brand_ready:
        add_stage(
            "brand-intake",
            "Brand truth is incomplete and must be established before creative specialization",
        )

    reference_count = int(context.get("reference_count", 0) or 0)
    mix_references = bool(context.get("mix_references", False))
    reference_mode = str(context.get("reference_mode", "inspiration"))
    difficulty_mode = str(context.get("difficulty_mode", "normal"))

    supported_reference_modes = {
        "structural-fidelity",
        "translation",
        "inspiration",
        "mix",
    }
    supported_difficulty_modes = {"normal", "preserve"}
    invalid_modes: list[str] = []
    if reference_mode not in supported_reference_modes:
        invalid_modes.append(f"reference_mode={reference_mode!r}")
    if difficulty_mode not in supported_difficulty_modes:
        invalid_modes.append(f"difficulty_mode={difficulty_mode!r}")
    if invalid_modes:
        blockers.append({
            "name": "routing-context",
            "reason": (
                "Unsupported routing mode(s): "
                + ", ".join(invalid_modes)
                + ". Production must stop until the task context is corrected"
            ),
        })
        return {
            "version": 1,
            "status": "blocked",
            "entry": "motion-director",
            "deliverable": str(context.get("deliverable", "broad-film")),
            "installed": sorted(
                name for name, present in availability.items() if present
            ),
            "stages": stages,
            "required_references": sorted(set(required_references)),
            "constraints": {
                "reference_mode": reference_mode,
                "difficulty_preservation": False,
            },
            "skipped_optional": skipped_optional,
            "blockers": blockers,
            "warnings": warnings,
        }

    difficulty_preservation = difficulty_mode == "preserve"

    if (
        reference_count >= 1
        and (reference_mode == "structural-fidelity" or difficulty_preservation)
    ):
        add_stage(
            "reference-fidelity",
            "Reference fidelity is a production constraint, so signature mechanics and difficulty must be locked before specialization",
        )
    if reference_count >= 2 and mix_references:
        add_stage(
            "mix-and-match",
            "Multiple references must be recombined into an original direction before production",
            required=False,
        )
        if not availability.get("mix-and-match", False):
            warnings.append(
                "mix-and-match is unavailable. Use motion-director reference analysis and creative-distance rules"
            )

    deliverable = str(context.get("deliverable", "broad-film"))
    review_only = bool(context.get("review_only", False))
    if not review_only:
        specialist = SPECIALISTS.get(deliverable)
        if specialist:
            add_stage(
                specialist,
                f"Deliverable class '{deliverable}' maps to the dedicated {specialist} specialist",
            )

    language = str(context.get("language", "")).lower()
    if language in {"ar", "arabic", "rtl"}:
        required_references.append("skills/motion-director/references/arabic-motion.md")

    if bool(context.get("heavy_media", False)):
        add_stage(
            "gpu-policy",
            "Heavy media work must prove a hardware-accelerated path before execution",
        )

    if bool(context.get("hang_prone", False)):
        add_stage(
            "work-guard",
            "Hang-prone execution should run behind the installed reliability guard",
            required=False,
        )
        if not availability.get("work-guard", False):
            warnings.append(
                "work-guard is unavailable. Use bounded commands with explicit timeout and preserved evidence"
            )

    if bool(context.get("final_video", False)) or review_only:
        add_stage(
            "video-review-loop",
            "A rendered video exists and final signoff requires evidence-based motion review",
        )

    return {
        "version": 1,
        "status": "blocked" if blockers else "ready",
        "entry": "motion-director",
        "deliverable": deliverable,
        "installed": sorted(name for name, present in availability.items() if present),
        "stages": stages,
        "required_references": sorted(set(required_references)),
        "constraints": {
            "reference_mode": reference_mode,
            "difficulty_preservation": difficulty_preservation,
        },
        "skipped_optional": skipped_optional,
        "blockers": blockers,
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    default_root = Path(__file__).resolve().parents[3]
    default_network = Path(__file__).resolve().parent.parent / "router" / "skill-network.json"

    parser = argparse.ArgumentParser(description="Build an inspectable motion-skill route")
    parser.add_argument("--context", required=True, type=Path, help="JSON task context")
    parser.add_argument("--pack-root", type=Path, default=default_root, help="motion-graphics-skills root")
    parser.add_argument("--network", type=Path, default=default_network, help="skill network JSON")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        context = load_json(args.context)
        network = load_json(args.network)
        availability = discover_nodes(args.pack_root, network)
        result = build_route(context, network, availability)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 3 if result.get("status") == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())

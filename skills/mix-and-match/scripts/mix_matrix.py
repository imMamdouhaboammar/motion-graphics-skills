#!/usr/bin/env python3
"""Create source-balanced creative gene recipes from a reference gene pool.

This helper does not judge originality or aesthetics. It only gives an agent
several deterministic cross-reference scaffolds and flags source dominance.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

DEFAULT_CATEGORIES = [
    "metaphor",
    "structure",
    "rhythm",
    "composition",
    "typography",
    "image",
    "material",
    "motion",
    "transition",
    "spatial",
    "color",
    "sound",
]


def load_pool(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("gene pool root must be an object")
    refs = data.get("references")
    if not isinstance(refs, list) or len(refs) < 2:
        raise ValueError("gene pool needs at least two references")
    if any(not isinstance(ref, dict) for ref in refs):
        raise ValueError("reference entries must be objects")
    ids = [str(ref.get("id", "")).strip() for ref in refs]
    if any(not ref_id for ref_id in ids):
        raise ValueError("every reference needs a non-empty id")
    if len(ids) != len(set(ids)):
        raise ValueError("reference ids must be unique")
    return data


def normalize_genes(ref: dict) -> dict[str, list[str]]:
    genes = ref.get("genes", {})
    if not isinstance(genes, dict):
        return {}
    result: dict[str, list[str]] = {}
    for category, values in genes.items():
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, list):
            continue
        clean = [str(value).strip() for value in values if str(value).strip()]
        if clean:
            result[str(category)] = clean
    return result


def source_limit(slot_count: int, source_count: int) -> int:
    if source_count <= 2:
        return math.ceil(slot_count / 2)
    return max(1, math.floor(slot_count * 0.40))


def available_categories(refs: list[dict]) -> list[str]:
    seen = set()
    ordered = []
    for category in DEFAULT_CATEGORIES:
        if any(category in ref["_genes"] for ref in refs):
            ordered.append(category)
            seen.add(category)
    extras = sorted(
        {
            category
            for ref in refs
            for category in ref["_genes"]
            if category not in seen
        }
    )
    return ordered + extras


def find_assignment(
    refs: list[dict],
    categories: list[str],
    target_slots: int,
    rng: random.Random,
    max_per_source: int,
) -> list[tuple[str, dict]] | None:
    ordered_categories = sorted(categories)
    rng.shuffle(ordered_categories)
    source_ids = [ref["id"] for ref in refs]
    ref_by_id = {ref["id"]: ref for ref in refs}

    options: dict[str, list[str]] = {}
    for category in ordered_categories:
        source_options = [
            ref["id"] for ref in refs if category in ref["_genes"]
        ]
        rng.shuffle(source_options)
        options[category] = source_options

    counts: Counter = Counter()
    memo: set[tuple[int, int, tuple[int, ...]]] = set()

    def search(position: int, slots_left: int) -> list[tuple[str, str]] | None:
        if slots_left == 0:
            return []
        if len(ordered_categories) - position < slots_left:
            return None
        if (
            sum(max_per_source - counts[source_id] for source_id in source_ids)
            < slots_left
        ):
            return None

        state = (
            position,
            slots_left,
            tuple(counts[source_id] for source_id in source_ids),
        )
        if state in memo:
            return None
        memo.add(state)

        category = ordered_categories[position]
        for source_id in options[category]:
            if counts[source_id] >= max_per_source:
                continue
            counts[source_id] += 1
            rest = search(position + 1, slots_left - 1)
            counts[source_id] -= 1
            if rest is not None:
                return [(category, source_id), *rest]

        return search(position + 1, slots_left)

    assignment = search(0, target_slots)
    if assignment is None:
        return None
    return [
        (category, ref_by_id[source_id])
        for category, source_id in assignment
    ]


def build_recipe(refs: list[dict], categories: list[str], seed: int, index: int) -> dict:
    rng = random.Random(seed + index * 1009)
    target_slots = min(6, len(categories))
    if len(refs) <= 2 and target_slots > 2 and target_slots % 2:
        target_slots -= 1

    base_limit = source_limit(target_slots, len(refs))
    assignment = None
    used_limit = base_limit
    for candidate_limit in range(base_limit, target_slots + 1):
        assignment = find_assignment(
            refs,
            categories,
            target_slots,
            rng,
            candidate_limit,
        )
        if assignment is not None:
            used_limit = candidate_limit
            break

    slots = []
    counts: Counter = Counter()
    for category, source in assignment or []:
        gene = rng.choice(source["_genes"][category])
        counts[source["id"]] += 1
        slots.append(
            {
                "category": category,
                "source": source["id"],
                "role": source.get("role", "primary"),
                "domain": source.get("domain", "unknown"),
                "gene": gene,
            }
        )

    shares = {
        source_id: round(count / len(slots), 3)
        for source_id, count in counts.items()
        if slots
    }
    max_share = (
        max(counts.values(), default=0) / len(slots)
        if slots
        else 0.0
    )
    warnings = []
    if len(shares) < 2:
        warnings.append("recipe uses fewer than two sources")

    base_threshold = 0.50 if len(refs) <= 2 else 0.40
    achievable_threshold = used_limit / len(slots) if slots else base_threshold
    threshold = max(base_threshold, achievable_threshold)
    if max_share > threshold + 1e-9:
        warnings.append(
            f"source dominance {max_share:.0%} exceeds target {threshold:.0%}"
        )

    return {
        "id": f"recipe-{index + 1}",
        "slots": slots,
        "source_share": shares,
        "warnings": warnings,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("gene_pool", type=Path)
    parser.add_argument("--recipes", type=int, default=3)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    if args.recipes < 1 or args.recipes > 9:
        parser.error("--recipes must be between 1 and 9")

    try:
        data = load_pool(args.gene_pool)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    refs = []
    for raw in data["references"]:
        ref = dict(raw)
        ref["id"] = str(ref["id"])
        ref["_genes"] = normalize_genes(ref)
        refs.append(ref)

    categories = available_categories(refs)
    if len(categories) < 2:
        print("error: gene pool needs at least two usable gene categories", file=sys.stderr)
        return 2

    recipes = [
        build_recipe(refs, categories, args.seed, index)
        for index in range(args.recipes)
    ]

    output = {
        "brief": data.get("brief", ""),
        "recipe_count": len(recipes),
        "note": "Source spread is a dominance check, not an originality score.",
        "recipes": recipes,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

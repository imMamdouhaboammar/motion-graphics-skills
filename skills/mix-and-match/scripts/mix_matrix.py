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
    refs = data.get("references")
    if not isinstance(refs, list) or len(refs) < 2:
        raise ValueError("gene pool needs at least two references")
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


def build_recipe(refs: list[dict], categories: list[str], seed: int, index: int) -> dict:
    rng = random.Random(seed + index * 1009)
    target_slots = min(6, len(categories))
    if len(refs) <= 2 and target_slots > 2 and target_slots % 2:
        target_slots -= 1
    remaining = set(categories)
    counts: Counter = Counter()
    limit = source_limit(target_slots, len(refs))
    slots = []

    for _ in range(target_slots):
        eligible = [
            ref
            for ref in refs
            if any(category in ref["_genes"] for category in remaining)
        ]
        if not eligible:
            break

        under_limit = [ref for ref in eligible if counts[ref["id"]] < limit]
        pool = under_limit or eligible
        min_count = min(counts[ref["id"]] for ref in pool)
        pool = [ref for ref in pool if counts[ref["id"]] == min_count]
        rng.shuffle(pool)
        source = pool[0]

        source_categories = [
            category for category in remaining if category in source["_genes"]
        ]
        source_categories.sort()
        category = rng.choice(source_categories)
        remaining.remove(category)
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
    max_share = max(shares.values(), default=0.0)
    warnings = []
    if len(shares) < 2:
        warnings.append("recipe uses fewer than two sources")
    threshold = 0.50 if len(refs) <= 2 else 0.40
    if max_share > threshold:
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

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from pipeline_config import SIZE_ORDER


def sort_sizes(sizes: list[str]) -> list[str]:
    indexed = {size: idx for idx, size in enumerate(SIZE_ORDER)}

    def sort_key(size: str) -> tuple[int, str]:
        upper = size.upper()
        if upper.isdigit():
            return (int(upper), upper)
        if "/" in upper:
            left = upper.split("/", 1)[0]
            return (indexed.get(left, 999), upper)
        return (indexed.get(upper, 999), upper)

    return sorted((size.upper() for size in sizes), key=sort_key)


def series_width(stock_by_size: dict[str, int], ordered_sizes: list[str]) -> int:
    best = 0
    current = 0
    for size in ordered_sizes:
        if stock_by_size.get(size, 0) > 0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def active_size_count(stock_by_size: dict[str, int]) -> int:
    return sum(1 for qty in stock_by_size.values() if qty > 0)


def size_position(size: str, ordered_sizes: list[str]) -> str:
    if size not in ordered_sizes:
        return "unknown"
    idx = ordered_sizes.index(size)
    if idx == 0 or idx == len(ordered_sizes) - 1:
        return "edge"
    return "middle"


def would_break_sequence(stock_by_size: dict[str, int], ordered_sizes: list[str], size: str, qty: int) -> bool:
    if stock_by_size.get(size, 0) < qty:
        return True
    before = series_width(stock_by_size, ordered_sizes)
    after_inventory = dict(stock_by_size)
    after_inventory[size] = max(0, after_inventory.get(size, 0) - qty)
    after = series_width(after_inventory, ordered_sizes)
    return after < before and before >= 3


def candidate_qty_range(donor_stock: int, observed_qtys: set[int]) -> list[int]:
    max_qty = max(observed_qtys) if observed_qtys else 2
    feasible_max = max(0, donor_stock - 1)
    return list(range(1, min(max_qty, feasible_max) + 1))


def move_key(move: dict[str, Any]) -> tuple[str, str, str, str, int]:
    return (
        str(move["article_id"]),
        str(move["from_store"]),
        str(move["to_store"]),
        str(move["size"]).upper(),
        int(move["qty"]),
    )


def build_candidate_examples(combined_records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    observed_qtys = {
        int(move["qty"])
        for record in combined_records
        for move in record.get("moves", [])
    }

    examples_by_key: dict[tuple[str, str, str, str, int], dict[str, Any]] = {}
    article_summaries: list[dict[str, Any]] = []
    label_counter: Counter[int] = Counter()
    total_observed_moves = 0

    def add_example(
        article_id: str,
        stores: dict[str, dict[str, Any]],
        ordered_sizes: list[str],
        candidate: dict[str, Any],
        accepted_by_human: int,
    ) -> None:
        key = move_key(candidate)
        donor = stores[candidate["from_store"]]
        receiver = stores[candidate["to_store"]]
        size = candidate["size"]
        qty = int(candidate["qty"])

        donor_stock_by_size = {candidate_size: int(donor.get(candidate_size, 0)) for candidate_size in ordered_sizes}
        receiver_stock_by_size = {
            candidate_size: int(receiver.get(candidate_size, 0))
            for candidate_size in ordered_sizes
        }
        donor_stock = int(donor.get(size, 0))
        receiver_stock = int(receiver.get(size, 0))

        donor_after = dict(donor_stock_by_size)
        donor_after[size] = max(0, donor_after.get(size, 0) - qty)
        receiver_after = dict(receiver_stock_by_size)
        receiver_after[size] = receiver_after.get(size, 0) + qty

        examples_by_key[key] = {
            "article_id": article_id,
            "candidate_move": candidate,
            "label": {
                "accepted_by_human": accepted_by_human,
            },
            "features": {
                "size_position": size_position(size, ordered_sizes),
                "donor_stock_for_size": donor_stock,
                "receiver_stock_for_size": receiver_stock,
                "donor_total_stock": sum(donor_stock_by_size.values()),
                "receiver_total_stock": sum(receiver_stock_by_size.values()),
                "donor_sales": int(donor.get("sold", 0)),
                "receiver_sales": int(receiver.get("sold", 0)),
                "sales_difference": int(receiver.get("sold", 0)) - int(donor.get("sold", 0)),
                "donor_store_rank": donor.get("store_sales_rank"),
                "receiver_store_rank": receiver.get("store_sales_rank"),
                "donor_store_total_stock_week": donor.get("store_total_stock_week"),
                "receiver_store_total_stock_week": receiver.get("store_total_stock_week"),
                "store_total_stock_tiebreak_advantage": (
                    (donor.get("store_total_stock_week") or 0) - (receiver.get("store_total_stock_week") or 0)
                ),
                "donor_store_size_class": donor.get("store_size_class"),
                "receiver_store_size_class": receiver.get("store_size_class"),
                "donor_size_count": active_size_count(donor_stock_by_size),
                "receiver_size_count": active_size_count(receiver_stock_by_size),
                "donor_series_width_before": series_width(donor_stock_by_size, ordered_sizes),
                "donor_series_width_after": series_width(donor_after, ordered_sizes),
                "receiver_series_width_before": series_width(receiver_stock_by_size, ordered_sizes),
                "receiver_series_width_after": series_width(receiver_after, ordered_sizes),
                "receiver_missing_size_before": receiver_stock == 0,
                "donor_is_double_size": donor_stock >= 2,
                "donor_is_triple_plus_size": donor_stock >= 3,
                "donor_would_hit_zero": donor_stock - qty == 0,
                "donor_would_break_sequence": would_break_sequence(
                    donor_stock_by_size, ordered_sizes, size, qty
                ),
                "donor_below_min_total_after": sum(donor_after.values()) < 3,
                "donor_below_min_size_count_after": active_size_count(donor_after) < 3,
                "receiver_reaches_min_total_after": sum(receiver_after.values()) >= 3,
                "receiver_reaches_min_size_count_after": active_size_count(receiver_after) >= 3,
            },
        }

    for record in combined_records:
        article_id = str(record["article_id"])
        snapshot = record["snapshot"]
        stores = snapshot["stores"]
        ordered_sizes = sort_sizes(snapshot["sizes"])
        observed_moves = [
            {
                "article_id": article_id,
                "from_store": str(move["from_store"]),
                "to_store": str(move["to_store"]),
                "size": str(move["size"]).upper(),
                "qty": int(move["qty"]),
            }
            for move in record.get("moves", [])
        ]
        observed_move_keys = {move_key(move) for move in observed_moves}
        total_observed_moves += len(observed_move_keys)

        for observed_move in observed_moves:
            if observed_move["from_store"] not in stores or observed_move["to_store"] not in stores:
                continue
            add_example(article_id, stores, ordered_sizes, observed_move, accepted_by_human=1)

        for size in ordered_sizes:
            for from_store, donor in stores.items():
                donor_stock = int(donor.get(size, 0))
                if donor_stock <= 1:
                    continue

                for to_store, receiver in stores.items():
                    if from_store == to_store:
                        continue

                    for qty in candidate_qty_range(donor_stock, observed_qtys):
                        candidate = {
                            "article_id": article_id,
                            "from_store": str(from_store),
                            "to_store": str(to_store),
                            "size": size,
                            "qty": qty,
                        }
                        accepted_by_human = 1 if move_key(candidate) in observed_move_keys else 0
                        add_example(article_id, stores, ordered_sizes, candidate, accepted_by_human)

        article_examples = [
            example for example in examples_by_key.values()
            if example["article_id"] == article_id
        ]
        article_example_count = len(article_examples)
        article_positive_count = sum(
            example["label"]["accepted_by_human"]
            for example in article_examples
        )

        article_summaries.append(
            {
                "article_id": article_id,
                "candidate_count": article_example_count,
                "accepted_candidate_count": article_positive_count,
                "observed_move_count": len(observed_move_keys),
                "observed_candidate_coverage": (
                    article_positive_count / len(observed_move_keys)
                ) if observed_move_keys else 0.0,
            }
        )

    examples = list(examples_by_key.values())
    for example in examples:
        label_counter[example["label"]["accepted_by_human"]] += 1

    summary = {
        "candidate_count": len(examples),
        "observed_move_count": total_observed_moves,
        "accepted_candidate_count": label_counter[1],
        "rejected_or_not_chosen_candidate_count": label_counter[0],
        "positive_rate": (label_counter[1] / len(examples)) if examples else 0.0,
        "observed_candidate_coverage": (
            label_counter[1] / total_observed_moves
        ) if total_observed_moves else 0.0,
        "articles": article_summaries,
    }
    return examples, summary


def generate_training_data_from_records(
    combined_records: list[dict[str, Any]],
    week_dir: Path,
    year: int | None = None,
    week: int | None = None,
) -> dict[str, Any]:
    examples, summary = build_candidate_examples(combined_records)

    if year is not None or week is not None:
        for example in examples:
            if year is not None:
                example["year"] = year
            if week is not None:
                example["week"] = week
                example["article_group_id"] = f"{year or 'unknown'}-{week}-{example['article_id']}"

    candidates_path = week_dir / "candidate_moves.json"
    training_path = week_dir / "training_examples.json"
    summary_path = week_dir / "training_summary.json"

    candidate_moves = [example["candidate_move"] for example in examples]
    candidates_path.write_text(json.dumps(candidate_moves, indent=2, ensure_ascii=False), encoding="utf-8")
    training_path.write_text(json.dumps(examples, indent=2, ensure_ascii=False), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "candidate_moves_path": str(candidates_path),
        "training_examples_path": str(training_path),
        "training_summary_path": str(summary_path),
        **summary,
    }


def generate_training_data(
    week_dir: Path,
    year: int | None = None,
    week: int | None = None,
    combined_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if combined_records is None:
        combined_records = json.loads((week_dir / "combined.json").read_text(encoding="utf-8"))
    return generate_training_data_from_records(combined_records, week_dir, year=year, week=week)

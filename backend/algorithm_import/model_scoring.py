from __future__ import annotations

import math
from typing import Any

NUMERIC_FEATURES = [
    "donor_stock_for_size",
    "receiver_stock_for_size",
    "donor_total_stock",
    "receiver_total_stock",
    "donor_sales",
    "receiver_sales",
    "sales_difference",
    "donor_store_rank",
    "receiver_store_rank",
    "donor_store_total_stock_week",
    "receiver_store_total_stock_week",
    "store_total_stock_tiebreak_advantage",
    "donor_size_count",
    "receiver_size_count",
    "donor_series_width_before",
    "donor_series_width_after",
    "receiver_series_width_before",
    "receiver_series_width_after",
]

BOOLEAN_FEATURES = [
    "receiver_missing_size_before",
    "donor_is_double_size",
    "donor_is_triple_plus_size",
    "donor_would_hit_zero",
    "donor_would_break_sequence",
    "donor_below_min_total_after",
    "donor_below_min_size_count_after",
    "receiver_reaches_min_total_after",
    "receiver_reaches_min_size_count_after",
]

CATEGORICAL_FEATURES = [
    "size_position",
    "donor_store_size_class",
    "receiver_store_size_class",
]


def _sort_sizes(sizes: list[str]) -> list[str]:
    normalized = [str(size).upper() for size in sizes]
    if all(size.isdigit() for size in normalized):
        return sorted(normalized, key=int)
    return normalized


def _series_width(stock_by_size: dict[str, int], ordered_sizes: list[str]) -> int:
    best = 0
    current = 0
    for size in ordered_sizes:
        if stock_by_size.get(size, 0) > 0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def _active_size_count(stock_by_size: dict[str, int]) -> int:
    return sum(1 for qty in stock_by_size.values() if qty > 0)


def _size_position(size: str, ordered_sizes: list[str]) -> str:
    if size not in ordered_sizes:
        return "unknown"
    index = ordered_sizes.index(size)
    if index == 0 or index == len(ordered_sizes) - 1:
        return "edge"
    return "middle"


def _would_break_sequence(
    stock_by_size: dict[str, int],
    ordered_sizes: list[str],
    size: str,
    qty: int,
) -> bool:
    if stock_by_size.get(size, 0) < qty:
        return True

    before = _series_width(stock_by_size, ordered_sizes)
    after_inventory = dict(stock_by_size)
    after_inventory[size] = max(0, after_inventory.get(size, 0) - qty)
    after = _series_width(after_inventory, ordered_sizes)
    return after < before and before >= 3


def _candidate_qty_range(donor_stock: int, observed_qtys: set[int]) -> list[int]:
    max_qty = max(observed_qtys) if observed_qtys else 2
    feasible_max = max(0, donor_stock - 1)
    return list(range(1, min(max_qty, feasible_max) + 1))


def _candidate_key(candidate_move: dict[str, Any]) -> tuple[str, str, str, str, int]:
    return (
        str(candidate_move["article_id"]),
        str(candidate_move["from_store"]),
        str(candidate_move["to_store"]),
        str(candidate_move["size"]),
        int(candidate_move["qty"]),
    )


def _raw_feature_vector(features: dict[str, Any], feature_spec: dict[str, Any]) -> list[float]:
    vector: list[float] = []

    for feature_name in NUMERIC_FEATURES:
        value = features.get(feature_name, 0)
        vector.append(float(value if value is not None else 0.0))

    for feature_name in BOOLEAN_FEATURES:
        vector.append(1.0 if features.get(feature_name, False) else 0.0)

    categorical_vocab = feature_spec.get("categorical_vocab", {})
    for feature_name in CATEGORICAL_FEATURES:
        current = str(features.get(feature_name, "unknown"))
        for value in categorical_vocab.get(feature_name, []):
            vector.append(1.0 if current == value else 0.0)

    means = feature_spec.get("means", [])
    stds = feature_spec.get("stds", [])
    normalized: list[float] = []
    for index, value in enumerate(vector):
        feature_name = feature_spec["feature_names"][index]
        if feature_name in NUMERIC_FEATURES:
            mean = float(means[index]) if index < len(means) else 0.0
            std = float(stds[index]) if index < len(stds) else 1.0
            divisor = std if abs(std) > 1e-8 else 1.0
            normalized.append((value - mean) / divisor)
        else:
            normalized.append(value)
    return normalized


def _sigmoid(value: float) -> float:
    clipped = max(min(value, 30.0), -30.0)
    return 1.0 / (1.0 + math.exp(-clipped))


def _score_features(features: dict[str, Any], model_artifacts: dict[str, Any]) -> float:
    feature_spec = model_artifacts["feature_spec"]
    vector = _raw_feature_vector(features, feature_spec)
    weights = model_artifacts["weights"]
    bias = float(model_artifacts["bias"])
    score = bias + sum(float(weight) * value for weight, value in zip(weights, vector))
    return _sigmoid(score)


def generate_scored_candidates_for_record(
    record: dict[str, Any],
    week_records: list[dict[str, Any]],
    model_artifacts: dict[str, Any],
) -> list[dict[str, Any]]:
    article_id = str(record["article_id"])
    snapshot = record["snapshot"]
    stores = snapshot["stores"]
    ordered_sizes = _sort_sizes(snapshot["sizes"])
    observed_qtys = {
        int(move["qty"])
        for week_record in week_records
        for move in week_record.get("moves", [])
    }

    candidates: dict[tuple[str, str, str, str, int], dict[str, Any]] = {}

    for size in ordered_sizes:
        for from_store, donor in stores.items():
            donor_stock = int(donor.get(size, 0))
            if donor_stock <= 1:
                continue

            donor_stock_by_size = {
                candidate_size: int(donor.get(candidate_size, 0))
                for candidate_size in ordered_sizes
            }

            for to_store, receiver in stores.items():
                if from_store == to_store:
                    continue

                receiver_stock_by_size = {
                    candidate_size: int(receiver.get(candidate_size, 0))
                    for candidate_size in ordered_sizes
                }

                for qty in _candidate_qty_range(donor_stock, observed_qtys):
                    donor_after = dict(donor_stock_by_size)
                    donor_after[size] = max(0, donor_after.get(size, 0) - qty)
                    receiver_after = dict(receiver_stock_by_size)
                    receiver_after[size] = receiver_after.get(size, 0) + qty

                    candidate_move = {
                        "article_id": article_id,
                        "from_store": str(from_store),
                        "to_store": str(to_store),
                        "size": str(size).upper(),
                        "qty": int(qty),
                    }
                    key = _candidate_key(candidate_move)

                    features = {
                        "size_position": _size_position(size, ordered_sizes),
                        "donor_stock_for_size": donor_stock,
                        "receiver_stock_for_size": int(receiver.get(size, 0)),
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
                            (donor.get("store_total_stock_week") or 0)
                            - (receiver.get("store_total_stock_week") or 0)
                        ),
                        "donor_store_size_class": donor.get("store_size_class"),
                        "receiver_store_size_class": receiver.get("store_size_class"),
                        "donor_size_count": _active_size_count(donor_stock_by_size),
                        "receiver_size_count": _active_size_count(receiver_stock_by_size),
                        "donor_series_width_before": _series_width(donor_stock_by_size, ordered_sizes),
                        "donor_series_width_after": _series_width(donor_after, ordered_sizes),
                        "receiver_series_width_before": _series_width(receiver_stock_by_size, ordered_sizes),
                        "receiver_series_width_after": _series_width(receiver_after, ordered_sizes),
                        "receiver_missing_size_before": int(receiver.get(size, 0)) == 0,
                        "donor_is_double_size": donor_stock >= 2,
                        "donor_is_triple_plus_size": donor_stock >= 3,
                        "donor_would_hit_zero": donor_stock - qty == 0,
                        "donor_would_break_sequence": _would_break_sequence(
                            donor_stock_by_size,
                            ordered_sizes,
                            size,
                            qty,
                        ),
                        "donor_below_min_total_after": sum(donor_after.values()) < 3,
                        "donor_below_min_size_count_after": _active_size_count(donor_after) < 3,
                        "receiver_reaches_min_total_after": sum(receiver_after.values()) >= 3,
                        "receiver_reaches_min_size_count_after": _active_size_count(receiver_after) >= 3,
                    }

                    candidates[key] = {
                        "move": candidate_move,
                        "features": features,
                        "score": _score_features(features, model_artifacts),
                    }

    return sorted(candidates.values(), key=lambda item: item["score"], reverse=True)

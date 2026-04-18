from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


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

CATEGORICAL_FEATURES = [
    "size_position",
    "donor_store_size_class",
    "receiver_store_size_class",
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


@dataclass
class FeatureSpec:
    numeric_features: list[str]
    boolean_features: list[str]
    categorical_vocab: dict[str, list[str]]
    feature_names: list[str]
    means: list[float]
    stds: list[float]


def sigmoid(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values, -30, 30)
    return 1.0 / (1.0 + np.exp(-clipped))


def article_sort_key(value: str) -> tuple[int, str]:
    parts = value.split("-")
    if len(parts) >= 3 and parts[-1].isdigit():
        return (int(parts[-1]), value)
    if value.isdigit():
        return (int(value), value)
    return (10**9, value)


def article_split(article_ids: list[str], test_ratio: float = 0.25) -> tuple[set[str], set[str]]:
    ordered = sorted(article_ids, key=article_sort_key)
    test_count = max(1, int(len(ordered) * test_ratio))
    test_articles = set(ordered[-test_count:])
    train_articles = set(ordered[:-test_count])
    return train_articles, test_articles


def build_feature_spec(train_examples: list[dict[str, Any]]) -> FeatureSpec:
    categorical_vocab: dict[str, list[str]] = {}
    for feature_name in CATEGORICAL_FEATURES:
        values = sorted(
            {
                str(example["features"].get(feature_name, "unknown"))
                for example in train_examples
            }
        )
        categorical_vocab[feature_name] = values

    feature_names: list[str] = []
    feature_names.extend(NUMERIC_FEATURES)
    feature_names.extend(BOOLEAN_FEATURES)
    for feature_name in CATEGORICAL_FEATURES:
        for value in categorical_vocab[feature_name]:
            feature_names.append(f"{feature_name}={value}")

    raw_matrix = []
    for example in train_examples:
        raw_matrix.append(raw_feature_vector(example, categorical_vocab))

    matrix = np.array(raw_matrix, dtype=float) if raw_matrix else np.zeros((0, len(feature_names)))

    means: list[float] = []
    stds: list[float] = []
    for idx, feature_name in enumerate(feature_names):
        if feature_name in NUMERIC_FEATURES:
            column = matrix[:, idx]
            mean = float(column.mean()) if len(column) else 0.0
            std = float(column.std()) if len(column) else 1.0
            means.append(mean)
            stds.append(std if std > 1e-8 else 1.0)
        else:
            means.append(0.0)
            stds.append(1.0)

    return FeatureSpec(
        numeric_features=NUMERIC_FEATURES,
        boolean_features=BOOLEAN_FEATURES,
        categorical_vocab=categorical_vocab,
        feature_names=feature_names,
        means=means,
        stds=stds,
    )


def raw_feature_vector(example: dict[str, Any], categorical_vocab: dict[str, list[str]]) -> list[float]:
    features = example["features"]
    vector: list[float] = []

    for feature_name in NUMERIC_FEATURES:
        value = features.get(feature_name, 0)
        vector.append(float(value if value is not None else 0.0))

    for feature_name in BOOLEAN_FEATURES:
        vector.append(1.0 if features.get(feature_name, False) else 0.0)

    for feature_name in CATEGORICAL_FEATURES:
        current = str(features.get(feature_name, "unknown"))
        for value in categorical_vocab[feature_name]:
            vector.append(1.0 if current == value else 0.0)

    return vector


def vectorize_examples(examples: list[dict[str, Any]], spec: FeatureSpec) -> np.ndarray:
    rows = [raw_feature_vector(example, spec.categorical_vocab) for example in examples]
    matrix = np.array(rows, dtype=float) if rows else np.zeros((0, len(spec.feature_names)))

    for idx, feature_name in enumerate(spec.feature_names):
        if feature_name in NUMERIC_FEATURES:
            matrix[:, idx] = (matrix[:, idx] - spec.means[idx]) / spec.stds[idx]

    return matrix


def labels_from_examples(examples: list[dict[str, Any]]) -> np.ndarray:
    return np.array(
        [float(example["label"]["accepted_by_human"]) for example in examples],
        dtype=float,
    )


def train_logistic_regression(
    x_train: np.ndarray,
    y_train: np.ndarray,
    learning_rate: float = 0.05,
    epochs: int = 1200,
    l2_penalty: float = 0.001,
) -> tuple[np.ndarray, float, list[float]]:
    weights = np.zeros(x_train.shape[1], dtype=float)
    bias = 0.0
    losses: list[float] = []

    for _ in range(epochs):
        logits = x_train @ weights + bias
        predictions = sigmoid(logits)

        error = predictions - y_train
        grad_w = (x_train.T @ error) / len(x_train) + l2_penalty * weights
        grad_b = float(error.mean())

        weights -= learning_rate * grad_w
        bias -= learning_rate * grad_b

        eps = 1e-9
        loss = -np.mean(
            y_train * np.log(predictions + eps) + (1 - y_train) * np.log(1 - predictions + eps)
        )
        loss += 0.5 * l2_penalty * float(np.sum(weights * weights))
        losses.append(float(loss))

    return weights, bias, losses


def predict_scores(matrix: np.ndarray, weights: np.ndarray, bias: float) -> np.ndarray:
    return sigmoid(matrix @ weights + bias)


def top_k_overlap(
    examples: list[dict[str, Any]],
    scores: np.ndarray,
) -> dict[str, Any]:
    by_article: dict[str, list[tuple[dict[str, Any], float]]] = {}
    for example, score in zip(examples, scores.tolist()):
        by_article.setdefault(example["article_id"], []).append((example, float(score)))

    total_observed = 0
    total_overlap = 0
    total_selected = 0
    article_results: list[dict[str, Any]] = []

    for article_id, items in by_article.items():
        observed_count = sum(int(item[0]["label"]["accepted_by_human"]) for item in items)
        total_observed += observed_count
        ranked = sorted(items, key=lambda item: item[1], reverse=True)
        selected = ranked[:observed_count] if observed_count > 0 else []

        selected_keys = {
            candidate_key(item[0]["candidate_move"])
            for item in selected
        }
        observed_keys = {
            candidate_key(item[0]["candidate_move"])
            for item in items
            if item[0]["label"]["accepted_by_human"] == 1
        }

        overlap = len(selected_keys & observed_keys)
        total_overlap += overlap
        total_selected += len(selected)

        article_results.append(
            {
                "article_id": article_id,
                "observed_count": observed_count,
                "selected_count": len(selected),
                "top_k_overlap": overlap,
            }
        )

    return {
        "observed_count": total_observed,
        "selected_count": total_selected,
        "overlap_count": total_overlap,
        "top_k_recall": (total_overlap / total_observed) if total_observed else 0.0,
        "top_k_precision": (total_overlap / total_selected) if total_selected else 0.0,
        "per_article": article_results,
    }


def candidate_key(candidate_move: dict[str, Any]) -> tuple[str, str, str, str, int]:
    return (
        str(candidate_move["article_id"]),
        str(candidate_move["from_store"]),
        str(candidate_move["to_store"]),
        str(candidate_move["size"]),
        int(candidate_move["qty"]),
    )


def binary_metrics(y_true: np.ndarray, scores: np.ndarray, threshold: float = 0.5) -> dict[str, float]:
    predictions = scores >= threshold
    positives = y_true == 1
    negatives = y_true == 0

    tp = int(np.sum(predictions & positives))
    fp = int(np.sum(predictions & negatives))
    tn = int(np.sum((~predictions) & negatives))
    fn = int(np.sum((~predictions) & positives))

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    accuracy = (tp + tn) / len(y_true) if len(y_true) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "threshold": threshold,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy,
        "f1": f1,
    }


def average_precision(y_true: np.ndarray, scores: np.ndarray) -> float:
    order = np.argsort(-scores)
    y_sorted = y_true[order]
    positives = int(np.sum(y_true))
    if positives == 0:
        return 0.0

    hits = 0
    precision_sum = 0.0
    for idx, value in enumerate(y_sorted, start=1):
        if value == 1:
            hits += 1
            precision_sum += hits / idx
    return precision_sum / positives


def feature_importance(weights: np.ndarray, spec: FeatureSpec, top_n: int = 20) -> list[dict[str, Any]]:
    pairs = [
        {"feature": name, "weight": float(weight), "abs_weight": float(abs(weight))}
        for name, weight in zip(spec.feature_names, weights.tolist())
    ]
    return sorted(pairs, key=lambda item: item["abs_weight"], reverse=True)[:top_n]


def _train_and_evaluate_examples(examples: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    article_ids = sorted(
        {
            example.get("article_group_id", example["article_id"])
            for example in examples
        },
        key=article_sort_key,
    )
    train_articles, test_articles = article_split(article_ids)

    train_examples = [
        example
        for example in examples
        if example.get("article_group_id", example["article_id"]) in train_articles
    ]
    test_examples = [
        example
        for example in examples
        if example.get("article_group_id", example["article_id"]) in test_articles
    ]

    spec = build_feature_spec(train_examples)
    x_train = vectorize_examples(train_examples, spec)
    y_train = labels_from_examples(train_examples)
    x_test = vectorize_examples(test_examples, spec)
    y_test = labels_from_examples(test_examples)

    weights, bias, losses = train_logistic_regression(x_train, y_train)
    train_scores = predict_scores(x_train, weights, bias)
    test_scores = predict_scores(x_test, weights, bias)

    metrics = {
        "split": {
            "train_article_count": len(train_articles),
            "test_article_count": len(test_articles),
            "train_example_count": len(train_examples),
            "test_example_count": len(test_examples),
            "train_articles": sorted(train_articles, key=article_sort_key),
            "test_articles": sorted(test_articles, key=article_sort_key),
        },
        "train_metrics": {
            "average_precision": average_precision(y_train, train_scores),
            "binary": binary_metrics(y_train, train_scores),
            "top_k": top_k_overlap(train_examples, train_scores),
        },
        "test_metrics": {
            "average_precision": average_precision(y_test, test_scores),
            "binary": binary_metrics(y_test, test_scores),
            "top_k": top_k_overlap(test_examples, test_scores),
        },
        "training": {
            "epochs": len(losses),
            "initial_loss": losses[0] if losses else None,
            "final_loss": losses[-1] if losses else None,
        },
        "feature_importance": feature_importance(weights, spec),
    }

    scored_examples = []
    for example, score in zip(test_examples, test_scores.tolist()):
        scored_examples.append(
            {
                "article_id": example["article_id"],
                "candidate_move": example["candidate_move"],
                "label": example["label"],
                "score": float(score),
            }
        )
    scored_examples.sort(key=lambda item: (int(item["article_id"]), -item["score"]))

    model_artifacts = {
        "bias": float(bias),
        "weights": weights.tolist(),
        "feature_spec": {
            "feature_names": spec.feature_names,
            "numeric_features": spec.numeric_features,
            "boolean_features": spec.boolean_features,
            "categorical_vocab": spec.categorical_vocab,
            "means": spec.means,
            "stds": spec.stds,
        },
    }

    (output_dir / "model_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "model_scored_test_examples.json").write_text(
        json.dumps(scored_examples, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "model_artifacts.json").write_text(
        json.dumps(model_artifacts, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return metrics


def train_and_evaluate_model(week_dir: Path) -> dict[str, Any]:
    examples = json.loads((week_dir / "training_examples.json").read_text(encoding="utf-8"))
    return _train_and_evaluate_examples(examples, week_dir)


def train_and_evaluate_aggregate_model(aggregate_dir: Path) -> dict[str, Any]:
    examples = json.loads((aggregate_dir / "training_examples_all.json").read_text(encoding="utf-8"))
    return _train_and_evaluate_examples(examples, aggregate_dir)

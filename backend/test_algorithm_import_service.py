from __future__ import annotations

import json
from pathlib import Path

import db_models

from algorithm_import.model_scoring import BOOLEAN_FEATURES, CATEGORICAL_FEATURES, NUMERIC_FEATURES
from algorithm_import.reader import ArtifactReadError
from algorithm_import.service import build_dataset_status, build_proposal_comparison, build_week_evaluation


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _feature_names() -> list[str]:
    feature_names = [*NUMERIC_FEATURES, *BOOLEAN_FEATURES]
    categorical_vocab = {
        "size_position": ["edge", "middle", "unknown"],
        "donor_store_size_class": ["small", "medium", "large", "unknown"],
        "receiver_store_size_class": ["small", "medium", "large", "unknown"],
    }
    for feature_name in CATEGORICAL_FEATURES:
        for value in categorical_vocab[feature_name]:
            feature_names.append(f"{feature_name}={value}")
    return feature_names


def _create_test_dataset(data_root: Path) -> None:
    week_12_dir = data_root / "2026" / "week_12"
    week_13_dir = data_root / "2026" / "week_13"
    aggregate = data_root / "2026" / "aggregate"

    week_12_record = {
        "article_id": "ART-123",
        "snapshot": {
            "sizes": ["36", "38"],
            "stores": {
                "1": {
                    "36": 3,
                    "38": 2,
                    "sold": 1,
                    "store_sales_rank": 2,
                    "store_total_stock_week": 5,
                    "store_size_class": "medium",
                },
                "2": {
                    "36": 0,
                    "38": 1,
                    "sold": 5,
                    "store_sales_rank": 1,
                    "store_total_stock_week": 1,
                    "store_size_class": "small",
                },
                "3": {
                    "36": 1,
                    "38": 0,
                    "sold": 2,
                    "store_sales_rank": 3,
                    "store_total_stock_week": 1,
                    "store_size_class": "small",
                },
            },
        },
        "moves": [{"from_store": "1", "to_store": "2", "size": "36", "qty": 1}],
    }
    week_13_record = {
        "article_id": "ART-123",
        "snapshot": {
            "sizes": ["36", "38"],
            "stores": {
                "1": {
                    "36": 4,
                    "38": 2,
                    "sold": 1,
                    "store_sales_rank": 2,
                    "store_total_stock_week": 6,
                    "store_size_class": "medium",
                },
                "2": {
                    "36": 0,
                    "38": 0,
                    "sold": 6,
                    "store_sales_rank": 1,
                    "store_total_stock_week": 0,
                    "store_size_class": "small",
                },
                "3": {
                    "36": 1,
                    "38": 1,
                    "sold": 2,
                    "store_sales_rank": 3,
                    "store_total_stock_week": 2,
                    "store_size_class": "small",
                },
            },
        },
        "moves": [{"from_store": "1", "to_store": "2", "size": "36", "qty": 1}],
    }

    _write_json(
        week_12_dir / "baseline_summary.json",
        {
            "year": 2026,
            "week": 12,
            "proposal_count": 4,
            "observed_move_count": 2,
            "model_opportunity_count": 5,
            "overlap_move_count": 1,
            "observed_opportunity_recall": 0.5,
            "model_overlap_ratio": 0.2,
        },
    )
    _write_json(week_12_dir / "baseline_evaluation.json", {"matched_articles": 1, "articles": []})
    _write_json(week_12_dir / "training_summary.json", {"week": 12, "example_count": 10})
    _write_json(week_12_dir / "combined.json", [week_12_record])
    _write_json(
        week_12_dir / "baseline_proposals.json",
        [{"volgnummer": "ART-123", "moves": [{"from_store": "1", "to_store": "3", "size": "38", "qty": 1}]}],
    )

    _write_json(
        week_13_dir / "baseline_summary.json",
        {
            "year": 2026,
            "week": 13,
            "proposal_count": 5,
            "observed_move_count": 3,
            "model_opportunity_count": 6,
            "overlap_move_count": 2,
            "observed_opportunity_recall": 0.667,
            "model_overlap_ratio": 0.333,
        },
    )
    _write_json(week_13_dir / "baseline_evaluation.json", {"matched_articles": 1, "articles": []})
    _write_json(week_13_dir / "training_summary.json", {"week": 13, "example_count": 12})
    _write_json(week_13_dir / "combined.json", [week_13_record])
    _write_json(
        week_13_dir / "baseline_proposals.json",
        [{"volgnummer": "ART-123", "moves": [{"from_store": "1", "to_store": "3", "size": "36", "qty": 1}]}],
    )

    feature_names = _feature_names()
    _write_json(
        aggregate / "refresh_state.json",
        {
            "latest_week": 13,
            "processed_week_count": 2,
        },
    )
    _write_json(
        aggregate / "training_examples_all_summary.json",
        {
            "weeks_included": [12, 13],
            "total_example_count": 20,
            "total_positive_count": 5,
            "total_negative_count": 15,
            "positive_rate": 0.25,
        },
    )
    _write_json(
        aggregate / "model_metrics.json",
        {
            "test_metrics": {
                "average_precision": 0.81,
                "top_k": {"top_k_recall": 0.84, "top_k_precision": 0.4},
                "binary": {"precision": 0.55, "recall": 0.61},
            },
            "feature_importance": [
                {"feature": "receiver_missing_size_before", "weight": 0.7, "abs_weight": 0.7},
                {"feature": "sales_difference", "weight": 0.4, "abs_weight": 0.4},
            ],
        },
    )
    _write_json(
        aggregate / "model_artifacts.json",
        {
            "feature_spec": {
                "feature_names": feature_names,
                "means": [0.0] * len(feature_names),
                "stds": [1.0] * len(feature_names),
                "categorical_vocab": {
                    "size_position": ["edge", "middle", "unknown"],
                    "donor_store_size_class": ["small", "medium", "large", "unknown"],
                    "receiver_store_size_class": ["small", "medium", "large", "unknown"],
                },
            },
            "weights": [0.05] * len(feature_names),
            "bias": -0.1,
        },
    )


def test_build_dataset_status_reads_available_weeks_and_model_summary(tmp_path: Path):
    data_root = tmp_path / "external-data"
    _create_test_dataset(data_root)

    payload = build_dataset_status(data_root)

    assert payload["data_available"] is True
    assert payload["assist_mode"] == "off"
    assert payload["latest_year"] == 2026
    assert payload["latest_week"] == 13
    assert payload["processed_week_count"] == 2
    assert [week["week"] for week in payload["weeks_available"]] == [13, 12]
    assert payload["aggregate_training_summary"]["total_example_count"] == 20
    assert payload["aggregate_model_summary"]["top_k_recall_test"] == 0.84
    assert payload["aggregate_model_summary"]["feature_importance"][0]["feature"] == "receiver_missing_size_before"
    assert payload["errors"] == []


def test_build_week_evaluation_reads_required_artifacts(tmp_path: Path):
    data_root = tmp_path / "external-data"
    _create_test_dataset(data_root)

    payload = build_week_evaluation(2026, 13, data_root)

    assert payload["year"] == 2026
    assert payload["week"] == 13
    assert payload["summary"]["proposal_count"] == 5
    assert payload["training_summary"]["example_count"] == 12
    assert payload["lineage"]["baseline_summary"]["source_path"].endswith("baseline_summary.json")


def test_build_week_evaluation_raises_when_required_artifact_missing(tmp_path: Path):
    data_root = tmp_path / "external-data"
    _create_test_dataset(data_root)
    (data_root / "2026" / "week_13" / "training_summary.json").unlink()

    try:
        build_week_evaluation(2026, 13, data_root)
    except ArtifactReadError as exc:
        assert "training_summary.json" in str(exc)
    else:
        raise AssertionError("Expected ArtifactReadError for missing training_summary.json")


def test_build_proposal_comparison_uses_latest_matching_week_and_returns_diffs(tmp_path: Path):
    data_root = tmp_path / "external-data"
    _create_test_dataset(data_root)
    proposal = db_models.Proposal(
        id=999,
        artikelnummer="ART-123",
        article_name="Testartikel",
        moves=[{"from_store": "1", "to_store": "2", "size": "36", "qty": 1}],
        total_moves=1,
        total_quantity=1,
        status="pending",
    )

    payload = build_proposal_comparison(proposal, data_root)

    assert payload["available"] is True
    assert payload["latest_matching_week"] == {"year": 2026, "week": 13}
    assert payload["comparison"]["manual_observed"]["move_count"] == 1
    assert payload["comparison"]["baseline"]["available"] is True
    assert payload["comparison"]["model"]["available"] is True
    assert payload["comparison"]["model"]["total_candidate_count"] > 0
    assert payload["comparison"]["drt_vs_manual"]["overlap_count"] == 1
    assert payload["comparison"]["drt_vs_baseline"]["right_only_count"] == 1
    assert payload["comparison"]["lineage"]["combined"]["source_path"].endswith("combined.json")

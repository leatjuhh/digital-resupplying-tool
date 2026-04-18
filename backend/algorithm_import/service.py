from __future__ import annotations

from pathlib import Path
from typing import Any

import db_models

from .config import get_algorithm_assist_mode, get_external_algorithm_data_root
from .model_scoring import generate_scored_candidates_for_record
from .reader import (
    ArtifactReadError,
    aggregate_dir,
    list_available_weeks,
    list_available_years,
    read_json_artifact,
    week_dir,
)


def build_config_status(data_root: Path | None = None) -> dict[str, Any]:
    """Geeft huidig actieve assist_mode en model-versie terug voor UI-badge."""
    data_root = data_root or get_external_algorithm_data_root()
    assist_mode = get_algorithm_assist_mode()

    model_version: str | None = None
    model_available = False

    if data_root.exists():
        years = list_available_years(data_root)
        if years:
            agg = aggregate_dir(data_root, years[-1])
            artifacts, _ = read_json_artifact(agg / "model_artifacts.json", required=False)
            if isinstance(artifacts, dict):
                model_available = True
                model_version = artifacts.get("model_version") or f"v1_{years[-1]}"

    return {
        "assist_mode": assist_mode,
        "model_available": model_available,
        "model_version": model_version,
        "data_root": str(data_root),
    }


def _latest_year(data_root: Path) -> int | None:
    years = list_available_years(data_root)
    return years[-1] if years else None


def _move_key(move: dict[str, Any]) -> tuple[str, str, str, str, int]:
    article_value = move.get("article_id") or move.get("volgnummer") or move.get("artikelnummer") or ""
    return (
        str(article_value),
        str(move.get("from_store", "")),
        str(move.get("to_store", "")),
        str(move.get("size", "")).upper(),
        int(move.get("qty", 0)),
    )


def _normalize_move(move: dict[str, Any], article_id: str) -> dict[str, Any]:
    normalized = {
        "article_id": article_id,
        "from_store": str(move.get("from_store", "")),
        "to_store": str(move.get("to_store", "")),
        "size": str(move.get("size", "")).upper(),
        "qty": int(move.get("qty", 0)),
    }
    if "score" in move:
        normalized["score"] = float(move["score"])
    return normalized


def _diff_moves(left_moves: list[dict[str, Any]], right_moves: list[dict[str, Any]], article_id: str) -> dict[str, Any]:
    left_map = {_move_key(move): _normalize_move(move, article_id) for move in left_moves}
    right_map = {_move_key(move): _normalize_move(move, article_id) for move in right_moves}
    overlap_keys = sorted(set(left_map.keys()) & set(right_map.keys()))
    left_only_keys = sorted(set(left_map.keys()) - set(right_map.keys()))
    right_only_keys = sorted(set(right_map.keys()) - set(left_map.keys()))

    return {
        "overlap_count": len(overlap_keys),
        "left_only_count": len(left_only_keys),
        "right_only_count": len(right_only_keys),
        "overlap_moves": [left_map[key] for key in overlap_keys],
        "left_only_moves": [left_map[key] for key in left_only_keys],
        "right_only_moves": [right_map[key] for key in right_only_keys],
    }


def _summary_feature_importance(metrics_payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not metrics_payload:
        return []
    return list(metrics_payload.get("feature_importance", []))[:8]


def build_dataset_status(data_root: Path | None = None) -> dict[str, Any]:
    data_root = data_root or get_external_algorithm_data_root()
    assist_mode = get_algorithm_assist_mode()

    if not data_root.exists():
        return {
            "data_available": False,
            "assist_mode": assist_mode,
            "dataset_root": str(data_root),
            "latest_year": None,
            "latest_week": None,
            "processed_week_count": 0,
            "weeks_available": [],
            "aggregate_training_summary": None,
            "aggregate_model_summary": {
                "data_available": False,
                "feature_importance": [],
                "lineage": None,
            },
            "refresh_state_lineage": None,
            "errors": [f"Externe dataset root niet gevonden: {data_root}"],
        }

    latest_year = _latest_year(data_root)
    if latest_year is None:
        return {
            "data_available": False,
            "assist_mode": assist_mode,
            "dataset_root": str(data_root),
            "latest_year": None,
            "latest_week": None,
            "processed_week_count": 0,
            "weeks_available": [],
            "aggregate_training_summary": None,
            "aggregate_model_summary": {
                "data_available": False,
                "feature_importance": [],
                "lineage": None,
            },
            "refresh_state_lineage": None,
            "errors": [f"Geen jaardata gevonden onder: {data_root}"],
        }

    errors: list[str] = []
    weeks_available: list[dict[str, Any]] = []
    for week in list_available_weeks(data_root, latest_year):
        summary_path = week_dir(data_root, latest_year, week) / "baseline_summary.json"
        try:
            payload, lineage = read_json_artifact(summary_path)
            weeks_available.append(
                {
                    "year": int(payload["year"]),
                    "week": int(payload["week"]),
                    "proposal_count": int(payload["proposal_count"]),
                    "observed_move_count": int(payload["observed_move_count"]),
                    "model_opportunity_count": int(payload["model_opportunity_count"]),
                    "overlap_move_count": int(payload["overlap_move_count"]),
                    "observed_opportunity_recall": float(payload["observed_opportunity_recall"]),
                    "model_overlap_ratio": float(payload["model_overlap_ratio"]),
                    "lineage": lineage,
                }
            )
        except (ArtifactReadError, KeyError, ValueError, TypeError) as exc:
            errors.append(str(exc))

    agg_dir = aggregate_dir(data_root, latest_year)
    refresh_state, refresh_lineage = read_json_artifact(agg_dir / "refresh_state.json", required=False)
    training_summary, _ = read_json_artifact(agg_dir / "training_examples_all_summary.json", required=False)
    model_metrics, model_metrics_lineage = read_json_artifact(agg_dir / "model_metrics.json", required=False)

    latest_week = refresh_state.get("latest_week") if isinstance(refresh_state, dict) else None
    processed_week_count = refresh_state.get("processed_week_count", 0) if isinstance(refresh_state, dict) else 0

    aggregate_model_summary = {
        "data_available": bool(model_metrics),
        "average_precision_test": (
            model_metrics.get("test_metrics", {}).get("average_precision")
            if isinstance(model_metrics, dict)
            else None
        ),
        "top_k_recall_test": (
            model_metrics.get("test_metrics", {}).get("top_k", {}).get("top_k_recall")
            if isinstance(model_metrics, dict)
            else None
        ),
        "top_k_precision_test": (
            model_metrics.get("test_metrics", {}).get("top_k", {}).get("top_k_precision")
            if isinstance(model_metrics, dict)
            else None
        ),
        "binary_precision_test": (
            model_metrics.get("test_metrics", {}).get("binary", {}).get("precision")
            if isinstance(model_metrics, dict)
            else None
        ),
        "binary_recall_test": (
            model_metrics.get("test_metrics", {}).get("binary", {}).get("recall")
            if isinstance(model_metrics, dict)
            else None
        ),
        "feature_importance": _summary_feature_importance(model_metrics),
        "lineage": model_metrics_lineage,
    }

    return {
        "data_available": bool(weeks_available or training_summary or model_metrics),
        "assist_mode": assist_mode,
        "dataset_root": str(data_root),
        "latest_year": latest_year,
        "latest_week": latest_week,
        "processed_week_count": processed_week_count,
        "weeks_available": sorted(weeks_available, key=lambda item: (item["year"], item["week"]), reverse=True),
        "aggregate_training_summary": training_summary,
        "aggregate_model_summary": aggregate_model_summary,
        "refresh_state_lineage": refresh_lineage,
        "errors": errors,
    }


def build_week_evaluation(year: int, week: int, data_root: Path | None = None) -> dict[str, Any]:
    data_root = data_root or get_external_algorithm_data_root()
    week_path = week_dir(data_root, year, week)
    summary_payload, summary_lineage = read_json_artifact(week_path / "baseline_summary.json")
    evaluation_payload, evaluation_lineage = read_json_artifact(week_path / "baseline_evaluation.json")
    training_payload, training_lineage = read_json_artifact(week_path / "training_summary.json")

    return {
        "year": year,
        "week": week,
        "summary": summary_payload,
        "evaluation": evaluation_payload,
        "training_summary": training_payload,
        "lineage": {
            "baseline_summary": summary_lineage,
            "baseline_evaluation": evaluation_lineage,
            "training_summary": training_lineage,
        },
    }


def _find_matching_records(article_id: str, data_root: Path) -> list[dict[str, Any]]:
    matches = []
    for year in reversed(list_available_years(data_root)):
        for week in reversed(list_available_weeks(data_root, year)):
            week_path = week_dir(data_root, year, week)
            combined_payload, combined_lineage = read_json_artifact(week_path / "combined.json", required=False)
            if not isinstance(combined_payload, list):
                continue

            record = next((item for item in combined_payload if str(item.get("article_id")) == article_id), None)
            if not record:
                continue

            baseline_payload, baseline_lineage = read_json_artifact(
                week_path / "baseline_proposals.json",
                required=False,
            )

            matches.append(
                {
                    "year": year,
                    "week": week,
                    "record": record,
                    "week_records": combined_payload,
                    "combined_lineage": combined_lineage,
                    "baseline_payload": baseline_payload,
                    "baseline_lineage": baseline_lineage,
                }
            )
    return matches


def enrich_moves_with_model_scores(
    volgnummer: str,
    proposal_moves: list[dict[str, Any]],
    data_root: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Voeg model_score en feature_snapshot toe aan proposal moves (shadow mode).

    Zoekt het artikel op in de Herverdelingsalgoritme combined.json bestanden.
    Scoort alle kandidaten met het model en matcht de DRT-moves op
    (from_store, to_store, size, qty). Bij niet-gevonden move of missing model:
    model_score=None, feature_snapshot=None.

    Returns:
        (enriched_moves, model_meta) — model_meta bevat versie-info voor applied_rules.
    """
    data_root = data_root or get_external_algorithm_data_root()
    article_id = str(volgnummer)

    no_model_meta: dict[str, Any] = {"model_score_applied": False}

    if not data_root.exists():
        return proposal_moves, no_model_meta

    # Laad model artifacts
    years = list_available_years(data_root)
    if not years:
        return proposal_moves, no_model_meta

    agg = aggregate_dir(data_root, years[-1])
    model_artifacts, _ = read_json_artifact(agg / "model_artifacts.json", required=False)
    if not isinstance(model_artifacts, dict):
        return proposal_moves, no_model_meta

    # Vind meest recente record voor dit artikel
    matches = _find_matching_records(article_id, data_root)
    if not matches:
        return proposal_moves, no_model_meta

    latest = matches[0]
    record = latest["record"]
    week_records = latest["week_records"]

    # Scoor alle kandidaten
    try:
        scored_candidates = generate_scored_candidates_for_record(record, week_records, model_artifacts)
    except Exception:
        return proposal_moves, no_model_meta

    # Bouw lookup: (from_store, to_store, size, qty) → {score, features}
    score_lookup: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    for candidate in scored_candidates:
        move = candidate["move"]
        key = (
            str(move.get("from_store", "")),
            str(move.get("to_store", "")),
            str(move.get("size", "")).upper(),
            int(move.get("qty", 0)),
        )
        score_lookup[key] = {
            "score": float(candidate["score"]),
            "features": candidate.get("features", {}),
        }

    model_version = model_artifacts.get("model_version") or f"v1_{years[-1]}"
    enriched: list[dict[str, Any]] = []
    for move in proposal_moves:
        key = (
            str(move.get("from_store", "")),
            str(move.get("to_store", "")),
            str(move.get("size", "")).upper(),
            int(move.get("qty", 0)),
        )
        match = score_lookup.get(key)
        enriched.append({
            **move,
            "model_score": round(match["score"], 4) if match else None,
            "feature_snapshot": match["features"] if match else None,
        })

    model_meta = {
        "model_score_applied": True,
        "model_version": model_version,
        "week": latest["week"],
        "year": latest["year"],
    }
    return enriched, model_meta


def build_proposal_comparison(proposal: db_models.Proposal, data_root: Path | None = None) -> dict[str, Any]:
    data_root = data_root or get_external_algorithm_data_root()
    article_id = str(proposal.artikelnummer)
    matches = _find_matching_records(article_id, data_root)
    current_moves = [_normalize_move(move, article_id) for move in (proposal.moves or [])]

    if not matches:
        return {
            "available": False,
            "proposal_id": proposal.id,
            "artikelnummer": article_id,
            "article_name": proposal.article_name,
            "current_proposal": {
                "move_count": len(current_moves),
                "moves": current_moves,
            },
            "matched_weeks": [],
            "latest_matching_week": None,
            "comparison": None,
        }

    latest = matches[0]
    record = latest["record"]
    week_records = latest["week_records"]
    observed_moves = [_normalize_move(move, article_id) for move in record.get("moves", [])]

    baseline_moves: list[dict[str, Any]] = []
    if isinstance(latest["baseline_payload"], list):
        baseline_match = next(
            (item for item in latest["baseline_payload"] if str(item.get("volgnummer")) == article_id),
            None,
        )
        if baseline_match:
            baseline_moves = [_normalize_move(move, article_id) for move in baseline_match.get("moves", [])]

    agg_dir = aggregate_dir(data_root, latest["year"])
    model_artifacts, model_lineage = read_json_artifact(agg_dir / "model_artifacts.json", required=False)
    model_metrics, _ = read_json_artifact(agg_dir / "model_metrics.json", required=False)

    model_payload: dict[str, Any] = {
        "available": False,
        "selection_size": 0,
        "total_candidate_count": 0,
        "selected_moves": [],
        "top_candidates": [],
        "average_precision_test": (
            model_metrics.get("test_metrics", {}).get("average_precision")
            if isinstance(model_metrics, dict)
            else None
        ),
        "top_k_recall_test": (
            model_metrics.get("test_metrics", {}).get("top_k", {}).get("top_k_recall")
            if isinstance(model_metrics, dict)
            else None
        ),
    }

    model_selected_moves: list[dict[str, Any]] = []
    if isinstance(model_artifacts, dict):
        scored_candidates = generate_scored_candidates_for_record(record, week_records, model_artifacts)
        selection_size = max(len(current_moves), len(observed_moves), len(baseline_moves), 1)
        model_selected_moves = [{**item["move"], "score": round(float(item["score"]), 4)} for item in scored_candidates[:selection_size]]
        model_payload = {
            **model_payload,
            "available": True,
            "selection_size": selection_size,
            "total_candidate_count": len(scored_candidates),
            "selected_moves": model_selected_moves,
            "top_candidates": [{**item["move"], "score": round(float(item["score"]), 4)} for item in scored_candidates[:10]],
        }

    snapshot = record.get("snapshot", {})
    stores = snapshot.get("stores", {})
    total_inventory = 0
    total_sales = 0
    for store in stores.values():
        total_sales += int(store.get("sold", 0))
        total_inventory += sum(
            int(value)
            for key, value in store.items()
            if key not in {"sold", "store_name", "store_size_class", "store_sales_rank", "store_total_stock_week"}
        )

    return {
        "available": True,
        "proposal_id": proposal.id,
        "artikelnummer": article_id,
        "article_name": proposal.article_name,
        "current_proposal": {
            "move_count": len(current_moves),
            "moves": current_moves,
        },
        "matched_weeks": [{"year": match["year"], "week": match["week"]} for match in matches],
        "latest_matching_week": {"year": latest["year"], "week": latest["week"]},
        "comparison": {
            "year": latest["year"],
            "week": latest["week"],
            "article_context": {
                "size_count": len(snapshot.get("sizes", [])),
                "store_count": len(stores),
                "total_inventory": total_inventory,
                "total_sales": total_sales,
            },
            "manual_observed": {
                "move_count": len(observed_moves),
                "moves": observed_moves,
            },
            "baseline": {
                "available": latest["baseline_payload"] is not None,
                "move_count": len(baseline_moves),
                "moves": baseline_moves,
            },
            "model": model_payload,
            "drt_vs_manual": _diff_moves(current_moves, observed_moves, article_id),
            "drt_vs_baseline": _diff_moves(current_moves, baseline_moves, article_id) if latest["baseline_payload"] is not None else None,
            "drt_vs_model": _diff_moves(current_moves, model_selected_moves, article_id) if model_payload["available"] else None,
            "manual_vs_model": _diff_moves(observed_moves, model_selected_moves, article_id) if model_payload["available"] else None,
            "lineage": {
                "combined": latest["combined_lineage"],
                "baseline_proposals": latest["baseline_lineage"],
                "model_artifacts": model_lineage,
            },
        },
    }

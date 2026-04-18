from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from model_training import train_and_evaluate_aggregate_model, train_and_evaluate_model
from run_baseline import main as _unused  # keep module importable for tooling
from training_data import generate_training_data
from week_sources import resolve_pdf_dir
from week_pipeline import run_week_pipeline


WEEK_DIR_PATTERN = re.compile(r"^week_(\d+)$")


def run_baseline_for_week(
    week_dir: Path,
    year: int,
    week: int,
    records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    from legacy_redistribution.baseline import generate_baseline_proposal_from_record, proposal_to_dict

    if records is None:
        combined_path = week_dir / "combined.json"
        records = json.loads(combined_path.read_text(encoding="utf-8"))

    proposals = [
        proposal_to_dict(generate_baseline_proposal_from_record(record, batch_id=week))
        for record in records
    ]

    output_path = week_dir / "baseline_proposals.json"
    output_path.write_text(json.dumps(proposals, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "year": year,
        "week": week,
        "proposal_count": len(proposals),
        "articles_with_moves": sum(1 for proposal in proposals if proposal["total_moves"] > 0),
        "articles_without_moves": sum(1 for proposal in proposals if proposal["total_moves"] == 0),
        "interpretation": "Observed decisions versus model-detected redistribution opportunities",
    }

    def move_key(move: dict[str, Any]) -> tuple[str, str, str, str, int]:
        return (
            str(move["article_id"]) if "article_id" in move else str(move["volgnummer"]),
            str(move["from_store"]),
            str(move["to_store"]),
            str(move["size"]),
            int(move["qty"]),
        )

    proposal_map = {proposal["volgnummer"]: proposal for proposal in proposals}
    per_article_evaluation = []
    total_observed_moves = 0
    total_model_opportunities = 0
    total_overlap_moves = 0

    for record in records:
        article_id = str(record["article_id"])
        observed_moves = list(record.get("moves", []))
        suggested_moves = proposal_map[article_id]["moves"]

        observed_keys = {move_key(move) for move in observed_moves}
        suggested_keys = {move_key(move) for move in suggested_moves}

        overlap_moves = sorted(observed_keys & suggested_keys)
        observed_only = sorted(observed_keys - suggested_keys)
        model_only = sorted(suggested_keys - observed_keys)

        total_observed_moves += len(observed_keys)
        total_model_opportunities += len(suggested_keys)
        total_overlap_moves += len(overlap_moves)

        per_article_evaluation.append(
            {
                "article_id": article_id,
                "observed_move_count": len(observed_keys),
                "model_opportunity_count": len(suggested_keys),
                "overlap_move_count": len(overlap_moves),
                "observed_only_count": len(observed_only),
                "model_only_count": len(model_only),
                "overlap_moves": overlap_moves,
                "observed_only_moves": observed_only,
                "model_only_moves": model_only,
            }
        )

    evaluation = {
        "year": year,
        "week": week,
        "interpretation": {
            "observed_moves": "Handmatige Excel-verplaatsingen uit de week.",
            "model_opportunities": "Kansen die de baseline-logica ziet in de voorraadrapportage.",
            "overlap_moves": "Moves die zowel handmatig zijn gedaan als door het model zijn voorgesteld.",
            "warning": (
                "Deze evaluatie behandelt handmatige moves niet als absolute waarheid. "
                "Het doel is inzicht in overlap en gemiste of extra kansen."
            ),
        },
        "observed_move_count": total_observed_moves,
        "model_opportunity_count": total_model_opportunities,
        "overlap_move_count": total_overlap_moves,
        "observed_opportunity_recall": (
            total_overlap_moves / total_observed_moves
        ) if total_observed_moves else 0.0,
        "model_overlap_ratio": (
            total_overlap_moves / total_model_opportunities
        ) if total_model_opportunities else 0.0,
        "observed_only_count": total_observed_moves - total_overlap_moves,
        "model_only_count": total_model_opportunities - total_overlap_moves,
        "per_article": per_article_evaluation,
    }

    (week_dir / "baseline_evaluation.json").write_text(
        json.dumps(evaluation, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    summary["observed_move_count"] = total_observed_moves
    summary["model_opportunity_count"] = total_model_opportunities
    summary["overlap_move_count"] = total_overlap_moves
    summary["observed_opportunity_recall"] = evaluation["observed_opportunity_recall"]
    summary["model_overlap_ratio"] = evaluation["model_overlap_ratio"]
    summary["observed_only_count"] = evaluation["observed_only_count"]
    summary["model_only_count"] = evaluation["model_only_count"]

    (week_dir / "baseline_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def process_single_week(
    *,
    year: int,
    week: int,
    source_root: Path,
    output_root: Path,
    excel_path: Path | None = None,
) -> dict[str, Any]:
    source_week_dir = source_root / f"Jaar {year}" / f"Week {week}"
    pipeline_result = run_week_pipeline(
        week=week,
        year=year,
        week_dir=source_week_dir,
        output_root=output_root,
        excel_path=excel_path,
    )

    output_week_dir = output_root / str(year) / f"week_{week}"
    combined_records = pipeline_result["combined"]
    baseline_summary = run_baseline_for_week(output_week_dir, year, week, records=combined_records)
    training_summary = generate_training_data(
        output_week_dir,
        year=year,
        week=week,
        combined_records=combined_records,
    )

    return {
        "year": year,
        "week": week,
        "output_week_dir": str(output_week_dir),
        "analysis": pipeline_result["analysis"],
        "baseline_summary": baseline_summary,
        "training_summary": training_summary,
    }


def available_processed_weeks(output_year_dir: Path) -> list[int]:
    weeks: list[int] = []
    if not output_year_dir.exists():
        return weeks
    for child in output_year_dir.iterdir():
        match = WEEK_DIR_PATTERN.match(child.name)
        if child.is_dir() and match:
            weeks.append(int(match.group(1)))
    return sorted(weeks)


def combine_training_examples(output_root: Path, year: int, weeks: list[int]) -> dict[str, Any]:
    combined_examples: list[dict[str, Any]] = []
    week_summaries: list[dict[str, Any]] = []

    for week in weeks:
        week_dir = output_root / str(year) / f"week_{week}"
        summary_path = week_dir / "training_summary.json"
        examples_path = week_dir / "training_examples.json"
        if not summary_path.exists() or not examples_path.exists():
            continue

        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        examples = json.loads(examples_path.read_text(encoding="utf-8"))
        combined_examples.extend(examples)
        week_summaries.append(
            {
                "week": week,
                "candidate_count": summary["candidate_count"],
                "observed_move_count": summary["observed_move_count"],
                "accepted_candidate_count": summary["accepted_candidate_count"],
            }
        )

    aggregate_dir = output_root / str(year) / "aggregate"
    aggregate_dir.mkdir(parents=True, exist_ok=True)

    combined_path = aggregate_dir / "training_examples_all.json"
    combined_path.write_text(json.dumps(combined_examples, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "year": year,
        "weeks_included": [item["week"] for item in week_summaries],
        "week_summaries": week_summaries,
        "total_example_count": len(combined_examples),
        "total_positive_count": sum(
            1 for example in combined_examples if example["label"]["accepted_by_human"] == 1
        ),
    }
    summary["total_negative_count"] = summary["total_example_count"] - summary["total_positive_count"]
    summary["positive_rate"] = (
        summary["total_positive_count"] / summary["total_example_count"]
    ) if summary["total_example_count"] else 0.0

    (aggregate_dir / "training_examples_all_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def refresh_all_available_weeks(
    *,
    year: int,
    source_root: Path,
    output_root: Path,
    weeks: list[int] | None = None,
) -> dict[str, Any]:
    if weeks is None:
        source_year_dir = source_root / f"Jaar {year}"
        weeks = []
        if source_year_dir.exists():
            for child in source_year_dir.iterdir():
                if child.is_dir() and child.name.startswith("Week "):
                    try:
                        week = int(child.name.split(" ", 1)[1])
                    except ValueError:
                        continue
                    if (child / "Ingevoerd.xlsx").exists() and resolve_pdf_dir(child) is not None:
                        weeks.append(week)
        weeks = sorted(set(weeks))

    processed = []
    for week in weeks:
        processed.append(
            process_single_week(
                year=year,
                week=week,
                source_root=source_root,
                output_root=output_root,
            )
        )

    aggregate_summary = combine_training_examples(output_root, year, weeks)
    aggregate_dir = output_root / str(year) / "aggregate"
    aggregate_model_metrics = None
    if aggregate_summary["total_example_count"] > 0:
        aggregate_model_metrics = train_and_evaluate_aggregate_model(aggregate_dir)

    # Train first on the latest available week for quick feedback.
    latest_week = max(weeks) if weeks else None
    latest_model_metrics = None
    if latest_week is not None:
        latest_model_metrics = train_and_evaluate_model(output_root / str(year) / f"week_{latest_week}")

    state = {
        "year": year,
        "weeks_processed": weeks,
        "processed_week_count": len(weeks),
        "latest_week": latest_week,
        "aggregate_training_summary": aggregate_summary,
        "aggregate_model_metrics": aggregate_model_metrics,
        "latest_model_metrics": latest_model_metrics,
    }
    state_path = output_root / str(year) / "aggregate" / "refresh_state.json"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state

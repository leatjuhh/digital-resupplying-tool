"""
Offline evaluatiehaak voor situatieclassificatie.

Leest lokale gecombineerde weekbestanden en vergelijkt de shadow-mode
classificatie met handmatige weekmoves, zonder live serverafhankelijkheid.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .adapter import article_from_combined_record
from .constraints import DEFAULT_PARAMS, RedistributionParams
from .domain import ArticleSituation
from .situation import collect_article_situation_metrics, classify_article_situation


def _empty_situation_map() -> Dict[str, int]:
    return {situation.value: 0 for situation in ArticleSituation}


def load_combined_records(combined_path: Path) -> List[dict]:
    """Lees een gecombineerd weekbestand in."""
    return json.loads(combined_path.read_text(encoding="utf-8"))


def evaluate_combined_records(
    records: Iterable[dict],
    *,
    year: int,
    week: int,
    source: str,
    params: Optional[RedistributionParams] = None,
) -> Dict:
    """Evalueer één weekbestand en groepeer handmatige moves per situatie."""
    if params is None:
        params = DEFAULT_PARAMS

    records = list(records)
    situation_counts = Counter(_empty_situation_map())
    moved_article_counts = Counter(_empty_situation_map())
    observed_move_counts = Counter(_empty_situation_map())
    per_article = []

    for record in records:
        article = article_from_combined_record(record, batch_id=week)
        metrics = collect_article_situation_metrics(article)
        situation = classify_article_situation(article, params)
        observed_moves = list(record.get("moves", []))
        observed_move_count = len(observed_moves)

        situation_counts[situation.value] += 1
        if observed_move_count > 0:
            moved_article_counts[situation.value] += 1
            observed_move_counts[situation.value] += observed_move_count

        per_article.append(
            {
                "article_id": str(record["article_id"]),
                "situation": situation.value,
                "observed_move_count": observed_move_count,
                "total_inventory": metrics.total_inventory,
                "total_sales": metrics.total_sales,
                "active_store_count": metrics.active_store_count,
                "avg_units_per_active_store": round(metrics.avg_units_per_active_store, 3),
                "avg_units_per_size": round(metrics.avg_units_per_size, 3),
                "stock_to_sales_ratio": round(metrics.stock_to_sales_ratio, 3),
            }
        )

    return {
        "year": year,
        "week": week,
        "source": source,
        "article_count": len(records),
        "observed_move_count": sum(item["observed_move_count"] for item in per_article),
        "moved_article_count": sum(1 for item in per_article if item["observed_move_count"] > 0),
        "situation_counts": dict(situation_counts),
        "moved_article_counts_by_situation": dict(moved_article_counts),
        "observed_move_counts_by_situation": dict(observed_move_counts),
        "per_article": per_article,
    }


def evaluate_week_directory(
    week_dir: Path,
    *,
    year: int,
    week: int,
    params: Optional[RedistributionParams] = None,
) -> Dict:
    """Evalueer één weekmap die een `combined.json` bevat."""
    combined_path = week_dir / "combined.json"
    records = load_combined_records(combined_path)
    return evaluate_combined_records(
        records,
        year=year,
        week=week,
        source=str(combined_path),
        params=params,
    )


def evaluate_dataset_weeks(
    data_root: Path,
    *,
    year: int,
    weeks: Iterable[int],
    params: Optional[RedistributionParams] = None,
) -> Dict:
    """Evalueer meerdere lokale weekmappen en aggregeer de uitkomsten."""
    if params is None:
        params = DEFAULT_PARAMS

    week_summaries = []
    total_situation_counts = Counter(_empty_situation_map())
    total_moved_article_counts = Counter(_empty_situation_map())
    total_observed_move_counts = Counter(_empty_situation_map())

    for week in weeks:
        summary = evaluate_week_directory(
            data_root / str(year) / f"week_{week}",
            year=year,
            week=week,
            params=params,
        )
        week_summaries.append(summary)
        total_situation_counts.update(summary["situation_counts"])
        total_moved_article_counts.update(summary["moved_article_counts_by_situation"])
        total_observed_move_counts.update(summary["observed_move_counts_by_situation"])

    return {
        "year": year,
        "weeks": week_summaries,
        "article_count": sum(summary["article_count"] for summary in week_summaries),
        "observed_move_count": sum(summary["observed_move_count"] for summary in week_summaries),
        "moved_article_count": sum(summary["moved_article_count"] for summary in week_summaries),
        "situation_counts": dict(total_situation_counts),
        "moved_article_counts_by_situation": dict(total_moved_article_counts),
        "observed_move_counts_by_situation": dict(total_observed_move_counts),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--weeks", type=int, nargs="+", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = evaluate_dataset_weeks(
        args.data_root,
        year=args.year,
        weeks=args.weeks,
    )

    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()

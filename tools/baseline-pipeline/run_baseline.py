from __future__ import annotations

import argparse
import json
from pathlib import Path

from legacy_redistribution.baseline import generate_baseline_proposal_from_record, proposal_to_dict


def move_key(move: dict) -> tuple:
    return (
        str(move["article_id"]) if "article_id" in move else str(move["volgnummer"]),
        str(move["from_store"]),
        str(move["to_store"]),
        str(move["size"]),
        int(move["qty"]),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    args = parser.parse_args()

    week_dir = args.data_root / str(args.year) / f"week_{args.week}"
    combined_path = week_dir / "combined.json"
    records = json.loads(combined_path.read_text(encoding="utf-8"))

    proposals = [
        proposal_to_dict(generate_baseline_proposal_from_record(record, batch_id=args.week))
        for record in records
    ]

    output_path = week_dir / "baseline_proposals.json"
    output_path.write_text(json.dumps(proposals, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "year": args.year,
        "week": args.week,
        "proposal_count": len(proposals),
        "articles_with_moves": sum(1 for proposal in proposals if proposal["total_moves"] > 0),
        "articles_without_moves": sum(1 for proposal in proposals if proposal["total_moves"] == 0),
    }

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
        "year": args.year,
        "week": args.week,
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
    evaluation_path = week_dir / "baseline_evaluation.json"
    evaluation_path.write_text(json.dumps(evaluation, indent=2, ensure_ascii=False), encoding="utf-8")

    summary["interpretation"] = "Observed decisions versus model-detected redistribution opportunities"
    summary["observed_move_count"] = total_observed_moves
    summary["model_opportunity_count"] = total_model_opportunities
    summary["overlap_move_count"] = total_overlap_moves
    summary["observed_opportunity_recall"] = evaluation["observed_opportunity_recall"]
    summary["model_overlap_ratio"] = evaluation["model_overlap_ratio"]
    summary["observed_only_count"] = evaluation["observed_only_count"]
    summary["model_only_count"] = evaluation["model_only_count"]

    summary_path = week_dir / "baseline_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()

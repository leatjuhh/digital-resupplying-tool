"""
Backtesting adapter: draait het DRT-algoritme op historische snapshot-data
en slaat de voorstellen op als drt_proposals.json per week.

Hierdoor kan evaluate_proposals.py (in tools/) de DRT-uitvoer
met dezelfde semantische maatstaf beoordelen als de externe baseline.

Gebruik (vanuit backend/ met de backend venv):
    venv\\Scripts\\python backtest_drt.py --week 12
    venv\\Scripts\\python backtest_drt.py --all
    venv\\Scripts\\python backtest_drt.py --week 12 13 14 16 --no-bundle
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent))

from redistribution.domain import ArticleStock, StoreInventory
from redistribution.constraints import RedistributionParams, get_size_order
from redistribution.adapter import detect_size_type
from redistribution.bundle_planner import generate_moves_for_article
from redistribution.bv_config import get_bv_config
from redistribution.store_config import is_redistribution_candidate
from redistribution.store_profiles import get_store_profile

DATA_ROOT = Path(__file__).parent / "algorithm_data" / "2026"


def snapshot_to_article(snap: dict, week: int) -> ArticleStock:
    """Bouw ArticleStock op vanuit snapshot-JSON (zonder database)."""
    article = ArticleStock(
        volgnummer=str(snap["article_id"]),
        omschrijving=snap.get("meta", {}).get("Omschrijving", ""),
        batch_id=week,
    )
    article.all_sizes = get_size_order(snap.get("sizes", []))
    article.size_type = detect_size_type(article.all_sizes)

    bv_cfg = get_bv_config()

    for store_id, store_data in snap.get("stores", {}).items():
        if not is_redistribution_candidate(store_id):
            continue

        inventory = {sz: int(store_data.get(sz, 0)) for sz in snap["sizes"]}
        sold = int(store_data.get("sold", 0))

        store_inv = StoreInventory(
            store_code=store_id,
            store_name=store_data.get("store_name", store_id),
            bv_name=bv_cfg.get_bv(store_id),
            inventory=inventory,
            sales={"TOTAL": sold} if sold > 0 else {},
        )

        profile = get_store_profile(store_id)
        store_inv.calculate_metrics(
            batch_total=0,
            max_capacity=profile.max_capacity if profile else 0,
            store_total=int(store_data.get("store_total_stock_week", 0)),
        )
        article.stores[store_id] = store_inv

    article.calculate_aggregates()
    return article


def backtest_week(week: int, params: RedistributionParams) -> int:
    week_dir = DATA_ROOT / f"week_{week}"
    records = json.loads((week_dir / "combined.json").read_text(encoding="utf-8"))

    proposals = []
    move_total = 0

    for record in records:
        snap = record.get("snapshot")
        if not snap:
            continue

        article = snapshot_to_article(snap, week)
        working_inv: Dict[str, Dict[str, int]] = {
            sc: dict(si.inventory) for sc, si in article.stores.items()
        }

        if params.enable_bundle_planner:
            moves, applied_rules = generate_moves_for_article(article, params, working_inv)
        else:
            from redistribution.algorithm import generate_moves_for_size
            moves = []
            for size in article.all_sizes:
                moves.extend(generate_moves_for_size(article, size, params, working_inv))
            applied_rules = ["Per-size greedy (fallback)"]

        proposals.append({
            "volgnummer": article.volgnummer,
            "article_name": article.omschrijving,
            "total_moves": len(moves),
            "applied_rules": applied_rules,
            "moves": [
                {
                    "from_store": m.from_store,
                    "to_store": m.to_store,
                    "size": m.size,
                    "qty": m.qty,
                }
                for m in moves
            ],
        })
        move_total += len(moves)

    output = week_dir / "drt_proposals.json"
    output.write_text(json.dumps(proposals, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Week {week}: {len(proposals)} artikelen, {move_total} moves → {output.name}")
    return move_total


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Draait DRT-algoritme op historische snapshots voor backtesting."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--week", type=int, nargs="+", metavar="W")
    group.add_argument("--all", action="store_true")
    parser.add_argument(
        "--no-bundle",
        action="store_true",
        help="Per-maat greedy in plaats van bundle-planner (vergelijkingsbasis)",
    )
    args = parser.parse_args()

    weeks = (
        sorted(int(p.name.split("_")[1]) for p in DATA_ROOT.iterdir()
               if p.is_dir() and p.name.startswith("week_"))
        if args.all
        else args.week
    )

    params = RedistributionParams()
    if args.no_bundle:
        params.enable_bundle_planner = False

    planner = "bundle-planner" if params.enable_bundle_planner else "per-maat greedy"
    print(f"DRT backtesting ({planner}):")
    for week in weeks:
        try:
            backtest_week(week, params)
        except FileNotFoundError as exc:
            print(f"  Week {week}: data niet gevonden ({exc})")


if __name__ == "__main__":
    main()

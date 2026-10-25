"""
Gedifferentieerde evaluatie van herverdelingsvoorstellen vs. handmatige ground truth.

Verbetert de bestaande exacte-match evaluatie met een semantische
kostenfunctie die domeinkennis meeweegt: maatcategorieën, filiaaltypen
en de logistieke richting van moves.

Gebruik:
    python tools/evaluate_proposals.py --week 12
    python tools/evaluate_proposals.py --week 12 13 14 16
    python tools/evaluate_proposals.py --all
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

DATA_ROOT = Path(__file__).parent.parent / "backend" / "algorithm_data" / "2026"

SIZE_ORDER = [
    "XXS", "XS", "XS/S", "S", "S/M", "M", "M/L",
    "L", "L/XL", "XL", "XL/XX", "XXL", "XXXL", "3XL", "4XL",
]
SIZE_CLASS_ORDER = {"klein": 0, "middel": 1, "groot": 2}

# Gewogen kosten per categorie (0 = perfect, 1 = totale miss)
COST = {
    "A": 0.00,  # Exacte treffer
    "B": 0.20,  # Juiste richting, andere maar geldige filialen
    "C": 0.50,  # Zelfde artikel+maat, suboptimale filiaalrichting
    "D": 0.70,  # Zelfde artikel, andere maat
    "E": 1.00,  # Volledig gemist
}


@dataclass
class Move:
    article_id: str
    from_store: str
    to_store: str
    size: str
    qty: int

    def key(self) -> tuple:
        return (self.article_id, self.from_store, self.to_store, self.size, self.qty)


@dataclass
class EvalResult:
    week: int
    total_gt: int = 0
    total_proposed: int = 0
    categories: dict = field(default_factory=lambda: defaultdict(int))
    per_article: dict = field(default_factory=dict)
    missed_by_size: dict = field(default_factory=lambda: defaultdict(int))
    spurious_count: int = 0


# ---------------------------------------------------------------------------
# Hulpfuncties
# ---------------------------------------------------------------------------

def size_distance(s1: str, s2: str) -> int:
    """Afstand tussen twee maten in de maatreeks (0 = gelijk, 99 = onbekend)."""
    try:
        return abs(SIZE_ORDER.index(s1) - SIZE_ORDER.index(s2))
    except ValueError:
        return 99


def store_similarity(store_a: str, store_b: str, profiles: dict) -> float:
    """
    Gelijkenis-score [0, 1] tussen twee filialen op basis van
    filiaalklasse (50%) en verkooprang (50%).
    """
    if store_a == store_b:
        return 1.0
    p_a = profiles.get(store_a)
    p_b = profiles.get(store_b)
    if not p_a or not p_b:
        return 0.3

    class_a = SIZE_CLASS_ORDER.get(p_a.get("size_class", ""), 1)
    class_b = SIZE_CLASS_ORDER.get(p_b.get("size_class", ""), 1)
    class_sim = 1.0 if class_a == class_b else (0.5 if abs(class_a - class_b) == 1 else 0.0)

    rank_a = p_a.get("sales_rank", 4)
    rank_b = p_b.get("sales_rank", 4)
    rank_sim = 1.0 - abs(rank_a - rank_b) / 7.0

    return 0.5 * class_sim + 0.5 * rank_sim


def is_valid_donor(snapshot: dict, store: str, size: str) -> bool:
    """Filiaal heeft >1 stuks van deze maat (kan doneren en houdt er zelf één over)."""
    return snapshot.get("stores", {}).get(store, {}).get(size, 0) > 1


def is_valid_receiver(snapshot: dict, store: str, size: str) -> bool:
    """Filiaal heeft 0 stuks van deze maat (ontvangt zinvol)."""
    return snapshot.get("stores", {}).get(store, {}).get(size, 0) == 0


# ---------------------------------------------------------------------------
# Categorie-toewijzing per GT-move
# ---------------------------------------------------------------------------

def categorize(
    gt: Move,
    proposed: list[Move],
    snapshot: dict,
    profiles: dict,
) -> tuple[str, Optional[Move]]:
    """
    Koppel een ground-truth move aan de best passende voorgestelde move
    en retourneer de foutcategorie plus die beste match.

    Categorieën:
      A  Exacte treffer
      B  Zelfde artikel+maat, beide filialen logistiek correct (surplus→deficit)
      C  Zelfde artikel+maat, maar filiaalrichting suboptimaal
      D  Zelfde artikel, andere maat
      E  Niet gevonden
    """
    if not proposed:
        return "E", None

    # A: exact
    for p in proposed:
        if p.key() == gt.key():
            return "A", p

    same_art = [p for p in proposed if p.article_id == gt.article_id]
    if not same_art:
        return "E", None

    same_size = [p for p in same_art if p.size == gt.size]

    if same_size:
        # B: richting correct (donor heeft surplus, receiver heeft 0)
        for p in same_size:
            if is_valid_donor(snapshot, p.from_store, p.size) and \
               is_valid_receiver(snapshot, p.to_store, p.size):
                return "B", p
        # C: richting suboptimaal
        return "C", same_size[0]

    # D: zelfde artikel, dichtstbijzijnde maat
    closest = min(same_art, key=lambda p: size_distance(p.size, gt.size))
    return "D", closest


# ---------------------------------------------------------------------------
# Data laden
# ---------------------------------------------------------------------------

PROPOSALS_FILE = {
    "baseline": "baseline_proposals.json",
    "drt": "drt_proposals.json",
}


def load_week(week: int, source: str = "baseline") -> tuple[list[Move], list[Move], dict]:
    week_dir = DATA_ROOT / f"week_{week}"

    raw_gt = json.loads((week_dir / "moves.json").read_text(encoding="utf-8"))
    gt_moves = [
        Move(
            article_id=str(m["article_id"]),
            from_store=str(m["from_store"]),
            to_store=str(m["to_store"]),
            size=str(m["size"]),
            qty=int(m["qty"]),
        )
        for m in raw_gt
    ]

    proposals_filename = PROPOSALS_FILE.get(source, "baseline_proposals.json")
    raw_proposals = json.loads((week_dir / proposals_filename).read_text(encoding="utf-8"))
    proposed_moves = [
        Move(
            article_id=str(proposal["volgnummer"]),
            from_store=str(m["from_store"]),
            to_store=str(m["to_store"]),
            size=str(m["size"]),
            qty=int(m["qty"]),
        )
        for proposal in raw_proposals
        for m in proposal.get("moves", [])
    ]

    snapshots = {
        str(s["article_id"]): s
        for s in json.loads((week_dir / "snapshots.json").read_text(encoding="utf-8"))
    }

    return gt_moves, proposed_moves, snapshots


def build_profiles(snapshots: dict) -> dict:
    """Aggregeer filiaalprofielen uit alle snapshot-records."""
    profiles: dict = {}
    for snapshot in snapshots.values():
        for store_id, store_data in snapshot.get("stores", {}).items():
            if store_id not in profiles:
                profiles[store_id] = {
                    "name": store_data.get("store_name", store_id),
                    "size_class": store_data.get("store_size_class", ""),
                    "sales_rank": store_data.get("store_sales_rank", 4),
                }
    return profiles


# ---------------------------------------------------------------------------
# Evaluatie
# ---------------------------------------------------------------------------

def evaluate_week(week: int, source: str = "baseline") -> EvalResult:
    gt_moves, proposed_moves, snapshots = load_week(week, source)
    profiles = build_profiles(snapshots)

    result = EvalResult(week=week, total_gt=len(gt_moves), total_proposed=len(proposed_moves))

    proposed_by_article: dict[str, list[Move]] = defaultdict(list)
    for p in proposed_moves:
        proposed_by_article[p.article_id].append(p)

    matched_proposed_keys: set = set()

    for gt in gt_moves:
        snapshot = snapshots.get(gt.article_id, {})
        art_proposed = proposed_by_article.get(gt.article_id, [])

        cat, best = categorize(gt, art_proposed, snapshot, profiles)
        result.categories[cat] += 1

        art_entry = result.per_article.setdefault(gt.article_id, defaultdict(int))
        art_entry[cat] += 1

        if cat == "E":
            result.missed_by_size[gt.size] += 1

        if best is not None:
            matched_proposed_keys.add(best.key())

    result.spurious_count = sum(
        1 for p in proposed_moves if p.key() not in matched_proposed_keys
    )
    return result


def semantic_recall(r: EvalResult) -> float:
    found = r.categories["A"] + r.categories["B"]
    return found / r.total_gt if r.total_gt else 0.0


def weighted_cost(r: EvalResult) -> float:
    total = sum(COST.get(cat, 1.0) * n for cat, n in r.categories.items())
    return total / r.total_gt if r.total_gt else 1.0


# ---------------------------------------------------------------------------
# Rapport
# ---------------------------------------------------------------------------

def print_report(r: EvalResult) -> None:
    gt = r.total_gt
    prop = r.total_proposed
    cats = r.categories

    print(f"\n{'='*58}")
    print(f"  EVALUATIE WEEK {r.week}")
    print(f"{'='*58}")
    print(f"  Ground truth moves:    {gt:5d}")
    print(f"  Baseline voorstellen:  {prop:5d}")

    print("\n  HUIDIGE MAATSTAF (exact match):")
    a = cats.get("A", 0)
    print(f"    Recall:    {a/gt*100:5.1f}%  ({a}/{gt})")
    if prop:
        print(f"    Precision: {a/prop*100:5.1f}%  ({a}/{prop})")

    print("\n  NIEUWE MAATSTAF (semantisch):")
    print(f"    Semantische recall:   {semantic_recall(r)*100:5.1f}%  (cat A+B / GT)")
    print(f"    Gewogen kostenscore:  {weighted_cost(r):.3f}  (0=perfect, 1=alles gemist)")

    print("\n  FOUTCATEGORIEËN:")
    labels = {
        "A": "Exacte treffer",
        "B": "Juiste richting, andere filialen",
        "C": "Zelfde maat, suboptimale filialen",
        "D": "Zelfde artikel, andere maat",
        "E": "Volledig gemist",
    }
    for cat, label in labels.items():
        n = cats.get(cat, 0)
        bar = "█" * int(n / gt * 30)
        print(f"    {cat}  {label:<36} {n:4d}  ({n/gt*100:5.1f}%)  {bar}")
    print(f"    F  {'Onterecht voorgesteld':<36} {r.spurious_count:4d}")

    if r.missed_by_size:
        print("\n  MEEST VOLLEDIG GEMISTE MATEN (cat E):")
        for size, count in sorted(r.missed_by_size.items(), key=lambda x: -x[1])[:6]:
            print(f"    {size:<8} {count}")

    # Top 5 artikelen met meeste misses
    miss_per_article = {
        art: d.get("E", 0) for art, d in r.per_article.items() if d.get("E", 0) > 0
    }
    if miss_per_article:
        top5 = sorted(miss_per_article.items(), key=lambda x: -x[1])[:5]
        print("\n  TOP-5 ARTIKELEN MET MEESTE MISSES:")
        for art, n in top5:
            print(f"    Artikel {art:<10} {n} gemiste moves")
    print()


def print_summary(results: list[EvalResult]) -> None:
    total_gt = sum(r.total_gt for r in results)
    total_a = sum(r.categories.get("A", 0) for r in results)
    total_ab = sum(r.categories.get("A", 0) + r.categories.get("B", 0) for r in results)
    avg_cost = sum(weighted_cost(r) for r in results) / len(results)

    print(f"{'='*58}")
    print("  SAMENVATTING ALLE WEKEN")
    print(f"{'='*58}")
    print(f"  Exact recall:          {total_a/total_gt*100:5.1f}%  ({total_a}/{total_gt})")
    print(f"  Semantische recall:    {total_ab/total_gt*100:5.1f}%  ({total_ab}/{total_gt})")
    print(f"  Gem. kostenscore:      {avg_cost:.3f}")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gedifferentieerde evaluatie van herverdelingsvoorstellen."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--week", type=int, nargs="+", metavar="W", help="Weeknummer(s)")
    group.add_argument("--all", action="store_true", help="Evalueer alle beschikbare weken")
    parser.add_argument(
        "--source",
        choices=["baseline", "drt"],
        default="baseline",
        help="Voorstellenbron: 'baseline' (extern) of 'drt' (backtest_drt.py uitvoer)",
    )
    args = parser.parse_args()

    if args.all:
        weeks = sorted(
            int(p.name.split("_")[1])
            for p in DATA_ROOT.iterdir()
            if p.is_dir() and p.name.startswith("week_")
        )
    else:
        weeks = args.week

    print(f"Bron: {args.source}")
    results = []
    for week in weeks:
        try:
            r = evaluate_week(week, args.source)
            print_report(r)
            results.append(r)
        except FileNotFoundError as exc:
            print(f"Week {week}: data niet gevonden ({exc})")

    if len(results) > 1:
        print_summary(results)


if __name__ == "__main__":
    main()

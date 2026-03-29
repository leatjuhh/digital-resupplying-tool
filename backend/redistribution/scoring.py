"""
Scoring systeem voor herverdelingsmoves
Score is gebaseerd op demand-verschil: verplaats van lage naar hoge vraag.
"""

from typing import List
from .domain import Move, StoreInventory, ArticleStock
from .constraints import RedistributionParams


def calculate_move_score(
    move: Move,
    from_store: StoreInventory,
    to_store: StoreInventory,
    article: ArticleStock,
    params: RedistributionParams,
) -> float:
    """
    Bereken score voor een move op basis van demand-verschil.

    Moves van lage-demand naar hoge-demand winkels scoren hoger.
    Score range: 0.0 - 1.0
    """
    demand_diff = to_store.demand_score - from_store.demand_score

    # Normaliseer naar 0.0 - 1.0: demand_diff zit tussen -1.0 en +1.0
    score = max(0.0, min(1.0, 0.5 + (demand_diff / 2.0)))

    move.score = score

    # Genereer uitleg
    if demand_diff > 0.1:
        to_pct = to_store.demand_score * 100
        move.reason = f"Hoge demand in doel winkel ({to_pct:.0f}% verkocht)"
    elif demand_diff < -0.1:
        from_pct = from_store.demand_score * 100
        move.reason = f"Lage demand in bron winkel ({from_pct:.0f}% verkocht)"
    else:
        move.reason = "Balancering voorraad"

    return score


def filter_low_quality_moves(
    moves: List[Move],
    min_score: float = 0.2,
) -> List[Move]:
    """Filter moves met te lage score"""
    return [m for m in moves if m.score >= min_score]

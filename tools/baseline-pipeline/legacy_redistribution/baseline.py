"""
Alternatieve baseline herverdelingslogica.

Doel:
- compatibel blijven met DRT Proposal/Move output
- niet automatisch "optimaal verdeeld" claimen als er geen voorstel uitkomt
- expliciet sturen op verkoop, seriebehoud en ontbrekende maten
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .adapter import article_from_combined_record
from .constraints import DEFAULT_PARAMS, RedistributionParams
from .domain import ArticleStock, Move, Proposal, StoreInventory
from .scoring import calculate_move_score


@dataclass
class RuleEvaluation:
    """
    Interne evaluatie van donor- of ontvangergeschiktheid.
    """

    store_code: str
    score: float
    reasons: List[str]


def _series_width(inventory: Dict[str, int], all_sizes: List[str]) -> int:
    best = 0
    current = 0
    for size in all_sizes:
        if inventory.get(size, 0) > 0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def _would_break_sequence(store: StoreInventory, article: ArticleStock, size: str) -> bool:
    sequences = article.size_sequences.get(store.store_code, [])
    return any(sequence.would_break_on_removal(size) for sequence in sequences)


def _donor_score(
    store: StoreInventory,
    article: ArticleStock,
    size: str,
) -> Optional[RuleEvaluation]:
    qty = store.inventory.get(size, 0)
    if qty <= 1:
        return None

    remaining_total = store.total_inventory - 1
    remaining_size_count = sum(
        1
        for candidate_size, candidate_qty in store.inventory.items()
        if candidate_qty - (1 if candidate_size == size else 0) > 0
    )

    if remaining_total < 3:
        return None
    if remaining_size_count < 3:
        return None

    score = 0.0
    reasons: List[str] = []

    if qty >= 3:
        score += 2.0
        reasons.append("ruime voorraad in donor")
    elif qty == 2:
        score += 1.0
        reasons.append("dubbele maat in donor")

    if store.total_sales == 0:
        score += 2.0
        reasons.append("geen verkoop in donor")
    else:
        score += max(0.0, 1.5 - store.demand_score * 2)
        if store.demand_score < 0.35:
            reasons.append("lage demand in donor")

    if _would_break_sequence(store, article, size):
        score -= 2.5
        reasons.append("zou maatserie breken")

    if qty - 1 == 0:
        score -= 4.0
        reasons.append("laatste maat zou verdwijnen")

    if score <= 0:
        return None

    return RuleEvaluation(store.store_code, score, reasons)


def _receiver_score(
    store: StoreInventory,
    article: ArticleStock,
    size: str,
) -> Optional[RuleEvaluation]:
    qty = store.inventory.get(size, 0)
    if qty > 0:
        return None

    score = 0.0
    reasons: List[str] = []

    if store.total_sales > 0:
        score += min(3.0, store.total_sales / 2)
        reasons.append("verkoop in ontvanger")

    before_width = _series_width(store.inventory, article.all_sizes)
    hypothetical_inventory = dict(store.inventory)
    hypothetical_inventory[size] = hypothetical_inventory.get(size, 0) + 1
    after_width = _series_width(hypothetical_inventory, article.all_sizes)

    if after_width > before_width:
        score += 2.0
        reasons.append("verbetert maatserie")

    if store.total_inventory < 3:
        score += 1.5
        reasons.append("lage totale winkelvoorraad")

    size_index = article.all_sizes.index(size) if size in article.all_sizes else -1
    if 0 < size_index < len(article.all_sizes) - 1:
        score += 0.5
        reasons.append("middenmaat ontbreekt")

    if score <= 0:
        return None

    return RuleEvaluation(store.store_code, score, reasons)


def _select_candidates(
    article: ArticleStock,
    size: str,
) -> Tuple[List[RuleEvaluation], List[RuleEvaluation]]:
    donors: List[RuleEvaluation] = []
    receivers: List[RuleEvaluation] = []

    for store in article.stores.values():
        donor_eval = _donor_score(store, article, size)
        if donor_eval:
            donors.append(donor_eval)

        receiver_eval = _receiver_score(store, article, size)
        if receiver_eval:
            receivers.append(receiver_eval)

    donors.sort(key=lambda evaluation: evaluation.score, reverse=True)
    receivers.sort(key=lambda evaluation: evaluation.score, reverse=True)
    return donors, receivers


def generate_baseline_moves_for_article(
    article: ArticleStock,
    params: Optional[RedistributionParams] = None,
) -> List[Move]:
    """
    Genereer baseline moves voor een artikel.
    """
    if params is None:
        params = DEFAULT_PARAMS

    moves: List[Move] = []
    working_inventory = {
        store_code: dict(store.inventory)
        for store_code, store in article.stores.items()
    }

    for size in article.all_sizes:
        article_state = ArticleStock(
            volgnummer=article.volgnummer,
            omschrijving=article.omschrijving,
            batch_id=article.batch_id,
            stores={},
            all_sizes=article.all_sizes,
            size_type=article.size_type,
        )

        for store_code, original_store in article.stores.items():
            cloned_store = StoreInventory(
                store_code=original_store.store_code,
                store_name=original_store.store_name,
                bv_name=original_store.bv_name,
                inventory=dict(working_inventory[store_code]),
                sales=dict(original_store.sales),
            )
            cloned_store.calculate_metrics()
            article_state.stores[store_code] = cloned_store
        article_state.calculate_aggregates()
        article_state.size_sequences = article.size_sequences

        donors, receivers = _select_candidates(article_state, size)

        used_receivers: set[str] = set()
        for donor_eval in donors:
            donor = article_state.stores[donor_eval.store_code]
            for receiver_eval in receivers:
                if receiver_eval.store_code in used_receivers:
                    continue

                receiver = article_state.stores[receiver_eval.store_code]
                if donor.store_code == receiver.store_code:
                    continue
                if donor.inventory.get(size, 0) <= 1:
                    continue
                if receiver.inventory.get(size, 0) > 0:
                    continue

                move = Move(
                    volgnummer=article_state.volgnummer,
                    size=size,
                    from_store=donor.store_code,
                    from_store_name=donor.store_name,
                    to_store=receiver.store_code,
                    to_store_name=receiver.store_name,
                    qty=1,
                )
                calculate_move_score(move, donor, receiver, article_state, params)
                move.score += donor_eval.score + receiver_eval.score
                move.reason = "; ".join(donor_eval.reasons + receiver_eval.reasons)

                moves.append(move)
                used_receivers.add(receiver.store_code)
                working_inventory[donor.store_code][size] -= 1
                working_inventory[receiver.store_code][size] += 1
                break

    moves.sort(key=lambda move: move.score, reverse=True)
    return moves


def generate_baseline_proposal_from_record(
    record: Dict,
    params: Optional[RedistributionParams] = None,
    batch_id: int = 0,
) -> Proposal:
    """
    Genereer Proposal op basis van een gecombineerd weekrecord.
    """
    if params is None:
        params = DEFAULT_PARAMS

    article = article_from_combined_record(record, batch_id=batch_id)
    moves = generate_baseline_moves_for_article(article, params=params)

    if moves:
        reason = (
            f"Baseline herverdeling voor {len(moves)} moves op basis van verkoop, "
            "seriebehoud en ontbrekende maten."
        )
        applied_rules = [
            "Sales-first Baseline",
            "Sequence Protection",
            "Missing Size Recovery",
            "No False Optimal Label",
        ]
    else:
        reason = (
            "Geen voorstel gegenereerd door de huidige baseline-regels. "
            "Dit betekent niet automatisch dat het artikel optimaal verdeeld is; "
            "handmatige beoordeling blijft nodig."
        )
        applied_rules = [
            "Sales-first Baseline",
            "Sequence Protection",
            "Manual Review Required",
        ]

    proposal = Proposal(
        volgnummer=article.volgnummer,
        article_name=article.omschrijving,
        batch_id=batch_id,
        moves=moves,
        status="pending",
        reason=reason,
        applied_rules=applied_rules,
    )
    proposal.calculate_aggregates()
    return proposal


def proposal_to_dict(proposal: Proposal) -> Dict:
    """
    Serialize Proposal naar JSON-geschikte dict.
    """
    return {
        "volgnummer": proposal.volgnummer,
        "article_name": proposal.article_name,
        "batch_id": proposal.batch_id,
        "status": proposal.status,
        "reason": proposal.reason,
        "applied_rules": proposal.applied_rules,
        "total_moves": proposal.total_moves,
        "total_quantity": proposal.total_quantity,
        "stores_affected": sorted(proposal.stores_affected),
        "moves": [
            {
                "volgnummer": move.volgnummer,
                "size": move.size,
                "from_store": move.from_store,
                "from_store_name": move.from_store_name,
                "to_store": move.to_store,
                "to_store_name": move.to_store_name,
                "qty": move.qty,
                "score": move.score,
                "reason": move.reason,
            }
            for move in proposal.moves
        ],
    }


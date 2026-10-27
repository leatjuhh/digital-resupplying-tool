"""Legacy per-maat greedy-planner (Fase 3, PR-022).

Het oude, demand-gedreven per-maat-pad plus de BV-consolidatie. Alleen actief
wanneer de feature-flag `enable_bundle_planner=False` de nieuwe bundle-planner
uitzet; bewaard als fallback. De actieve planner staat in bundle_planner.py.
"""
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from .domain import ArticleStock, Move, StoreInventory
from .constraints import RedistributionParams
from .bv_config import BVConfig, validate_bv_move
from .scoring import calculate_move_score
from .sequence import _series_width

logger = logging.getLogger(__name__)


def _would_break_sequence(inventory: Dict[str, int], size: str, all_sizes: List[str]) -> bool:
    """Check of het weghalen van de laatste stuk van een maat een aaneengesloten reeks breekt."""
    if inventory.get(size, 0) != 1:
        return False
    before = _series_width(inventory, all_sizes)
    hyp = dict(inventory)
    hyp[size] = 0
    return _series_width(hyp, all_sizes) < before


def _would_improve_sequence(inventory: Dict[str, int], size: str, all_sizes: List[str]) -> bool:
    """Check of toevoeging van een maat de aaneengesloten reeks verbetert."""
    before = _series_width(inventory, all_sizes)
    hyp = dict(inventory)
    hyp[size] = hyp.get(size, 0) + 1
    return _series_width(hyp, all_sizes) > before


def _score_as_donor(
    store: StoreInventory,
    size: str,
    params: RedistributionParams,
    all_sizes: List[str],
    working_inv: Dict[str, int],
) -> Optional[Tuple[float, int]]:
    """
    Evalueer donorgeschiktheid voor een maat op basis van werkende voorraad.
    Geeft (score, beschikbaar) of None als niet geschikt.
    """
    qty = working_inv.get(size, 0)
    if qty <= 0:
        return None

    score = 0.0

    if qty >= 3:
        score += 2.0
    elif qty == 2:
        score += 1.0
    # qty == 1: geen bonus of penalty — demand bepaalt of donatie zin heeft

    if store.total_sales == 0:
        score += 2.0
    else:
        score += max(0.0, 1.5 - store.demand_score * 2)

    if _would_break_sequence(working_inv, size, all_sizes):
        # Niet-verkopende winkels: serie-behoud minder relevant
        score -= 0.5 if store.total_sales == 0 else 2.5

    # Capaciteitspositie: volle winkel is eerder donor (tiebreaker ±0.75)
    if store.capacity_ratio > 0:
        score += (store.capacity_ratio - 0.5) * 1.5

    if score <= 0:
        return None

    return (score, max(1, qty - 1))


def _score_as_receiver(
    store: StoreInventory,
    size: str,
    all_sizes: List[str],
    working_inv: Dict[str, int],
) -> Optional[float]:
    """
    Evalueer ontvangergeschiktheid voor een maat op basis van werkende voorraad.
    Geeft score of None als niet geschikt.
    """
    if working_inv.get(size, 0) > 0:
        return None

    score = 0.0

    if store.total_sales > 0:
        score += min(3.0, store.total_sales / 2)

    if _would_improve_sequence(working_inv, size, all_sizes):
        score += 2.0

    current_total = sum(v for v in working_inv.values() if v > 0)
    if current_total < 3:
        score += 1.5

    size_idx = all_sizes.index(size) if size in all_sizes else -1
    if 0 < size_idx < len(all_sizes) - 1:
        score += 0.5

    # Capaciteitspositie: lege winkel ontvangt eerder, volle winkel minder (tiebreaker ±0.75)
    if store.capacity_ratio > 0:
        score += (0.5 - store.capacity_ratio) * 1.5

    if score <= 0:
        return None

    return score


def generate_moves_for_size(
    article: ArticleStock,
    size: str,
    params: RedistributionParams,
    working_inventory: Dict[str, Dict[str, int]],
    bv_config: Optional[BVConfig] = None,
) -> List[Move]:
    """
    Genereer moves voor één specifieke maat (demand-gedreven, baseline-stijl).

    Donors: winkel met >= 2 stuks, voldoende totaalvoorraad, lage demand.
    Ontvangers: winkel met 0 stuks, hoge demand of serie-verbetering.
    Elke ontvanger krijgt maximaal 1 stuk per maat per pass.
    Werkende voorraad wordt direct bijgehouden zodat latere maten dit meenemen.
    """
    donors: List[Tuple[str, int, float]] = []
    receivers: List[Tuple[str, float]] = []

    for store_code, store_inv in article.stores.items():
        wk_inv = working_inventory[store_code]

        donor_result = _score_as_donor(store_inv, size, params, article.all_sizes, wk_inv)
        if donor_result:
            score, available = donor_result
            donors.append((store_code, available, score))

        recv_score = _score_as_receiver(store_inv, size, article.all_sizes, wk_inv)
        if recv_score is not None:
            receivers.append((store_code, recv_score))

    donors.sort(key=lambda x: x[2], reverse=True)
    receivers.sort(key=lambda x: x[1], reverse=True)

    if not donors or not receivers:
        return []

    moves: List[Move] = []
    used_receivers: set = set()

    for from_store, _available, _donor_score in donors:
        from_store_inv = article.stores[from_store]

        for to_store, _recv_score in receivers:
            if to_store in used_receivers:
                continue
            if from_store == to_store:
                continue
            # Niet-verkopende donor mag zijn laatste stuk weggeven;
            # verkopende donor behoudt altijd minstens 1.
            min_keep = 0 if from_store_inv.total_sales == 0 else 1
            if working_inventory[from_store].get(size, 0) <= min_keep:
                break

            if params.enforce_bv_separation:
                is_valid, _reason = validate_bv_move(
                    from_store, to_store, params.enforce_bv_separation, config=bv_config
                )
                if not is_valid:
                    continue

            to_store_inv = article.stores[to_store]

            move = Move(
                volgnummer=article.volgnummer,
                size=size,
                from_store=from_store,
                from_store_name=from_store_inv.store_name,
                to_store=to_store,
                to_store_name=to_store_inv.store_name,
                qty=1,
                from_bv=from_store_inv.bv_name,
                to_bv=to_store_inv.bv_name,
            )

            calculate_move_score(move, from_store_inv, to_store_inv, article, params)
            moves.append(move)

            working_inventory[from_store][size] -= 1
            working_inventory[to_store][size] = working_inventory[to_store].get(size, 0) + 1
            used_receivers.add(to_store)
            # Geen break — donor mag meerdere receivers bedienen zolang hij
            # genoeg voorraad heeft (check bovenaan inner loop via working_inv)

    return moves


# ============================================================================
# (legacy) check_and_consolidate_fragmented_bv — nu alleen gebruikt als
# feature-flag `enable_bundle_planner=False` de nieuwe planner uitzet.
# ============================================================================


def check_and_consolidate_fragmented_bv(
    article: ArticleStock,
    params: RedistributionParams,
) -> Tuple[List[Move], List[str]]:
    """
    Check of een BV gefragmenteerd is (≤ min_items_per_store stuks totaal)
    en genereer consolidatie moves naar best verkopende winkel.
    """
    if not params.enable_bv_consolidation:
        return [], []

    moves = []
    applied_rules = []

    # Groepeer voorraad per BV
    bv_inventory: Dict[str, Dict[str, Dict[str, int]]] = defaultdict(lambda: defaultdict(dict))
    bv_stores: Dict[str, List[str]] = defaultdict(list)

    for store_code, store_inv in article.stores.items():
        bv_name = store_inv.bv_name
        if not bv_name:
            continue
        bv_stores[bv_name].append(store_code)
        for size, qty in store_inv.inventory.items():
            if qty > 0:
                bv_inventory[bv_name][store_code][size] = qty

    for bv_name, stores_in_bv in bv_stores.items():
        if len(stores_in_bv) < 2:
            continue

        total_inventory = sum(
            sum(sizes.values())
            for store_sizes in bv_inventory[bv_name].values()
            for sizes in [store_sizes]
        )

        if total_inventory > params.min_items_per_store:
            continue

        logger.info(
            f"[BV_CONSOLIDATION] BV {bv_name} has only {total_inventory} items "
            f"(≤ {params.min_items_per_store}), consolidating..."
        )

        # Bepaal beste winkel: hoogste verkoop, dan hoogste voorraad
        best_store = None
        best_score = -1

        for store_code in stores_in_bv:
            store_inv = article.stores[store_code]
            score = (store_inv.total_sales * 1000) + (store_inv.total_inventory * 10)
            if score > best_score or (score == best_score and (best_store is None or store_code < best_store)):
                best_score = score
                best_store = store_code

        if not best_store:
            continue

        for from_store in stores_in_bv:
            if from_store == best_store:
                continue

            from_store_inv = article.stores[from_store]
            to_store_inv = article.stores[best_store]

            for size, qty in from_store_inv.inventory.items():
                if qty <= 0:
                    continue

                move = Move(
                    volgnummer=article.volgnummer,
                    size=size,
                    from_store=from_store,
                    from_store_name=from_store_inv.store_name,
                    to_store=best_store,
                    to_store_name=to_store_inv.store_name,
                    qty=qty,
                    from_bv=from_store_inv.bv_name,
                    to_bv=to_store_inv.bv_name,
                    reason=f"BV Consolidatie: {bv_name} heeft slechts {total_inventory} items",
                )

                calculate_move_score(move, from_store_inv, to_store_inv, article, params)
                move.score = max(move.score, 0.8)  # Minimum score voor consolidatie

                moves.append(move)

        if moves:
            applied_rules.append(f"BV Consolidation (≤{params.min_items_per_store} items)")

    return moves, applied_rules

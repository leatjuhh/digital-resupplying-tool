"""Artikel-level bundle-planner met harde min-3 regel (Fase 3, PR-022).

De actieve herverdelingsplanner: verdeelt de voorraad per BV-groep zó dat elke
winkel óf 0 óf >= min_items_per_receiver stuks houdt. BV-configuratie wordt via
dependency injection meegegeven (Fase 3.3).
"""
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from .domain import ArticleStock, Move
from .constraints import RedistributionParams
from .bv_config import BVConfig, validate_bv_move
from .scoring import calculate_move_score
from .sequence import _series_width

logger = logging.getLogger(__name__)


# ============================================================================
# BUNDLE PLANNER — Artikel-level herverdeling met harde min-3 regel
# ============================================================================
#
# Vervangt de oude per-maat greedy door een artikel-level planner die
# structureel garandeert dat elke winkel óf 0 stuks, óf ≥ min_items_per_receiver
# (default 3) heeft na herverdeling.
#
# Algoritme per BV-groep (of over alle winkels als BV-separation uit staat):
#   1. Pool = totale voorraad in de groep.
#   2. Pool < min_qty  → alles naar top-ranked winkel (R1-uitzondering).
#   3. Anders: rank winkels, pak floor(pool / min_qty) receivers.
#   4. Voor elke pick (in rangorde): `_assign_bundle` tot receiver op min_qty.
#   5. `_drain_non_receivers`: elke niet-gekozen winkel naar 0.
#
# Receiver-ranking (composite sort key):
#   (-total_sales, -series_width, -total_inventory, +store_total_inventory,
#    +store_code)
# Dit implementeert R2 (verkoop eerst, dan complete serie, dan volume) en R3
# (bij gelijkspel wint lágere totale winkelvoorraad — tiebreaker-data komt uit
# PDFBatch.extra_data bij batch-aanmaak).
# ============================================================================


def _make_bundle_move(
    article: ArticleStock,
    from_store: str,
    to_store: str,
    size: str,
    working_inv: Dict[str, Dict[str, int]],
    params: RedistributionParams,
    reason: str,
) -> Move:
    """Creëer één Move, werk working_inv bij, en zet een consolidation-score."""
    from_inv = article.stores[from_store]
    to_inv = article.stores[to_store]

    move = Move(
        volgnummer=article.volgnummer,
        size=size,
        from_store=from_store,
        from_store_name=from_inv.store_name,
        to_store=to_store,
        to_store_name=to_inv.store_name,
        qty=1,
        from_bv=from_inv.bv_name,
        to_bv=to_inv.bv_name,
        reason=reason,
    )
    calculate_move_score(move, from_inv, to_inv, article, params)
    # Bundle-planner moves zijn per definitie gewenst (regel-afgedwongen);
    # voorkom dat de low-score filter ze weggooit.
    move.score = max(move.score, 0.8)

    working_inv[from_store][size] = working_inv[from_store].get(size, 0) - 1
    working_inv[to_store][size] = working_inv[to_store].get(size, 0) + 1
    return move


def _group_by_bv(article: ArticleStock) -> Dict[str, List[str]]:
    """Groepeer store_codes per BV. Winkels zonder BV krijgen eigen groep '_none'."""
    groups: Dict[str, List[str]] = defaultdict(list)
    for code, store in article.stores.items():
        key = store.bv_name or "_none"
        groups[key].append(code)
    return dict(groups)


def _group_total(
    store_codes: List[str], working_inv: Dict[str, Dict[str, int]]
) -> int:
    return sum(
        qty
        for sc in store_codes
        for qty in working_inv.get(sc, {}).values()
        if qty > 0
    )


def _store_inv_total(working_inv: Dict[str, Dict[str, int]], store: str) -> int:
    return sum(q for q in working_inv.get(store, {}).values() if q > 0)


def _series_width_inv(working_inv_store: Dict[str, int], all_sizes: List[str]) -> int:
    return _series_width(working_inv_store, all_sizes)


def _rank_receivers(
    article: ArticleStock,
    store_codes: List[str],
    working_inv: Dict[str, Dict[str, int]],
) -> List[str]:
    """Rangschik winkels als potentiële receivers volgens R2 + R3."""
    def sort_key(sc: str):
        store = article.stores[sc]
        inv = working_inv[sc]
        return (
            -store.total_sales,                        # R2a: verkoop eerst
            -_series_width_inv(inv, article.all_sizes),  # R2b: complete serie
            -sum(inv.values()),                        # R2c: meeste stuks
            store.store_total_inventory,              # R3: lager = receiver
            sc,                                        # deterministisch
        )

    return sorted(store_codes, key=sort_key)


def _donor_order(
    picks: List[str],
    all_stores: List[str],
    working_inv: Dict[str, Dict[str, int]],
    min_qty: int,
    receiver: str,
) -> List[str]:
    """Geef donor-volgorde: non-picks eerst (moeten hoe dan ook leeg),
    daarna picks met surplus boven min_qty. Receiver zelf uitgesloten.
    """
    non_picks = [s for s in all_stores if s not in picks and s != receiver]
    pick_donors = [
        s for s in picks
        if s != receiver and _store_inv_total(working_inv, s) > min_qty
    ]
    return [s for s in non_picks if _store_inv_total(working_inv, s) > 0] + pick_donors


def _bv_compatible(
    from_store: str,
    to_store: str,
    params: RedistributionParams,
    bv_config: Optional[BVConfig] = None,
) -> bool:
    if not params.enforce_bv_separation:
        return True
    valid, _ = validate_bv_move(from_store, to_store, True, config=bv_config)
    return valid


def _assign_bundle(
    article: ArticleStock,
    receiver: str,
    picks: List[str],
    all_stores: List[str],
    working_inv: Dict[str, Dict[str, int]],
    params: RedistributionParams,
    min_qty: int,
    bv_config: Optional[BVConfig] = None,
) -> List[Move]:
    """Voed receiver tot ≥ min_qty stuks, bij voorkeur met een aaneengesloten serie."""
    moves: List[Move] = []
    recv_inv = working_inv[receiver]
    guard = 0

    while _store_inv_total(working_inv, receiver) < min_qty:
        guard += 1
        if guard > 200:  # vangnet tegen infinite loops
            logger.warning(
                f"[BUNDLE] Guard breek in _assign_bundle voor {article.volgnummer}/{receiver}"
            )
            break

        # Voorkeur-maten: nog niet aanwezig (serie-uitbreiding), in size-order.
        missing = [sz for sz in article.all_sizes if recv_inv.get(sz, 0) == 0]
        fallback = [sz for sz in article.all_sizes if recv_inv.get(sz, 0) > 0]
        size_preference = missing + fallback

        moved = False
        donors = _donor_order(picks, all_stores, working_inv, min_qty, receiver)

        for size in size_preference:
            for donor in donors:
                if working_inv[donor].get(size, 0) <= 0:
                    continue
                # Pick-donor mag niet onder min_qty zakken
                if donor in picks and _store_inv_total(working_inv, donor) - 1 < min_qty:
                    continue
                if not _bv_compatible(donor, receiver, params, bv_config):
                    continue
                moves.append(_make_bundle_move(
                    article, donor, receiver, size, working_inv, params,
                    reason=f"Bundle naar {article.stores[receiver].store_name} (≥{min_qty})",
                ))
                moved = True
                break
            if moved:
                break

        if not moved:
            # Geen valide donor/maat meer — stop, drain handelt resten af
            break

    return moves


def _drain_non_receivers(
    article: ArticleStock,
    picks: List[str],
    all_stores: List[str],
    working_inv: Dict[str, Dict[str, int]],
    params: RedistributionParams,
    bv_config: Optional[BVConfig] = None,
) -> List[Move]:
    """Forceer elke niet-pick winkel naar 0: resterende stuks naar picks."""
    moves: List[Move] = []
    non_picks = [s for s in all_stores if s not in picks]

    for donor in non_picks:
        for size in list(article.all_sizes):
            while working_inv[donor].get(size, 0) > 0:
                target = next(
                    (p for p in picks if _bv_compatible(donor, p, params, bv_config)),
                    None,
                )
                if target is None:
                    # Geen BV-compatibele pick → stock blijft staan (vangnet)
                    logger.warning(
                        f"[BUNDLE] Geen BV-compatibele pick voor drain "
                        f"{article.volgnummer}/{donor} size={size}"
                    )
                    break
                moves.append(_make_bundle_move(
                    article, donor, target, size, working_inv, params,
                    reason=f"Leeghalen {article.stores[donor].store_name} (<{params.min_items_per_receiver})",
                ))
    return moves


def _consolidate_all_to_top(
    article: ArticleStock,
    store_codes: List[str],
    working_inv: Dict[str, Dict[str, int]],
    params: RedistributionParams,
    bv_config: Optional[BVConfig] = None,
) -> List[Move]:
    """Totaal in groep < min_qty: alles naar top-ranked winkel."""
    ranked = _rank_receivers(article, store_codes, working_inv)
    if not ranked:
        return []
    top = ranked[0]

    moves: List[Move] = []
    for donor in store_codes:
        if donor == top:
            continue
        if not _bv_compatible(donor, top, params, bv_config):
            continue
        for size in list(article.all_sizes):
            while working_inv[donor].get(size, 0) > 0:
                moves.append(_make_bundle_move(
                    article, donor, top, size, working_inv, params,
                    reason=f"Volledige consolidatie naar {article.stores[top].store_name} (pool <{params.min_items_per_receiver})",
                ))
    return moves


def _plan_group(
    article: ArticleStock,
    store_codes: List[str],
    params: RedistributionParams,
    working_inv: Dict[str, Dict[str, int]],
    bv_config: Optional[BVConfig] = None,
) -> List[Move]:
    """Plan herverdeling voor één BV-groep (of alle winkels als cross-BV)."""
    min_qty = params.min_items_per_receiver
    pool = _group_total(store_codes, working_inv)

    if pool == 0:
        return []

    if pool < min_qty:
        return _consolidate_all_to_top(article, store_codes, working_inv, params, bv_config)

    # Aantal receivers = hoeveel bundels van min_qty passen
    max_picks = pool // min_qty
    ranked = _rank_receivers(article, store_codes, working_inv)
    picks = ranked[:max_picks]

    moves: List[Move] = []
    for recv in picks:
        moves.extend(_assign_bundle(
            article, recv, picks, store_codes, working_inv, params, min_qty, bv_config
        ))

    moves.extend(_drain_non_receivers(
        article, picks, store_codes, working_inv, params, bv_config
    ))
    return moves


def generate_moves_for_article(
    article: ArticleStock,
    params: RedistributionParams,
    working_inv: Dict[str, Dict[str, int]],
    bv_config: Optional[BVConfig] = None,
) -> Tuple[List[Move], List[str]]:
    """Artikel-level bundle-planner. Retourneert (moves, applied_rules).

    `bv_config` kan expliciet worden meegegeven (dependency injection); bij None
    wordt de gedeelde read-only BV-configuratie gebruikt.
    """
    applied_rules: List[str] = []

    if params.enforce_bv_separation:
        groups = _group_by_bv(article)
        all_moves: List[Move] = []
        for _bv_name, store_codes in groups.items():
            all_moves.extend(_plan_group(article, store_codes, params, working_inv, bv_config))
        applied_rules.append(
            f"Bundle Planner (per BV, ≥{params.min_items_per_receiver}/winkel)"
        )
    else:
        store_codes = list(article.stores.keys())
        all_moves = _plan_group(article, store_codes, params, working_inv, bv_config)
        applied_rules.append(
            f"Bundle Planner (cross-BV, ≥{params.min_items_per_receiver}/winkel)"
        )

    return all_moves, applied_rules

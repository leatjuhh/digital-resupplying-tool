"""
Kern herverdelingsalgoritme
Genereert herverdelingsvoorstellen per artikel
"""

import logging
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from sqlalchemy.orm import Session

from .domain import ArticleStock, StoreInventory, Move, Proposal, SizeType
from .constraints import (
    RedistributionParams, DEFAULT_PARAMS,
    get_size_order, LETTER_SIZE_ORDER,
)
from .bv_config import get_bv_config, validate_bv_move
from .scoring import calculate_move_score, filter_low_quality_moves
from .store_config import is_redistribution_candidate
from .situation import classify_article_situation, format_situation_rule
from .store_profiles import get_store_profile
from db_models import ArtikelVoorraad, PDFBatch

logger = logging.getLogger(__name__)


def calculate_batch_store_totals(db: Session, batch_id: int) -> Dict[str, int]:
    """Berekent totaalvoorraad per filiaal over alle artikelen in een batch."""
    from sqlalchemy import func as sa_func
    rows = (
        db.query(ArtikelVoorraad.filiaal_code, sa_func.sum(ArtikelVoorraad.voorraad))
        .filter(ArtikelVoorraad.batch_id == batch_id)
        .group_by(ArtikelVoorraad.filiaal_code)
        .all()
    )
    return {
        code: int(total or 0)
        for code, total in rows
        if is_redistribution_candidate(code)
    }


def detect_size_type(sizes: List[str]) -> SizeType:
    """Detecteer het type maat reeks"""
    if not sizes:
        return SizeType.CUSTOM
    if all(s.isdigit() for s in sizes):
        return SizeType.NUMERIC
    if all(s.upper() in LETTER_SIZE_ORDER for s in sizes):
        return SizeType.LETTER
    return SizeType.CUSTOM


def load_store_total_inventory(db: Session, batch_id: int) -> Dict[str, int]:
    """Lees opgegeven totale winkelvoorraad per filiaal uit PDFBatch.extra_data.

    Deze data wordt bij batch-aanmaak door de gebruiker ingevoerd en dient als
    tiebreaker wanneer 2+ winkels gelijke verkoop hebben. Lege/ontbrekende data
    betekent: fallback naar deterministische volgorde op store_code.
    """
    batch = db.query(PDFBatch).filter(PDFBatch.id == batch_id).first()
    if not batch or not batch.extra_data:
        logger.warning(
            f"[STORE_TOTALS] Geen extra_data voor batch {batch_id} — "
            "tiebreaker valt terug op store_code."
        )
        return {}
    raw = batch.extra_data.get("store_total_inventory") or {}
    return {str(code): int(qty) for code, qty in raw.items() if qty is not None}


def load_article_data(
    db: Session,
    volgnummer: str,
    batch_id: int,
    batch_store_totals: Optional[Dict[str, int]] = None,
    store_total_inventory: Optional[Dict[str, int]] = None,
) -> Optional[ArticleStock]:
    """Laad artikel voorraad data uit database"""
    records = db.query(ArtikelVoorraad).filter(
        ArtikelVoorraad.volgnummer == volgnummer,
        ArtikelVoorraad.batch_id == batch_id,
    ).all()

    if not records:
        return None

    article = ArticleStock(
        volgnummer=volgnummer,
        omschrijving=records[0].omschrijving if records else "",
        batch_id=batch_id,
    )

    bv_config = get_bv_config()

    stores_data: Dict[str, Dict] = defaultdict(lambda: {
        'inventory': {},
        'sales_total': 0,
        'store_name': '',
        'bv_name': None,
    })

    all_sizes_set = set()

    for record in records:
        store_code = record.filiaal_code

        if not is_redistribution_candidate(store_code):
            continue

        size = record.maat

        stores_data[store_code]['inventory'][size] = record.voorraad
        stores_data[store_code]['sales_total'] = max(
            stores_data[store_code]['sales_total'],
            record.verkocht,
        )
        stores_data[store_code]['store_name'] = record.filiaal_naam
        stores_data[store_code]['bv_name'] = bv_config.get_bv(store_code)

        all_sizes_set.add(size)

    all_sizes_list = list(all_sizes_set)
    article.all_sizes = get_size_order(all_sizes_list)
    article.size_type = detect_size_type(article.all_sizes)

    for store_code, data in stores_data.items():
        store_inv = StoreInventory(
            store_code=store_code,
            store_name=data['store_name'],
            bv_name=data['bv_name'],
            inventory=data['inventory'],
            sales={"TOTAL": data['sales_total']} if data['sales_total'] > 0 else {},
        )
        batch_total = batch_store_totals.get(store_code, 0) if batch_store_totals else 0
        store_total = (
            store_total_inventory.get(store_code, 0) if store_total_inventory else 0
        )
        profile = get_store_profile(store_code)
        max_capacity = profile.max_capacity if profile else 0
        store_inv.calculate_metrics(
            batch_total=batch_total,
            max_capacity=max_capacity,
            store_total=store_total,
        )
        article.stores[store_code] = store_inv

    article.calculate_aggregates()
    return article


def _series_width(inventory: Dict[str, int], all_sizes: List[str]) -> int:
    """Bereken breedte van de langste aaneengesloten maatreeks met voorraad."""
    best = 0
    current = 0
    for size in all_sizes:
        if inventory.get(size, 0) > 0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


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
                    from_store, to_store, params.enforce_bv_separation
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


def _bv_compatible(from_store: str, to_store: str, params: RedistributionParams) -> bool:
    if not params.enforce_bv_separation:
        return True
    valid, _ = validate_bv_move(from_store, to_store, True)
    return valid


def _assign_bundle(
    article: ArticleStock,
    receiver: str,
    picks: List[str],
    all_stores: List[str],
    working_inv: Dict[str, Dict[str, int]],
    params: RedistributionParams,
    min_qty: int,
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
                if not _bv_compatible(donor, receiver, params):
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
) -> List[Move]:
    """Forceer elke niet-pick winkel naar 0: resterende stuks naar picks."""
    moves: List[Move] = []
    non_picks = [s for s in all_stores if s not in picks]

    for donor in non_picks:
        for size in list(article.all_sizes):
            while working_inv[donor].get(size, 0) > 0:
                target = next(
                    (p for p in picks if _bv_compatible(donor, p, params)),
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
        if not _bv_compatible(donor, top, params):
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
) -> List[Move]:
    """Plan herverdeling voor één BV-groep (of alle winkels als cross-BV)."""
    min_qty = params.min_items_per_receiver
    pool = _group_total(store_codes, working_inv)

    if pool == 0:
        return []

    if pool < min_qty:
        return _consolidate_all_to_top(article, store_codes, working_inv, params)

    # Aantal receivers = hoeveel bundels van min_qty passen
    max_picks = pool // min_qty
    ranked = _rank_receivers(article, store_codes, working_inv)
    picks = ranked[:max_picks]

    moves: List[Move] = []
    for recv in picks:
        moves.extend(_assign_bundle(
            article, recv, picks, store_codes, working_inv, params, min_qty
        ))

    moves.extend(_drain_non_receivers(
        article, picks, store_codes, working_inv, params
    ))
    return moves


def generate_moves_for_article(
    article: ArticleStock,
    params: RedistributionParams,
    working_inv: Dict[str, Dict[str, int]],
) -> Tuple[List[Move], List[str]]:
    """Artikel-level bundle-planner. Retourneert (moves, applied_rules)."""
    applied_rules: List[str] = []

    if params.enforce_bv_separation:
        groups = _group_by_bv(article)
        all_moves: List[Move] = []
        for _bv_name, store_codes in groups.items():
            all_moves.extend(_plan_group(article, store_codes, params, working_inv))
        applied_rules.append(
            f"Bundle Planner (per BV, ≥{params.min_items_per_receiver}/winkel)"
        )
    else:
        store_codes = list(article.stores.keys())
        all_moves = _plan_group(article, store_codes, params, working_inv)
        applied_rules.append(
            f"Bundle Planner (cross-BV, ≥{params.min_items_per_receiver}/winkel)"
        )

    return all_moves, applied_rules


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
    bv_config = get_bv_config()

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


def generate_redistribution_proposals_for_article(
    db: Session,
    volgnummer: str,
    batch_id: int,
    params: Optional[RedistributionParams] = None,
    batch_store_totals: Optional[Dict[str, int]] = None,
    store_total_inventory: Optional[Dict[str, int]] = None,
) -> Optional[Proposal]:
    """
    Genereer herverdelingsvoorstel voor één artikel.

    Stappen:
    1. Laad artikel data
    2. Classificeer situatie (shadow mode)
    3. Check BV consolidatie (prioriteit)
    4. Genereer moves per maat (greedy)
    5. Filter lage-kwaliteit moves
    6. Creëer Proposal
    """
    if params is None:
        params = DEFAULT_PARAMS

    # === STAP 1: Data ophalen ===
    article = load_article_data(
        db, volgnummer, batch_id, batch_store_totals, store_total_inventory
    )

    if article is None:
        logger.info(f"Article {volgnummer} not found in database")
        return None

    if not article.stores or len(article.stores) < 2:
        logger.info(f"Article {volgnummer} has {len(article.stores) if article.stores else 0} stores, need at least 2")
        return None

    # === STAP 2: Situatie classificatie ===
    situation_rule = format_situation_rule(classify_article_situation(article, params))

    # === STAP 3: Move generatie ===
    # Werkende voorraad bijgehouden over alle moves: elke move werkt dit bij,
    # zodat volgende beslissingen de actuele stand gebruiken.
    working_inventory: Dict[str, Dict[str, int]] = {
        store_code: dict(store_inv.inventory)
        for store_code, store_inv in article.stores.items()
    }

    if params.enable_bundle_planner:
        # Nieuwe artikel-level planner met harde min-3 regel
        all_moves, planner_rules = generate_moves_for_article(
            article, params, working_inventory
        )
        applied_rules = [situation_rule, *planner_rules]
    else:
        # Legacy pad: oude BV-consolidatie + per-maat greedy (feature-flag off)
        consolidation_moves, consolidation_rules = check_and_consolidate_fragmented_bv(
            article, params
        )
        if consolidation_moves:
            all_moves = consolidation_moves
            applied_rules = [situation_rule, *consolidation_rules]
        else:
            all_moves = []
            applied_rules = [situation_rule]
            for size in article.all_sizes:
                all_moves.extend(generate_moves_for_size(
                    article, size, params, working_inventory
                ))
            if params.enforce_bv_separation:
                applied_rules.append("BV Separation")
            applied_rules.append("Sales-first Allocation")

    # === STAP 5: Filter ===
    filtered_moves = filter_low_quality_moves(all_moves, min_score=params.min_move_score) if all_moves else []

    # === STAP 6: Proposal (altijd, ook als geen moves) ===
    if not filtered_moves:
        reason = (
            "Geen herverdelingsvoorstel op basis van de huidige regels. "
            "Dit betekent niet automatisch dat het artikel optimaal verdeeld is."
        )
        applied_rules = [situation_rule, "Manual Review Required"]
    else:
        reason = f"Herverdeling voor {len(filtered_moves)} moves over {len(article.stores)} winkels"

    proposal = Proposal(
        volgnummer=article.volgnummer,
        article_name=article.omschrijving,
        batch_id=batch_id,
        moves=filtered_moves,
        status="pending",
        reason=reason,
        applied_rules=applied_rules,
    )

    proposal.calculate_aggregates()
    return proposal


def generate_redistribution_proposals_for_batch(
    db: Session,
    batch_id: int,
    params: Optional[RedistributionParams] = None,
) -> List[Proposal]:
    """Genereer herverdelingsvoorstellen voor alle artikelen in een batch"""
    records = db.query(ArtikelVoorraad.volgnummer).filter(
        ArtikelVoorraad.batch_id == batch_id,
    ).distinct().all()

    volgnummers = [r[0] for r in records]

    # Eenmalig totaalvoorraad per filiaal berekenen voor capacity scoring
    batch_store_totals = calculate_batch_store_totals(db, batch_id)

    # Door gebruiker opgegeven totale winkelvoorraad (tiebreaker bij sales=0)
    store_total_inventory = load_store_total_inventory(db, batch_id)

    proposals = []
    for volgnummer in volgnummers:
        proposal = generate_redistribution_proposals_for_article(
            db, volgnummer, batch_id, params,
            batch_store_totals=batch_store_totals,
            store_total_inventory=store_total_inventory,
        )
        if proposal:
            proposals.append(proposal)

    return proposals

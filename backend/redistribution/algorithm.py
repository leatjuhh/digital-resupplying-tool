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
from .situation import classify_article_situation, format_situation_rule
from .store_profiles import get_store_profile
from db_models import ArtikelVoorraad

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
    return {code: int(total or 0) for code, total in rows}


def detect_size_type(sizes: List[str]) -> SizeType:
    """Detecteer het type maat reeks"""
    if not sizes:
        return SizeType.CUSTOM
    if all(s.isdigit() for s in sizes):
        return SizeType.NUMERIC
    if all(s.upper() in LETTER_SIZE_ORDER for s in sizes):
        return SizeType.LETTER
    return SizeType.CUSTOM


def load_article_data(
    db: Session,
    volgnummer: str,
    batch_id: int,
    batch_store_totals: Optional[Dict[str, int]] = None,
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
        profile = get_store_profile(store_code)
        max_capacity = profile.max_capacity if profile else 0
        store_inv.calculate_metrics(batch_total=batch_total, max_capacity=max_capacity)
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
    article = load_article_data(db, volgnummer, batch_id, batch_store_totals)

    if article is None:
        logger.info(f"Article {volgnummer} not found in database")
        return None

    if not article.stores or len(article.stores) < 2:
        logger.info(f"Article {volgnummer} has {len(article.stores) if article.stores else 0} stores, need at least 2")
        return None

    # === STAP 2: Situatie classificatie ===
    situation_rule = format_situation_rule(classify_article_situation(article, params))

    # === STAP 3: BV Consolidatie (prioriteit) ===
    consolidation_moves, consolidation_rules = check_and_consolidate_fragmented_bv(article, params)

    if consolidation_moves:
        all_moves = consolidation_moves
        applied_rules = [situation_rule, *consolidation_rules]
    else:
        # === STAP 4: Normale move generatie per maat ===
        # Werkende voorraad bijgehouden over alle maten: donaties in eerdere
        # maten tellen mee zodat een winkel niet te veel geeft.
        working_inventory: Dict[str, Dict[str, int]] = {
            store_code: dict(store_inv.inventory)
            for store_code, store_inv in article.stores.items()
        }

        all_moves = []
        applied_rules = [situation_rule]

        for size in article.all_sizes:
            all_moves.extend(generate_moves_for_size(article, size, params, working_inventory))

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

    proposals = []
    for volgnummer in volgnummers:
        proposal = generate_redistribution_proposals_for_article(
            db, volgnummer, batch_id, params, batch_store_totals
        )
        if proposal:
            proposals.append(proposal)

    return proposals

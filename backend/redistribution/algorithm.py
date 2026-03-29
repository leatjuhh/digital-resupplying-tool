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
from db_models import ArtikelVoorraad

logger = logging.getLogger(__name__)


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
        store_inv.calculate_metrics()
        article.stores[store_code] = store_inv

    article.calculate_aggregates()
    return article


def identify_surplus_and_shortage(
    article: ArticleStock,
    size: str,
    params: RedistributionParams,
) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]]]:
    """
    Identificeer overschotten en tekorten voor een specifieke maat.

    Surplus-winkels met lage demand leveren eerst.
    Shortage-winkels met hoge demand ontvangen eerst.
    """
    surplus = []
    shortage = []

    avg_inventory = article.average_inventory_per_size.get(size, 0)
    if avg_inventory == 0:
        return surplus, shortage

    oversupply_threshold = avg_inventory * params.oversupply_threshold
    undersupply_threshold = avg_inventory * params.undersupply_threshold

    for store_code, store_inv in article.stores.items():
        qty = store_inv.inventory.get(size, 0)
        if qty == 0:
            continue

        if qty > oversupply_threshold:
            excess_qty = int(qty - avg_inventory)
            if excess_qty >= params.min_move_quantity:
                priority = 1.0 - store_inv.demand_score
                surplus.append((store_code, excess_qty, priority))

        elif qty < undersupply_threshold:
            needed_qty = int(avg_inventory - qty)
            if needed_qty >= params.min_move_quantity:
                priority = store_inv.demand_score
                shortage.append((store_code, needed_qty, priority))

    surplus.sort(key=lambda x: x[2], reverse=True)
    shortage.sort(key=lambda x: x[2], reverse=True)

    return [(s[0], s[1]) for s in surplus], [(s[0], s[1]) for s in shortage]


def generate_moves_for_size(
    article: ArticleStock,
    size: str,
    params: RedistributionParams,
) -> List[Move]:
    """Genereer moves voor één specifieke maat (greedy matching)"""
    moves = []

    surplus_stores, shortage_stores = identify_surplus_and_shortage(article, size, params)
    if not surplus_stores or not shortage_stores:
        return moves

    for from_store, available_qty in surplus_stores:
        from_store_inv = article.stores[from_store]

        for to_store, needed_qty in shortage_stores[:]:
            to_store_inv = article.stores[to_store]

            if params.enforce_bv_separation:
                is_valid, _reason = validate_bv_move(
                    from_store, to_store, params.enforce_bv_separation
                )
                if not is_valid:
                    continue

            move_qty = min(available_qty, needed_qty, params.max_move_quantity)
            if move_qty < params.min_move_quantity:
                continue

            move = Move(
                volgnummer=article.volgnummer,
                size=size,
                from_store=from_store,
                from_store_name=from_store_inv.store_name,
                to_store=to_store,
                to_store_name=to_store_inv.store_name,
                qty=move_qty,
                from_bv=from_store_inv.bv_name,
                to_bv=to_store_inv.bv_name,
            )

            calculate_move_score(move, from_store_inv, to_store_inv, article, params)
            moves.append(move)

            available_qty -= move_qty
            needed_qty -= move_qty

            if needed_qty <= 0:
                shortage_stores.remove((to_store, needed_qty + move_qty))
            else:
                idx = shortage_stores.index((to_store, needed_qty + move_qty))
                shortage_stores[idx] = (to_store, needed_qty)

            if available_qty <= 0:
                break

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
    article = load_article_data(db, volgnummer, batch_id)

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
        all_moves = []
        applied_rules = [situation_rule]

        for size in article.all_sizes:
            all_moves.extend(generate_moves_for_size(article, size, params))

        if params.enforce_bv_separation:
            applied_rules.append("BV Separation")
        applied_rules.append("Demand-based Allocation")

    # === STAP 5: Filter ===
    filtered_moves = filter_low_quality_moves(all_moves, min_score=params.min_move_score) if all_moves else []

    # === STAP 6: Proposal (altijd, ook als geen moves) ===
    if not filtered_moves:
        reason = "Dit artikel is reeds optimaal verdeeld. Er hoeven geen wijzigingen aangebracht te worden."
        applied_rules = [situation_rule, "Optimal Distribution Analysis"]
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
    proposals = []

    for volgnummer in volgnummers:
        proposal = generate_redistribution_proposals_for_article(
            db, volgnummer, batch_id, params
        )
        if proposal:
            proposals.append(proposal)

    return proposals

"""
Kern herverdelingsalgoritme
Genereert herverdelingsvoorstellen per artikel
"""

from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
import re

from .domain import (
    ArticleStock, StoreInventory, Move, Proposal,
    SizeSequence, SizeType
)
from .constraints import (
    RedistributionParams, DEFAULT_PARAMS,
    get_size_order, LETTER_SIZE_ORDER
)
from .bv_config import get_bv_config, validate_bv_move
from .scoring import calculate_move_score
from db_models import ArtikelVoorraad


def detect_size_type(sizes: List[str]) -> SizeType:
    """
    Detecteer het type maat reeks
    
    Args:
        sizes: Lijst van maten
        
    Returns:
        SizeType enum
    """
    if not sizes:
        return SizeType.CUSTOM
    
    # Check numeriek
    if all(s.isdigit() for s in sizes):
        return SizeType.NUMERIC
    
    # Check letter maten
    sizes_upper = [s.upper() for s in sizes]
    if all(s in LETTER_SIZE_ORDER for s in sizes_upper):
        return SizeType.LETTER
    
    return SizeType.CUSTOM


def detect_size_sequences(
    store_inventory: Dict[str, int],
    all_sizes_sorted: List[str],
    min_width: int = 3
) -> List[SizeSequence]:
    """
    Detecteer opeenvolgende maatreeksen in een winkel
    
    Args:
        store_inventory: Voorraad per maat {maat: aantal}
        all_sizes_sorted: Alle maten in juiste volgorde
        min_width: Minimale breedte van een reeks
        
    Returns:
        Lijst van SizeSequence objecten
    """
    sequences = []
    
    # Vind welke maten aanwezig zijn
    available_sizes = [s for s in all_sizes_sorted if s in store_inventory and store_inventory[s] > 0]
    
    if len(available_sizes) < min_width:
        return sequences
    
    # Vind opeenvolgende reeksen
    current_sequence = []
    
    for i, size in enumerate(all_sizes_sorted):
        if size in available_sizes:
            current_sequence.append(size)
        else:
            # Reeks is onderbroken
            if len(current_sequence) >= min_width:
                size_type = detect_size_type(current_sequence)
                sequences.append(SizeSequence(
                    store_code="",  # Wordt later ingevuld
                    sizes=current_sequence.copy(),
                    size_type=size_type,
                    width=len(current_sequence)
                ))
            current_sequence = []
    
    # Check laatste reeks
    if len(current_sequence) >= min_width:
        size_type = detect_size_type(current_sequence)
        sequences.append(SizeSequence(
            store_code="",
            sizes=current_sequence.copy(),
            size_type=size_type,
            width=len(current_sequence)
        ))
    
    return sequences


def load_article_data(
    db: Session,
    volgnummer: str,
    batch_id: int
) -> Optional[ArticleStock]:
    """
    Laad artikel voorraad data uit database
    
    Args:
        db: Database sessie
        volgnummer: Artikelnummer
        batch_id: Batch ID
        
    Returns:
        ArticleStock object of None als niet gevonden
    """
    # Haal alle voorraad records op voor dit artikel
    records = db.query(ArtikelVoorraad).filter(
        ArtikelVoorraad.volgnummer == volgnummer,
        ArtikelVoorraad.batch_id == batch_id
    ).all()
    
    if not records:
        return None
    
    # Maak ArticleStock object
    article = ArticleStock(
        volgnummer=volgnummer,
        omschrijving=records[0].omschrijving if records else "",
        batch_id=batch_id
    )
    
    # Verzamel BV config
    bv_config = get_bv_config()
    
    # Groepeer per winkel
    stores_data: Dict[str, Dict] = defaultdict(lambda: {
        'inventory': {},
        'sales_total': 0,
        'store_name': '',
        'bv_name': None
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
    
    # Bepaal maat volgorde
    all_sizes_list = list(all_sizes_set)
    article.all_sizes = get_size_order(all_sizes_list)
    article.size_type = detect_size_type(article.all_sizes)
    
    # Maak StoreInventory objecten
    for store_code, data in stores_data.items():
        store_inv = StoreInventory(
            store_code=store_code,
            store_name=data['store_name'],
            bv_name=data['bv_name'],
            inventory=data['inventory'],
            # PDF verkoop is per winkel totaal, niet per maat.
            sales={"TOTAL": data['sales_total']} if data['sales_total'] > 0 else {}
        )
        store_inv.calculate_metrics()
        article.stores[store_code] = store_inv
        
        # Detecteer maatreeksen
        sequences = detect_size_sequences(
            data['inventory'],
            article.all_sizes,
            min_width=3
        )
        
        # Update store_code in sequences
        for seq in sequences:
            seq.store_code = store_code
        
        article.size_sequences[store_code] = sequences
    
    # Bereken aggregates
    article.calculate_aggregates()
    
    return article


def identify_surplus_and_shortage(
    article: ArticleStock,
    size: str,
    params: RedistributionParams
) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]]]:
    """
    Identificeer overschotten en tekorten voor een specifieke maat
    
    Args:
        article: Artikel voorraad
        size: Maat om te analyseren
        params: Algorithme parameters
        
    Returns:
        Tuple van (surplus_list, shortage_list)
        waarbij elk item (store_code, quantity) is
    """
    surplus = []
    shortage = []
    
    # Haal gemiddelde voorraad voor deze maat op
    avg_inventory = article.average_inventory_per_size.get(size, 0)
    
    if avg_inventory == 0:
        return surplus, shortage
    
    # Bepaal drempelwaarden
    oversupply_threshold = avg_inventory * params.oversupply_threshold
    undersupply_threshold = avg_inventory * params.undersupply_threshold
    
    # Analyseer elke winkel
    for store_code, store_inv in article.stores.items():
        qty = store_inv.inventory.get(size, 0)
        
        if qty == 0:
            continue
        
        # Check overschot
        if qty > oversupply_threshold:
            excess_qty = int(qty - avg_inventory)
            if excess_qty >= params.min_move_quantity:
                # Weeg demand mee: lage demand winkels leveren eerst
                priority_score = 1.0 - store_inv.demand_score
                surplus.append((store_code, excess_qty, priority_score))
        
        # Check tekort
        elif qty < undersupply_threshold:
            needed_qty = int(avg_inventory - qty)
            if needed_qty >= params.min_move_quantity:
                # Weeg demand mee: hoge demand winkels krijgen eerst
                priority_score = store_inv.demand_score
                shortage.append((store_code, needed_qty, priority_score))
    
    # Sorteer op priority (hoogste eerst)
    surplus.sort(key=lambda x: x[2], reverse=True)
    shortage.sort(key=lambda x: x[2], reverse=True)
    
    # Return zonder priority score (alleen store en qty)
    return [(s[0], s[1]) for s in surplus], [(s[0], s[1]) for s in shortage]


def generate_moves_for_size(
    article: ArticleStock,
    size: str,
    params: RedistributionParams
) -> List[Move]:
    """
    Genereer moves voor één specifieke maat (greedy matching)
    
    Args:
        article: Artikel voorraad
        size: Maat
        params: Algorithme parameters
        
    Returns:
        Lijst van Move objecten
    """
    moves = []
    
    # Identificeer overschotten en tekorten
    surplus_stores, shortage_stores = identify_surplus_and_shortage(
        article, size, params
    )
    
    if not surplus_stores or not shortage_stores:
        return moves
    
    # Greedy matching: match elk overschot met tekorten
    bv_config = get_bv_config()
    
    for from_store, available_qty in surplus_stores:
        from_store_inv = article.stores[from_store]
        
        for to_store, needed_qty in shortage_stores[:]:  # Copy list for modification
            to_store_inv = article.stores[to_store]
            
            # Check BV constraint
            if params.enforce_bv_separation:
                is_valid, reason = validate_bv_move(
                    from_store, to_store, params.enforce_bv_separation
                )
                if not is_valid:
                    continue  # Skip deze move
            
            # Bepaal hoeveel te verplaatsen
            move_qty = min(available_qty, needed_qty, params.max_move_quantity)
            
            if move_qty < params.min_move_quantity:
                continue
            
            # Maak move
            move = Move(
                volgnummer=article.volgnummer,
                size=size,
                from_store=from_store,
                from_store_name=from_store_inv.store_name,
                to_store=to_store,
                to_store_name=to_store_inv.store_name,
                qty=move_qty,
                from_bv=from_store_inv.bv_name,
                to_bv=to_store_inv.bv_name
            )
            
            # Bereken score
            calculate_move_score(move, from_store_inv, to_store_inv, article, params)
            
            moves.append(move)
            
            # Update remaining quantities
            available_qty -= move_qty
            needed_qty -= move_qty
            
            # Update shortage list
            if needed_qty <= 0:
                shortage_stores.remove((to_store, needed_qty + move_qty))
            else:
                # Update qty in list
                idx = shortage_stores.index((to_store, needed_qty + move_qty))
                shortage_stores[idx] = (to_store, needed_qty)
            
            # Als bron leeg is, stop met deze bron
            if available_qty <= 0:
                break
    
    return moves


def check_and_consolidate_fragmented_bv(
    article: ArticleStock,
    params: RedistributionParams
) -> Tuple[List[Move], List[str]]:
    """
    Check of een BV gefragmenteerd is (≤ min_items_per_store stuks totaal)
    en genereer consolidatie moves indien nodig
    
    Args:
        article: Artikel voorraad
        params: Algorithme parameters
        
    Returns:
        Tuple van (moves_lijst, applied_rules_lijst)
    """
    import logging
    logger = logging.getLogger(__name__)
    
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
    
    # Check elke BV
    for bv_name, stores_in_bv in bv_stores.items():
        if len(stores_in_bv) < 2:
            continue  # Niks te consolideren met 1 winkel
        
        # Tel totale voorraad in deze BV (alle maten samen)
        total_inventory = sum(
            sum(sizes.values())
            for store_sizes in bv_inventory[bv_name].values()
            for sizes in [store_sizes]
        )
        
        if total_inventory > params.min_items_per_store:
            continue  # Niet gefragmenteerd
        
        logger.info(f"[BV_CONSOLIDATION] BV {bv_name} has only {total_inventory} items total (≤ {params.min_items_per_store}), consolidating...")
        
        # Bepaal beste winkel om naar te consolideren
        best_store = None
        best_score = -1
        
        for store_code in stores_in_bv:
            store_inv = article.stores[store_code]
            
            # Score gebaseerd op:
            # 1. Hoogste verkoop (priority)
            # 2. Hoogste voorraad (fallback)
            # 3. Alfabetisch (tiebreaker)
            total_sales = store_inv.total_sales
            total_inv = store_inv.total_inventory
            
            score = (total_sales * 1000) + (total_inv * 10)  # Verkoop weegt zwaarder
            
            if score > best_score or (score == best_score and (best_store is None or store_code < best_store)):
                best_score = score
                best_store = store_code
        
        if not best_store:
            continue
        
        logger.info(f"[BV_CONSOLIDATION] Consolidating to {best_store} ({article.stores[best_store].store_name}) - Sales: {article.stores[best_store].total_sales}, Inventory: {article.stores[best_store].total_inventory}")
        
        # Genereer moves om alles naar beste winkel te verplaatsen
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
                    reason=f"BV Consolidatie: {bv_name} heeft slechts {total_inventory} items, consolideren naar best verkopende winkel"
                )
                
                # Score de move (hoog omdat dit een strategische consolidatie is)
                calculate_move_score(move, from_store_inv, to_store_inv, article, params)
                move.score = max(move.score, 0.8)  # Minimum score voor consolidatie moves
                
                moves.append(move)
        
        if moves:
            applied_rules.append(f"BV Consolidation (≤{params.min_items_per_store} items)")
    
    return moves, applied_rules


def generate_redistribution_proposals_for_article(
    db: Session,
    volgnummer: str,
    batch_id: int,
    params: Optional[RedistributionParams] = None
) -> Optional[Proposal]:
    """
    Genereer herverdelingsvoorstel voor één artikel
    
    Dit is de hoofdfunctie die alle stappen uitvoert:
    1. Laad artikel data uit database
    2. Analyseer voorraad en verkoop per winkel
    3. Detecteer maatreeksen
    4. Genereer moves per maat (greedy)
    5. Score en filter moves
    6. Optioneel: optimalisatie fase
    7. Creëer Proposal object
    
    Args:
        db: Database sessie
        volgnummer: Artikelnummer
        batch_id: Batch ID
        params: Algorithme parameters (optioneel, gebruikt DEFAULT_PARAMS)
        
    Returns:
        Proposal object of None als geen voorstellen nodig
    """
    if params is None:
        params = DEFAULT_PARAMS
    
    import logging
    logger = logging.getLogger(__name__)
    
    # === STAP 1: Data Ophalen ===
    article = load_article_data(db, volgnummer, batch_id)
    
    if article is None:
        logger.info(f"[PROPOSAL_DEBUG] Article {volgnummer} not found in database")
        return None
    
    if not article.stores or len(article.stores) < 2:
        # Kan niet herverdelen met minder dan 2 winkels
        logger.info(f"[PROPOSAL_DEBUG] Article {volgnummer} has {len(article.stores) if article.stores else 0} stores, need at least 2")
        return None
    
    # === STAP 2-3: Analyse gebeurt al in load_article_data ===
    
    # === STAP 3B: Check BV Consolidatie (prioriteit) ===
    consolidation_moves, consolidation_rules = check_and_consolidate_fragmented_bv(article, params)
    
    # Als consolidatie moves zijn gemaakt, gebruik die
    if consolidation_moves:
        logger.info(f"[PROPOSAL_DEBUG] Article {volgnummer}: Using {len(consolidation_moves)} BV consolidation moves")
        all_moves = consolidation_moves
        applied_rules = consolidation_rules
    else:
        # === STAP 4: Normale Move Generatie per maat ===
        all_moves = []
        applied_rules = []
        
        logger.info(f"[PROPOSAL_DEBUG] Article {volgnummer}: Generating moves for {len(article.all_sizes)} sizes across {len(article.stores)} stores")
        
        for size in article.all_sizes:
            size_moves = generate_moves_for_size(article, size, params)
            if size_moves:
                logger.info(f"[PROPOSAL_DEBUG] Size {size}: Generated {len(size_moves)} moves")
            all_moves.extend(size_moves)
        
        # Track welke regels zijn toegepast
        if params.enforce_bv_separation:
            applied_rules.append("BV Separation")
        if params.min_sequence_width > 0:
            applied_rules.append(f"Min {params.min_sequence_width} Sequence Width")
        applied_rules.append("Demand-based Allocation")
    
    # === STAP 5: Score en Filter (alleen als we moves hebben) ===
    filtered_moves = []
    
    if all_moves:
        # Moves zijn al gescoord in generate_moves_for_size of check_and_consolidate_fragmented_bv
        # Filter lage kwaliteit moves (behalve consolidation moves die al hoog gescoord zijn)
        from .scoring import filter_low_quality_moves
        filtered_moves = filter_low_quality_moves(all_moves, min_score=0.2)
    
    # === STAP 6: Optimalisatie (indien enabled en moves beschikbaar) ===
    optimization_explanation = None
    
    if filtered_moves and params.enable_optimization:
        from .optimizer import optimize_move_consolidation
        from .constraints import DEFAULT_OPTIMIZATION_PARAMS
        
        optimized_result = optimize_move_consolidation(
            filtered_moves,
            article,
            DEFAULT_OPTIMIZATION_PARAMS
        )
        
        if optimized_result:
            filtered_moves = optimized_result.moves
            optimization_explanation = optimized_result.explanation
    
    # === STAP 7: Creëer Proposal (ALTIJD, ook als geen moves) ===
    # Bepaal reason en applied_rules
    if not filtered_moves:
        # Geen moves = artikel is optimaal verdeeld
        reason = "Dit artikel is reeds optimaal verdeeld. Er hoeven geen wijzigingen aangebracht te worden."
        applied_rules = ["Optimal Distribution Analysis"]
        logger.info(f"[PROPOSAL_DEBUG] Article {volgnummer}: No moves needed, creating 'optimal distribution' proposal")
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
        optimization_applied=params.enable_optimization and optimization_explanation is not None,
        optimization_explanation=optimization_explanation
    )
    
    # Bereken aggregates
    proposal.calculate_aggregates()
    
    return proposal


def generate_redistribution_proposals_for_batch(
    db: Session,
    batch_id: int,
    params: Optional[RedistributionParams] = None
) -> List[Proposal]:
    """
    Genereer herverdelingsvoorstellen voor alle artikelen in een batch
    
    Args:
        db: Database sessie
        batch_id: Batch ID
        params: Algorithme parameters (optioneel)
        
    Returns:
        Lijst van Proposal objecten
    """
    # Haal alle unieke artikelnummers op in deze batch
    records = db.query(ArtikelVoorraad.volgnummer).filter(
        ArtikelVoorraad.batch_id == batch_id
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

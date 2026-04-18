"""
Scoring systeem voor herverdelingsmoves
Bepaalt hoe goed een move is op basis van demand, series, en efficiency
"""

from typing import Dict, List, Optional
from .domain import Move, StoreInventory, SizeSequence, ArticleStock
from .constraints import RedistributionParams


def calculate_demand_score(
    from_store: StoreInventory,
    to_store: StoreInventory,
    size: str,
    params: RedistributionParams
) -> float:
    """
    Bereken demand score voor een move
    
    Een goede move verplaatst van lage demand naar hoge demand.
    
    Args:
        from_store: Bron winkel
        to_store: Doel winkel
        size: Maat
        params: Algorithme parameters
        
    Returns:
        Demand score (0.0 - 1.0)
    """
    # Haal demand scores op
    from_demand = from_store.demand_score
    to_demand = to_store.demand_score
    
    # Als doel winkel hogere demand heeft, is dit een goede move
    demand_diff = to_demand - from_demand
    
    # Normaliseer naar 0.0 - 1.0 range
    # Negatieve waarden = slechte move (van hoge naar lage demand)
    # Positieve waarden = goede move (van lage naar hoge demand)
    
    if demand_diff > 0:
        # Goede move - schaal naar 0.5 - 1.0
        # Bij maximaal verschil (1.0) krijg je score 1.0
        score = 0.5 + (demand_diff / 2.0)
    else:
        # Slechte move - schaal naar 0.0 - 0.5
        # Bij maximaal negatief verschil (-1.0) krijg je score 0.0
        score = 0.5 + (demand_diff / 2.0)
    
    # Clamp tussen 0 en 1
    return max(0.0, min(1.0, score))


def calculate_series_score(
    from_store: StoreInventory,
    to_store: StoreInventory,
    size: str,
    article: ArticleStock,
    params: RedistributionParams
) -> float:
    """
    Bereken serie score voor een move
    
    Goede moves behouden of versterken maatseries.
    Slechte moves breken series.
    
    Args:
        from_store: Bron winkel
        to_store: Doel winkel
        size: Maat
        article: Artikel voorraad info
        params: Algorithme parameters
        
    Returns:
        Serie score (0.0 - 1.0)
    """
    score = 0.5  # Neutral start
    
    # Check of deze move een serie zou breken in bron winkel
    from_sequences = article.size_sequences.get(from_store.store_code, [])
    breaks_source_sequence = False
    
    for seq in from_sequences:
        if seq.would_break_on_removal(size):
            breaks_source_sequence = True
            break
    
    if breaks_source_sequence:
        # Penalty voor het breken van een serie
        score -= params.sequence_break_penalty
    
    # Check of deze move een serie zou creëren/versterken in doel winkel
    to_sequences = article.size_sequences.get(to_store.store_code, [])
    to_inventory = to_store.inventory
    
    # Check of toevoegen van deze maat een bestaande serie versterkt
    creates_or_extends_sequence = False
    
    for seq in to_sequences:
        # Check of deze maat naast een bestaande serie zit
        all_sizes_sorted = article.all_sizes
        if size in all_sizes_sorted:
            size_idx = all_sizes_sorted.index(size)
            
            # Check of naast deze maat een serie is
            if size_idx > 0:
                prev_size = all_sizes_sorted[size_idx - 1]
                if prev_size in seq.sizes:
                    creates_or_extends_sequence = True
                    break
            
            if size_idx < len(all_sizes_sorted) - 1:
                next_size = all_sizes_sorted[size_idx + 1]
                if next_size in seq.sizes:
                    creates_or_extends_sequence = True
                    break
    
    if creates_or_extends_sequence:
        # Bonus voor het creëren/versterken van een serie
        score += params.sequence_creation_bonus
    
    # Clamp tussen 0 en 1
    return max(0.0, min(1.0, score))


def calculate_efficiency_score(
    qty: int,
    params: RedistributionParams
) -> float:
    """
    Bereken efficiency score voor een move
    
    Grotere moves zijn efficiënter (minder transport kosten per item).
    
    Args:
        qty: Aantal stuks in de move
        params: Algorithme parameters
        
    Returns:
        Efficiency score (0.0 - 1.0)
    """
    # Schaal lineair van min naar max quantity
    if qty <= params.min_move_quantity:
        return 0.1  # Minimum score voor zeer kleine moves
    
    if qty >= params.max_move_quantity:
        return 1.0  # Maximum score
    
    # Lineair schalen tussen min en max
    score = (qty - params.min_move_quantity) / (params.max_move_quantity - params.min_move_quantity)
    
    return max(0.0, min(1.0, score))


def calculate_move_score(
    move: Move,
    from_store: StoreInventory,
    to_store: StoreInventory,
    article: ArticleStock,
    params: RedistributionParams
) -> float:
    """
    Bereken totale score voor een move
    
    Combineert demand, series, en efficiency scores met wegingen.
    
    Args:
        move: De move om te scoren
        from_store: Bron winkel
        to_store: Doel winkel
        article: Artikel voorraad info
        params: Algorithme parameters
        
    Returns:
        Totale score (0.0 - 1.0)
    """
    # Bereken individuele scores
    demand_score = calculate_demand_score(from_store, to_store, move.size, params)
    series_score = calculate_series_score(from_store, to_store, move.size, article, params)
    efficiency_score = calculate_efficiency_score(move.qty, params)
    
    # Combineer met wegingen
    total_score = (
        demand_score * params.demand_weight +
        series_score * params.series_weight +
        efficiency_score * params.efficiency_weight
    )
    
    # Update move metadata
    move.score = total_score
    
    # Genereer uitleg
    reasons = []
    
    if demand_score > 0.6:
        to_demand_pct = to_store.demand_score * 100
        reasons.append(f"Hoge demand in doel winkel ({to_demand_pct:.0f}% verkocht)")
    elif demand_score < 0.4:
        from_demand_pct = from_store.demand_score * 100
        reasons.append(f"Lage demand in bron winkel ({from_demand_pct:.0f}% verkocht)")
    
    if series_score > 0.7:
        reasons.append("Versterkt maatserie")
    elif series_score < 0.3:
        reasons.append("Breekt maatserie")
    
    if efficiency_score > 0.7:
        reasons.append(f"Efficiënte move ({move.qty} stuks)")
    
    move.reason = "; ".join(reasons) if reasons else "Balancering voorraad"
    
    return total_score


def rank_moves(
    moves: List[Move],
    article: ArticleStock,
    params: RedistributionParams
) -> List[Move]:
    """
    Rangschik moves op score (hoogste eerst)
    
    Args:
        moves: Lijst van moves
        article: Artikel info
        params: Parameters
        
    Returns:
        Gesorteerde lijst van moves
    """
    # Sorteer op score (hoogste eerst)
    return sorted(moves, key=lambda m: m.score, reverse=True)


def filter_low_quality_moves(
    moves: List[Move],
    min_score: float = 0.3
) -> List[Move]:
    """
    Filter moves met te lage score
    
    Args:
        moves: Lijst van moves
        min_score: Minimale score om te behouden
        
    Returns:
        Gefilterde lijst van moves
    """
    return [m for m in moves if m.score >= min_score]


def calculate_consolidation_score(
    move_a: Move,
    move_b: Move,
    destinations_before: Dict[str, set],
    params
) -> float:
    """
    Bereken consolidation score voor een swap tussen twee moves
    
    Gebruikt voor optimalisatie fase.
    
    Args:
        move_a: Eerste move
        move_b: Tweede move
        destinations_before: Huidige bestemmingen per bron
        params: Optimalisatie parameters
        
    Returns:
        Consolidation score (hoger = betere swap)
    """
    # Check hoeveel bestemmingen elke bron heeft
    a_dest_count = len(destinations_before.get(move_a.from_store, set()))
    b_dest_count = len(destinations_before.get(move_b.from_store, set()))
    
    # Simuleer swap effect
    # Als we A's bestemming toewijzen aan B en vice versa
    
    # Zou A minder bestemmingen krijgen?
    a_improvement = 0
    if move_a.to_store in destinations_before.get(move_a.from_store, set()):
        # Als we deze bestemming weghalen en het was de enige naar die bestemming
        temp_dests = destinations_before.get(move_a.from_store, set()).copy()
        temp_dests.discard(move_a.to_store)
        if move_b.to_store not in temp_dests:
            temp_dests.add(move_b.to_store)
        
        new_count = len(temp_dests)
        a_improvement = a_dest_count - new_count
    
    # Zou B minder bestemmingen krijgen?
    b_improvement = 0
    if move_b.to_store in destinations_before.get(move_b.from_store, set()):
        temp_dests = destinations_before.get(move_b.from_store, set()).copy()
        temp_dests.discard(move_b.to_store)
        if move_a.to_store not in temp_dests:
            temp_dests.add(move_a.to_store)
        
        new_count = len(temp_dests)
        b_improvement = b_dest_count - new_count
    
    # Totale verbetering
    total_improvement = a_improvement + b_improvement
    
    # Quantity match score (hoe goed matchen de hoeveelheden)
    qty_ratio = min(move_a.qty, move_b.qty) / max(move_a.qty, move_b.qty)
    
    # Combineer scores
    consolidation_component = total_improvement * params.consolidation_weight
    quantity_component = qty_ratio * params.quantity_match_weight
    
    # Series preservation (negatief als swap series zou breken)
    series_component = 0.5 * params.series_preservation_weight
    if move_a.breaks_sequence or move_b.breaks_sequence:
        series_component *= 0.5  # Penalty
    
    total_score = consolidation_component + quantity_component + series_component
    
    return total_score

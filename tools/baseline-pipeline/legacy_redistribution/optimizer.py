"""
Move consolidation optimizer
Optimaliseert moves om aantal verzend-bestemmingen per winkel te minimaliseren
"""

from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass

from .domain import (
    Move, ArticleStock, ConsolidationMetrics,
    OptimizationExplanation, SwapDetail
)
from .constraints import OptimizationParams
from .scoring import calculate_consolidation_score


@dataclass
class OptimizationResult:
    """Resultaat van optimalisatie"""
    moves: List[Move]
    explanation: OptimizationExplanation
    improved: bool


def calculate_destinations_per_source(moves: List[Move]) -> Dict[str, Set[str]]:
    """
    Bereken aantal unieke bestemmingen per bron
    
    Args:
        moves: Lijst van moves
        
    Returns:
        Dictionary {source: set(destinations)}
    """
    destinations = defaultdict(set)
    
    for move in moves:
        destinations[move.from_store].add(move.to_store)
    
    return dict(destinations)


def find_swap_candidate(
    target_move: Move,
    all_moves: List[Move],
    destinations_map: Dict[str, Set[str]],
    params: OptimizationParams
) -> Optional[Tuple[Move, float]]:
    """
    Vind beste swap kandidaat voor een gegeven move
    
    Args:
        target_move: Move waarvoor we een swap zoeken
        all_moves: Alle beschikbare moves
        destinations_map: Huidige bestemmingen per bron
        params: Optimalisatie parameters
        
    Returns:
        Tuple van (beste_move, score) of None
    """
    best_candidate = None
    best_score = 0.0
    
    for candidate in all_moves:
        # Skip zelfde move
        if candidate == target_move:
            continue
        
        # Check of het dezelfde maat is
        if candidate.size != target_move.size:
            continue
        
        # Check quantity match (binnen toegestaan verschil)
        qty_ratio = min(candidate.qty, target_move.qty) / max(candidate.qty, target_move.qty)
        if qty_ratio < (1.0 - params.max_swap_quantity_diff):
            continue
        
        # Check of swap zou verbeteren
        # Huidige situatie
        target_dests = len(destinations_map.get(target_move.from_store, set()))
        candidate_dests = len(destinations_map.get(candidate.from_store, set()))
        current_total = target_dests + candidate_dests
        
        # Na swap
        # Target zou naar candidate's bestemming gaan
        # Candidate zou naar target's bestemming gaan
        
        # Simuleer nieuwe bestemmingen
        target_new_dests = destinations_map.get(target_move.from_store, set()).copy()
        target_new_dests.discard(target_move.to_store)
        target_new_dests.add(candidate.to_store)
        
        candidate_new_dests = destinations_map.get(candidate.from_store, set()).copy()
        candidate_new_dests.discard(candidate.to_store)
        candidate_new_dests.add(target_move.to_store)
        
        new_total = len(target_new_dests) + len(candidate_new_dests)
        
        # Check of verbetering
        if new_total >= current_total:
            continue  # Geen verbetering
        
        # Bereken consolidation score
        score = calculate_consolidation_score(
            target_move, candidate, destinations_map, params
        )
        
        if score > best_score:
            best_score = score
            best_candidate = candidate
    
    if best_candidate and best_score > 0:
        return (best_candidate, best_score)
    
    return None


def apply_swap(
    moves: List[Move],
    move_a: Move,
    move_b: Move
) -> List[Move]:
    """
    Voer een swap uit tussen twee moves
    
    Wissel de bestemmingen om tussen move_a en move_b.
    
    Args:
        moves: Lijst van moves
        move_a: Eerste move
        move_b: Tweede move
        
    Returns:
        Nieuwe lijst van moves met swap toegepast
    """
    new_moves = []
    
    for move in moves:
        if move == move_a:
            # Swap: move_a gaat nu naar move_b's bestemming
            swapped = Move(
                volgnummer=move.volgnummer,
                size=move.size,
                from_store=move.from_store,
                from_store_name=move.from_store_name,
                to_store=move_b.to_store,
                to_store_name=move_b.to_store_name,
                qty=move.qty,
                score=move.score,
                reason=move.reason,
                from_bv=move.from_bv,
                to_bv=move_b.to_bv,
                breaks_sequence=move.breaks_sequence,
                creates_sequence=move.creates_sequence,
                original_move=False,
                swap_reason=f"Swapped with {move_b.from_store}"
            )
            new_moves.append(swapped)
        
        elif move == move_b:
            # Swap: move_b gaat nu naar move_a's bestemming
            swapped = Move(
                volgnummer=move.volgnummer,
                size=move.size,
                from_store=move.from_store,
                from_store_name=move.from_store_name,
                to_store=move_a.to_store,
                to_store_name=move_a.to_store_name,
                qty=move.qty,
                score=move.score,
                reason=move.reason,
                from_bv=move.from_bv,
                to_bv=move_a.to_bv,
                breaks_sequence=move.breaks_sequence,
                creates_sequence=move.creates_sequence,
                original_move=False,
                swap_reason=f"Swapped with {move_a.from_store}"
            )
            new_moves.append(swapped)
        
        else:
            new_moves.append(move)
    
    return new_moves


def optimize_move_consolidation(
    moves: List[Move],
    article: ArticleStock,
    params: OptimizationParams
) -> Optional[OptimizationResult]:
    """
    Optimaliseer moves door consolidatie (reduceer aantal bestemmingen per bron)
    
    Strategie:
    1. Identificeer bronnen met meerdere bestemmingen
    2. Zoek swap mogelijkheden die consolideren
    3. Voer swaps uit als ze voldoende voordeel bieden
    4. Herhaal tot geen verbeteringen meer mogelijk
    
    Args:
        moves: Lijst van initiële moves
        article: Artikel informatie
        params: Optimalisatie parameters
        
    Returns:
        OptimizationResult met geoptimaliseerde moves
    """
    if not params.enable_consolidation:
        return None
    
    if len(moves) < 2:
        return None  # Niets te optimaliseren
    
    # === METRICS VOOR ===
    destinations_before = calculate_destinations_per_source(moves)
    total_shipments_before = len(moves)
    unique_routes_before = len(set((m.from_store, m.to_store) for m in moves))
    dests_per_source_before = {k: len(v) for k, v in destinations_before.items()}
    
    # === OPTIMALISATIE LOOP ===
    optimized_moves = moves.copy()
    swap_details = []
    swaps_performed = 0
    swaps_attempted = 0
    
    for iteration in range(params.max_swap_iterations):
        improved_this_iteration = False
        
        # Bereken huidige staat
        current_destinations = calculate_destinations_per_source(optimized_moves)
        
        # Vind bronnen met meerdere bestemmingen
        multi_dest_sources = [
            source for source, dests in current_destinations.items()
            if len(dests) > 1
        ]
        
        if not multi_dest_sources:
            break  # Alles al geoptimaliseerd
        
        # Voor elke bron met meerdere bestemmingen, probeer swaps
        for source in multi_dest_sources:
            if swaps_performed >= params.max_swaps_per_article:
                break
            
            # Vind moves van deze bron
            source_moves = [m for m in optimized_moves if m.from_store == source]
            
            for move in source_moves:
                swaps_attempted += 1
                
                # Zoek swap kandidaat
                swap_candidate = find_swap_candidate(
                    move,
                    optimized_moves,
                    current_destinations,
                    params
                )
                
                if swap_candidate:
                    candidate_move, score = swap_candidate
                    
                    # Check of swap voordeel biedt
                    if score >= params.min_consolidation_benefit:
                        # Voer swap uit
                        before_a = f"{move.from_store} → {move.to_store}: {move.qty}x {move.size}"
                        before_b = f"{candidate_move.from_store} → {candidate_move.to_store}: {candidate_move.qty}x {candidate_move.size}"
                        
                        optimized_moves = apply_swap(optimized_moves, move, candidate_move)
                        
                        # Find swapped moves
                        after_a_move = next(m for m in optimized_moves if m.from_store == move.from_store and m.size == move.size and not m.original_move)
                        after_b_move = next(m for m in optimized_moves if m.from_store == candidate_move.from_store and m.size == candidate_move.size and not m.original_move)
                        
                        after_a = f"{after_a_move.from_store} → {after_a_move.to_store}: {after_a_move.qty}x {after_a_move.size}"
                        after_b = f"{after_b_move.from_store} → {after_b_move.to_store}: {after_b_move.qty}x {after_b_move.size}"
                        
                        # Track swap
                        swap_detail = SwapDetail(
                            move_a_before=before_a,
                            move_a_after=after_a,
                            move_b_before=before_b,
                            move_b_after=after_b,
                            reason=f"Reduced {move.from_store}'s destinations",
                            benefit=int(score)
                        )
                        swap_details.append(swap_detail)
                        
                        swaps_performed += 1
                        improved_this_iteration = True
                        
                        if params.verbose_logging:
                            print(f"Swap {swaps_performed}: {before_a} <-> {before_b}")
                        
                        break  # Next source
        
        if not improved_this_iteration:
            break  # Geen verdere verbeteringen mogelijk
    
    # === METRICS NA ===
    destinations_after = calculate_destinations_per_source(optimized_moves)
    total_shipments_after = len(optimized_moves)
    unique_routes_after = len(set((m.from_store, m.to_store) for m in optimized_moves))
    dests_per_source_after = {k: len(v) for k, v in destinations_after.items()}
    
    # Bereken metrics
    metrics = ConsolidationMetrics(
        total_shipments_before=total_shipments_before,
        unique_routes_before=unique_routes_before,
        destinations_per_source_before=dests_per_source_before,
        total_shipments_after=total_shipments_after,
        unique_routes_after=unique_routes_after,
        destinations_per_source_after=dests_per_source_after,
        swaps_performed=swaps_performed,
        swaps_attempted=swaps_attempted
    )
    metrics.calculate_improvement()
    
    # Check of we echt verbeterd hebben
    if metrics.shipments_saved <= 0 and metrics.routes_saved <= 0:
        return None  # Geen verbetering
    
    # Maak explanation
    explanation = OptimizationExplanation(
        optimization_type="move_consolidation",
        destinations_before={k: list(v) for k, v in destinations_before.items()},
        destinations_after={k: list(v) for k, v in destinations_after.items()},
        swaps=swap_details,
        metrics=metrics
    )
    explanation.generate_summary()
    
    return OptimizationResult(
        moves=optimized_moves,
        explanation=explanation,
        improved=True
    )

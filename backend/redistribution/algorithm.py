"""
Kern herverdelingsalgoritme — orchestratie (Fase 3, PR-022).

Deze module knoopt de deelstappen aan elkaar: data laden (data_loading),
situatie classificeren (situation), moves genereren (bundle_planner of het
legacy pad), filteren (scoring) en het Proposal opbouwen. De onderliggende
logica staat in aparte modules; de meest gebruikte symbolen worden hier
her-geëxporteerd voor achterwaartse compatibiliteit.
"""
import logging
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from .domain import Proposal
from .constraints import RedistributionParams, DEFAULT_PARAMS
from .bv_config import BVConfig, get_bv_config
from .store_profiles import StoreProfile
from .scoring import filter_low_quality_moves
from .situation import classify_article_situation, format_situation_rule
from .data_loading import (
    calculate_batch_store_totals,
    load_store_total_inventory,
    load_article_data,
)
from .bundle_planner import generate_moves_for_article
from .legacy_size_planner import (
    generate_moves_for_size,
    check_and_consolidate_fragmented_bv,
)
from db_models import ArtikelVoorraad

logger = logging.getLogger(__name__)

# Backwards-compat re-exports: deze symbolen zijn in Fase 3 naar aparte modules
# verplaatst, maar blijven via redistribution.algorithm importeerbaar zodat
# bestaande imports (o.a. tests) ongewijzigd werken.
__all__ = [
    "generate_redistribution_proposals_for_article",
    "generate_redistribution_proposals_for_batch",
    "generate_moves_for_article",
    "generate_moves_for_size",
    "load_article_data",
    "calculate_batch_store_totals",
    "load_store_total_inventory",
    "check_and_consolidate_fragmented_bv",
]


def generate_redistribution_proposals_for_article(
    db: Session,
    volgnummer: str,
    batch_id: int,
    params: Optional[RedistributionParams] = None,
    batch_store_totals: Optional[Dict[str, int]] = None,
    store_total_inventory: Optional[Dict[str, int]] = None,
    bv_config: Optional[BVConfig] = None,
    store_profiles: Optional[Dict[str, StoreProfile]] = None,
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

    # BV-configuratie éénmalig resolven (BVConfig() doet file-I/O) en expliciet
    # doorgeven aan alle onderliggende stappen (dependency injection).
    if bv_config is None:
        bv_config = get_bv_config()

    # === STAP 1: Data ophalen ===
    article = load_article_data(
        db, volgnummer, batch_id, batch_store_totals, store_total_inventory,
        bv_config=bv_config, store_profiles=store_profiles,
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
            article, params, working_inventory, bv_config
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
                    article, size, params, working_inventory, bv_config
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
    bv_config: Optional[BVConfig] = None,
    store_profiles: Optional[Dict[str, StoreProfile]] = None,
) -> List[Proposal]:
    """Genereer herverdelingsvoorstellen voor alle artikelen in een batch.

    `bv_config`/`store_profiles` kunnen expliciet worden meegegeven (dependency
    injection). De BV-configuratie wordt hier éénmalig per batch geresolved
    (BVConfig() doet file-I/O) en aan elk artikel doorgegeven.
    """
    records = db.query(ArtikelVoorraad.volgnummer).filter(
        ArtikelVoorraad.batch_id == batch_id,
    ).distinct().all()

    volgnummers = [r[0] for r in records]

    # Eenmalig totaalvoorraad per filiaal berekenen voor capacity scoring
    batch_store_totals = calculate_batch_store_totals(db, batch_id)

    # Door gebruiker opgegeven totale winkelvoorraad (tiebreaker bij sales=0)
    store_total_inventory = load_store_total_inventory(db, batch_id)

    # Config één keer resolven en hergebruiken over alle artikelen in de batch.
    if bv_config is None:
        bv_config = get_bv_config()

    proposals = []
    for volgnummer in volgnummers:
        proposal = generate_redistribution_proposals_for_article(
            db, volgnummer, batch_id, params,
            batch_store_totals=batch_store_totals,
            store_total_inventory=store_total_inventory,
            bv_config=bv_config,
            store_profiles=store_profiles,
        )
        if proposal:
            proposals.append(proposal)

    return proposals

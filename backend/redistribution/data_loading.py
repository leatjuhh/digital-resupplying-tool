"""Data-laadlaag voor het herverdelingsalgoritme (Fase 3, PR-022).

Zet databaserijen om naar in-memory ArticleStock-objecten — inlezen en
aggregeren, geen planning-/scoringlogica. BV-configuratie en winkelprofielen
worden via dependency injection meegegeven (Fase 3.3).
"""
import logging
from collections import defaultdict
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from .domain import ArticleStock, StoreInventory, SizeType
from .constraints import get_size_order, LETTER_SIZE_ORDER
from .bv_config import BVConfig, get_bv_config
from .store_config import is_redistribution_candidate
from .store_profiles import StoreProfile, get_store_profile
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
    bv_config: Optional[BVConfig] = None,
    store_profiles: Optional[Dict[str, StoreProfile]] = None,
) -> Optional[ArticleStock]:
    """Laad artikel voorraad data uit database.

    `bv_config` en `store_profiles` kunnen expliciet worden meegegeven
    (dependency injection); bij None wordt de gedeelde read-only configuratie
    gebruikt.
    """
    records = db.query(ArtikelVoorraad).filter(
        ArtikelVoorraad.volgnummer == volgnummer,
        ArtikelVoorraad.batch_id == batch_id,
    ).all()

    if not records:
        return None

    article = ArticleStock(
        volgnummer=volgnummer,
        omschrijving=str(records[0].omschrijving),
        batch_id=batch_id,
    )

    bv_config = bv_config if bv_config is not None else get_bv_config()

    stores_data: Dict[str, Dict] = defaultdict(lambda: {
        'inventory': {},
        'sales_total': 0,
        'store_name': '',
        'bv_name': None,
    })

    all_sizes_set = set()

    for record in records:
        # DB→domein-grens: ORM-kolommen expliciet als str typen (record.* is voor
        # de typechecker Column[str], op runtime een gewone str).
        store_code = str(record.filiaal_code)

        if not is_redistribution_candidate(store_code):
            continue

        size = str(record.maat)

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
        profile = get_store_profile(store_code, store_profiles)
        max_capacity = profile.max_capacity if profile else 0
        store_inv.calculate_metrics(
            batch_total=batch_total,
            max_capacity=max_capacity,
            store_total=store_total,
        )
        article.stores[store_code] = store_inv

    article.calculate_aggregates()
    return article

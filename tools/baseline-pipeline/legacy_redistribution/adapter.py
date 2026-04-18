"""
Adapterlaag tussen gecombineerde weekdataset en DRT domain models.
Behoudt Proposal/Move compatibiliteit zonder database-afhankelijkheid.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .constraints import get_size_order, LETTER_SIZE_ORDER
from .domain import ArticleStock, SizeSequence, SizeType, StoreInventory


def detect_size_type(sizes: List[str]) -> SizeType:
    """
    Detecteer type maatreeks.
    """
    if not sizes:
        return SizeType.CUSTOM

    if all(size.isdigit() for size in sizes):
        return SizeType.NUMERIC

    sizes_upper = [size.upper() for size in sizes]
    if all(size in LETTER_SIZE_ORDER or "/" in size for size in sizes_upper):
        return SizeType.LETTER

    return SizeType.CUSTOM


def detect_size_sequences(
    store_inventory: Dict[str, int],
    all_sizes_sorted: List[str],
    min_width: int = 3,
) -> List[SizeSequence]:
    """
    Detecteer opeenvolgende maatreeksen in een winkel.
    """
    sequences: List[SizeSequence] = []
    available_sizes = [size for size in all_sizes_sorted if store_inventory.get(size, 0) > 0]

    if len(available_sizes) < min_width:
        return sequences

    current_sequence: List[str] = []
    for size in all_sizes_sorted:
        if store_inventory.get(size, 0) > 0:
            current_sequence.append(size)
        else:
            if len(current_sequence) >= min_width:
                sequences.append(
                    SizeSequence(
                        store_code="",
                        sizes=current_sequence.copy(),
                        size_type=detect_size_type(current_sequence),
                        width=len(current_sequence),
                    )
                )
            current_sequence = []

    if len(current_sequence) >= min_width:
        sequences.append(
            SizeSequence(
                store_code="",
                sizes=current_sequence.copy(),
                size_type=detect_size_type(current_sequence),
                width=len(current_sequence),
            )
        )

    return sequences


def article_from_combined_record(record: Dict, batch_id: int = 0) -> ArticleStock:
    """
    Converteer een gecombineerd weekrecord naar ArticleStock.
    """
    snapshot = record["snapshot"]
    article = ArticleStock(
        volgnummer=str(record["article_id"]),
        omschrijving=snapshot.get("meta", {}).get("Omschrijving", ""),
        batch_id=batch_id,
    )

    all_sizes = snapshot.get("sizes", [])
    article.all_sizes = get_size_order(all_sizes)
    article.size_type = detect_size_type(article.all_sizes)

    for store_code, store_data in snapshot.get("stores", {}).items():
        inventory = {
            size: int(store_data.get(size, 0))
            for size in article.all_sizes
        }
        sold = int(store_data.get("sold", 0) or 0)

        store = StoreInventory(
            store_code=str(store_code),
            store_name=store_data.get("store_name", str(store_code)),
            inventory=inventory,
            sales={"TOTAL": sold} if sold > 0 else {},
        )
        store.calculate_metrics()
        article.stores[store.store_code] = store

        sequences = detect_size_sequences(inventory, article.all_sizes, min_width=3)
        for sequence in sequences:
            sequence.store_code = store.store_code
        article.size_sequences[store.store_code] = sequences

    article.calculate_aggregates()
    return article


def manual_moves_from_record(record: Dict) -> List[Dict]:
    """
    Haal handmatige moves op uit een gecombineerd record.
    """
    return list(record.get("moves", []))


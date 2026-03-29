"""
Adapterlaag tussen geïmporteerde weekbestanden en DRT-domainmodellen.

Read-only helper voor offline evaluatie zonder database- of Linux-servertoegang.
"""

from __future__ import annotations

from typing import Dict, List

from .constraints import get_size_order, LETTER_SIZE_ORDER
from .domain import ArticleStock, SizeType, StoreInventory


def detect_size_type(sizes: List[str]) -> SizeType:
    """Detecteer type maatreeks."""
    if not sizes:
        return SizeType.CUSTOM
    if all(size.isdigit() for size in sizes):
        return SizeType.NUMERIC
    sizes_upper = [size.upper() for size in sizes]
    if all(size in LETTER_SIZE_ORDER or "/" in size for size in sizes_upper):
        return SizeType.LETTER
    return SizeType.CUSTOM


def article_from_combined_record(record: Dict, batch_id: int = 0) -> ArticleStock:
    """Converteer een gecombineerd weekrecord naar ArticleStock."""
    snapshot = record["snapshot"]
    article = ArticleStock(
        volgnummer=str(record["article_id"]),
        omschrijving=snapshot.get("meta", {}).get("Omschrijving", ""),
        batch_id=batch_id,
    )

    article.all_sizes = get_size_order(snapshot.get("sizes", []))
    article.size_type = detect_size_type(article.all_sizes)

    for store_code, store_data in snapshot.get("stores", {}).items():
        inventory = {
            size: int(store_data.get(size, 0) or 0)
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

    article.calculate_aggregates()
    return article

"""
Helpers voor assignment-sync en detailopbouw.
"""

from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session

import db_models
from redistribution.constraints import get_size_order
from utils import sort_store_ids


def _collect_store_inventory(voorraad_records: list[db_models.ArtikelVoorraad]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    stores_inventory: dict[str, dict[str, Any]] = {}
    all_sizes: set[str] = set()

    for record in voorraad_records:
        store_key = record.filiaal_code
        if store_key not in stores_inventory:
            stores_inventory[store_key] = {
                "store_id": record.filiaal_code,
                "store_name": record.filiaal_naam,
                "sizes": {},
                "sold_total": 0,
            }

        stores_inventory[store_key]["sizes"][record.maat] = record.voorraad
        stores_inventory[store_key]["sold_total"] = max(
            stores_inventory[store_key]["sold_total"],
            record.verkocht,
        )
        all_sizes.add(record.maat)

    return stores_inventory, list(all_sizes)


def _group_moves_by_route(moves: list[dict[str, Any]] | None) -> dict[tuple[str, str], dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}

    for move in moves or []:
        from_store = str(move.get("from_store") or "").strip()
        to_store = str(move.get("to_store") or "").strip()
        size = str(move.get("size") or "").strip()
        qty = int(move.get("qty") or 0)

        if not from_store or not to_store or not size or qty <= 0:
            continue

        route_key = (from_store, to_store)
        if route_key not in grouped:
            grouped[route_key] = {
                "from_store_name": move.get("from_store_name") or from_store,
                "to_store_name": move.get("to_store_name") or to_store,
                "sizes": defaultdict(int),
            }

        grouped[route_key]["sizes"][size] += qty

    return grouped


def sync_assignments_from_approved_proposals(db: Session) -> int:
    """
    Maak idempotent assignments aan voor alle goedgekeurde proposals met echte moves.
    """
    proposals = db.query(db_models.Proposal).filter(db_models.Proposal.status == "approved").all()
    batches = {
        batch.id: batch.naam
        for batch in db.query(db_models.PDFBatch).all()
    }

    created_count = 0
    for proposal in proposals:
        created_count += sync_assignments_for_proposal(db, proposal, batches.get(proposal.pdf_batch_id))

    db.commit()
    return created_count


def sync_assignments_for_proposal(
    db: Session,
    proposal: db_models.Proposal,
    batch_name: str | None = None,
) -> int:
    """
    Zet een goedgekeurd voorstel om in store-facing assignments.
    """
    if proposal.status != "approved":
        return 0

    route_groups = _group_moves_by_route(proposal.moves)
    if not route_groups:
        return 0

    # Geen batch → geen assignments aanmaken (bv. testvoorstellen zonder batch)
    if proposal.pdf_batch_id is None:
        return 0

    if batch_name is None and proposal.pdf_batch_id:
        batch = db.query(db_models.PDFBatch).filter(db_models.PDFBatch.id == proposal.pdf_batch_id).first()
        batch_name = batch.naam if batch else f"Batch {proposal.pdf_batch_id}"

    created_count = 0
    for (from_store_code, to_store_code), route_data in route_groups.items():
        series = db.query(db_models.AssignmentSeries).filter(
            db_models.AssignmentSeries.pdf_batch_id == proposal.pdf_batch_id,
            db_models.AssignmentSeries.store_code == from_store_code,
        ).first()

        if not series:
            series = db_models.AssignmentSeries(
                pdf_batch_id=proposal.pdf_batch_id,
                batch_name=batch_name or f"Batch {proposal.pdf_batch_id}",
                store_code=from_store_code,
                store_name=route_data["from_store_name"],
                description=f"Uitvoering voor {route_data['from_store_name']} in {batch_name or f'Batch {proposal.pdf_batch_id}'}",
            )
            db.add(series)
            db.flush()
            created_count += 1
        else:
            series.batch_name = batch_name or series.batch_name
            series.store_name = route_data["from_store_name"]
            series.description = f"Uitvoering voor {route_data['from_store_name']} in {series.batch_name}"

        size_order = get_size_order(list(route_data["sizes"].keys()))
        size_quantities = [
            {"size": size, "qty": int(route_data["sizes"][size])}
            for size in size_order
            if int(route_data["sizes"][size]) > 0
        ]

        item = db.query(db_models.AssignmentItem).filter(
            db_models.AssignmentItem.proposal_id == proposal.id,
            db_models.AssignmentItem.from_store_code == from_store_code,
            db_models.AssignmentItem.to_store_code == to_store_code,
        ).first()

        if not item:
            item = db_models.AssignmentItem(
                series_id=series.id,
                proposal_id=proposal.id,
                artikelnummer=proposal.artikelnummer,
                article_name=proposal.article_name,
                from_store_code=from_store_code,
                from_store_name=route_data["from_store_name"],
                to_store_code=to_store_code,
                to_store_name=route_data["to_store_name"],
                size_quantities=size_quantities,
                total_quantity=sum(entry["qty"] for entry in size_quantities),
                status="open",
            )
            db.add(item)
            created_count += 1
        else:
            item.series_id = series.id
            item.article_name = proposal.article_name
            item.artikelnummer = proposal.artikelnummer
            item.from_store_name = route_data["from_store_name"]
            item.to_store_name = route_data["to_store_name"]
            item.size_quantities = size_quantities
            item.total_quantity = sum(entry["qty"] for entry in size_quantities)

    return created_count


def build_assignment_item_detail(db: Session, item: db_models.AssignmentItem) -> dict[str, Any]:
    """
    Bouw detaildata voor een assignment-item op basis van proposal + voorraad.
    """
    proposal = db.query(db_models.Proposal).filter(db_models.Proposal.id == item.proposal_id).first()
    if not proposal:
        raise ValueError("Proposal not found for assignment item")

    voorraad_records = db.query(db_models.ArtikelVoorraad).filter(
        db_models.ArtikelVoorraad.batch_id == proposal.pdf_batch_id,
        db_models.ArtikelVoorraad.volgnummer == proposal.artikelnummer,
    ).all()

    if not voorraad_records:
        raise ValueError("Inventory data not found for assignment item")

    first_record = voorraad_records[0]
    metadata = first_record.pdf_metadata or {}

    stores_inventory, all_sizes = _collect_store_inventory(voorraad_records)
    assignment_sizes = [entry.get("size", "") for entry in item.size_quantities or [] if entry.get("size")]
    sorted_sizes = get_size_order(list(set(all_sizes).union(assignment_sizes)))

    relevant_store_ids = [store_id for store_id in [item.from_store_code, item.to_store_code] if store_id in stores_inventory]
    sorted_store_ids = sort_store_ids(relevant_store_ids)

    proposed_inventory: dict[str, dict[str, int]] = {}
    for store_id in sorted_store_ids:
        proposed_inventory[store_id] = dict(stores_inventory[store_id]["sizes"])

    for size_entry in item.size_quantities or []:
        size = str(size_entry.get("size") or "")
        qty = int(size_entry.get("qty") or 0)
        if not size or qty <= 0:
            continue

        if item.from_store_code in proposed_inventory:
            current_from = proposed_inventory[item.from_store_code].get(size, 0)
            proposed_inventory[item.from_store_code][size] = max(0, current_from - qty)

        if item.to_store_code in proposed_inventory:
            proposed_inventory[item.to_store_code][size] = proposed_inventory[item.to_store_code].get(size, 0) + qty

    stores_data = []
    for store_id in sorted_store_ids:
        store = stores_inventory[store_id]
        stores_data.append({
            "id": store["store_id"],
            "name": store["store_name"],
            "inventory_current": [store["sizes"].get(size, 0) for size in sorted_sizes],
            "inventory_proposed": [proposed_inventory[store_id].get(size, 0) for size in sorted_sizes],
            "sold": store["sold_total"],
        })

    return {
        "assignment_id": item.id,
        "proposal_id": proposal.id,
        "batch_id": proposal.pdf_batch_id,
        "artikelnummer": proposal.artikelnummer,
        "article_name": proposal.article_name,
        "status": item.status,
        "size_quantities": item.size_quantities or [],
        "total_quantity": item.total_quantity,
        "failure_reason": item.failure_reason,
        "failure_size": item.failure_size,
        "failure_notes": item.failure_notes,
        "metadata": metadata,
        "sizes": sorted_sizes,
        "stores": stores_data,
        "from_store_code": item.from_store_code,
        "from_store_name": item.from_store_name,
        "to_store_code": item.to_store_code,
        "to_store_name": item.to_store_name,
        "completed_at": item.completed_at.isoformat() if item.completed_at else None,
    }

"""
PDF Ingest API Router — HTTP-laag (Fase 3.1).

Deze module bevat uitsluitend de HTTP-laag: route-definities, authenticatie/
autorisatie, request-validatie (Pydantic) en response-mapping. De
domeinlogica staat in `pdf_ingest_service.py`, de persistentie in
`pdf_ingest_persistence.py` (architectuurgrens, hoofdstuk 5 + R4.4).
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
import json
import os
import shutil
import logging

from database import get_db
from db_models import PDFBatch, ArtikelVoorraad, PDFParseLog, Proposal, Feedback, User
from auth import require_permission
from assignment_service import (
    remove_assignments_for_proposal,
    sync_assignments_for_proposal,
)
from utils import (
    sort_store_ids,
    secure_pdf_filename,
    UnsafeFilenameError,
)
from pdf_ingest_service import (
    apply_moves_to_inventory,
    collect_store_inventory,
    is_optimal_distribution_proposal,
    run_batch_ingest,
)
# Backwards-compat re-export: deze constante is in Fase 3.1 naar
# pdf_ingest_service verplaatst, maar blijft via deze module importeerbaar zodat
# bestaande imports (o.a. tests) ongewijzigd werken.
from pdf_ingest_service import OPTIMAL_DISTRIBUTION_RULE  # noqa: F401

# Logging: centrale configuratie staat in main.py (PR-019); hier alleen een
# module-logger ophalen.
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

# Upload directory
UPLOAD_DIR = "backend/uploads/pdf_batches"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class RejectProposalRequest(BaseModel):
    reason: Optional[str] = None
    reason_code: Optional[str] = None  # Reden-code uit feedback dropdown


class MoveInput(BaseModel):
    # Validatie van door de client aangeleverde moves (PR-015, R7.3/R9.1). De
    # core-velden zijn verplicht en getypeerd, zodat een onvolledige move een
    # nette 422 oplevert i.p.v. verderop een ongevangen KeyError. Extra velden
    # (from_store_name, score, from_bv, feature_snapshot, ...) worden bewaard
    # via extra="allow", zodat de round-trip met de frontend intact blijft.
    model_config = ConfigDict(extra="allow")
    size: str
    from_store: str
    to_store: str
    qty: int


class UpdateProposalRequest(BaseModel):
    moves: List[MoveInput]
    reason_code: Optional[str] = None  # Reden voor de edit
    comment: Optional[str] = None      # Optionele toelichting


@router.post("/ingest")
async def ingest_pdfs(
    files: List[UploadFile] = File(...),
    batch_name: Optional[str] = Form(None),
    store_total_inventory: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("upload_pdfs"))
):
    """
    Ingest one or more PDF files.

    De feitelijke verwerking (batch-aanmaak, opslaan, parsen, persisteren en
    proposal-generatie) gebeurt in `pdf_ingest_service.run_batch_ingest`; deze
    handler doet alleen de HTTP-specifieke stappen: input-parsing, validatie en
    het teruggeven van de JSON-response.
    """
    logger.info(f"[INGEST_START] Received {len(files)} files")

    # Parse store_total_inventory JSON (optionele HTTP-input)
    extra_data = None
    if store_total_inventory:
        try:
            parsed_totals = json.loads(store_total_inventory)
            if not isinstance(parsed_totals, dict):
                raise ValueError("store_total_inventory moet een object zijn")
            extra_data = {
                "store_total_inventory": {
                    str(k): int(v) for k, v in parsed_totals.items()
                },
                "captured_at": datetime.now().isoformat(),
            }
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Ongeldige store_total_inventory: {exc}",
            )

    # Valideer bestandsnamen vóórdat een batch wordt aangemaakt: een onveilige
    # naam (path traversal, niet-.pdf) is een client-/securityfout die de hele
    # aanvraag weigert met 400, zodat er geen wees-batch achterblijft.
    safe_filenames = []
    for file in files:
        try:
            safe_filenames.append(secure_pdf_filename(file.filename))
        except UnsafeFilenameError as exc:
            raise HTTPException(status_code=400, detail=f"Ongeldige bestandsnaam: {exc}")

    # Default batch-naam
    if not batch_name:
        batch_name = f"Batch {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    payload = run_batch_ingest(
        db, files, safe_filenames, batch_name, extra_data, UPLOAD_DIR
    )
    return JSONResponse(content=payload)


@router.get("/batches")
async def get_batches(db: Session = Depends(get_db)):
    """
    Get all PDF batches

    Returns:
        List of batches with their status
    """
    batches = db.query(PDFBatch).order_by(PDFBatch.created_at.desc()).all()

    return [
        {
            "id": batch.id,
            "naam": batch.naam,
            "status": batch.status,
            "pdf_count": batch.pdf_count,
            "processed_count": batch.processed_count,
            "created_at": batch.created_at.isoformat()
        }
        for batch in batches
    ]


@router.get("/batches/{batch_id}")
async def get_batch_details(batch_id: int, db: Session = Depends(get_db)):
    """
    Get details for a specific batch

    Args:
        batch_id: Batch ID

    Returns:
        Batch details with voorraad records
    """
    batch = db.query(PDFBatch).filter(PDFBatch.id == batch_id).first()

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Get voorraad records
    voorraad_records = db.query(ArtikelVoorraad).filter(
        ArtikelVoorraad.batch_id == batch_id
    ).all()

    # Get logs
    logs = db.query(PDFParseLog).filter(
        PDFParseLog.batch_id == batch_id
    ).order_by(PDFParseLog.created_at.desc()).limit(50).all()

    return {
        "id": batch.id,
        "naam": batch.naam,
        "status": batch.status,
        "pdf_count": batch.pdf_count,
        "processed_count": batch.processed_count,
        "created_at": batch.created_at.isoformat(),
        "record_count": len(voorraad_records),
        "records": [
            {
                "id": record.id,
                "volgnummer": record.volgnummer,
                "omschrijving": record.omschrijving,
                "filiaal_code": record.filiaal_code,
                "filiaal_naam": record.filiaal_naam,
                "maat": record.maat,
                "voorraad": record.voorraad,
                "verkocht": record.verkocht
            }
            for record in voorraad_records[:100]  # Limit for performance
        ],
        "logs": [
            {
                "phase": log.phase,
                "level": log.level,
                "message": log.message,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
    }


@router.delete("/batches/{batch_id}")
async def delete_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_batches"))
):
    """
    Delete a batch and all its data

    Args:
        batch_id: Batch ID

    Returns:
        Success message
    """
    batch = db.query(PDFBatch).filter(PDFBatch.id == batch_id).first()

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Delete voorraad records
    db.query(ArtikelVoorraad).filter(ArtikelVoorraad.batch_id == batch_id).delete()

    # Delete logs
    db.query(PDFParseLog).filter(PDFParseLog.batch_id == batch_id).delete()

    # Delete batch
    db.delete(batch)
    db.commit()

    # Delete files
    batch_dir = os.path.join(UPLOAD_DIR, f"batch_{batch_id}")
    if os.path.exists(batch_dir):
        shutil.rmtree(batch_dir)

    return {"message": f"Batch {batch_id} deleted successfully"}


@router.get("/batches/{batch_id}/proposals")
async def get_batch_proposals(batch_id: int, db: Session = Depends(get_db)):
    """
    Get all proposals for a specific batch

    Args:
        batch_id: PDF Batch ID

    Returns:
        List of proposals with their details
    """
    batch = db.query(PDFBatch).filter(PDFBatch.id == batch_id).first()

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Get proposals
    proposals = db.query(Proposal).filter(
        Proposal.pdf_batch_id == batch_id
    ).all()

    # Count by status
    status_counts = {
        'pending': 0,
        'approved': 0,
        'rejected': 0,
        'edited': 0
    }

    for proposal in proposals:
        status_counts[proposal.status] = status_counts.get(proposal.status, 0) + 1

    return {
        "batch_id": batch_id,
        "batch_name": batch.naam,
        "total_proposals": len(proposals),
        "status_counts": status_counts,
        "proposals": [
            {
                "id": p.id,
                "artikelnummer": p.artikelnummer,
                "article_name": p.article_name,
                "total_moves": p.total_moves,
                "total_quantity": p.total_quantity,
                "status": p.status,
                "reason": p.reason,
                "applied_rules": p.applied_rules,
                "optimization_applied": p.optimization_applied,
                "stores_affected": p.stores_affected,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "reviewed_at": p.reviewed_at.isoformat() if p.reviewed_at else None,
                "reviewed_by": p.reviewed_by,
                "moves": p.moves
            }
            for p in proposals
        ]
    }


@router.get("/proposals/{proposal_id}")
async def get_proposal_detail(proposal_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific proposal

    Args:
        proposal_id: Proposal ID

    Returns:
        Detailed proposal information
    """
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    return {
        "id": proposal.id,
        "batch_id": proposal.pdf_batch_id,
        "artikelnummer": proposal.artikelnummer,
        "article_name": proposal.article_name,
        "moves": proposal.moves,
        "total_moves": proposal.total_moves,
        "total_quantity": proposal.total_quantity,
        "status": proposal.status,
        "reason": proposal.reason,
        "applied_rules": proposal.applied_rules,
        "optimization_applied": proposal.optimization_applied,
        "stores_affected": proposal.stores_affected,
        "created_at": proposal.created_at.isoformat() if proposal.created_at else None,
        "reviewed_at": proposal.reviewed_at.isoformat() if proposal.reviewed_at else None,
        "reviewed_by": proposal.reviewed_by,
        "rejection_reason": proposal.rejection_reason
    }


@router.get("/proposals/{proposal_id}/full")
async def get_proposal_with_full_inventory(proposal_id: int, db: Session = Depends(get_db)):
    """
    Get proposal with complete inventory table and applied moves

    Args:
        proposal_id: Proposal ID

    Returns:
        Complete proposal with inventory data and moves visualization
    """
    # Haal proposal op
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Haal voorraad data op voor dit artikel
    voorraad_records = db.query(ArtikelVoorraad).filter(
        ArtikelVoorraad.batch_id == proposal.pdf_batch_id,
        ArtikelVoorraad.volgnummer == proposal.artikelnummer
    ).all()

    if not voorraad_records:
        raise HTTPException(status_code=404, detail="Inventory data not found for this article")

    # Verzamel metadata van eerste record
    first_record = voorraad_records[0]
    metadata = first_record.pdf_metadata or {}

    # Groepeer voorraad per winkel en maat (domeinlaag)
    stores_inventory, all_sizes = collect_store_inventory(voorraad_records)

    # Sorteer maten
    from redistribution.constraints import get_size_order
    sorted_sizes = get_size_order(list(all_sizes))

    # Sorteer store IDs numeriek (niet lexicografisch!)
    sorted_store_ids = sort_store_ids(list(stores_inventory.keys()))

    # Pas moves toe op voorraad om "proposed" situatie te krijgen (domeinlaag)
    proposed_inventory = apply_moves_to_inventory(stores_inventory, proposal.moves)

    # Bouw stores array (gebruik numeriek gesorteerde IDs)
    stores_data = []
    for store_id in sorted_store_ids:
        store = stores_inventory[store_id]

        # Bouw current en proposed arrays
        current_inventory = [store["sizes"].get(size, 0) for size in sorted_sizes]
        proposed_inv = [proposed_inventory[store_id].get(size, 0) for size in sorted_sizes]

        stores_data.append({
            "id": store["store_id"],
            "name": store["store_name"],
            "inventory_current": current_inventory,
            "inventory_proposed": proposed_inv,
            "sold": store["sold_total"]
        })

    is_optimal_distribution = is_optimal_distribution_proposal(proposal)

    return {
        "id": proposal.id,
        "batch_id": proposal.pdf_batch_id,
        "artikelnummer": proposal.artikelnummer,
        "article_name": proposal.article_name,
        "status": proposal.status,
        "reason": proposal.reason,
        "applied_rules": proposal.applied_rules,
        "moves": proposal.moves,
        "total_moves": proposal.total_moves,
        "total_quantity": proposal.total_quantity,
        "stores_affected": proposal.stores_affected,
        "created_at": proposal.created_at.isoformat() if proposal.created_at else None,
        "reviewed_at": proposal.reviewed_at.isoformat() if proposal.reviewed_at else None,
        "reviewed_by": proposal.reviewed_by,
        "rejection_reason": proposal.rejection_reason,
        "metadata": metadata,
        "sizes": sorted_sizes,
        "stores": stores_data,
        "is_optimal_distribution": is_optimal_distribution,
        "optimal_distribution_reason": proposal.reason if is_optimal_distribution else None,
    }


@router.post("/proposals/{proposal_id}/approve")
async def approve_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("approve_proposals"))
):
    """
    Approve a proposal

    Args:
        proposal_id: Proposal ID

    Returns:
        Updated proposal
    """
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Idempotentie (PR-006): een reeds goedgekeurd voorstel niet opnieuw
    # verwerken. Zonder deze guard maakt elke herhaalde aanroep (dubbele klik,
    # retry) opnieuw een Feedback-rij per move aan. We geven de bestaande staat
    # terug zonder neveneffecten.
    if proposal.status == 'approved':
        return {
            "id": proposal.id,
            "status": proposal.status,
            "reviewed_at": proposal.reviewed_at.isoformat() if proposal.reviewed_at else None,
        "reviewed_by": proposal.reviewed_by,
            "message": "Proposal was al goedgekeurd (geen wijziging)"
        }

    proposal.status = 'approved'
    proposal.reviewed_at = datetime.now()
    proposal.reviewed_by = current_user.username
    proposal.rejection_reason = None

    # Automatisch feedback-record aanmaken per move (geen dialog nodig bij approve)
    for idx, move in enumerate(proposal.moves or []):
        fb = Feedback(
            proposal_id=proposal.id,
            user_id=current_user.id,
            category="approval",
            action_taken="approved",
            move_index=idx,
            feature_snapshot=move.get("feature_snapshot"),
            model_score_at_time=move.get("model_score"),
        )
        db.add(fb)

    sync_assignments_for_proposal(db, proposal)
    db.commit()
    db.refresh(proposal)

    return {
        "id": proposal.id,
        "status": proposal.status,
        "reviewed_at": proposal.reviewed_at.isoformat(),
        "reviewed_by": proposal.reviewed_by,
        "message": "Proposal approved successfully"
    }


@router.post("/proposals/{proposal_id}/reject")
async def reject_proposal(
    proposal_id: int,
    payload: Optional[RejectProposalRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("reject_proposals"))
):
    """
    Reject a proposal

    Args:
        proposal_id: Proposal ID
        reason: Optional rejection reason

    Returns:
        Updated proposal
    """
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Idempotentie (hoofdstuk 6): een reeds afgekeurd voorstel niet opnieuw
    # verwerken — anders maakt elke herhaalde aanroep (dubbele klik, retry) een
    # extra rejection-Feedback-rij aan. Consistent met approve_proposal.
    if proposal.status == 'rejected':
        return {
            "id": proposal.id,
            "status": proposal.status,
            "reviewed_at": proposal.reviewed_at.isoformat() if proposal.reviewed_at else None,
            "reviewed_by": proposal.reviewed_by,
            "rejection_reason": proposal.rejection_reason,
            "message": "Proposal was al afgekeurd (geen wijziging)"
        }

    rejection_reason = payload.reason if payload else None
    reason_code = payload.reason_code if payload and hasattr(payload, "reason_code") else None

    proposal.status = 'rejected'
    proposal.reviewed_at = datetime.now()
    proposal.reviewed_by = current_user.username
    proposal.rejection_reason = rejection_reason

    # Verwijder eerder (bij goedkeuring) aangemaakte store-facing assignments,
    # zodat winkels geen opdracht voor een nu afgekeurd voorstel blijven zien.
    remove_assignments_for_proposal(db, proposal)

    # Feedback-record op proposal-niveau bij reject
    fb = Feedback(
        proposal_id=proposal.id,
        user_id=current_user.id,
        category="rejection",
        action_taken="rejected",
        reason_code=reason_code,
        comment=rejection_reason,
    )
    db.add(fb)

    db.commit()
    db.refresh(proposal)

    return {
        "id": proposal.id,
        "status": proposal.status,
        "reviewed_at": proposal.reviewed_at.isoformat(),
        "reviewed_by": proposal.reviewed_by,
        "rejection_reason": proposal.rejection_reason,
        "message": "Proposal rejected successfully"
    }


@router.put("/proposals/{proposal_id}")
async def update_proposal(
    proposal_id: int,
    payload: UpdateProposalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("edit_proposals"))
):
    """
    Update a proposal with edited moves

    Args:
        proposal_id: Proposal ID
        moves: Updated list of moves

    Returns:
        Updated proposal
    """
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Update moves — serialiseer de gevalideerde modellen terug naar dicts voor
    # de JSON-kolom (extra velden blijven behouden via extra="allow").
    proposal.moves = [move.model_dump() for move in payload.moves]
    proposal.status = 'edited'
    proposal.reviewed_at = datetime.now()
    proposal.reviewed_by = current_user.username

    # Recalculate totals
    proposal.total_moves = len(payload.moves)
    proposal.total_quantity = sum(move.qty for move in payload.moves)

    # Update stores affected
    stores = set()
    for move in payload.moves:
        stores.add(move.from_store)
        stores.add(move.to_store)
    proposal.stores_affected = list(stores)

    # Feedback-record op proposal-niveau bij edit
    fb = Feedback(
        proposal_id=proposal.id,
        user_id=current_user.id,
        category="edit",
        action_taken="edited",
        reason_code=payload.reason_code,
        comment=payload.comment,
    )
    db.add(fb)

    db.commit()
    db.refresh(proposal)

    return {
        "id": proposal.id,
        "status": proposal.status,
        "total_moves": proposal.total_moves,
        "total_quantity": proposal.total_quantity,
        "reviewed_at": proposal.reviewed_at.isoformat() if proposal.reviewed_at else None,
        "reviewed_by": proposal.reviewed_by,
        "message": "Proposal updated successfully"
    }

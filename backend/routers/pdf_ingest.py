"""
PDF Ingest API Router
Handles PDF upload and extraction
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
import logging

from database import get_db
from db_models import PDFBatch, ArtikelVoorraad, PDFParseLog, Proposal
from pdf_extract import parse_pdf_to_records
from redistribution.algorithm import generate_redistribution_proposals_for_batch
from redistribution.constraints import DEFAULT_PARAMS
from utils import sort_stores_by_code, sort_store_ids

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

# Upload directory
UPLOAD_DIR = "backend/uploads/pdf_batches"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/ingest")
async def ingest_pdfs(
    files: List[UploadFile] = File(...),
    batch_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Ingest one or more PDF files
    
    Args:
        files: List of PDF files to process
        batch_name: Optional name for the batch
        db: Database session
        
    Returns:
        JSON response with batch info and processing results
    """
    logger.info(f"[INGEST_START] Received {len(files)} files")
    
    # Create batch
    if not batch_name:
        batch_name = f"Batch {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    batch = PDFBatch(
        naam=batch_name,
        status="PENDING",
        pdf_count=len(files),
        processed_count=0
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    
    batch_id = batch.id
    logger.info(f"[BATCH_CREATE] Created batch {batch_id}: {batch_name}")
    
    # Create batch upload directory
    batch_dir = os.path.join(UPLOAD_DIR, f"batch_{batch_id}")
    os.makedirs(batch_dir, exist_ok=True)
    
    # Process each PDF
    results = []
    success_count = 0
    failed_count = 0
    
    for file in files:
        logger.info(f"[FILE_PROCESS] Processing {file.filename}")
        
        try:
            # Save uploaded file
            file_path = os.path.join(batch_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Parse PDF
            parsed = parse_pdf_to_records(file_path)
            
            # Check for errors
            if parsed.errors:
                # Log errors
                for error in parsed.errors:
                    log_entry = PDFParseLog(
                        batch_id=batch_id,
                        phase="VALIDATION",
                        level="ERROR",
                        message=error,
                        extra_data={"filename": file.filename}
                    )
                    db.add(log_entry)
                
                failed_count += 1
                results.append({
                    "filename": file.filename,
                    "status": "FAILED",
                    "errors": parsed.errors,
                    "artikel_count": 0
                })
                continue
            
            # Save extracted data to database
            artikel_count = save_to_database(db, batch_id, parsed, file.filename)
            
            success_count += 1
            results.append({
                "filename": file.filename,
                "status": "SUCCESS",
                "artikel_count": artikel_count,
                "volgnummer": parsed.meta.get("Volgnummer"),
                "omschrijving": parsed.meta.get("Omschrijving")
            })
            
            logger.info(f"[FILE_SUCCESS] {file.filename}: {artikel_count} records saved")
            
        except Exception as e:
            logger.error(f"[FILE_ERROR] Error processing {file.filename}: {e}", exc_info=True)
            
            # Log error
            log_entry = PDFParseLog(
                batch_id=batch_id,
                phase="PROCESSING",
                level="ERROR",
                message=f"Failed to process file: {str(e)}",
                extra_data={"filename": file.filename}
            )
            db.add(log_entry)
            
            failed_count += 1
            results.append({
                "filename": file.filename,
                "status": "FAILED",
                "errors": [str(e)],
                "artikel_count": 0
            })
    
    # Update batch status
    batch.processed_count = success_count
    
    if failed_count == 0:
        batch.status = "SUCCESS"
    elif success_count == 0:
        batch.status = "FAILED"
    else:
        batch.status = "PARTIAL_SUCCESS"
    
    db.commit()
    
    logger.info(f"[INGEST_COMPLETE] Batch {batch_id}: {success_count} success, {failed_count} failed")
    
    # Generate redistribution proposals if any files were successfully processed
    proposals_count = 0
    if success_count > 0:
        try:
            logger.info(f"[PROPOSALS_START] Generating proposals for batch {batch_id}")
            proposals_count = generate_and_save_proposals(db, batch_id)
            logger.info(f"[PROPOSALS_SUCCESS] Generated {proposals_count} proposals for batch {batch_id}")
        except Exception as e:
            logger.error(f"[PROPOSALS_ERROR] Failed to generate proposals: {e}", exc_info=True)
            # Log error but don't fail the entire batch
            log_entry = PDFParseLog(
                batch_id=batch_id,
                phase="PROPOSAL_GENERATION",
                level="ERROR",
                message=f"Failed to generate proposals: {str(e)}",
                extra_data={}
            )
            db.add(log_entry)
            db.commit()
    
    return JSONResponse(content={
        "batch_id": batch_id,
        "batch_name": batch_name,
        "status": batch.status,
        "total_files": len(files),
        "success_count": success_count,
        "failed_count": failed_count,
        "proposals_generated": proposals_count,
        "results": results
    })


def save_to_database(db: Session, batch_id: int, parsed, filename: str) -> int:
    """
    Save parsed data to database
    
    Args:
        db: Database session
        batch_id: Batch ID
        parsed: ParsedDoc object
        filename: Original filename
        
    Returns:
        Number of records saved
    """
    count = 0
    
    # Get metadata
    volgnummer = parsed.meta.get("Volgnummer", "")
    omschrijving = parsed.meta.get("Omschrijving", "")
    
    # Save each row as separate records (one per size)
    for row in parsed.rows:
        filiaal_code = row.get("filiaal_code", "")
        filiaal_naam = row.get("filiaal_naam", "")
        voorraad_per_maat = row.get("voorraad_per_maat", {})
        verkocht = row.get("verkocht", 0)
        
        # Track if we've saved verkocht for this filiaal yet
        # Only save verkocht value in the FIRST record per filiaal to avoid duplication
        first_record_for_filiaal = True
        
        # Create a record for each size with voorraad > 0
        for maat, voorraad in voorraad_per_maat.items():
            if voorraad > 0 or (verkocht > 0 and first_record_for_filiaal):  # Only save if there's meaningful data
                record = ArtikelVoorraad(
                    batch_id=batch_id,
                    volgnummer=volgnummer,
                    omschrijving=omschrijving,
                    filiaal_code=filiaal_code,
                    filiaal_naam=filiaal_naam,
                    maat=maat,
                    voorraad=voorraad,
                    verkocht=verkocht if first_record_for_filiaal else 0,  # Only store verkocht in first record
                    pdf_metadata=parsed.meta
                )
                db.add(record)
                count += 1
                first_record_for_filiaal = False  # Subsequent records get verkocht=0
    
    db.commit()
    
    # Log success
    log_entry = PDFParseLog(
        batch_id=batch_id,
        phase="DATABASE_SAVE",
        level="INFO",
        message=f"Saved {count} records from {filename}",
        extra_data={
            "filename": filename,
            "volgnummer": volgnummer,
            "record_count": count
        }
    )
    db.add(log_entry)
    db.commit()
    
    return count


def generate_and_save_proposals(db: Session, batch_id: int) -> int:
    """
    Generate redistribution proposals for a batch and save them to database
    
    Args:
        db: Database session
        batch_id: PDF Batch ID
        
    Returns:
        Number of proposals created
    """
    # Generate proposals using the redistribution algorithm
    proposals = generate_redistribution_proposals_for_batch(db, batch_id, DEFAULT_PARAMS)
    
    if not proposals:
        return 0
    
    # Save each proposal to database
    saved_count = 0
    for proposal in proposals:
        # Convert proposal to database model
        db_proposal = Proposal(
            pdf_batch_id=batch_id,
            artikelnummer=proposal.volgnummer,
            article_name=proposal.article_name,
            moves=[
                {
                    "size": move.size,
                    "from_store": move.from_store,
                    "from_store_name": move.from_store_name,
                    "to_store": move.to_store,
                    "to_store_name": move.to_store_name,
                    "qty": move.qty,
                    "score": round(move.score, 2),
                    "reason": move.reason,
                    "from_bv": move.from_bv,
                    "to_bv": move.to_bv
                }
                for move in proposal.moves
            ],
            total_moves=proposal.total_moves,
            total_quantity=proposal.total_quantity,
            status='pending',
            reason=proposal.reason,
            applied_rules=proposal.applied_rules,
            optimization_applied=str(proposal.optimization_applied).lower(),
            stores_affected=list(proposal.stores_affected)
        )
        db.add(db_proposal)
        saved_count += 1
    
    db.commit()
    
    # Log success
    log_entry = PDFParseLog(
        batch_id=batch_id,
        phase="PROPOSAL_GENERATION",
        level="INFO",
        message=f"Generated {saved_count} redistribution proposals",
        extra_data={"proposals_count": saved_count}
    )
    db.add(log_entry)
    db.commit()
    
    return saved_count


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
async def delete_batch(batch_id: int, db: Session = Depends(get_db)):
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
    
    # Groepeer voorraad per winkel en maat
    stores_inventory = {}
    all_sizes = set()
    
    for record in voorraad_records:
        store_key = record.filiaal_code
        if store_key not in stores_inventory:
            stores_inventory[store_key] = {
                "store_id": record.filiaal_code,
                "store_name": record.filiaal_naam,
                "sizes": {},
                "sales": {}
            }
        
        stores_inventory[store_key]["sizes"][record.maat] = record.voorraad
        stores_inventory[store_key]["sales"][record.maat] = record.verkocht
        all_sizes.add(record.maat)
    
    # Sorteer maten
    from redistribution.constraints import get_size_order
    sorted_sizes = get_size_order(list(all_sizes))
    
    # Sorteer store IDs numeriek (niet lexicografisch!)
    sorted_store_ids = sort_store_ids(list(stores_inventory.keys()))
    
    # Pas moves toe op voorraad om "proposed" situatie te krijgen
    proposed_inventory = {}
    for store_id, data in stores_inventory.items():
        proposed_inventory[store_id] = dict(data["sizes"])  # Copy current
    
    # Apply moves
    for move in proposal.moves:
        from_store = move["from_store"]
        to_store = move["to_store"]
        size = move["size"]
        qty = move["qty"]
        
        # Verwijder van bron
        if from_store in proposed_inventory and size in proposed_inventory[from_store]:
            proposed_inventory[from_store][size] = max(0, proposed_inventory[from_store][size] - qty)
        
        # Voeg toe aan bestemming
        if to_store in proposed_inventory:
            if size not in proposed_inventory[to_store]:
                proposed_inventory[to_store][size] = 0
            proposed_inventory[to_store][size] += qty
    
    # Bouw stores array (gebruik numeriek gesorteerde IDs)
    stores_data = []
    for store_id in sorted_store_ids:
        store = stores_inventory[store_id]
        
        # Bereken totale verkoop voor deze winkel
        total_sales = sum(store["sales"].values())
        
        # Bouw current en proposed arrays
        current_inventory = [store["sizes"].get(size, 0) for size in sorted_sizes]
        proposed_inv = [proposed_inventory[store_id].get(size, 0) for size in sorted_sizes]
        
        stores_data.append({
            "id": store["store_id"],
            "name": store["store_name"],
            "inventory_current": current_inventory,
            "inventory_proposed": proposed_inv,
            "sold": total_sales
        })
    
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
        "rejection_reason": proposal.rejection_reason,
        "metadata": metadata,
        "sizes": sorted_sizes,
        "stores": stores_data
    }


@router.post("/proposals/{proposal_id}/approve")
async def approve_proposal(proposal_id: int, db: Session = Depends(get_db)):
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
    
    proposal.status = 'approved'
    proposal.reviewed_at = datetime.now()
    proposal.rejection_reason = None
    
    db.commit()
    db.refresh(proposal)
    
    return {
        "id": proposal.id,
        "status": proposal.status,
        "reviewed_at": proposal.reviewed_at.isoformat(),
        "message": "Proposal approved successfully"
    }


@router.post("/proposals/{proposal_id}/reject")
async def reject_proposal(
    proposal_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
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
    
    proposal.status = 'rejected'
    proposal.reviewed_at = datetime.now()
    proposal.rejection_reason = reason
    
    db.commit()
    db.refresh(proposal)
    
    return {
        "id": proposal.id,
        "status": proposal.status,
        "reviewed_at": proposal.reviewed_at.isoformat(),
        "rejection_reason": proposal.rejection_reason,
        "message": "Proposal rejected successfully"
    }


@router.put("/proposals/{proposal_id}")
async def update_proposal(
    proposal_id: int,
    moves: List[dict],
    db: Session = Depends(get_db)
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
    
    # Update moves
    proposal.moves = moves
    proposal.status = 'edited'
    
    # Recalculate totals
    proposal.total_moves = len(moves)
    proposal.total_quantity = sum(move.get('qty', 0) for move in moves)
    
    # Update stores affected
    stores = set()
    for move in moves:
        stores.add(move.get('from_store'))
        stores.add(move.get('to_store'))
    proposal.stores_affected = list(stores)
    
    db.commit()
    db.refresh(proposal)
    
    return {
        "id": proposal.id,
        "status": proposal.status,
        "total_moves": proposal.total_moves,
        "total_quantity": proposal.total_quantity,
        "message": "Proposal updated successfully"
    }

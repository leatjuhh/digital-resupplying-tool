"""
PDF Ingest API Router
Handles PDF upload and extraction
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
import logging

from database import get_db
from db_models import PDFBatch, ArtikelVoorraad, PDFParseLog
from pdf_extract import parse_pdf_to_records

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
    batch_name: Optional[str] = None,
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
    
    return JSONResponse(content={
        "batch_id": batch_id,
        "batch_name": batch_name,
        "status": batch.status,
        "total_files": len(files),
        "success_count": success_count,
        "failed_count": failed_count,
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
        
        # Create a record for each size with voorraad > 0
        for maat, voorraad in voorraad_per_maat.items():
            if voorraad > 0 or verkocht > 0:  # Only save if there's meaningful data
                record = ArtikelVoorraad(
                    batch_id=batch_id,
                    volgnummer=volgnummer,
                    omschrijving=omschrijving,
                    filiaal_code=filiaal_code,
                    filiaal_naam=filiaal_naam,
                    maat=maat,
                    voorraad=voorraad,
                    verkocht=verkocht,
                    pdf_metadata=parsed.meta
                )
                db.add(record)
                count += 1
    
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

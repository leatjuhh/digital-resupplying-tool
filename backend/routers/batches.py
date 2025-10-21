# Importeer FastAPI componenten en database dependencies
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime

# Importeer database models en Pydantic models
from database import get_db
import db_models
from models import BatchCreate, BatchResponse, PDFUploadResponse, BatchDetailResponse

# Importeer PDF parser
from pdf_parser import parse_voorraad_pdf, validate_pdf

# Maak router aan voor batch endpoints
router = APIRouter()

# Upload directory voor PDF bestanden
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/batches/create", response_model=BatchResponse)
async def create_batch(batch_data: BatchCreate, db: Session = Depends(get_db)):
    """
    Maak een nieuwe batch aan voor PDF uploads
    
    De batch groepeert meerdere PDF's die samen verwerkt worden.
    """
    # Maak nieuwe batch in database
    new_batch = db_models.Batch(
        name=batch_data.name,
        status="processing",
        pdf_count=0,
        processed_count=0
    )
    
    # Voeg toe aan database
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    
    return new_batch


@router.post("/batches/{batch_id}/upload", response_model=PDFUploadResponse)
async def upload_pdf_to_batch(
    batch_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload een PDF naar een bestaande batch
    
    De PDF wordt opgeslagen en automatisch geparsed.
    """
    # Check of batch bestaat
    batch = db.query(db_models.Batch).filter(db_models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Check of bestand een PDF is
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Maak batch-specifieke directory
    batch_dir = os.path.join(UPLOAD_DIR, f"batch_{batch_id}")
    os.makedirs(batch_dir, exist_ok=True)
    
    # Genereer unieke bestandsnaam
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(batch_dir, safe_filename)
    
    # Sla PDF op
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Valideer PDF
    if not validate_pdf(file_path):
        os.remove(file_path)  # Verwijder invalide bestand
        raise HTTPException(status_code=400, detail="Invalid PDF file")
    
    # Parse PDF direct (sync voor nu)
    parse_result = parse_voorraad_pdf(file_path)
    
    # Maak BatchPDF record
    batch_pdf = db_models.BatchPDF(
        batch_id=batch_id,
        filename=file.filename,
        file_path=file_path,
        status="completed" if parse_result.get("success") else "failed",
        parsed_data=parse_result,
        error_message=parse_result.get("error") if not parse_result.get("success") else None,
        processed_at=datetime.now()
    )
    
    db.add(batch_pdf)
    
    # Update batch counts
    batch.pdf_count += 1
    if parse_result.get("success"):
        batch.processed_count += 1
    
    # Check of alle PDF's verwerkt zijn
    if batch.pdf_count == batch.processed_count:
        batch.status = "completed"
    
    db.commit()
    
    return PDFUploadResponse(
        batch_id=batch_id,
        filename=file.filename,
        status=batch_pdf.status,
        message=f"Extracted {len(parse_result.get('artikelnummers', []))} artikelnummers" if parse_result.get("success") else f"Failed: {parse_result.get('error')}"
    )


@router.get("/batches/{batch_id}", response_model=BatchDetailResponse)
async def get_batch_details(batch_id: int, db: Session = Depends(get_db)):
    """
    Haal gedetailleerde informatie op van een batch
    
    Inclusief lijst van alle PDF's in de batch.
    """
    # Zoek batch
    batch = db.query(db_models.Batch).filter(db_models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Haal alle PDF's op van deze batch
    pdfs = db.query(db_models.BatchPDF).filter(
        db_models.BatchPDF.batch_id == batch_id
    ).all()
    
    # Converteer naar dict format
    pdf_list = []
    for pdf in pdfs:
        pdf_list.append({
            "id": pdf.id,
            "filename": pdf.filename,
            "status": pdf.status,
            "uploaded_at": pdf.uploaded_at.isoformat() if pdf.uploaded_at else None,
            "processed_at": pdf.processed_at.isoformat() if pdf.processed_at else None,
            "extracted_count": pdf.parsed_data.get("extracted_count", 0) if pdf.parsed_data else 0,
            "error": pdf.error_message
        })
    
    return BatchDetailResponse(
        id=batch.id,
        name=batch.name,
        status=batch.status,
        pdf_count=batch.pdf_count,
        processed_count=batch.processed_count,
        created_at=batch.created_at,
        pdfs=pdf_list
    )


@router.get("/batches", response_model=List[BatchResponse])
async def get_all_batches(db: Session = Depends(get_db)):
    """
    Haal alle batches op
    
    Gesorteerd op nieuwste eerst.
    """
    batches = db.query(db_models.Batch).order_by(
        db_models.Batch.created_at.desc()
    ).all()
    
    return batches

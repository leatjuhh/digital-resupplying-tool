"""
Redistribution API Router
Endpoints voor herverdelingsalgoritme en voorstellen
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from db_models import ArtikelVoorraad, Batch
from redistribution.algorithm import (
    generate_redistribution_proposals_for_article,
    generate_redistribution_proposals_for_batch
)
from redistribution.constraints import RedistributionParams, DEFAULT_PARAMS

router = APIRouter()


@router.post("/redistribution/generate/{batch_id}")
async def generate_proposals(
    batch_id: int,
    enforce_bv_separation: bool = Query(default=True, description="Enforce BV separation constraint"),
    min_move_quantity: int = Query(default=1, description="Minimum quantity per move"),
    enable_optimization: bool = Query(default=True, description="Enable move consolidation optimization"),
    db: Session = Depends(get_db)
):
    """
    Genereer herverdelingsvoorstellen voor een hele batch
    
    Parameters kunnen aangepast worden om het algoritme te configureren.
    """
    # Check of batch bestaat
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Check of er voorraad data is
    count = db.query(ArtikelVoorraad).filter(ArtikelVoorraad.batch_id == batch_id).count()
    if count == 0:
        raise HTTPException(status_code=400, detail="No inventory data found for this batch")
    
    # Configureer parameters
    params = RedistributionParams(
        enforce_bv_separation=enforce_bv_separation,
        min_move_quantity=min_move_quantity,
        enable_optimization=enable_optimization,
        oversupply_threshold=DEFAULT_PARAMS.oversupply_threshold,
        undersupply_threshold=DEFAULT_PARAMS.undersupply_threshold,
        max_move_quantity=DEFAULT_PARAMS.max_move_quantity,
        min_sequence_width=DEFAULT_PARAMS.min_sequence_width
    )
    
    # Genereer voorstellen
    proposals = generate_redistribution_proposals_for_batch(db, batch_id, params)
    
    if not proposals:
        return {
            "batch_id": batch_id,
            "proposals_count": 0,
            "message": "No redistribution needed for this batch",
            "proposals": []
        }
    
    # Converteer naar API response format
    proposals_data = []
    for proposal in proposals:
        proposals_data.append({
            "volgnummer": proposal.volgnummer,
            "article_name": proposal.article_name,
            "total_moves": proposal.total_moves,
            "total_quantity": proposal.total_quantity,
            "stores_affected": list(proposal.stores_affected),
            "status": proposal.status,
            "reason": proposal.reason,
            "applied_rules": proposal.applied_rules,
            "optimization_applied": proposal.optimization_applied,
            "moves": [
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
            ]
        })
    
    return {
        "batch_id": batch_id,
        "batch_name": batch.name,
        "proposals_count": len(proposals),
        "total_moves": sum(p.total_moves for p in proposals),
        "total_quantity": sum(p.total_quantity for p in proposals),
        "parameters": {
            "enforce_bv_separation": enforce_bv_separation,
            "min_move_quantity": min_move_quantity,
            "enable_optimization": enable_optimization
        },
        "proposals": proposals_data
    }


@router.get("/redistribution/article/{volgnummer}/batch/{batch_id}")
async def generate_article_proposal(
    volgnummer: str,
    batch_id: int,
    db: Session = Depends(get_db)
):
    """
    Genereer herverdelingsvoorstel voor een specifiek artikel
    """
    # Check of artikel bestaat in deze batch
    count = db.query(ArtikelVoorraad).filter(
        ArtikelVoorraad.volgnummer == volgnummer,
        ArtikelVoorraad.batch_id == batch_id
    ).count()
    
    if count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Article {volgnummer} not found in batch {batch_id}"
        )
    
    # Genereer voorstel
    proposal = generate_redistribution_proposals_for_article(
        db, volgnummer, batch_id, DEFAULT_PARAMS
    )
    
    if not proposal:
        return {
            "volgnummer": volgnummer,
            "batch_id": batch_id,
            "message": "No redistribution needed for this article",
            "proposal": None
        }
    
    return {
        "volgnummer": proposal.volgnummer,
        "article_name": proposal.article_name,
        "batch_id": proposal.batch_id,
        "total_moves": proposal.total_moves,
        "total_quantity": proposal.total_quantity,
        "stores_affected": list(proposal.stores_affected),
        "status": proposal.status,
        "reason": proposal.reason,
        "applied_rules": proposal.applied_rules,
        "optimization_applied": proposal.optimization_applied,
        "optimization_explanation": proposal.optimization_explanation.summary if proposal.optimization_explanation else None,
        "moves": [
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
                "to_bv": move.to_bv,
                "breaks_sequence": move.breaks_sequence,
                "creates_sequence": move.creates_sequence
            }
            for move in proposal.moves
        ]
    }


@router.get("/redistribution/inventory/{batch_id}")
async def get_inventory_data(
    batch_id: int,
    volgnummer: Optional[str] = Query(None, description="Filter by article number"),
    db: Session = Depends(get_db)
):
    """
    Haal voorraad data op voor debugging
    Geeft overzicht van voorraad per artikel/maat/winkel
    """
    # Check of batch bestaat
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Basis query
    query = db.query(ArtikelVoorraad).filter(ArtikelVoorraad.batch_id == batch_id)
    
    # Filter op artikel indien opgegeven
    if volgnummer:
        query = query.filter(ArtikelVoorraad.volgnummer == volgnummer)
    
    records = query.all()
    
    if not records:
        return {
            "batch_id": batch_id,
            "batch_name": batch.name,
            "total_records": 0,
            "articles": []
        }
    
    # Groepeer per artikel
    articles_data = {}
    for record in records:
        if record.volgnummer not in articles_data:
            articles_data[record.volgnummer] = {
                "volgnummer": record.volgnummer,
                "omschrijving": record.omschrijving,
                "stores": {}
            }
        
        if record.filiaal_code not in articles_data[record.volgnummer]["stores"]:
            articles_data[record.volgnummer]["stores"][record.filiaal_code] = {
                "store_code": record.filiaal_code,
                "store_name": record.filiaal_naam,
                "sizes": {}
            }
        
        articles_data[record.volgnummer]["stores"][record.filiaal_code]["sizes"][record.maat] = {
            "voorraad": record.voorraad,
            "verkocht": record.verkocht
        }
    
    return {
        "batch_id": batch_id,
        "batch_name": batch.name,
        "total_records": len(records),
        "total_articles": len(articles_data),
        "articles": list(articles_data.values())
    }


@router.get("/redistribution/batches")
async def get_batches_with_inventory(db: Session = Depends(get_db)):
    """
    Haal alle batches op die voorraad data hebben
    """
    batches = db.query(Batch).order_by(Batch.created_at.desc()).all()
    
    batches_data = []
    for batch in batches:
        # Tel artikelen en records
        article_count = db.query(ArtikelVoorraad.volgnummer).filter(
            ArtikelVoorraad.batch_id == batch.id
        ).distinct().count()
        
        record_count = db.query(ArtikelVoorraad).filter(
            ArtikelVoorraad.batch_id == batch.id
        ).count()
        
        if article_count > 0:  # Alleen batches met voorraad data
            batches_data.append({
                "id": batch.id,
                "name": batch.name,
                "status": batch.status,
                "created_at": batch.created_at.isoformat() if batch.created_at else None,
                "article_count": article_count,
                "record_count": record_count
            })
    
    return {
        "total_batches": len(batches_data),
        "batches": batches_data
    }

"""
Feedback router — vastleggen en exporteren van gebruikersfeedback op voorstellen.

Reden-codes v1:
  stock_mismatch      — voorraad klopt niet met werkelijkheid
  wrong_store_size    — verkeerde winkelgrootte ingeschat
  external_destination — artikel gaat naar outlet/magazijn/geen-filiaal
  seasonal_hold       — opslaan voor volgend seizoen
  customer_profile    — past niet bij klantenbestand deze winkel
  sequence_break      — zou maatreeks breken
  other_text          — vrije tekst (comment verplicht)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

import db_models
from auth import require_permission
from database import get_db

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

VALID_REASON_CODES = {
    "stock_mismatch",
    "wrong_store_size",
    "external_destination",
    "seasonal_hold",
    "customer_profile",
    "sequence_break",
    "other_text",
}

VALID_ACTIONS = {"approved", "edited", "rejected", "removed", "added"}


class FeedbackCreate(BaseModel):
    proposal_id: int
    action_taken: str
    category: str
    reason_code: Optional[str] = None
    comment: Optional[str] = None
    move_index: Optional[int] = None
    feature_snapshot: Optional[dict] = None
    model_score_at_time: Optional[float] = None

    @field_validator("action_taken")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in VALID_ACTIONS:
            raise ValueError(f"Ongeldig action_taken '{v}'. Kies uit: {VALID_ACTIONS}")
        return v

    @field_validator("reason_code")
    @classmethod
    def validate_reason_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_REASON_CODES:
            raise ValueError(f"Ongeldige reason_code '{v}'. Kies uit: {VALID_REASON_CODES}")
        return v


@router.post("/")
async def create_feedback(
    payload: FeedbackCreate,
    current_user: db_models.User = Depends(require_permission("view_proposals")),
    db: Session = Depends(get_db),
):
    """Leg feedback vast voor een proposal (of specifieke move binnen een proposal)."""
    proposal = db.query(db_models.Proposal).filter(
        db_models.Proposal.id == payload.proposal_id
    ).first()
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal niet gevonden")

    if payload.reason_code == "other_text" and not payload.comment:
        raise HTTPException(
            status_code=422,
            detail="comment is verplicht bij reason_code 'other_text'",
        )

    fb = db_models.Feedback(
        proposal_id=payload.proposal_id,
        category=payload.category,
        action_taken=payload.action_taken,
        reason_code=payload.reason_code,
        comment=payload.comment,
        move_index=payload.move_index,
        feature_snapshot=payload.feature_snapshot,
        model_score_at_time=payload.model_score_at_time,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return {"id": fb.id, "created_at": fb.created_at}


@router.get("/export")
async def export_feedback(
    from_date: Optional[str] = Query(None, description="ISO-datum YYYY-MM-DD"),
    to_date: Optional[str] = Query(None, description="ISO-datum YYYY-MM-DD"),
    current_user: db_models.User = Depends(require_permission("view_proposals")),
    db: Session = Depends(get_db),
):
    """
    Exporteer alle feedback-records als JSON — input voor Werkstroom C (retrain).

    Query params: from=YYYY-MM-DD, to=YYYY-MM-DD (optioneel)
    """
    query = db.query(db_models.Feedback)

    if from_date:
        try:
            dt_from = datetime.fromisoformat(from_date).replace(tzinfo=timezone.utc)
            query = query.filter(db_models.Feedback.created_at >= dt_from)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Ongeldige from_date: {from_date}")

    if to_date:
        try:
            dt_to = datetime.fromisoformat(to_date).replace(tzinfo=timezone.utc)
            query = query.filter(db_models.Feedback.created_at <= dt_to)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Ongeldige to_date: {to_date}")

    records = query.order_by(db_models.Feedback.created_at).all()

    return {
        "count": len(records),
        "from_date": from_date,
        "to_date": to_date,
        "feedback": [
            {
                "id": fb.id,
                "proposal_id": fb.proposal_id,
                "action_taken": fb.action_taken,
                "category": fb.category,
                "reason_code": fb.reason_code,
                "comment": fb.comment,
                "move_index": fb.move_index,
                "feature_snapshot": fb.feature_snapshot,
                "model_score_at_time": fb.model_score_at_time,
                "created_at": fb.created_at.isoformat() if fb.created_at else None,
            }
            for fb in records
        ],
    }


@router.get("/reason-codes")
async def get_reason_codes(
    current_user: db_models.User = Depends(require_permission("view_proposals")),
):
    """Geeft de beschikbare reden-codes terug voor de frontend dropdown."""
    _ = current_user
    return {
        "reason_codes": [
            {"code": "stock_mismatch", "label": "Voorraad klopt niet"},
            {"code": "wrong_store_size", "label": "Verkeerde winkelgrootte"},
            {"code": "external_destination", "label": "Externe bestemming (outlet/magazijn)"},
            {"code": "seasonal_hold", "label": "Opslaan voor volgend seizoen"},
            {"code": "customer_profile", "label": "Past niet bij klantprofiel winkel"},
            {"code": "sequence_break", "label": "Breekt maatreeks"},
            {"code": "other_text", "label": "Anders (toelichting verplicht)"},
        ]
    }

"""
Assignments router - echte store-facing uitvoeringsflow op basis van goedgekeurde proposals.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

import db_models
from assignment_service import build_assignment_item_detail, sync_assignments_from_approved_proposals
from auth import require_permission
from database import get_db

router = APIRouter(prefix="/api/assignments", tags=["assignments"])


class CompleteAssignmentRequest(BaseModel):
    notes: Optional[str] = None


class FailAssignmentRequest(BaseModel):
    reason: str
    size: str
    notes: Optional[str] = None


def _get_role_name(db: Session, user: db_models.User) -> str:
    role = db.query(db_models.Role).filter(db_models.Role.id == user.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Gebruiker heeft geen geldige rol",
        )
    return role.name


def _derive_series_status(items: list[db_models.AssignmentItem]) -> str:
    if not items:
        return "open"
    if all(item.status == "completed" for item in items):
        return "completed"
    if any(item.status == "failed" for item in items):
        return "attention"
    if any(item.status == "completed" for item in items):
        return "in_progress"
    return "open"


def _require_series_access(
    db: Session,
    current_user: db_models.User,
    series: db_models.AssignmentSeries,
) -> str:
    role_name = _get_role_name(db, current_user)
    if role_name == "store":
        if not current_user.store_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Store gebruiker is nog niet gekoppeld aan een filiaal",
            )
        if series.store_code != current_user.store_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Geen toegang tot assignments van een ander filiaal",
            )
    return role_name


def _build_series_summary(series: db_models.AssignmentSeries) -> dict:
    items = list(series.items or [])
    completed = sum(1 for item in items if item.status == "completed")
    failed = sum(1 for item in items if item.status == "failed")
    open_count = sum(1 for item in items if item.status == "open")
    total = len(items)

    return {
        "id": series.id,
        "batch_id": series.pdf_batch_id,
        "batch_name": series.batch_name,
        "store_code": series.store_code,
        "store_name": series.store_name,
        "description": series.description,
        "count": total,
        "completed": completed,
        "failed": failed,
        "pending": open_count,
        "status": _derive_series_status(items),
        "created_at": series.created_at.isoformat() if series.created_at else None,
        "updated_at": series.updated_at.isoformat() if series.updated_at else None,
    }


@router.get("")
async def list_assignments(
    current_user: db_models.User = Depends(require_permission("view_assignments")),
    db: Session = Depends(get_db),
):
    sync_assignments_from_approved_proposals(db)

    role_name = _get_role_name(db, current_user)
    query = db.query(db_models.AssignmentSeries).order_by(
        db_models.AssignmentSeries.created_at.desc(),
        db_models.AssignmentSeries.id.desc(),
    )

    if role_name == "store":
        if not current_user.store_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Store gebruiker is nog niet gekoppeld aan een filiaal",
            )
        query = query.filter(db_models.AssignmentSeries.store_code == current_user.store_code)

    series_list = query.all()
    return {
        "series": [_build_series_summary(series) for series in series_list],
    }


@router.get("/{series_id}")
async def get_assignment_series(
    series_id: int,
    current_user: db_models.User = Depends(require_permission("view_assignments")),
    db: Session = Depends(get_db),
):
    sync_assignments_from_approved_proposals(db)

    series = db.query(db_models.AssignmentSeries).filter(db_models.AssignmentSeries.id == series_id).first()
    if not series:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignmentreeks niet gevonden")

    _require_series_access(db, current_user, series)

    items = sorted(series.items, key=lambda item: (item.status != "open", item.article_name.lower(), item.id))
    return {
        **_build_series_summary(series),
        "items": [
            {
                "id": item.id,
                "proposal_id": item.proposal_id,
                "artikelnummer": item.artikelnummer,
                "article_name": item.article_name,
                "from_store_code": item.from_store_code,
                "from_store_name": item.from_store_name,
                "to_store_code": item.to_store_code,
                "to_store_name": item.to_store_name,
                "size_quantities": item.size_quantities or [],
                "total_quantity": item.total_quantity,
                "status": item.status,
                "failure_reason": item.failure_reason,
                "failure_size": item.failure_size,
                "failure_notes": item.failure_notes,
                "completed_at": item.completed_at.isoformat() if item.completed_at else None,
            }
            for item in items
        ],
    }


@router.get("/{series_id}/items/{item_id}")
async def get_assignment_item(
    series_id: int,
    item_id: int,
    current_user: db_models.User = Depends(require_permission("view_assignments")),
    db: Session = Depends(get_db),
):
    sync_assignments_from_approved_proposals(db)

    series = db.query(db_models.AssignmentSeries).filter(db_models.AssignmentSeries.id == series_id).first()
    if not series:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignmentreeks niet gevonden")

    _require_series_access(db, current_user, series)

    item = db.query(db_models.AssignmentItem).filter(
        db_models.AssignmentItem.id == item_id,
        db_models.AssignmentItem.series_id == series_id,
    ).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment-item niet gevonden")

    try:
        detail = build_assignment_item_detail(db, item)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return {
        "series": _build_series_summary(series),
        "item": detail,
    }


@router.post("/items/{item_id}/complete")
async def complete_assignment_item(
    item_id: int,
    payload: Optional[CompleteAssignmentRequest] = None,
    current_user: db_models.User = Depends(require_permission("view_assignments")),
    db: Session = Depends(get_db),
):
    item = db.query(db_models.AssignmentItem).filter(db_models.AssignmentItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment-item niet gevonden")

    series = db.query(db_models.AssignmentSeries).filter(db_models.AssignmentSeries.id == item.series_id).first()
    if not series:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignmentreeks niet gevonden")

    _require_series_access(db, current_user, series)

    item.status = "completed"
    item.completed_at = datetime.now()
    item.failure_reason = None
    item.failure_size = None
    item.failure_notes = payload.notes if payload else None
    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "status": item.status,
        "completed_at": item.completed_at.isoformat() if item.completed_at else None,
        "message": "Assignment-item gemarkeerd als voltooid",
    }


@router.post("/items/{item_id}/fail")
async def fail_assignment_item(
    item_id: int,
    payload: FailAssignmentRequest,
    current_user: db_models.User = Depends(require_permission("view_assignments")),
    db: Session = Depends(get_db),
):
    item = db.query(db_models.AssignmentItem).filter(db_models.AssignmentItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment-item niet gevonden")

    series = db.query(db_models.AssignmentSeries).filter(db_models.AssignmentSeries.id == item.series_id).first()
    if not series:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignmentreeks niet gevonden")

    _require_series_access(db, current_user, series)

    item.status = "failed"
    item.completed_at = None
    item.failure_reason = payload.reason
    item.failure_size = payload.size
    item.failure_notes = payload.notes
    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "status": item.status,
        "failure_reason": item.failure_reason,
        "failure_size": item.failure_size,
        "failure_notes": item.failure_notes,
        "message": "Assignment-item gemarkeerd als niet uitvoerbaar",
    }

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import db_models
from algorithm_import.reader import ArtifactReadError
from algorithm_import.schemas import ExternalAlgorithmDatasetStatus
from algorithm_import.service import build_config_status, build_dataset_status, build_proposal_comparison, build_week_evaluation
from auth import require_permission
from database import get_db

router = APIRouter(prefix="/api/algorithm-import", tags=["algorithm-import"])


@router.get("/config")
async def get_algorithm_config(
    current_user: db_models.User = Depends(require_permission("view_proposals")),
):
    """Huidig actieve assist_mode + model-versie — voor UI-badge en debugging."""
    _ = current_user
    return build_config_status()


@router.get("/status", response_model=ExternalAlgorithmDatasetStatus)
async def get_algorithm_import_status(
    current_user: db_models.User = Depends(require_permission("view_proposals")),
):
    _ = current_user
    return build_dataset_status()


@router.get("/weeks/{year}/{week}")
async def get_algorithm_week_evaluation(
    year: int,
    week: int,
    current_user: db_models.User = Depends(require_permission("view_proposals")),
):
    _ = current_user
    try:
        return build_week_evaluation(year=year, week=week)
    except ArtifactReadError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/proposals/{proposal_id}/comparison")
async def get_algorithm_proposal_comparison(
    proposal_id: int,
    current_user: db_models.User = Depends(require_permission("view_proposals")),
    db: Session = Depends(get_db),
):
    _ = current_user
    proposal = db.query(db_models.Proposal).filter(db_models.Proposal.id == proposal_id).first()
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found")

    try:
        return build_proposal_comparison(proposal)
    except ArtifactReadError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

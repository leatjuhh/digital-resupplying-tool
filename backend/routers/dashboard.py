"""
Dashboard summary router - eerlijke, data-gedreven KPI's en aandachtspunten.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

import db_models
from auth import require_permission
from database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _iso(value) -> str | None:
    return value.isoformat() if value else None


def _build_pending_batches(db: Session) -> list[dict]:
    batches = db.query(db_models.PDFBatch).order_by(
        db_models.PDFBatch.created_at.desc(),
        db_models.PDFBatch.id.desc(),
    ).limit(10).all()

    result = []
    for batch in batches:
        proposals = db.query(
            db_models.Proposal.id,
            db_models.Proposal.status,
        ).filter(
            db_models.Proposal.pdf_batch_id == batch.id
        ).order_by(
            db_models.Proposal.id.asc()
        ).all()

        total_proposals = len(proposals)
        pending_proposals = sum(1 for _, status in proposals if status == "pending")

        if total_proposals == 0 or pending_proposals == 0:
            continue

        next_pending = next((proposal_id for proposal_id, status in proposals if status == "pending"), None)

        result.append(
            {
                "batch_id": batch.id,
                "batch_name": batch.naam,
                "created_at": _iso(batch.created_at),
                "total_proposals": total_proposals,
                "reviewed_proposals": total_proposals - pending_proposals,
                "pending_proposals": pending_proposals,
                "next_proposal_id": next_pending,
            }
        )

    return result


def _build_recent_activity(db: Session) -> list[dict]:
    activity = []

    recent_batches = db.query(db_models.PDFBatch).order_by(
        db_models.PDFBatch.created_at.desc(),
        db_models.PDFBatch.id.desc(),
    ).limit(3).all()
    for batch in recent_batches:
        activity.append(
            {
                "id": f"batch-{batch.id}",
                "kind": "batch",
                "title": "Nieuwe batch ingelezen",
                "description": f"{batch.naam} met {batch.pdf_count} PDF(s)",
                "created_at": _iso(batch.created_at),
                "href": f"/proposals/batch/{batch.id}",
                "_sort_value": batch.created_at,
            }
        )

    reviewed_proposals = db.query(db_models.Proposal).filter(
        db_models.Proposal.reviewed_at.isnot(None)
    ).order_by(
        db_models.Proposal.reviewed_at.desc(),
        db_models.Proposal.id.desc(),
    ).limit(4).all()
    for proposal in reviewed_proposals:
        status_label = {
            "approved": "Voorstel goedgekeurd",
            "rejected": "Voorstel afgekeurd",
            "edited": "Voorstel bewerkt",
        }.get(proposal.status, "Voorstel bijgewerkt")
        activity.append(
            {
                "id": f"proposal-{proposal.id}",
                "kind": "proposal",
                "title": status_label,
                "description": f"{proposal.article_name} ({proposal.artikelnummer})",
                "created_at": _iso(proposal.reviewed_at),
                "href": f"/proposals/{proposal.id}",
                "_sort_value": proposal.reviewed_at,
            }
        )

    assignment_updates = db.query(db_models.AssignmentItem).filter(
        db_models.AssignmentItem.status.in_(("completed", "failed"))
    ).order_by(
        db_models.AssignmentItem.updated_at.desc(),
        db_models.AssignmentItem.id.desc(),
    ).limit(4).all()
    for item in assignment_updates:
        title = "Opdracht voltooid" if item.status == "completed" else "Opdracht niet uitvoerbaar"
        activity.append(
            {
                "id": f"assignment-{item.id}",
                "kind": "assignment",
                "title": title,
                "description": f"{item.article_name} van {item.from_store_name} naar {item.to_store_name}",
                "created_at": _iso(item.updated_at),
                "href": f"/assignments/{item.series_id}",
                "_sort_value": item.updated_at,
            }
        )

    parse_issues = db.query(db_models.PDFParseLog).filter(
        db_models.PDFParseLog.level.in_(("WARNING", "ERROR"))
    ).order_by(
        db_models.PDFParseLog.created_at.desc(),
        db_models.PDFParseLog.id.desc(),
    ).limit(2).all()
    for log in parse_issues:
        activity.append(
            {
                "id": f"log-{log.id}",
                "kind": "parse_log",
                "title": f"Parse {log.level.lower()}",
                "description": log.message,
                "created_at": _iso(log.created_at),
                "href": f"/proposals/batch/{log.batch_id}",
                "_sort_value": log.created_at,
            }
        )

    activity.sort(key=lambda item: item["_sort_value"], reverse=True)

    return [
        {key: value for key, value in item.items() if key != "_sort_value"}
        for item in activity[:6]
    ]


def _build_attention_items(
    *,
    pending_proposals: int,
    pending_batches: list[dict],
    failed_assignment_items: int,
    recent_parse_issue: db_models.PDFParseLog | None,
    total_batches: int,
) -> list[dict]:
    items = []

    if pending_proposals > 0:
        items.append(
            {
                "id": "pending-proposals",
                "severity": "warning",
                "title": "Voorstellen wachten op beoordeling",
                "description": f"{pending_proposals} voorstel(len) open in {len(pending_batches)} reeks(en).",
                "href": "/proposals",
            }
        )

    if failed_assignment_items > 0:
        items.append(
            {
                "id": "failed-assignments",
                "severity": "warning",
                "title": "Opdrachten vragen opvolging",
                "description": f"{failed_assignment_items} assignment-item(s) staan op niet uitvoerbaar.",
                "href": "/assignments",
            }
        )

    if recent_parse_issue is not None:
        items.append(
            {
                "id": f"parse-{recent_parse_issue.id}",
                "severity": "info" if recent_parse_issue.level == "WARNING" else "warning",
                "title": "Recente parsemeldingen aanwezig",
                "description": recent_parse_issue.message,
                "href": f"/proposals/batch/{recent_parse_issue.batch_id}",
            }
        )

    if not items and total_batches > 0:
        items.append(
            {
                "id": "no-open-alerts",
                "severity": "info",
                "title": "Geen open aandachtspunten",
                "description": "Er zijn momenteel geen batches, proposals of assignments die directe opvolging vereisen.",
                "href": None,
            }
        )

    return items


@router.get("/summary")
async def get_dashboard_summary(
    current_user: db_models.User = Depends(require_permission("view_dashboard")),
    db: Session = Depends(get_db),
):
    _ = current_user
    proposal_status_counts = {
        "pending": 0,
        "approved": 0,
        "rejected": 0,
        "edited": 0,
    }
    for status, count in db.query(
        db_models.Proposal.status,
        func.count(db_models.Proposal.id),
    ).group_by(
        db_models.Proposal.status
    ).all():
        if status in proposal_status_counts:
            proposal_status_counts[status] = count

    assignment_status_counts = {
        "open": 0,
        "completed": 0,
        "failed": 0,
    }
    for status, count in db.query(
        db_models.AssignmentItem.status,
        func.count(db_models.AssignmentItem.id),
    ).group_by(
        db_models.AssignmentItem.status
    ).all():
        if status in assignment_status_counts:
            assignment_status_counts[status] = count

    total_batches = db.query(func.count(db_models.PDFBatch.id)).scalar() or 0
    active_store_count = db.query(
        func.count(func.distinct(db_models.ArtikelVoorraad.filiaal_code))
    ).scalar() or 0
    assignment_series_count = db.query(func.count(db_models.AssignmentSeries.id)).scalar() or 0

    pending_batches = _build_pending_batches(db)
    recent_activity = _build_recent_activity(db)
    recent_parse_issue = db.query(db_models.PDFParseLog).filter(
        db_models.PDFParseLog.level.in_(("WARNING", "ERROR"))
    ).order_by(
        db_models.PDFParseLog.created_at.desc(),
        db_models.PDFParseLog.id.desc(),
    ).first()

    return {
        "generated_at": _iso(datetime.utcnow()),
        "period_note": "Live totaaloverzicht. Periodevergelijkingen zijn bewust uitgeschakeld totdat de backend daar echte semantiek voor heeft.",
        "stats": {
            "total_proposals": sum(proposal_status_counts.values()),
            "pending_proposals": proposal_status_counts["pending"],
            "approved_proposals": proposal_status_counts["approved"],
            "rejected_proposals": proposal_status_counts["rejected"],
            "edited_proposals": proposal_status_counts["edited"],
            "open_assignment_items": assignment_status_counts["open"],
            "completed_assignment_items": assignment_status_counts["completed"],
            "failed_assignment_items": assignment_status_counts["failed"],
            "active_store_count": active_store_count,
            "total_batches": total_batches,
            "assignment_series_count": assignment_series_count,
        },
        "pending_batches": pending_batches,
        "recent_activity": recent_activity,
        "attention_items": _build_attention_items(
            pending_proposals=proposal_status_counts["pending"],
            pending_batches=pending_batches,
            failed_assignment_items=assignment_status_counts["failed"],
            recent_parse_issue=recent_parse_issue,
            total_batches=total_batches,
        ),
    }

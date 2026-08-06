"""Compenserende controle voor de audit trail (hoofdstuk 6/8): `reviewed_by`.

Verifieert dat het goedkeuren/afkeuren van een voorstel vastlegt *wie* de
review deed. De handlers worden direct (async) aangeroepen met een echte
wegwerp-DB-sessie (conftest) en een nagebootste ingelogde gebruiker; de
assignment-sync wordt gemockt zodat de test de audit-logica isoleert.
"""
import asyncio
from types import SimpleNamespace

import db_models
import routers.pdf_ingest as pi
from database import Base, SessionLocal, engine

# Zorg dat het schema (incl. de nieuwe reviewed_by-kolom) bestaat.
Base.metadata.create_all(bind=engine)


def _seed_pending(db) -> int:
    prop = db_models.Proposal(
        artikelnummer="TESTART",
        article_name="Testartikel",
        moves=[],
        status="pending",
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop.id


def test_approve_records_reviewer(monkeypatch):
    monkeypatch.setattr(pi, "sync_assignments_for_proposal", lambda db, proposal: None)
    db = SessionLocal()
    try:
        pid = _seed_pending(db)
        result = asyncio.run(pi.approve_proposal(
            pid, db=db, current_user=SimpleNamespace(id=101, username="alice")
        ))
        assert result["status"] == "approved"
        assert result["reviewed_by"] == "alice"

        prop = db.get(db_models.Proposal, pid)
        assert prop.reviewed_by == "alice"
        assert prop.reviewed_at is not None
    finally:
        db.close()


def test_reject_records_reviewer(monkeypatch):
    monkeypatch.setattr(pi, "sync_assignments_for_proposal", lambda db, proposal: None)
    db = SessionLocal()
    try:
        pid = _seed_pending(db)
        result = asyncio.run(pi.reject_proposal(
            pid, payload=None, db=db, current_user=SimpleNamespace(id=202, username="bob")
        ))
        assert result["status"] == "rejected"
        assert result["reviewed_by"] == "bob"

        prop = db.get(db_models.Proposal, pid)
        assert prop.reviewed_by == "bob"

        # De bijbehorende Feedback-mutatie legt óók de uitvoerende gebruiker vast.
        fb = db.query(db_models.Feedback).filter(
            db_models.Feedback.proposal_id == pid
        ).first()
        assert fb is not None and fb.user_id == 202
    finally:
        db.close()

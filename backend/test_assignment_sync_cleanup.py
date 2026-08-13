"""Regressietests: store-facing assignments mogen niet verweesd achterblijven.

Dekt de bug waarbij `sync_assignments_for_proposal` nooit verwijderde, waardoor
(a) een goedgekeurd-daarna-afgekeurd voorstel en (b) een edit die een route
weghaalt, uitvoerbare winkelopdrachten lieten staan die niet meer klopten. Plus
de nuances uit de code-review: reeds uitgevoerde opdrachten blijven behouden, en
een leesverzoek (brede sync) verwijdert nooit.
"""
import asyncio
from datetime import datetime
from types import SimpleNamespace

import db_models
import routers.pdf_ingest as pi
from assignment_service import (
    remove_assignments_for_proposal,
    sync_assignments_for_proposal,
)
from database import Base, SessionLocal, engine
from routers.pdf_ingest import MoveInput, UpdateProposalRequest

Base.metadata.create_all(bind=engine)

_MOVE_A = {"from_store": "1", "to_store": "2", "size": "M", "qty": 3,
           "from_store_name": "Winkel1", "to_store_name": "Winkel2"}
_MOVE_B = {"from_store": "1", "to_store": "3", "size": "M", "qty": 2,
           "from_store_name": "Winkel1", "to_store_name": "Winkel3"}


def _seed_approved(db, moves):
    batch = db_models.PDFBatch(naam="Testbatch")
    db.add(batch)
    db.commit()
    db.refresh(batch)
    prop = db_models.Proposal(
        artikelnummer="ART1", article_name="Artikel 1",
        moves=moves, status="approved", pdf_batch_id=batch.id,
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


def _items(db, proposal_id):
    return db.query(db_models.AssignmentItem).filter(
        db_models.AssignmentItem.proposal_id == proposal_id,
    ).all()


def test_remove_deletes_open_items_and_empty_series():
    db = SessionLocal()
    try:
        prop = _seed_approved(db, [_MOVE_A, _MOVE_B])
        sync_assignments_for_proposal(db, prop, cleanup_stale=True)
        db.commit()
        assert len(_items(db, prop.id)) == 2
        series_id = _items(db, prop.id)[0].series_id

        remove_assignments_for_proposal(db, prop)
        db.commit()

        assert _items(db, prop.id) == []
        assert db.query(db_models.AssignmentSeries).filter(
            db_models.AssignmentSeries.id == series_id,
        ).first() is None
    finally:
        db.close()


def test_completed_assignment_is_preserved():
    """Een al uitgevoerde (completed) opdracht is een auditrecord en mag niet
    door reject/cleanup verdwijnen."""
    db = SessionLocal()
    try:
        prop = _seed_approved(db, [_MOVE_A])
        sync_assignments_for_proposal(db, prop, cleanup_stale=True)
        db.commit()
        item = _items(db, prop.id)[0]
        item.status = "completed"
        item.completed_at = datetime.now()
        db.commit()

        remove_assignments_for_proposal(db, prop)
        db.commit()

        remaining = _items(db, prop.id)
        assert len(remaining) == 1 and remaining[0].status == "completed"
    finally:
        db.close()


def test_sync_cleanup_stale_true_drops_removed_route():
    db = SessionLocal()
    try:
        prop = _seed_approved(db, [_MOVE_A, _MOVE_B])
        sync_assignments_for_proposal(db, prop, cleanup_stale=True)
        db.commit()
        assert len(_items(db, prop.id)) == 2

        prop.moves = [_MOVE_A]
        db.commit()
        sync_assignments_for_proposal(db, prop, cleanup_stale=True)
        db.commit()

        routes = {(i.from_store_code, i.to_store_code) for i in _items(db, prop.id)}
        assert routes == {("1", "2")}
    finally:
        db.close()


def test_readpath_sync_default_does_not_delete():
    """Zonder cleanup_stale (de brede read-path-sync) mag er niets verwijderd
    worden — een GET heeft geen destructieve neveneffecten."""
    db = SessionLocal()
    try:
        prop = _seed_approved(db, [_MOVE_A, _MOVE_B])
        sync_assignments_for_proposal(db, prop, cleanup_stale=True)
        db.commit()
        assert len(_items(db, prop.id)) == 2

        prop.moves = [_MOVE_A]
        db.commit()
        sync_assignments_for_proposal(db, prop)  # default cleanup_stale=False
        db.commit()

        # Beide items blijven staan: het leespad verwijdert niet.
        assert len(_items(db, prop.id)) == 2
    finally:
        db.close()


def test_edit_endpoint_removes_open_assignments():
    """Het echte edit-endpoint (update_proposal) ruimt de nog-openstaande
    assignments op — het voorstel is na een edit niet meer 'approved'."""
    db = SessionLocal()
    try:
        prop = _seed_approved(db, [_MOVE_A, _MOVE_B])
        sync_assignments_for_proposal(db, prop, cleanup_stale=True)
        db.commit()
        assert len(_items(db, prop.id)) == 2

        payload = UpdateProposalRequest(moves=[MoveInput(**_MOVE_A)])
        asyncio.run(pi.update_proposal(
            prop.id, payload=payload, db=db,
            current_user=SimpleNamespace(id=1, username="x"),
        ))

        assert _items(db, prop.id) == []
        assert db.get(db_models.Proposal, prop.id).status == "edited"
    finally:
        db.close()


def test_reject_handler_removes_assignments():
    db = SessionLocal()
    try:
        prop = _seed_approved(db, [_MOVE_A])
        sync_assignments_for_proposal(db, prop, cleanup_stale=True)
        db.commit()
        assert len(_items(db, prop.id)) == 1

        asyncio.run(pi.reject_proposal(
            prop.id, payload=None, db=db,
            current_user=SimpleNamespace(id=1, username="x"),
        ))

        assert _items(db, prop.id) == []
        assert db.get(db_models.Proposal, prop.id).status == "rejected"
    finally:
        db.close()

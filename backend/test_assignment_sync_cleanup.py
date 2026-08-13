"""Regressietests: store-facing assignments mogen niet verweesd achterblijven.

Dekt de bug waarbij `sync_assignments_for_proposal` nooit verwijderde, waardoor
(a) een goedgekeurd-daarna-afgekeurd voorstel en (b) een edit die een route
weghaalt, uitvoerbare winkelopdrachten lieten staan die niet meer klopten.
"""
import asyncio
from types import SimpleNamespace

import db_models
import routers.pdf_ingest as pi
from assignment_service import (
    remove_assignments_for_proposal,
    sync_assignments_for_proposal,
)
from database import Base, SessionLocal, engine

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
        artikelnummer="ART1",
        article_name="Artikel 1",
        moves=moves,
        status="approved",
        pdf_batch_id=batch.id,
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


def _items(db, proposal_id):
    return db.query(db_models.AssignmentItem).filter(
        db_models.AssignmentItem.proposal_id == proposal_id,
    ).all()


def test_remove_deletes_all_items_and_empty_series():
    db = SessionLocal()
    try:
        prop = _seed_approved(db, [_MOVE_A, _MOVE_B])
        sync_assignments_for_proposal(db, prop)
        db.commit()
        assert len(_items(db, prop.id)) == 2
        series_id = _items(db, prop.id)[0].series_id

        remove_assignments_for_proposal(db, prop)
        db.commit()

        assert _items(db, prop.id) == []
        # De nu lege serie is opgeruimd.
        assert db.query(db_models.AssignmentSeries).filter(
            db_models.AssignmentSeries.id == series_id,
        ).first() is None
    finally:
        db.close()


def test_sync_removes_stale_route_after_edit():
    db = SessionLocal()
    try:
        prop = _seed_approved(db, [_MOVE_A, _MOVE_B])
        sync_assignments_for_proposal(db, prop)
        db.commit()
        assert len(_items(db, prop.id)) == 2

        # "Edit": route 1->3 verwijderd; opnieuw synchroniseren.
        prop.moves = [_MOVE_A]
        db.commit()
        sync_assignments_for_proposal(db, prop)
        db.commit()

        routes = {(i.from_store_code, i.to_store_code) for i in _items(db, prop.id)}
        assert routes == {("1", "2")}  # alleen de behouden route blijft
    finally:
        db.close()


def test_reject_handler_removes_assignments():
    db = SessionLocal()
    try:
        prop = _seed_approved(db, [_MOVE_A])
        sync_assignments_for_proposal(db, prop)
        db.commit()
        assert len(_items(db, prop.id)) == 1

        asyncio.run(pi.reject_proposal(
            prop.id, payload=None, db=db, current_user=SimpleNamespace(id=1, username="x"),
        ))

        assert _items(db, prop.id) == []
        assert db.get(db_models.Proposal, prop.id).status == "rejected"
    finally:
        db.close()

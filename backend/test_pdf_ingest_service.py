"""Tests voor de geëxtraheerde PDF-ingest-domeinlaag (Fase 3.1, PR-022).

Dit is het regressievangnet dat de ingest-orkestratie (`run_batch_ingest`) en de
domein-helpers borgt, die vóór de opsplitsing van `routers/pdf_ingest.py` géén
geautomatiseerde dekking hadden. De tests draaien tegen de wegwerpdatabase uit
`conftest.py` en mocken de PDF-parser + het herverdelingsalgoritme, zodat ze
deterministisch de orkestratie zelf testen.
"""
from __future__ import annotations

import io
from types import SimpleNamespace

import db_models  # noqa: F401 -- registreert de modellen op Base
from database import Base, SessionLocal, engine
from pdf_extract import ParsedDoc
import pdf_ingest_service as svc
from pdf_ingest_service import apply_moves_to_inventory, build_proposal_rows

# Zorg dat het schema bestaat in de (wegwerp) testdatabase uit conftest.py.
Base.metadata.create_all(bind=engine)


class _FakeUpload:
    """Minimale nabootsing van Starlette's UploadFile (alleen .file + .filename)."""

    def __init__(self, data: bytes, filename: str) -> None:
        self.file = io.BytesIO(data)
        self.filename = filename


def _ok_parsed() -> ParsedDoc:
    return ParsedDoc(
        meta={"Volgnummer": "12345", "Omschrijving": "Testartikel"},
        rows=[{
            "filiaal_code": "5",
            "filiaal_naam": "Panningen",
            "voorraad_per_maat": {"S": 3, "M": 2},
            "verkocht": 6,
        }],
    )


def _err_parsed() -> ParsedDoc:
    return ParsedDoc(errors=["Validatiefout in PDF"])


# --- Pure domein-helpers ------------------------------------------------------

def test_apply_moves_to_inventory_conserves_and_skips_incomplete():
    stores_inventory = {
        "1": {"sizes": {"M": 5}},
        "2": {"sizes": {"M": 0}},
    }
    moves = [
        {"from_store": "1", "to_store": "2", "size": "M", "qty": 3},
        {"to_store": "2", "size": "M", "qty": 1},  # from_store ontbreekt -> skip
    ]
    proposed = apply_moves_to_inventory(stores_inventory, moves)
    assert proposed["1"]["M"] == 2
    assert proposed["2"]["M"] == 3
    # Voorraadbehoud: de onvolledige move is genegeerd, de som blijft 5.
    assert proposed["1"]["M"] + proposed["2"]["M"] == 5


def test_build_proposal_rows_off_mode_serializes_moves():
    move = SimpleNamespace(
        size="M", from_store="1", from_store_name="A", to_store="2",
        to_store_name="B", qty=3, score=0.876, reason="r", from_bv="X", to_bv="Y",
    )
    proposal = SimpleNamespace(
        volgnummer="123", article_name="Art", moves=[move], total_moves=1,
        total_quantity=3, reason="reden", applied_rules=["R1"],
        optimization_applied=True, stores_affected={"1", "2"},
    )
    rows = build_proposal_rows([proposal], "off", use_model_scoring=False)
    assert len(rows) == 1
    row = rows[0]
    assert row["artikelnummer"] == "123"
    assert row["optimization_applied"] == "true"  # bool -> lowercased string
    assert row["moves"][0]["score"] == 0.88       # afgerond op 2 decimalen
    assert row["moves"][0]["model_score"] is None
    assert set(row["stores_affected"]) == {"1", "2"}


# --- Ingest-orkestratie (run_batch_ingest) ------------------------------------

def test_run_batch_ingest_success(monkeypatch, tmp_path):
    monkeypatch.setattr(svc, "parse_pdf_to_records", lambda path: _ok_parsed())
    monkeypatch.setattr(svc, "generate_and_save_proposals", lambda db, batch_id: 2)

    db = SessionLocal()
    try:
        files = [_FakeUpload(b"%PDF-1.4 test", "artikel.pdf")]
        payload = svc.run_batch_ingest(
            db, files, ["artikel.pdf"], "Testbatch", None, str(tmp_path)
        )
        assert payload["status"] == "SUCCESS"
        assert payload["success_count"] == 1
        assert payload["failed_count"] == 0
        assert payload["proposals_generated"] == 2
        assert payload["results"][0]["artikel_count"] == 2  # S=3, M=2 -> 2 records

        batch = db.query(db_models.PDFBatch).filter(
            db_models.PDFBatch.id == payload["batch_id"]
        ).first()
        assert batch is not None and batch.status == "SUCCESS"
        records = db.query(db_models.ArtikelVoorraad).filter(
            db_models.ArtikelVoorraad.batch_id == payload["batch_id"]
        ).all()
        assert len(records) == 2
    finally:
        db.close()


def test_run_batch_ingest_partial_success(monkeypatch, tmp_path):
    parsed_seq = [_ok_parsed(), _err_parsed()]
    monkeypatch.setattr(svc, "parse_pdf_to_records", lambda path: parsed_seq.pop(0))
    monkeypatch.setattr(svc, "generate_and_save_proposals", lambda db, batch_id: 1)

    db = SessionLocal()
    try:
        files = [_FakeUpload(b"a", "a.pdf"), _FakeUpload(b"b", "b.pdf")]
        payload = svc.run_batch_ingest(
            db, files, ["a.pdf", "b.pdf"], "Batch", None, str(tmp_path)
        )
        assert payload["status"] == "PARTIAL_SUCCESS"
        assert payload["success_count"] == 1
        assert payload["failed_count"] == 1
    finally:
        db.close()


def test_run_batch_ingest_all_failed_skips_proposals(monkeypatch, tmp_path):
    monkeypatch.setattr(svc, "parse_pdf_to_records", lambda path: _err_parsed())
    gen_called = {"value": False}

    def _fake_gen(db, batch_id):
        gen_called["value"] = True
        return 5

    monkeypatch.setattr(svc, "generate_and_save_proposals", _fake_gen)

    db = SessionLocal()
    try:
        files = [_FakeUpload(b"x", "x.pdf")]
        payload = svc.run_batch_ingest(
            db, files, ["x.pdf"], "Batch", None, str(tmp_path)
        )
        assert payload["status"] == "FAILED"
        assert payload["failed_count"] == 1
        assert payload["proposals_generated"] == 0
        # Bij 0 successen mag proposal-generatie niet aangeroepen worden.
        assert gen_called["value"] is False
    finally:
        db.close()

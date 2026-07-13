"""Security-regressietests voor Fase 1 (production-readiness plan).

Deze tests borgen dat de hardening uit Fase 1 niet stilzwijgend terugdraait.
Ze draaien tegen een wegwerpdatabase (zie backend/conftest.py) en hebben geen
geseede data nodig: de auth-dependency weigert een ongeauthenticeerde aanroep
vóórdat de handler de database raakt.

Gekoppelde bevindingen: PR-001 (auth op muterende endpoints).
"""
from __future__ import annotations

import asyncio
import io
import os
import subprocess
import sys
import tempfile
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from main import app
import db_models
from database import SessionLocal
from routers.pdf_ingest import approve_proposal
from utils import (
    secure_pdf_filename,
    save_upload_within_limit,
    UnsafeFilenameError,
    UploadTooLargeError,
)

client = TestClient(app)

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))


class _FakeUpload:
    """Minimale nabootsing van Starlette's UploadFile (alleen .file nodig)."""

    def __init__(self, data: bytes) -> None:
        self.file = io.BytesIO(data)

# Elk muterend endpoint met de HTTP-methode. Zonder Authorization-header MOET
# elk van deze een 401 teruggeven (OAuth2PasswordBearer weigert de ontbrekende
# token), nooit een 2xx.
MUTATING_ENDPOINTS = [
    ("post", "/api/pdf/ingest"),
    ("delete", "/api/pdf/batches/1"),
    ("post", "/api/pdf/proposals/1/approve"),
    ("post", "/api/pdf/proposals/1/reject"),
    ("put", "/api/pdf/proposals/1"),
    ("post", "/api/batches/create"),
    ("post", "/api/batches/1/upload"),
    ("post", "/api/redistribution/generate/1"),
    ("post", "/api/articles"),
    ("put", "/api/articles/TEST123"),
    ("delete", "/api/articles/TEST123"),
]


@pytest.mark.parametrize("method,path", MUTATING_ENDPOINTS)
def test_mutating_endpoint_rejects_unauthenticated_request(method: str, path: str):
    response = client.request(method, path)
    assert response.status_code == 401, (
        f"{method.upper()} {path} gaf {response.status_code} in plaats van 401 "
        f"zonder authenticatie — muterend endpoint is niet beschermd!"
    )


def test_missing_secret_key_fails_fast():
    """Zonder SECRET_KEY MOET het importeren van auth fail-fast falen (PR-002).

    Draait in een lege tijdelijke werkmap met PYTHONPATH naar backend, zodat een
    eventueel lokaal backend/.env de test niet beïnvloedt (load_dotenv vindt daar
    geen .env) en SECRET_KEY gegarandeerd ontbreekt.
    """
    env = {k: v for k, v in os.environ.items() if k != "SECRET_KEY"}
    env["PYTHONPATH"] = BACKEND_DIR
    with tempfile.TemporaryDirectory() as empty_cwd:
        result = subprocess.run(
            [sys.executable, "-c", "import auth"],
            cwd=empty_cwd,
            env=env,
            capture_output=True,
            text=True,
        )
    assert result.returncode != 0, (
        "auth-import zonder SECRET_KEY had fail-fast moeten falen, maar slaagde"
    )
    assert "SECRET_KEY" in result.stderr, (
        f"Verwachtte een SECRET_KEY-foutmelding, kreeg: {result.stderr!r}"
    )


# --- Upload-veiligheid: filename-sanitisering + groottelimiet (PR-004/PR-005) -

@pytest.mark.parametrize(
    "bad_name",
    [
        None,
        "",
        "../../etc/passwd.pdf",
        "..\\..\\windows\\evil.pdf",
        "sub/dir/report.pdf",
        "report.txt",
        "report.exe",
        "..",
        "with\x00null.pdf",
    ],
)
def test_secure_pdf_filename_rejects_unsafe_names(bad_name):
    with pytest.raises(UnsafeFilenameError):
        secure_pdf_filename(bad_name)


@pytest.mark.parametrize(
    "good_name,expected",
    [
        ("voorraad.pdf", "voorraad.pdf"),
        ("Rapport 2026-07.PDF", "Rapport 2026-07.PDF"),
        ("artikel_56490.pdf", "artikel_56490.pdf"),
    ],
)
def test_secure_pdf_filename_accepts_normal_names(good_name, expected):
    assert secure_pdf_filename(good_name) == expected


def test_save_upload_within_limit_writes_small_file(tmp_path):
    dest = tmp_path / "ok.pdf"
    written = save_upload_within_limit(_FakeUpload(b"%PDF-1.4 klein"), str(dest), max_bytes=1024)
    assert written == len(b"%PDF-1.4 klein")
    assert dest.read_bytes() == b"%PDF-1.4 klein"


def test_save_upload_within_limit_rejects_and_cleans_up_oversized(tmp_path):
    dest = tmp_path / "too_big.pdf"
    payload = b"x" * 5000
    with pytest.raises(UploadTooLargeError):
        save_upload_within_limit(_FakeUpload(payload), str(dest), max_bytes=1024)
    # Het gedeeltelijke bestand mag niet blijven staan.
    assert not dest.exists()


# --- Idempotentie van approve (PR-006) ---------------------------------------

def test_approve_is_idempotent_when_already_approved():
    """Een reeds goedgekeurd voorstel opnieuw approven maakt geen dubbele
    Feedback-rijen aan en heeft geen neveneffecten."""
    db = SessionLocal()
    try:
        proposal = db_models.Proposal(
            artikelnummer="TESTART",
            article_name="Test artikel",
            moves=[{"from_store": "1", "to_store": "2", "size": "M", "qty": 3}],
            status="approved",
            reviewed_at=datetime.now(),
        )
        db.add(proposal)
        db.commit()
        db.refresh(proposal)
        proposal_id = proposal.id

        feedback_before = (
            db.query(db_models.Feedback)
            .filter(db_models.Feedback.proposal_id == proposal_id)
            .count()
        )

        result = asyncio.run(
            approve_proposal(proposal_id=proposal_id, db=db, current_user=None)
        )

        feedback_after = (
            db.query(db_models.Feedback)
            .filter(db_models.Feedback.proposal_id == proposal_id)
            .count()
        )

        assert "al goedgekeurd" in result["message"]
        assert feedback_after == feedback_before, "approve mag geen dubbele Feedback-rijen aanmaken"
    finally:
        db.close()


# --- Refresh-endpoint foutafhandeling (PR-008) -------------------------------

def test_refresh_with_invalid_token_returns_401():
    """Een ongeldig/malformed refresh token geeft 401 (JWTError-pad), niet 500."""
    response = client.post("/api/auth/refresh", json={"refresh_token": "not-a-valid-jwt"})
    assert response.status_code == 401


# --- Getypeerde moves-validatie (PR-015) -------------------------------------

def test_move_input_rejects_missing_core_field():
    """Een move zonder verplicht core-veld faalt validatie (endpoint -> 422),
    i.p.v. verderop een ongevangen KeyError."""
    from pydantic import ValidationError
    from routers.pdf_ingest import UpdateProposalRequest

    with pytest.raises(ValidationError):
        # from_store ontbreekt
        UpdateProposalRequest(moves=[{"size": "M", "to_store": "2", "qty": 3}])


def test_move_input_preserves_extra_fields():
    """De core-velden worden gevalideerd terwijl extra velden behouden blijven
    (round-trip met de frontend blijft intact)."""
    from routers.pdf_ingest import UpdateProposalRequest

    req = UpdateProposalRequest(moves=[{
        "size": "M", "from_store": "1", "to_store": "2", "qty": 3,
        "from_store_name": "Winkel A", "score": 0.9, "from_bv": "X",
    }])
    dumped = req.moves[0].model_dump()
    assert dumped["from_store"] == "1"
    assert dumped["qty"] == 3
    assert dumped["from_store_name"] == "Winkel A"  # extra veld bewaard
    assert dumped["score"] == 0.9


# --- Health check met DB-connectiviteit (PR-019) -----------------------------

def test_health_check_reports_database_connectivity():
    """/health voert een echte DB-query uit en rapporteert de databasestatus."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["database"] == "ok"


# --- CORS: ALLOWED_ORIGINS wordt daadwerkelijk toegepast (PR-009) -------------

def test_allowed_origins_env_var_is_honored():
    """Een via ALLOWED_ORIGINS geconfigureerde origin krijgt een CORS-antwoord.

    De app leest ALLOWED_ORIGINS bij import, dus dit draait in een subprocess met
    een custom waarde en een eigen wegwerpdatabase.
    """
    with tempfile.TemporaryDirectory() as cwd:
        db_path = os.path.join(cwd, "cors_test.db")
        env = {
            **os.environ,
            "ALLOWED_ORIGINS": "http://custom.example:3000",
            "SECRET_KEY": "test-secret-key-not-for-production-use",
            "DATABASE_URL": f"sqlite:///{db_path}",
            "PYTHONPATH": BACKEND_DIR,
        }
        code = (
            "from fastapi.testclient import TestClient\n"
            "from main import app\n"
            "c = TestClient(app)\n"
            "r = c.get('/health', headers={'Origin': 'http://custom.example:3000'})\n"
            "print('ACAO=' + str(r.headers.get('access-control-allow-origin')))\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], cwd=cwd, env=env, capture_output=True, text=True
        )
    assert result.returncode == 0, result.stderr
    assert "ACAO=http://custom.example:3000" in result.stdout, result.stdout

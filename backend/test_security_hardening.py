"""Security regression tests for production-readiness hardening."""
import importlib
import sys

import pytest
from fastapi.testclient import TestClient

from main import app
from routers.pdf_ingest import get_safe_pdf_filename


client = TestClient(app)


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("post", "/api/pdf/ingest", {"files": ("voorraad.pdf", b"%PDF-1.4", "application/pdf")}),
        ("delete", "/api/pdf/batches/1", None),
        ("post", "/api/pdf/proposals/1/approve", None),
        ("post", "/api/pdf/proposals/1/reject", {}),
        ("put", "/api/pdf/proposals/1", {"moves": []}),
        ("post", "/api/batches/create", {"name": "Security test"}),
        ("post", "/api/redistribution/generate/1", None),
        (
            "post",
            "/api/articles",
            {
                "artikelnummer": "SEC-1",
                "omschrijving": "Security test",
                "voorraad_per_winkel": {},
            },
        ),
        (
            "put",
            "/api/articles/SEC-1",
            {
                "artikelnummer": "SEC-1",
                "omschrijving": "Security test",
                "voorraad_per_winkel": {},
            },
        ),
        ("delete", "/api/articles/SEC-1", None),
    ],
)
def test_mutating_endpoints_require_authentication(method, path, payload):
    request = getattr(client, method)
    if isinstance(payload, dict) and "files" in payload:
        kwargs = {"files": payload}
    else:
        kwargs = {"json": payload} if payload is not None else {}

    response = request(path, **kwargs)

    assert response.status_code in {401, 403}


@pytest.mark.parametrize(
    "filename",
    [
        "../../database.db",
        "/tmp/voorraad.pdf",
        "..\\..\\evil.pdf",
        "nested/voorraad.pdf",
        "voorraad.txt",
        "..pdf",
        "",
        None,
    ],
)
def test_pdf_ingest_rejects_unsafe_filenames(filename):
    with pytest.raises(Exception):
        get_safe_pdf_filename(filename)


def test_pdf_ingest_accepts_plain_pdf_filename():
    assert get_safe_pdf_filename("voorraad-week-13.pdf") == "voorraad-week-13.pdf"


def test_auth_module_requires_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    sys.modules.pop("auth", None)

    with pytest.raises(RuntimeError, match="SECRET_KEY environment variable is required"):
        importlib.import_module("auth")

    monkeypatch.setenv("SECRET_KEY", "restored-test-secret")
    sys.modules.pop("auth", None)
    importlib.import_module("auth")

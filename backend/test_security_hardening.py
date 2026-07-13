"""Security-regressietests voor Fase 1 (production-readiness plan).

Deze tests borgen dat de hardening uit Fase 1 niet stilzwijgend terugdraait.
Ze draaien tegen een wegwerpdatabase (zie backend/conftest.py) en hebben geen
geseede data nodig: de auth-dependency weigert een ongeauthenticeerde aanroep
vóórdat de handler de database raakt.

Gekoppelde bevindingen: PR-001 (auth op muterende endpoints).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

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

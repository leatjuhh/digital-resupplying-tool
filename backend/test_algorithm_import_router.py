from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

import db_models
from auth import get_password_hash
from database import SessionLocal
from main import app
from test_algorithm_import_service import _create_test_dataset


client = TestClient(app)


def _login(username: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/auth/login?remember_me=false",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_user_without_proposals_permission() -> tuple[str, str]:
    db = SessionLocal()
    username = f"algo-no-view-{uuid4().hex[:8]}"
    role_name = f"algo-no-view-role-{uuid4().hex[:8]}"

    try:
        role = db_models.Role(
            name=role_name,
            display_name="Algorithm No View",
            description="Temporary test role without view_proposals permission",
            is_system_role=False,
        )
        db.add(role)
        db.commit()
        db.refresh(role)

        user = db_models.User(
            username=username,
            email=f"{username}@example.com",
            full_name="Algorithm No View Test",
            hashed_password=get_password_hash("StrongPass123!"),
            role_id=role.id,
            is_active=True,
        )
        db.add(user)
        db.commit()

        return username, role_name
    finally:
        db.close()


def _cleanup_temp_user_and_role(username: str, role_name: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(db_models.User).filter(db_models.User.username == username).first()
        if user:
            db.delete(user)
            db.commit()

        role = db.query(db_models.Role).filter(db_models.Role.name == role_name).first()
        if role:
            db.delete(role)
            db.commit()
    finally:
        db.close()


def _create_temp_proposal() -> int:
    db = SessionLocal()
    marker = uuid4().hex[:8]
    try:
        proposal = db_models.Proposal(
            artikelnummer="ART-123",
            article_name=f"External comparison {marker}",
            moves=[{"from_store": "1", "to_store": "2", "size": "36", "qty": 1}],
            total_moves=1,
            total_quantity=1,
            status="pending",
            reason="Test proposal",
            applied_rules=[],
            optimization_applied="false",
            stores_affected=["1", "2"],
        )
        db.add(proposal)
        db.commit()
        db.refresh(proposal)
        return proposal.id
    finally:
        db.close()


def _cleanup_temp_proposal(proposal_id: int) -> None:
    db = SessionLocal()
    try:
        proposal = db.query(db_models.Proposal).filter(db_models.Proposal.id == proposal_id).first()
        if proposal:
            db.delete(proposal)
            db.commit()
    finally:
        db.close()


def test_algorithm_import_status_requires_authentication():
    response = client.get("/api/algorithm-import/status")
    assert response.status_code == 401


def test_algorithm_import_status_returns_dataset_payload_for_admin(tmp_path: Path, monkeypatch):
    data_root = tmp_path / "external-data"
    _create_test_dataset(data_root)
    monkeypatch.setenv("EXTERNAL_ALGORITHM_DATA_ROOT", str(data_root))

    headers = _login("admin", "Admin123!")
    response = client.get("/api/algorithm-import/status", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_available"] is True
    assert payload["latest_week"] == 13
    assert payload["aggregate_model_summary"]["top_k_recall_test"] == 0.84


def test_algorithm_import_status_enforces_view_proposals_permission():
    username, role_name = _create_user_without_proposals_permission()

    try:
        headers = _login(username, "StrongPass123!")
        response = client.get("/api/algorithm-import/status", headers=headers)
        assert response.status_code == 403
    finally:
        _cleanup_temp_user_and_role(username, role_name)


def test_algorithm_import_proposal_comparison_returns_payload_for_existing_proposal(tmp_path: Path, monkeypatch):
    data_root = tmp_path / "external-data"
    _create_test_dataset(data_root)
    monkeypatch.setenv("EXTERNAL_ALGORITHM_DATA_ROOT", str(data_root))

    proposal_id = _create_temp_proposal()
    try:
        headers = _login("admin", "Admin123!")
        response = client.get(f"/api/algorithm-import/proposals/{proposal_id}/comparison", headers=headers)

        assert response.status_code == 200
        payload = response.json()
        assert payload["available"] is True
        assert payload["latest_matching_week"]["week"] == 13
        assert payload["comparison"]["drt_vs_manual"]["overlap_count"] == 1
    finally:
        _cleanup_temp_proposal(proposal_id)

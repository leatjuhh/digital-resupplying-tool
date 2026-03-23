from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

import db_models
from auth import get_password_hash
from database import SessionLocal
from main import app


client = TestClient(app)


def login(username: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/auth/login?remember_me=false",
        data={
            "username": username,
            "password": password,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_user_without_dashboard_permission() -> tuple[str, str]:
    db = SessionLocal()
    username = f"dashboard-no-view-{uuid4().hex[:8]}"
    role_name = f"dashboard-no-view-role-{uuid4().hex[:8]}"

    try:
        role = db_models.Role(
            name=role_name,
            display_name="Dashboard No View",
            description="Temporary test role without dashboard permission",
            is_system_role=False,
        )
        db.add(role)
        db.commit()
        db.refresh(role)

        user = db_models.User(
            username=username,
            email=f"{username}@example.com",
            full_name="Dashboard No View Test",
            hashed_password=get_password_hash("StrongPass123!"),
            role_id=role.id,
            is_active=True,
        )
        db.add(user)
        db.commit()

        return username, role_name
    finally:
        db.close()


def cleanup_temp_user_and_role(username: str, role_name: str) -> None:
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


def test_dashboard_summary_requires_authentication():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 401


def test_dashboard_summary_returns_real_aggregates_for_admin():
    headers = login("admin", "Admin123!")
    response = client.get("/api/dashboard/summary", headers=headers)

    assert response.status_code == 200

    payload = response.json()
    assert "stats" in payload
    assert "pending_batches" in payload
    assert "recent_activity" in payload
    assert "attention_items" in payload
    assert payload["stats"]["total_proposals"] >= 0
    assert payload["stats"]["total_batches"] >= 0
    assert payload["stats"]["active_store_count"] >= 0


def test_dashboard_summary_enforces_view_dashboard_permission():
    username, role_name = create_user_without_dashboard_permission()

    try:
        headers = login(username, "StrongPass123!")
        response = client.get("/api/dashboard/summary", headers=headers)
        assert response.status_code == 403
    finally:
        cleanup_temp_user_and_role(username, role_name)

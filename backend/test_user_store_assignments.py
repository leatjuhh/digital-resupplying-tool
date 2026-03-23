from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

import db_models
from database import SessionLocal
from main import app


client = TestClient(app)


def login_as_admin() -> dict[str, str]:
    response = client.post(
        "/api/auth/login?remember_me=false",
        data={
            "username": "admin",
            "password": "Admin123!",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def get_role_ids() -> tuple[int, int]:
    db = SessionLocal()
    try:
        store_role = db.query(db_models.Role).filter(db_models.Role.name == "store").first()
        user_role = db.query(db_models.Role).filter(db_models.Role.name == "user").first()
        assert store_role is not None
        assert user_role is not None
        return store_role.id, user_role.id
    finally:
        db.close()


def cleanup_user(username: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(db_models.User).filter(db_models.User.username == username).first()
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()


def test_create_store_user_requires_store_fields():
    headers = login_as_admin()
    store_role_id, _ = get_role_ids()
    username = f"store-test-{uuid4().hex[:8]}"

    try:
        response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": username,
                "email": f"{username}@example.com",
                "full_name": "Store Validation Test",
                "password": "StrongPass123!",
                "role_id": store_role_id,
                "is_active": True,
            },
        )

        assert response.status_code == 400
        assert "store_code" in response.json()["detail"]
    finally:
        cleanup_user(username)


def test_updating_user_to_non_store_clears_store_fields():
    headers = login_as_admin()
    store_role_id, user_role_id = get_role_ids()
    username = f"store-switch-{uuid4().hex[:8]}"

    try:
        create_response = client.post(
            "/api/users",
            headers=headers,
            json={
                "username": username,
                "email": f"{username}@example.com",
                "full_name": "Store Switch Test",
                "password": "StrongPass123!",
                "role_id": store_role_id,
                "is_active": True,
                "store_code": "99",
                "store_name": "Test Store",
            },
        )

        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        update_response = client.put(
            f"/api/users/{user_id}",
            headers=headers,
            json={
                "username": username,
                "email": f"{username}@example.com",
                "full_name": "Converted User",
                "role_id": user_role_id,
                "is_active": True,
                "store_code": None,
                "store_name": None,
            },
        )

        assert update_response.status_code == 200
        payload = update_response.json()
        assert payload["role_name"] == "user"
        assert payload["store_code"] is None
        assert payload["store_name"] is None

        db = SessionLocal()
        try:
            user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
            assert user is not None
            assert user.store_code is None
            assert user.store_name is None
        finally:
            db.close()
    finally:
        cleanup_user(username)

from __future__ import annotations

from app.tests.conftest import auth_header


def test_login_success_and_me(client, super_admin):
    headers = auth_header(client, "admin@example.com", "Admin123!")
    resp = client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "admin@example.com"
    assert resp.json()["role"] == "super_admin"


def test_login_wrong_password(client, super_admin):
    resp = client.post(
        "/api/v1/auth/login", json={"email": "admin@example.com", "password": "nope"}
    )
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post(
        "/api/v1/auth/login", json={"email": "ghost@example.com", "password": "whatever"}
    )
    assert resp.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_refresh_rotates_and_reuse_detected(client, super_admin):
    login = client.post(
        "/api/v1/auth/login", json={"email": "admin@example.com", "password": "Admin123!"}
    )
    old_cookie = login.cookies.get("refresh_token")
    assert old_cookie

    # First refresh succeeds and rotates the cookie.
    r1 = client.post("/api/v1/auth/refresh")
    assert r1.status_code == 200

    # Re-presenting the OLD token must fail (it was rotated/revoked).
    client.cookies.set("refresh_token", old_cookie)
    r2 = client.post("/api/v1/auth/refresh")
    assert r2.status_code == 401


def test_change_password(client, super_admin):
    headers = auth_header(client, "admin@example.com", "Admin123!")
    resp = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={"current_password": "Admin123!", "new_password": "NewPass123!"},
    )
    assert resp.status_code == 200
    assert client.post(
        "/api/v1/auth/login", json={"email": "admin@example.com", "password": "NewPass123!"}
    ).status_code == 200

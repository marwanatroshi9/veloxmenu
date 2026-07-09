"""Tests proving one restaurant can never read or mutate another's data."""
from __future__ import annotations

from app.tests.conftest import auth_header


def _create_category(client, headers, name="Cat"):
    return client.post(
        "/api/v1/restaurant/categories", headers=headers, json={"name": name}
    )


def test_manager_cannot_use_admin_endpoints(client, restaurant_a):
    headers = auth_header(client, "a@example.com", "Manager123!")
    assert client.get("/api/v1/admin/stats", headers=headers).status_code == 403
    assert client.get("/api/v1/admin/restaurants", headers=headers).status_code == 403


def test_category_is_scoped_to_own_restaurant(client, restaurant_a, restaurant_b):
    headers_a = auth_header(client, "a@example.com", "Manager123!")
    headers_b = auth_header(client, "b@example.com", "Manager123!")

    created = _create_category(client, headers_a, "A-only")
    assert created.status_code == 201
    cat_id = created.json()["id"]

    # B's list must not include A's category.
    list_b = client.get("/api/v1/restaurant/categories", headers=headers_b)
    assert all(c["id"] != cat_id for c in list_b.json())

    # B cannot update or delete A's category (404, not 403 — existence hidden).
    assert client.patch(
        f"/api/v1/restaurant/categories/{cat_id}", headers=headers_b, json={"name": "hax"}
    ).status_code == 404
    assert client.delete(
        f"/api/v1/restaurant/categories/{cat_id}", headers=headers_b
    ).status_code == 404


def test_menu_item_cannot_reference_foreign_category(client, restaurant_a, restaurant_b):
    headers_a = auth_header(client, "a@example.com", "Manager123!")
    headers_b = auth_header(client, "b@example.com", "Manager123!")

    cat_a = _create_category(client, headers_a, "A-cat").json()["id"]

    # B tries to attach an item to A's category id -> rejected.
    resp = client.post(
        "/api/v1/restaurant/menu-items",
        headers=headers_b,
        json={"name": "Steal", "price": "9.99", "category_id": cat_a},
    )
    assert resp.status_code == 400

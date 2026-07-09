from __future__ import annotations

from app.tests.conftest import auth_header


def _setup_category(client, headers):
    return client.post(
        "/api/v1/restaurant/categories", headers=headers, json={"name": "Mains"}
    ).json()["id"]


def test_menu_item_crud_and_duplicate(client, restaurant_a):
    headers = auth_header(client, "a@example.com", "Manager123!")
    cat_id = _setup_category(client, headers)

    create = client.post(
        "/api/v1/restaurant/menu-items",
        headers=headers,
        json={
            "name": "Burger",
            "price": "10.00",
            "discount_price": "8.50",
            "category_id": cat_id,
            "spicy_level": 2,
            "ingredients": ["Beef", "Bun"],
            "tags": ["Popular"],
        },
    )
    assert create.status_code == 201, create.text
    item = create.json()
    assert item["ingredients"] == ["Beef", "Bun"]
    assert item["spicy_level"] == 2

    item_id = item["id"]
    upd = client.patch(
        f"/api/v1/restaurant/menu-items/{item_id}",
        headers=headers,
        json={"name": "Cheeseburger", "is_featured": True},
    )
    assert upd.status_code == 200
    assert upd.json()["name"] == "Cheeseburger"
    assert upd.json()["is_featured"] is True

    dup = client.post(f"/api/v1/restaurant/menu-items/{item_id}/duplicate", headers=headers)
    assert dup.status_code == 201
    assert dup.json()["name"] == "Cheeseburger (Copy)"

    listing = client.get("/api/v1/restaurant/menu-items", headers=headers)
    assert listing.json()["meta"]["total"] == 2

    assert client.delete(
        f"/api/v1/restaurant/menu-items/{item_id}", headers=headers
    ).status_code == 200


def test_discount_must_be_lower_than_price(client, restaurant_a):
    headers = auth_header(client, "a@example.com", "Manager123!")
    cat_id = _setup_category(client, headers)
    resp = client.post(
        "/api/v1/restaurant/menu-items",
        headers=headers,
        json={"name": "X", "price": "5.00", "discount_price": "6.00", "category_id": cat_id},
    )
    assert resp.status_code == 422


def test_public_menu_hides_unavailable_and_invisible(client, db, restaurant_a):
    headers = auth_header(client, "a@example.com", "Manager123!")
    cat_id = _setup_category(client, headers)
    client.post(
        "/api/v1/restaurant/menu-items",
        headers=headers,
        json={"name": "Visible", "price": "5.00", "category_id": cat_id},
    )
    client.post(
        "/api/v1/restaurant/menu-items",
        headers=headers,
        json={"name": "Hidden", "price": "5.00", "category_id": cat_id, "is_available": False},
    )
    resp = client.get("/api/v1/public/restaurants/resto-a")
    assert resp.status_code == 200
    names = [i["name"] for c in resp.json()["categories"] for i in c["items"]]
    assert "Visible" in names
    assert "Hidden" not in names

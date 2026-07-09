"""Idempotent seed script.

Creates the bootstrap super admin, and — outside production — a demo restaurant
with a manager, categories and menu items so the app is immediately explorable.

Run with:  python -m seed
"""
from __future__ import annotations

import json

from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models.category import Category
from app.models.menu_item import MenuItem, SpicyLevel
from app.models.restaurant import Restaurant
from app.models.subscription import Subscription
from app.models.user import User, UserRole


def seed() -> None:
    db = SessionLocal()
    try:
        # --- Super admin ---
        admin = db.scalar(select(User).where(User.email == settings.FIRST_SUPERADMIN_EMAIL.lower()))
        if admin is None:
            admin = User(
                email=settings.FIRST_SUPERADMIN_EMAIL.lower(),
                hashed_password=hash_password(settings.FIRST_SUPERADMIN_PASSWORD),
                full_name="Platform Admin",
                role=UserRole.SUPER_ADMIN,
            )
            db.add(admin)
            db.commit()
            print(f"Created super admin: {admin.email}")
        else:
            print("Super admin already exists")

        if settings.ENVIRONMENT == "production":
            print("Production environment: skipping demo data")
            return

        # --- Demo restaurant ---
        restaurant = db.scalar(select(Restaurant).where(Restaurant.slug == "demo-bistro"))
        if restaurant is not None:
            print("Demo restaurant already exists")
            return

        restaurant = Restaurant(
            name="Demo Bistro",
            slug="demo-bistro",
            description="A cozy demo restaurant showcasing MenuHub.",
            theme_color="#E11D48",
            currency="USD",
            default_language="en",
            phone="+1 555 0100",
            whatsapp="+15550100",
            instagram="demobistro",
        )
        db.add(restaurant)
        db.flush()

        db.add(
            User(
                email="manager@demo.menuhub.app",
                hashed_password=hash_password("Manager123!"),
                full_name="Demo Manager",
                role=UserRole.RESTAURANT_MANAGER,
                restaurant_id=restaurant.id,
            )
        )
        db.add(Subscription(restaurant_id=restaurant.id))

        starters = Category(
            restaurant_id=restaurant.id, name="Starters", sort_order=0, is_visible=True
        )
        mains = Category(
            restaurant_id=restaurant.id, name="Main Courses", sort_order=1, is_visible=True
        )
        drinks = Category(
            restaurant_id=restaurant.id, name="Drinks", sort_order=2, is_visible=True
        )
        db.add_all([starters, mains, drinks])
        db.flush()

        db.add_all(
            [
                MenuItem(
                    restaurant_id=restaurant.id,
                    category_id=starters.id,
                    name="Bruschetta",
                    description="Grilled bread, tomato, basil, olive oil.",
                    price=6.50,
                    is_featured=True,
                    preparation_time=10,
                    calories=220,
                    spicy_level=SpicyLevel.NONE,
                    ingredients=json.dumps(["Bread", "Tomato", "Basil", "Olive oil"]),
                    tags=json.dumps(["Vegetarian"]),
                    sort_order=0,
                ),
                MenuItem(
                    restaurant_id=restaurant.id,
                    category_id=mains.id,
                    name="Spicy Arrabbiata",
                    description="Penne in a fiery tomato and chili sauce.",
                    price=13.00,
                    discount_price=11.00,
                    is_featured=True,
                    preparation_time=18,
                    calories=560,
                    spicy_level=SpicyLevel.HOT,
                    ingredients=json.dumps(["Penne", "Tomato", "Chili", "Garlic"]),
                    tags=json.dumps(["Spicy", "Vegetarian"]),
                    sort_order=0,
                ),
                MenuItem(
                    restaurant_id=restaurant.id,
                    category_id=drinks.id,
                    name="Fresh Lemonade",
                    description="Hand-squeezed lemons, mint, soda.",
                    price=4.00,
                    preparation_time=5,
                    calories=120,
                    spicy_level=SpicyLevel.NONE,
                    ingredients=json.dumps(["Lemon", "Mint", "Soda"]),
                    tags=json.dumps(["Cold"]),
                    sort_order=0,
                ),
            ]
        )
        db.commit()
        print("Seeded demo restaurant, manager (manager@demo.menuhub.app / Manager123!), and menu.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

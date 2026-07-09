from __future__ import annotations

import os

# Configure environment BEFORE importing the application settings.
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough-1234567890")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost/test")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("COOKIE_SECURE", "false")
# Effectively disable rate limits during tests.
os.environ.setdefault("RATE_LIMIT_AUTH", "100000/minute")
os.environ.setdefault("RATE_LIMIT_DEFAULT", "100000/minute")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.restaurant import Restaurant
from app.models.subscription import Subscription
from app.models.user import User, UserRole

# In-memory SQLite shared across connections for the test session.
engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture(autouse=True)
def _db_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def _get_db_override():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def super_admin(db):
    user = User(
        email="admin@example.com",
        hashed_password=hash_password("Admin123!"),
        full_name="Admin",
        role=UserRole.SUPER_ADMIN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_restaurant(db, slug: str, manager_email: str) -> tuple[Restaurant, User]:
    restaurant = Restaurant(name=slug.title(), slug=slug)
    db.add(restaurant)
    db.flush()
    manager = User(
        email=manager_email,
        hashed_password=hash_password("Manager123!"),
        role=UserRole.RESTAURANT_MANAGER,
        restaurant_id=restaurant.id,
    )
    db.add(manager)
    db.add(Subscription(restaurant_id=restaurant.id))
    db.commit()
    db.refresh(restaurant)
    db.refresh(manager)
    return restaurant, manager


@pytest.fixture
def restaurant_a(db):
    return _make_restaurant(db, "resto-a", "a@example.com")


@pytest.fixture
def restaurant_b(db):
    return _make_restaurant(db, "resto-b", "b@example.com")


def auth_header(client, email: str, password: str) -> dict[str, str]:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

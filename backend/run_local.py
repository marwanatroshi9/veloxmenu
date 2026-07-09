"""Launch the REAL MenuHub API against a local SQLite DB (no Docker/Postgres).

This patches only the DB engine/session at runtime; all routes, middleware,
auth, and validation are the genuine application objects. It also seeds a
photo-rich demo cafe so the public menu can be previewed end-to-end.
"""
import json
import os

os.environ.setdefault("SECRET_KEY", "local-run-secret-key-that-is-long-enough-123456")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://x:x@localhost/x")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("COOKIE_SECURE", "false")
os.environ.setdefault("PUBLIC_SITE_URL", "http://localhost:3000")
os.environ.setdefault("BACKEND_CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("FIRST_SUPERADMIN_EMAIL", "admin@menuhub.app")
os.environ.setdefault("FIRST_SUPERADMIN_PASSWORD", "ChangeMe123!")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.database.session as dbsession

DB_PATH = os.path.join(os.path.dirname(__file__), "menuhub_local.db")
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

sqlite_engine = create_engine(
    f"sqlite+pysqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
dbsession.engine = sqlite_engine
dbsession.SessionLocal = sessionmaker(
    bind=sqlite_engine, autoflush=False, autocommit=False, expire_on_commit=False
)

import app.models  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.database.base import Base  # noqa: E402
from app.models.category import Category  # noqa: E402
from app.models.menu_item import MenuItem, SpicyLevel  # noqa: E402
from app.models.restaurant import Restaurant  # noqa: E402
from app.models.subscription import Subscription  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402

Base.metadata.create_all(bind=sqlite_engine)


def _img(pid: str) -> str:
    return f"https://images.unsplash.com/photo-{pid}?w=600&q=80&auto=format&fit=crop"


def seed_demo() -> None:
    db = dbsession.SessionLocal()
    try:
        db.add(
            User(
                email="admin@menuhub.app",
                hashed_password=hash_password("ChangeMe123!"),
                full_name="Platform Admin",
                role=UserRole.SUPER_ADMIN,
            )
        )
        r = Restaurant(
            name="Malta Rest & Cafe",
            slug="demo-bistro",
            description="Specialty coffee & cafe.",
            theme_color="#F5333F",
            currency="IQD",
            default_language="en",
            phone="+964 750 000 0000",
        )
        db.add(r)
        db.flush()
        db.add(
            User(
                email="manager@demo.menuhub.app",
                hashed_password=hash_password("Manager123!"),
                full_name="Cafe Manager",
                role=UserRole.RESTAURANT_MANAGER,
                restaurant_id=r.id,
            )
        )
        db.add(Subscription(restaurant_id=r.id))

        cat_tr = {
            "Hot Coffee": {"ar": {"name": "قهوة ساخنة"}, "ckb": {"name": "قاوەی گەرم"}},
            "Hot Drinks": {"ar": {"name": "مشروبات ساخنة"}, "ckb": {"name": "خواردنەوەی گەرم"}},
            "Ice Latte": {"ar": {"name": "لاتيه مثلج"}, "ckb": {"name": "لاتێی سارد"}},
            "Cold Drinks": {"ar": {"name": "مشروبات باردة"}, "ckb": {"name": "خواردنەوەی سارد"}},
        }
        cats: dict[str, int] = {}
        for i, name in enumerate(["Hot Coffee", "Hot Drinks", "Ice Latte", "Cold Drinks"]):
            c = Category(
                restaurant_id=r.id,
                name=name,
                sort_order=i,
                is_visible=True,
                translations=json.dumps(cat_tr[name], ensure_ascii=False),
            )
            db.add(c)
            db.flush()
            cats[name] = c.id

        def item(cat, name, price, desc, img, featured=False, prep=None, spicy=0, tr=None):
            db.add(
                MenuItem(
                    restaurant_id=r.id,
                    category_id=cats[cat],
                    name=name,
                    description=desc,
                    price=price,
                    is_featured=featured,
                    preparation_time=prep,
                    spicy_level=SpicyLevel(spicy),
                    image_url=_img(img),
                    ingredients=json.dumps([]),
                    tags=json.dumps([]),
                    translations=json.dumps(tr or {}, ensure_ascii=False),
                    sort_order=0,
                )
            )

        item("Hot Coffee", "Espresso", 4500,
             "A concentrated Italian coffee with a strong flavor and a creamy foam.",
             "1510707577719-ae7c14805e3a", featured=True, prep=3,
             tr={
                 "ar": {"name": "إسبريسو",
                        "description": "قهوة إيطالية مركّزة بنكهة قوية ورغوة كريمية."},
                 "ckb": {"name": "ئێسپرێسۆ",
                         "description": "قاوەی ئیتالی چڕ بە تامێکی بەهێز و کەفێکی کرێمی."},
             })
        item("Hot Coffee", "Double espresso", 5500, "Two shots of espresso.",
             "1509042239860-f550ce710b93", prep=4,
             tr={"ar": {"name": "إسبريسو مزدوج", "description": "جرعتان من الإسبريسو."},
                 "ckb": {"name": "ئێسپرێسۆی دووجار", "description": "دوو شاتی ئێسپرێسۆ."}})
        item("Hot Coffee", "Turkish coffee", 5500, "Traditional Turkish-style coffee.",
             "1447933601403-0c6688de566e", prep=6)
        item("Hot Coffee", "Cappuccino", 6000,
             "Espresso with steamed milk and a thick layer of foam.",
             "1541167760496-1628856ab772", featured=True, prep=5)
        item("Hot Drinks", "Hot Chocolate", 6000, "Rich Belgian cocoa with steamed milk.",
             "1542990253-0d0f5be5f0ed", prep=5)
        item("Hot Drinks", "Green Tea", 4000, "Delicate loose-leaf green tea.",
             "1627435601361-ec25f5b1d0e5", prep=4)
        item("Ice Latte", "Iced Latte", 6500, "Chilled espresso with cold milk over ice.",
             "1517701550927-30cf4ba1dba5", featured=True, prep=4)
        item("Ice Latte", "Iced Caramel Macchiato", 7000,
             "Vanilla, milk, espresso and caramel.",
             "1461023058943-07fcbe16d735", prep=5)
        item("Cold Drinks", "Fresh Lemonade", 5000, "Hand-squeezed lemons, mint and soda.",
             "1621263764928-df1444c5e859", prep=3)
        item("Cold Drinks", "Mango Smoothie", 7500, "Blended mango with yoghurt and ice.",
             "1505252585461-04db1eb84625", prep=5)

        db.commit()
        print("Seeded 'Malta Rest & Cafe' demo (slug: demo-bistro).")
    finally:
        db.close()


seed_demo()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="warning")

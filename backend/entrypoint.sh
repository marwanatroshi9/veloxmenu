#!/usr/bin/env bash
set -euo pipefail

echo "Waiting for database..."
python - <<'PY'
import time
import sqlalchemy
from app.core.config import settings

url = str(settings.DATABASE_URL)
for attempt in range(30):
    try:
        engine = sqlalchemy.create_engine(url)
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        print("Database is ready.")
        break
    except Exception as exc:  # noqa: BLE001
        print(f"DB not ready ({attempt+1}/30): {exc}")
        time.sleep(2)
else:
    raise SystemExit("Database did not become ready in time")
PY

echo "Running migrations..."
alembic upgrade head

echo "Seeding..."
python -m seed || echo "Seed step skipped/failed (non-fatal)"

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"

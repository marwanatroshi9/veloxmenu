FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for building wheels (psycopg, pillow, bcrypt).
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
# Ensure the entrypoint is executable (the exec bit isn't preserved when the
# repo is committed from Windows).
RUN chmod +x entrypoint.sh

# Create the uploads dir so the mounted volume inherits appuser ownership.
RUN mkdir -p /app/uploads

# Non-root runtime user.
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Entrypoint runs migrations + seed, then starts the server. Invoked via bash so
# it works regardless of the file's executable bit.
CMD ["bash", "entrypoint.sh"]

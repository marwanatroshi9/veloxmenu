# MenuHub — Multi-Tenant Restaurant Menu SaaS

A production-oriented platform where many restaurants manage their own digital
menus from a private admin dashboard, and diners browse a fast, beautiful public
menu via a QR code. Built with a secure **multi-tenant** architecture — a
restaurant manager can only ever see and mutate their own restaurant's data.

- **Backend:** FastAPI · Python 3.13 · SQLAlchemy 2 · Alembic · PostgreSQL · JWT (+ refresh-token rotation) · Pydantic v2
- **Frontend:** Next.js 15 (App Router) · React 19 · TypeScript · Tailwind CSS · shadcn-style UI · Framer Motion · React Hook Form · Zod · TanStack Query · Zustand · Axios
- **Storage:** Cloudinary (auto compression, resize, WebP/AVIF)
- **Infra:** Docker · Docker Compose · Nginx reverse proxy (SSL-ready)

---

## Table of Contents

1. [Architecture](#architecture)
2. [Quick start (Docker)](#quick-start-docker)
3. [Local development](#local-development)
4. [Environment variables](#environment-variables)
5. [Folder structure](#folder-structure)
6. [Authentication & security](#authentication--security)
7. [API overview](#api-overview)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Implementation status](#implementation-status)

---

## Architecture

```
                         ┌──────────────┐
   Browser ──────────────►    Nginx     │  :80 / :443 (SSL-ready)
                         │  reverse proxy│
                         └───────┬───────┘
                    /api, /docs  │   /  (everything else)
                       ┌─────────┴──────────┐
                       ▼                    ▼
                ┌────────────┐        ┌────────────┐
                │  FastAPI   │        │  Next.js   │
                │  backend   │        │  frontend  │
                └──────┬─────┘        └────────────┘
                       ▼
                ┌────────────┐        ┌────────────┐
                │ PostgreSQL │        │ Cloudinary │  (images)
                └────────────┘        └────────────┘
```

**Multi-tenancy.** Every restaurant-scoped API route depends on
`get_current_restaurant`, which resolves the tenant **from the caller's JWT**, not
from request input. All queries are filtered by that restaurant id, and
cross-tenant object access returns `404` (existence is hidden). Super-admin routes
are gated by a separate `require_super_admin` dependency. This boundary is covered
by automated tests (`test_tenant_isolation.py`).

---

## Quick start (Docker)

Prerequisites: Docker + Docker Compose.

```bash
# 1. Configure environment
cp .env.example .env
cp backend/.env.example backend/.env
#   -> edit backend/.env: set a strong SECRET_KEY (>=32 chars) and, optionally,
#      your Cloudinary credentials.

# 2. Build & run the whole stack
docker compose up --build
```

On first boot the backend automatically:
- waits for PostgreSQL,
- runs Alembic migrations (`alembic upgrade head`),
- seeds a super admin and a demo restaurant (non-production only).

Then open:

| Surface            | URL                                   |
|--------------------|---------------------------------------|
| Public site        | http://localhost/                     |
| Demo menu          | http://localhost/demo-bistro          |
| API (Swagger)      | http://localhost/docs                 |
| API (ReDoc)        | http://localhost/redoc                |

**Default credentials** (change immediately):

| Role                | Email                        | Password       |
|---------------------|------------------------------|----------------|
| Super Admin         | `admin@menuhub.app`          | `ChangeMe123!` |
| Demo Manager        | `manager@demo.menuhub.app`   | `Manager123!`  |

> ⚠️ Use a real, non-reserved email domain. Addresses ending in `.local` are
> rejected by email validation and cannot be used to log in.

---

## Local development

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate    | Unix: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         # set SECRET_KEY + a reachable DATABASE_URL

alembic upgrade head
python -m seed
uvicorn app.main:app --reload
# API on http://localhost:8000  (docs at /docs)
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
npm run dev
# App on http://localhost:3000
```

---

## Environment variables

### Backend (`backend/.env`)

| Variable                       | Description                                             | Default |
|--------------------------------|---------------------------------------------------------|---------|
| `SECRET_KEY`                   | JWT signing secret (**required**, ≥32 chars)            | —       |
| `DATABASE_URL`                 | PostgreSQL DSN (`postgresql://…` is auto-upgraded to psycopg) | — |
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | Access-token lifetime                                   | `15`    |
| `REFRESH_TOKEN_EXPIRE_DAYS`    | Refresh-token lifetime                                  | `7`     |
| `COOKIE_SECURE`                | `true` in production (HTTPS)                             | `true`  |
| `COOKIE_SAMESITE`              | `lax` / `strict` / `none`                               | `lax`   |
| `BACKEND_CORS_ORIGINS`         | Comma-separated allowed origins                         | `http://localhost:3000` |
| `CLOUDINARY_*`                 | Cloud name / key / secret (image upload disabled if unset) | —    |
| `PUBLIC_SITE_URL`              | Base URL used in generated QR codes                     | `http://localhost:3000` |
| `RATE_LIMIT_DEFAULT` / `_AUTH` | Global and auth rate limits                             | `200/minute` / `10/minute` |
| `FIRST_SUPERADMIN_EMAIL/PASSWORD` | Bootstrap super-admin (seed only)                    | see file |

### Frontend (`frontend/.env.local`)

| Variable              | Description                              | Example |
|-----------------------|------------------------------------------|---------|
| `NEXT_PUBLIC_API_URL` | Base URL of the API incl. `/api/v1`      | `http://localhost:8000/api/v1` |

### Root (`.env`, docker-compose)

`POSTGRES_USER` · `POSTGRES_PASSWORD` · `POSTGRES_DB` · `NEXT_PUBLIC_API_URL`

---

## Folder structure

```
.
├── docker-compose.yml
├── nginx/
│   └── nginx.conf                 # reverse proxy, gzip, rate-limit, SSL block
├── backend/
│   ├── app/
│   │   ├── main.py                # app factory, CORS, security headers, rate limit
│   │   ├── api/                   # routers (v1) + router assembly + cookies
│   │   ├── auth/                  # JWT deps + login/refresh/rotation service
│   │   ├── core/                  # config, security (hashing/JWT), limiter
│   │   ├── database/              # engine/session + declarative base
│   │   ├── models/                # SQLAlchemy ORM models
│   │   ├── schemas/               # Pydantic v2 request/response models
│   │   ├── services/              # cloudinary, activity log
│   │   ├── utils/                 # slug, pagination
│   │   └── tests/                 # pytest (auth, tenant isolation, menu)
│   ├── alembic/                   # migrations (env + initial schema)
│   ├── seed.py                    # idempotent seed
│   ├── entrypoint.sh              # wait-for-db → migrate → seed → serve
│   └── Dockerfile
└── frontend/
    └── src/
        ├── app/                   # App Router: /, /login, /admin, /dashboard, /[slug]
        ├── components/            # UI primitives, shell, guard, providers
        ├── features/              # public-menu (interactive menu)
        ├── hooks/                 # zustand auth store
        ├── lib/                   # axios client (+refresh), token store, utils
        ├── services/              # typed API clients
        └── types/                 # shared TypeScript types
```

---

## Authentication & security

- **Passwords** hashed with **bcrypt** (passlib).
- **Access tokens**: short-lived JWTs carrying `sub`, `role`, and tenant (`rid`).
- **Refresh tokens**: opaque random strings, stored **hashed** (SHA-256) in an
  HttpOnly, Secure, SameSite cookie scoped to `/api/v1/auth`. Not in localStorage.
- **Refresh rotation with reuse detection**: each refresh revokes the presented
  token and issues a new one; re-presenting a revoked token revokes the whole
  token family (theft signal). Verified by tests.
- **Role-based authorization**: `super_admin` vs `restaurant_manager` dependencies.
- **Tenant isolation**: tenant derived from the token; cross-tenant access → 404.
- **Rate limiting**: global default + stricter auth limit (app layer) and an
  Nginx `limit_req` zone (edge layer).
- **Input validation** via Pydantic v2; **SQL-injection-safe** via SQLAlchemy
  parameterized queries; **security headers** (`X-Frame-Options`,
  `X-Content-Type-Options`, `Referrer-Policy`, HSTS in prod).
- **Audit log** (`activity_logs`) for logins, password changes, restaurant CRUD.
- **Suspended restaurants** block their managers from logging in and are hidden
  from the public site.

---

## API overview

Interactive docs: **`/docs`** (Swagger) and **`/redoc`**. All routes are under
`/api/v1`.

| Area | Endpoints (selection) |
|------|-----------------------|
| Auth | `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET /auth/me`, `POST /auth/change-password` |
| Super Admin | `GET /admin/stats`, `GET/POST /admin/restaurants`, `GET/PATCH/DELETE /admin/restaurants/{id}`, `POST …/suspend`, `POST …/activate`, `POST …/reset-manager-password`, `GET/PATCH …/subscription`, `POST …/logo`, `POST …/cover` |
| Restaurant | `GET/PATCH /restaurant/profile`, `POST /restaurant/logo|cover`, `GET /restaurant/stats` |
| Categories | `GET/POST /restaurant/categories`, `PATCH/DELETE …/{id}`, `PATCH …/reorder`, `POST …/{id}/image` |
| Menu items | `GET/POST /restaurant/menu-items` (paginate/search/filter/sort), `GET/PATCH/DELETE …/{id}`, `POST …/{id}/duplicate`, `POST …/{id}/image` |
| QR code | `GET /restaurant/qrcode?format=png|svg|pdf` |
| Public | `GET /public/restaurants/{slug}` |

All list endpoints support pagination (`page`, `page_size`), and menu/restaurant
lists support `search`, filters, and `sort_by`/`sort_order`.

---

## Testing

```bash
cd backend
.venv/Scripts/python -m pytest        # Windows
# or: pytest
```

Covered: login / wrong credentials / auth-required, refresh rotation & **reuse
detection**, change password, **tenant isolation** (list/update/delete/foreign
category), menu CRUD + duplicate + discount validation, and public-menu
visibility filtering. Tests run against an in-memory SQLite database.

Frontend:

```bash
cd frontend
npm run type-check     # tsc --noEmit
npm run build          # production build
```

---

## Deployment

1. Provision a host with Docker.
2. Set strong secrets in `.env` and `backend/.env` (`SECRET_KEY`,
   `POSTGRES_PASSWORD`), set `ENVIRONMENT=production`, `COOKIE_SECURE=true`, and
   real `BACKEND_CORS_ORIGINS` / `PUBLIC_SITE_URL`.
3. Add Cloudinary credentials to enable image uploads.
4. **TLS**: drop `fullchain.pem` / `privkey.pem` into `nginx/certs/`, uncomment the
   `443` server block and the HTTP→HTTPS redirect in `nginx/nginx.conf`.
5. `docker compose up -d --build`.

Migrations and the super-admin seed run automatically via `entrypoint.sh`. The
demo restaurant is **not** seeded when `ENVIRONMENT=production`.

### Creating new migrations

```bash
docker compose exec backend alembic revision --autogenerate -m "describe change"
docker compose exec backend alembic upgrade head
```

---

## Implementation status

**Fully implemented & verified**

- Secure JWT auth with refresh-token rotation + reuse detection (tested)
- Complete multi-tenant data model + migrations + idempotent seed
- Super-admin: stats, restaurant CRUD, suspend/activate, assign manager, reset
  password, subscription management, logo/cover upload, search + pagination
- Restaurant: profile + branding, category CRUD (+ visibility, reorder, image),
  menu-item CRUD (+ duplicate, availability, featured, filters, pagination)
- Public menu API + SEO/OpenGraph/Twitter/Schema.org, search, sticky category
  nav, featured, dark mode, RTL, animations, skeletons, 404
- QR code generation (PNG/SVG/PDF)
- Cloudinary upload service (compression/resize/WebP)
- Rate limiting, security headers, audit logging
- Docker Compose + Nginx + automatic migrations; frontend type-checks & builds

**Extension points (wired but intentionally minimal)**

- Drag-and-drop category reordering: API (`PATCH …/reorder`) and service are
  implemented; the dashboard currently exposes ordering via `sort_order` — wire a
  DnD library (e.g. `dnd-kit`) to the existing endpoint for pointer reordering.
- Full i18n dictionaries (EN/AR/CKB): RTL and per-restaurant language are wired;
  add translation JSON + a provider for UI string localization.
- Subscription billing is modeled and manageable by the super admin; connect a
  payment provider (e.g. Stripe) for live billing.

These are additive; the core product — secure multi-tenant menu management and a
premium public menu — is complete and runnable.

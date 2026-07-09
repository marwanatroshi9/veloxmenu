# Deploying MenuHub on Dokploy

Dokploy runs **Traefik** in front of your apps and issues **Let's Encrypt SSL**
automatically, so you don't use the bundled Nginx for TLS/ports. We keep Nginx
only as an internal path router so the whole app is served from **one domain**
(`/api` → backend, everything else → frontend). One origin = no CORS/cookie issues.

Use **[`docker-compose.dokploy.yml`](docker-compose.dokploy.yml)** for Dokploy
(not the plain `docker-compose.yml`, which publishes 80/443 itself).

## 1. DNS
Point your domain's **A record** to your Dokploy server's IP:
```
menu.example.com  ->  <server IP>
```

## 2. Create the app in Dokploy
1. **Project → Create Service → Compose.**
2. Source: your Git repo (or upload). Set **Compose Path** to `docker-compose.dokploy.yml`.

## 3. Environment variables (Dokploy → Environment)
```ini
POSTGRES_USER=menuhub
POSTGRES_PASSWORD=<long random db password>
POSTGRES_DB=menuhub

SECRET_KEY=<long random, >=32 chars>        # openssl rand -base64 48
PUBLIC_SITE_URL=https://menu.example.com     # your real https domain

FIRST_SUPERADMIN_EMAIL=you@example.com
FIRST_SUPERADMIN_PASSWORD=<strong admin password>

# Optional — enables image file uploads (else managers paste image URLs)
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```
Notes:
- `PUBLIC_SITE_URL` drives the frontend build (`NEXT_PUBLIC_API_URL`), the CORS
  origin, and the QR-code links — set it to your final `https://` domain **before
  the first deploy** (it is baked into the frontend at build time).
- `ENVIRONMENT=production`, `COOKIE_SECURE=true`, and `DATABASE_URL` are already
  set inside the compose file.

## 4. Domain + SSL (Dokploy → Domains)
Add a domain on the **`nginx`** service:
- **Host:** `menu.example.com`
- **Container port:** `80`
- **HTTPS:** on, **Certificate:** Let's Encrypt

Dokploy writes the Traefik labels and provisions the certificate. (The compose
file also has these labels commented out if you'd rather set them by hand.)

## 5. Deploy
Click **Deploy**. On first boot the backend automatically:
- waits for Postgres,
- runs `alembic upgrade head`,
- seeds the super-admin (demo data is skipped because `ENVIRONMENT=production`).

Then open `https://menu.example.com`, sign in at `/login` with your super-admin,
and **change the password** immediately (Admin → Account).

## Updating later
Push to your repo and hit **Redeploy** in Dokploy. Migrations run automatically.

## Giving a restaurant ("buyer") their menu
1. Super Admin → **Restaurants → New restaurant** (set the manager's email + password).
2. Send the owner their login; they change it under **Account**.
3. They build their menu (profile, categories, items, translations).
4. Their public menu is live at `https://menu.example.com/<their-slug>`.
5. **QR Code** page → download PNG/SVG/PDF to print for tables.

## Per-restaurant custom domains (optional)
To give a buyer their own domain (e.g. `menu.theirrestaurant.com`):
1. They add an A record to your Dokploy server IP.
2. In Dokploy → the `nginx` service → **Domains**, add the extra host (HTTPS on).
   Traefik issues a cert for it; it serves the same app. The restaurant is still
   reached at `/<their-slug>` (a true per-domain landing page is a small extra
   feature if you want it).

## Notes
- **Database:** kept inside compose with a persistent `pgdata` volume. To use a
  Dokploy-managed Postgres instead, remove the `db` service and point
  `DATABASE_URL` at it.
- **Scaling:** the API's rate limiter is in-memory (fine for one replica). For
  multiple backend replicas, switch it to Redis.

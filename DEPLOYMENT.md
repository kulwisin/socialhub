# DEPLOYMENT.md — SocialHub Deployment Guide

---

## Local Development (Mac M1/M2/Intel)

### First-time setup

```bash
git clone <repo> socialhub && cd socialhub

# 1. Create env files
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 2. Generate secrets (paste output into backend/.env)
make secrets

# 3. Start all services
make dev           # postgres + backend + frontend in Docker

# 4. Run migrations (only first time, or after new migrations)
make migrate
```

### Daily use

```bash
make dev           # start
make down          # stop
make migrate       # apply pending migrations
make logs          # tail all logs
make test          # run backend tests
```

### Access

| Service | URL |
|---|---|
| Dashboard | http://localhost:3000 |
| API Swagger | http://localhost:8000/docs |
| pgAdmin | http://localhost:5050 (admin@local / admin) |

---

## Production — Ubuntu Linux (VPS/Dedicated)

### Minimum server specs
- 2 vCPU, 4 GB RAM, 40 GB SSD
- Ubuntu 22.04 LTS (AMD64)
- Port 80 and 443 open

### 1. Server setup (one-time)

SSH into your server and run:
```bash
curl -fsSL https://raw.githubusercontent.com/<your-org>/socialhub/main/scripts/setup-prod.sh \
  | sudo bash
```

Or clone first and run locally:
```bash
git clone <repo> /opt/socialhub
sudo bash /opt/socialhub/scripts/setup-prod.sh
```

This installs Docker, configures UFW, enables fail2ban, creates a backup cron job.

### 2. Configure environment

```bash
cd /opt/socialhub

cp .env.example .env
nano .env   # set POSTGRES_PASSWORD, DOMAIN, CERTBOT_EMAIL, etc.

cp backend/.env.example backend/.env
nano backend/.env   # set APP_SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY, META_*

cp frontend/.env.example frontend/.env.local
nano frontend/.env.local  # set NEXT_PUBLIC_API_URL, NEXT_PUBLIC_META_APP_ID
```

`.env` required fields:
```env
POSTGRES_PASSWORD=<strong-random-password>
DOMAIN=yourdomain.com
CERTBOT_EMAIL=admin@yourdomain.com
NEXT_PUBLIC_API_URL=https://yourdomain.com
NEXT_PUBLIC_META_APP_ID=<from Meta developer portal>
```

`backend/.env` required fields:
```env
APP_SECRET_KEY=<openssl rand -hex 32>
ENCRYPTION_KEY=<fernet key>
DATABASE_URL=postgresql://socialhub:<password>@postgres:5432/socialhub
META_APP_ID=<from Meta developer portal>
META_APP_SECRET=<from Meta developer portal>
META_REDIRECT_URI=https://yourdomain.com/api/v1/auth/meta/callback
ALLOWED_ORIGINS=https://yourdomain.com
```

### 3. Deploy

```bash
cd /opt/socialhub
make prod-up       # build images + start all services
make prod-migrate  # run database migrations
```

### 4. Issue SSL certificate

```bash
# Start nginx first (serves ACME challenge over HTTP)
docker compose up -d nginx

# Issue certificate
docker compose run --rm certbot

# Restart nginx with SSL
docker compose restart nginx
```

The nginx config auto-redirects HTTP → HTTPS and uses the cert at
`/etc/letsencrypt/live/${DOMAIN}/`.

**Renewal** (auto via cron — add this if not already set):
```bash
# Renew monthly
0 0 1 * * cd /opt/socialhub && docker compose run --rm certbot renew && docker compose restart nginx
```

### 5. Verify deployment

```bash
make healthcheck
# or directly:
bash scripts/healthcheck.sh
```

Expected output:
```
  ✅  Backend /health              → 200
  ✅  Backend /api/v1/health       → 200
  ✅  Backend Swagger /docs        → 200
  ✅  Frontend /                   → 200

  Passed: 4  |  Failed: 0
```

---

## CI/CD — GitHub Actions

Two workflows:

| Workflow | Trigger | What it does |
|---|---|---|
| `ci.yml` | Push to `main`/`develop`, any PR | Lint + test + Docker build + push to GHCR |
| `deploy.yml` | CI passes on `main`, or manual | SSH deploy to production server |

### Required GitHub Secrets

Set in: **GitHub → Settings → Secrets and variables → Actions**

| Secret | Value |
|---|---|
| `TEST_ENCRYPTION_KEY` | A Fernet key for the test suite |
| `PROD_HOST` | Production server IP or hostname |
| `PROD_USER` | SSH user (e.g. `ubuntu`) |
| `PROD_SSH_KEY` | Private SSH key (the public key must be in `~/.ssh/authorized_keys` on the server) |
| `PROD_SSH_PORT` | SSH port (default 22) |

### Required GitHub Variables (not secrets)

Set in: **GitHub → Settings → Secrets and variables → Variables**

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://yourdomain.com` |
| `NEXT_PUBLIC_META_APP_ID` | Your Meta App ID |

---

## Backup and Restore

### Manual backup
```bash
make backup
# Output: ./backups/socialhub_YYYYMMDD_HHMMSS.sql.gz
```

### Automated backup
The setup script installs a daily cron at 03:00 UTC. Backups older than 7 days are automatically pruned.

### Restore
```bash
make restore file=./backups/socialhub_20260604_030000.sql.gz
```

---

## Rollback

```bash
cd /opt/socialhub

# 1. Restore database from last backup
make restore file=./backups/<latest>.sql.gz

# 2. Roll back to previous code
git checkout <previous-sha>

# 3. Rebuild and restart
make prod-up

# 4. Roll back DB migration if needed
make prod-rollback
```

---

## Resource Usage (production)

| Service | Memory limit |
|---|---|
| PostgreSQL | 512 MB |
| FastAPI backend | 512 MB |
| Next.js frontend | 256 MB |
| Nginx | 64 MB |
| **Total** | **~1.4 GB** |

Runs comfortably on a 4 GB VPS. On a 2 GB VPS, the setup script creates a 2 GB swapfile as a buffer.

---

## Troubleshooting

### Backend won't start — missing env var
```bash
docker compose logs backend | grep ERROR
```
Ensure all required fields in `backend/.env` are filled.

### `alembic upgrade head` fails
```bash
make prod-migrate
# if it times out:
docker compose exec backend alembic current
docker compose exec backend alembic upgrade head
```

### SSL certificate not found
```bash
# Re-issue certificate
docker compose run --rm certbot
docker compose restart nginx
```

### Disk full (media uploads)
```bash
df -h
# Clear old backups
find /opt/socialhub/backups -mtime +30 -delete
# Or prune unused Docker layers
docker system prune -f
```

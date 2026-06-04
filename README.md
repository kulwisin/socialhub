# SocialHub MVP

A personal dashboard to connect Instagram, Facebook, and TikTok accounts to virtual **devices**, upload a video once, and publish it across all selected platforms in one click.

---

## What It Does

1. **Create Devices** — a device is a named container that holds social accounts
2. **Connect Accounts** — link Instagram, Facebook, or TikTok to a device via OAuth
3. **Upload a Video** — drag-and-drop, add a caption
4. **Select Targets** — pick which devices/accounts to publish to
5. **Click Post** — SocialHub publishes to all selected platforms in parallel

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, React, TypeScript, TailwindCSS, shadcn/ui |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic |
| Database | PostgreSQL 16 |
| Auth | Meta OAuth 2.0 (Instagram + Facebook), TikTok OAuth |
| Dev | Docker Compose, Make |

---

## Quick Start

### Prerequisites
- Docker Desktop (Mac M1/M2/Intel or Linux)
- Make
- `openssl` (for secret generation)

### 1. Clone and configure

```bash
git clone <repo-url> socialhub
cd socialhub

cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Fill in META_APP_ID and META_APP_SECRET (see SECRET.md)
nano backend/.env
```

### 2. Generate secrets

```bash
make secrets
# Prints APP_SECRET_KEY and ENCRYPTION_KEY — paste into backend/.env
```

### 3. Start

```bash
make dev
# Runs: postgres + backend + frontend

make migrate   # First-time DB setup
```

### 4. Open

| Service | URL |
|---|---|
| Dashboard | http://localhost:3000 |
| API docs | http://localhost:8000/docs |
| pgAdmin | http://localhost:5050 |

---

## Project Layout

```
socialhub/
├── backend/          # FastAPI + SQLAlchemy
├── frontend/         # Next.js 15
├── scripts/          # DB init, nginx config
├── .github/          # CI workflow
├── docker-compose.dev.yml
├── docker-compose.yml
└── Makefile
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for module details.

---

## Platforms

| Platform | Status |
|---|---|
| Instagram Reels | ✅ Phase 4 |
| Facebook Video | ✅ Phase 4 |
| TikTok | 🔜 Architecture ready, integration Phase 6 |

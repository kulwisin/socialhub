# SECRET.md — Environment Variables & Secret Management

> Never commit `.env` files. This document describes every required variable.

---

## Backend — `backend/.env`

```env
# Application
APP_ENV=development
APP_DEBUG=true
APP_SECRET_KEY=          # openssl rand -hex 32
ALLOWED_ORIGINS=http://localhost:3000

# Database
DATABASE_URL=postgresql://socialhub:socialhub@postgres:5432/socialhub

# Encryption (stored tokens)
ENCRYPTION_KEY=          # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Meta (Instagram + Facebook)
META_APP_ID=             # developers.facebook.com → App ID
META_APP_SECRET=         # developers.facebook.com → App Secret  ← NEVER expose to frontend
META_REDIRECT_URI=http://localhost:8000/api/v1/auth/meta/callback
META_GRAPH_API_VERSION=v21.0

# TikTok (future)
TIKTOK_CLIENT_KEY=
TIKTOK_CLIENT_SECRET=

# Storage
MEDIA_DIR=/app/media     # inside container
```

## Frontend — `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_META_APP_ID=   # Same as META_APP_ID — App ID only, NOT secret
```

## Root — `.env` (Docker Compose variables)

```env
POSTGRES_DB=socialhub
POSTGRES_USER=socialhub
POSTGRES_PASSWORD=        # openssl rand -base64 16
PGADMIN_EMAIL=admin@local
PGADMIN_PASSWORD=admin
```

---

## Generating Secrets

```bash
# APP_SECRET_KEY
openssl rand -hex 32

# ENCRYPTION_KEY (Fernet)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# PostgreSQL password
openssl rand -base64 16
```

Or just run:
```bash
make secrets
```

---

## Meta App Setup

1. Go to https://developers.facebook.com
2. **Create App** → type: **Business**
3. Add products:
   - **Facebook Login**
   - **Instagram Graph API**
4. Facebook Login → Settings → Valid OAuth Redirect URIs:
   - `http://localhost:8000/api/v1/auth/meta/callback`
5. Copy **App ID** → `META_APP_ID` and `NEXT_PUBLIC_META_APP_ID`
6. Copy **App Secret** → `META_APP_SECRET` (backend only)
7. App Review → add permissions: `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`

### Required Instagram Permissions
| Permission | Purpose |
|---|---|
| `instagram_basic` | Read profile, media |
| `instagram_content_publish` | Post reels and images |
| `pages_show_list` | List Facebook Pages |
| `pages_read_engagement` | Read Page insights |

---

## Token Storage

Instagram and Facebook access tokens are **Fernet-encrypted** before being stored in the database.

```
Raw token → Fernet.encrypt(key) → base64 ciphertext stored in DB
Read      → Fernet.decrypt(key) → raw token used in API calls
```

The `ENCRYPTION_KEY` must remain stable — rotating it requires re-encrypting all tokens in the database.

---

## What NOT to Do

- Never put `META_APP_SECRET` in `NEXT_PUBLIC_*` variables
- Never log `access_token`, `refresh_token`, or `ENCRYPTION_KEY`
- Never commit `.env`, `backend/.env`, or `frontend/.env.local`

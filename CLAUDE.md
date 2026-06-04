# CLAUDE.md — SocialHub Development Standards

---

## Architecture

```
HTTP Request → Router → Service → Repository → Database
```

- **Routers** (`api/v1/endpoints/`) — HTTP only: parse input, call service, return response. Zero business logic.
- **Services** (`services/`) — all business logic, orchestration, platform API calls.
- **Repositories** (`repositories/`) — all database queries. No logic, only data access.
- **Models** (`models/`) — SQLAlchemy ORM only. No methods beyond `__repr__`.
- **Schemas** (`schemas/`) — Pydantic v2 request/response shapes. Separate `Create`, `Update`, `Response`.
- **Integrations** (`integrations/`) — raw HTTP clients for external APIs (Meta Graph, TikTok).

Frontend mirrors this:
```
Page → Feature Component → TanStack Query Hook → API Service → Backend
```

---

## Naming Conventions

### Python
| Entity | Convention | Example |
|---|---|---|
| Files | `snake_case` | `device_service.py` |
| Classes | `PascalCase` | `DeviceService` |
| Functions | `snake_case` | `get_device_by_id` |
| Pydantic schemas | `PascalCase` + suffix | `DeviceCreate`, `DeviceResponse` |
| Repository classes | `PascalCase` + `Repository` | `DeviceRepository` |

### TypeScript
| Entity | Convention | Example |
|---|---|---|
| Component files | `PascalCase.tsx` | `DeviceCard.tsx` |
| Hook files | `camelCase.ts` with `use` prefix | `useDevices.ts` |
| Service files | `camelCase.service.ts` | `device.service.ts` |
| Types | `PascalCase` | `Device`, `Platform` |

### Database
| Entity | Convention | Example |
|---|---|---|
| Tables | `snake_case` plural | `social_accounts` |
| Columns | `snake_case` | `device_id`, `created_at` |
| Indexes | `ix_<table>_<col>` | `ix_posts_status` |

---

## Coding Rules

### Python
- `from __future__ import annotations` at the top of every file
- All DB calls must be `async` using `AsyncSession`
- Use `ruff` for formatting and linting (line length 88)
- Type hints on all function signatures
- Raise domain exceptions (`DeviceNotFoundError`), let middleware convert to HTTP

### TypeScript
- `"strict": true` — no `any`
- TanStack Query for all server state
- Zustand for client-only state
- No `fetch()` calls in components — always via service layer

### Security
- Never log tokens, passwords, or secrets
- All sensitive DB columns use Fernet encryption
- Validate file uploads: type, size, duration limits
- Sanitize all user input at the API boundary

---

## Git Workflow

```
main          → stable, deployable
develop       → integration
feature/*     → new work (branch from develop)
fix/*         → bug fixes
```

Commit format:
```
feat(devices): add device status indicator
fix(instagram): handle expired token refresh
chore(deps): bump fastapi to 0.115
```

---

## Adding a New Platform

1. Create `backend/app/integrations/<platform>/client.py` — raw HTTP client
2. Create `backend/app/services/<platform>/service.py` — business logic
3. Add `platform` enum value in `models/social_account.py`
4. Add OAuth router in `api/v1/endpoints/<platform>_oauth.py`
5. Add publish method to `services/publisher.py`
6. Update frontend `Platform` type and UI

---

## Environment

- Local: `.env` files (never commit)
- Production: inject as env vars via Docker / server config
- See `SECRET.md` for all required variables and generation instructions

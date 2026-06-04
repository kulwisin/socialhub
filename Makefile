.PHONY: help \
        dev dev-bg down build \
        migrate rollback migration db-shell \
        test test-cov lint format typecheck \
        logs logs-backend logs-frontend logs-nginx \
        shell-backend shell-frontend \
        secrets clean \
        prod-up prod-down prod-migrate prod-rollback prod-logs prod-build \
        backup restore healthcheck

DC     = docker compose -f docker-compose.dev.yml
DC_PROD = docker compose -f docker-compose.yml

# ─── Help ─────────────────────────────────────────────────────────────────────

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ─── Development ──────────────────────────────────────────────────────────────

dev: ## Start dev environment (foreground — Ctrl+C to stop)
	$(DC) up

dev-bg: ## Start dev environment (background)
	$(DC) up -d

down: ## Stop all dev containers
	$(DC) down

build: ## Rebuild all dev images (no cache)
	$(DC) build --no-cache

# ─── Database (dev) ───────────────────────────────────────────────────────────

migrate: ## Run pending migrations
	$(DC) exec backend alembic upgrade head

rollback: ## Roll back one migration
	$(DC) exec backend alembic downgrade -1

migration: ## Create migration (usage: make migration msg="describe change")
	$(DC) exec backend alembic revision --autogenerate -m "$(msg)"

db-shell: ## Open psql shell
	$(DC) exec postgres psql -U socialhub -d socialhub

# ─── Testing ──────────────────────────────────────────────────────────────────

test: ## Run backend tests
	$(DC) exec backend pytest -v

test-cov: ## Run tests with HTML coverage report
	$(DC) exec backend pytest --cov=app --cov-report=html --cov-report=term

# ─── Code quality ─────────────────────────────────────────────────────────────

lint: ## Lint backend + frontend
	$(DC) exec backend ruff check .
	$(DC) exec frontend npx eslint src --max-warnings 0

format: ## Auto-format backend + frontend
	$(DC) exec backend ruff format .
	$(DC) exec frontend npx prettier --write src

typecheck: ## Type-check backend (mypy) + frontend (tsc)
	$(DC) exec backend mypy app
	$(DC) exec frontend npx tsc --noEmit

# ─── Logs ────────────────────────────────────────────────────────────────────

logs: ## Tail all dev logs
	$(DC) logs -f

logs-backend: ## Tail backend logs
	$(DC) logs -f backend

logs-frontend: ## Tail frontend logs
	$(DC) logs -f frontend

# ─── Shells ───────────────────────────────────────────────────────────────────

shell-backend: ## Open bash in backend container
	$(DC) exec backend bash

shell-frontend: ## Open sh in frontend container
	$(DC) exec frontend sh

# ─── Utilities ────────────────────────────────────────────────────────────────

secrets: ## Generate APP_SECRET_KEY and ENCRYPTION_KEY (paste into backend/.env)
	@echo ""
	@echo "APP_SECRET_KEY=$(shell openssl rand -hex 32)"
	@echo "ENCRYPTION_KEY=$(shell python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())' 2>/dev/null || echo '[pip install cryptography first]')"
	@echo ""

clean: ## Remove containers, volumes, and build caches
	$(DC) down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache  -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next        -exec rm -rf {} + 2>/dev/null || true

# ─── Production ───────────────────────────────────────────────────────────────

prod-up: ## Build and start production services
	$(DC_PROD) up -d --build

prod-down: ## Stop production services
	$(DC_PROD) down

prod-build: ## Rebuild production images (no cache)
	$(DC_PROD) build --no-cache

prod-migrate: ## Run migrations in production
	$(DC_PROD) exec backend alembic upgrade head

prod-rollback: ## Roll back one migration in production
	$(DC_PROD) exec backend alembic downgrade -1

prod-logs: ## Tail production logs
	$(DC_PROD) logs -f

# ─── Backup / Restore ─────────────────────────────────────────────────────────

backup: ## Create a timestamped database backup (./backups/)
	bash scripts/backup/backup.sh

restore: ## Restore from backup (usage: make restore file=./backups/socialhub_*.sql.gz)
	bash scripts/backup/restore.sh "$(file)"

# ─── Health ───────────────────────────────────────────────────────────────────

healthcheck: ## Check all service endpoints respond correctly
	bash scripts/healthcheck.sh

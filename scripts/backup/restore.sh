#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# SocialHub — PostgreSQL restore script
#
# Usage:
#   ./scripts/backup/restore.sh ./backups/socialhub_20260604_030000.sql.gz
#
# WARNING: This drops all existing data and replaces it with the backup.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BACKUP_FILE="${1:-}"

# ── Validate args ─────────────────────────────────────────────────────────────
if [[ -z "$BACKUP_FILE" ]]; then
  echo "Usage: $0 <backup-file.sql.gz>"
  echo ""
  echo "Available backups:"
  ls -lh "${ROOT_DIR}/backups/"*.sql.gz 2>/dev/null || echo "  (no backups found)"
  exit 1
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "[ERROR] Backup file not found: ${BACKUP_FILE}"
  exit 1
fi

# ── Load env ──────────────────────────────────────────────────────────────────
ENV_FILE="${ROOT_DIR}/.env"
if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  set -o allexport; source "$ENV_FILE"; set +o allexport
fi

POSTGRES_DB="${POSTGRES_DB:-socialhub}"
POSTGRES_USER="${POSTGRES_USER:-socialhub}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"

# ── Detect compose file ───────────────────────────────────────────────────────
if docker compose -f "${ROOT_DIR}/docker-compose.yml" ps postgres 2>/dev/null | grep -q "running\|Up"; then
  COMPOSE_FILE="${ROOT_DIR}/docker-compose.yml"
else
  COMPOSE_FILE="${ROOT_DIR}/docker-compose.dev.yml"
fi

# ── Confirm ───────────────────────────────────────────────────────────────────
BACKUP_SIZE="$(du -sh "${BACKUP_FILE}" | cut -f1)"
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  WARNING: Destructive operation                         ║"
echo "╠══════════════════════════════════════════════════════════╣"
printf "║  Restore file: %-43s ║\n" "$(basename "${BACKUP_FILE}") (${BACKUP_SIZE})"
printf "║  Target DB:    %-43s ║\n" "${POSTGRES_DB}"
echo "║                                                          ║"
echo "║  This will DROP and recreate all tables.                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
read -rp "Type 'yes' to confirm: " confirm
if [[ "$confirm" != "yes" ]]; then
  echo "Aborted."
  exit 0
fi

# ── Drop + recreate schema ────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Dropping existing schema…"
PGPASSWORD="${POSTGRES_PASSWORD}" \
docker compose -f "${COMPOSE_FILE}" exec -T postgres \
  psql --username="${POSTGRES_USER}" "${POSTGRES_DB}" \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# ── Restore ───────────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Restoring from ${BACKUP_FILE}…"
gunzip -c "${BACKUP_FILE}" | \
PGPASSWORD="${POSTGRES_PASSWORD}" \
docker compose -f "${COMPOSE_FILE}" exec -T postgres \
  psql --username="${POSTGRES_USER}" "${POSTGRES_DB}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Restore complete."
echo ""
echo "Next: restart the backend to pick up the restored state."
echo "  docker compose -f ${COMPOSE_FILE} restart backend"

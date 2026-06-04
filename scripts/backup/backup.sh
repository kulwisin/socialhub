#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# SocialHub — PostgreSQL backup script
#
# Usage:
#   ./scripts/backup/backup.sh              # interactive (reads .env)
#   KEEP_DAYS=14 ./scripts/backup/backup.sh # override retention
#
# Outputs:
#   ./backups/socialhub_YYYYMMDD_HHMMSS.sql.gz
#
# Cron (daily at 03:00):
#   0 3 * * * cd /opt/socialhub && ./scripts/backup/backup.sh >> /var/log/socialhub-backup.log 2>&1
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BACKUP_DIR="${ROOT_DIR}/backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="${BACKUP_DIR}/socialhub_${TIMESTAMP}.sql.gz"
KEEP_DAYS="${KEEP_DAYS:-7}"

# ── Load env ──────────────────────────────────────────────────────────────────
ENV_FILE="${ROOT_DIR}/.env"
if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  set -o allexport; source "$ENV_FILE"; set +o allexport
fi

POSTGRES_DB="${POSTGRES_DB:-socialhub}"
POSTGRES_USER="${POSTGRES_USER:-socialhub}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"

# ── Pre-flight ────────────────────────────────────────────────────────────────
mkdir -p "$BACKUP_DIR"

if ! docker compose -f "${ROOT_DIR}/docker-compose.yml" ps postgres 2>/dev/null | grep -q "running\|Up"; then
  # Fall back to dev compose
  COMPOSE_FILE="${ROOT_DIR}/docker-compose.dev.yml"
  if ! docker compose -f "$COMPOSE_FILE" ps postgres 2>/dev/null | grep -q "running\|Up"; then
    echo "[ERROR] PostgreSQL container is not running. Start it first."
    exit 1
  fi
else
  COMPOSE_FILE="${ROOT_DIR}/docker-compose.yml"
fi

# ── Dump ─────────────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting backup → ${BACKUP_FILE}"

PGPASSWORD="${POSTGRES_PASSWORD}" \
docker compose -f "${COMPOSE_FILE}" exec -T postgres \
  pg_dump \
    --username="${POSTGRES_USER}" \
    --format=plain \
    --no-owner \
    --no-acl \
    "${POSTGRES_DB}" \
  | gzip > "${BACKUP_FILE}"

BACKUP_SIZE="$(du -sh "${BACKUP_FILE}" | cut -f1)"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup complete: ${BACKUP_FILE} (${BACKUP_SIZE})"

# ── Prune old backups ─────────────────────────────────────────────────────────
PRUNED="$(find "${BACKUP_DIR}" -name "socialhub_*.sql.gz" -mtime "+${KEEP_DAYS}" -print -delete | wc -l | tr -d ' ')"
if [[ "$PRUNED" -gt 0 ]]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pruned ${PRUNED} backup(s) older than ${KEEP_DAYS} days"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup finished."

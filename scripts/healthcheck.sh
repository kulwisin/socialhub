#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# SocialHub — Service health check script
# Verifies all endpoints respond correctly.
# Exits 0 if all pass, 1 if any fail.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
PASS=0; FAIL=0

check() {
  local name="$1"
  local url="$2"
  local expected_status="${3:-200}"

  actual_status="$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url")"

  if [[ "$actual_status" == "$expected_status" ]]; then
    printf "  ✅  %-30s → %s\n" "$name" "$actual_status"
    PASS=$((PASS + 1))
  else
    printf "  ❌  %-30s → %s (expected %s)\n" "$name" "$actual_status" "$expected_status"
    FAIL=$((FAIL + 1))
  fi
}

echo ""
echo "SocialHub Health Check — $(date '+%Y-%m-%d %H:%M:%S')"
echo "────────────────────────────────────────────────────"

check "Backend /health"         "${BACKEND_URL}/health"
check "Backend /api/v1/health"  "${BACKEND_URL}/api/v1/health"
check "Backend Swagger /docs"   "${BACKEND_URL}/docs"
check "Frontend /"              "${BASE_URL}/"

echo ""
echo "────────────────────────────────────────────────────"
echo "  Passed: ${PASS}  |  Failed: ${FAIL}"
echo ""

if [[ "$FAIL" -gt 0 ]]; then
  echo "  Some checks failed. Check docker compose logs for details."
  exit 1
fi

echo "  All checks passed."
exit 0

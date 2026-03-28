#!/bin/sh
# check-openprodoc.sh — Pre-flight check for external OpenProdoc integration
#
# Run this script BEFORE starting the upgrade containers to verify
# that your existing OpenProdoc is properly configured and reachable.
#
# Usage:
#   ./check-openprodoc.sh [OPENPRODOC_URL] [DB_HOST] [DB_PORT] [DB_NAME] [DB_USER] [DB_PASSWORD]
#
# Or set the variables in .env and run without arguments.

# Load .env if present
if [ -f .env ]; then
    echo "Loading configuration from .env..."
    set -a
    . ./.env
    set +a
fi

# Defaults / arguments
OPD_URL="${1:-${OPENPRODOC_URL:-http://localhost:8080}}"
DB_HOST="${2:-${OPD_POSTGRES_HOST:-localhost}}"
DB_PORT="${3:-${OPD_POSTGRES_PORT:-5432}}"
DB_NAME="${4:-${OPD_POSTGRES_DB:-prodoc}}"
DB_USER="${5:-${OPD_POSTGRES_USER:-user1}}"
DB_PASS="${6:-${OPD_POSTGRES_PASSWORD:-pass1}}"

ERRORS=0

echo "=============================================="
echo "  OpenProdoc Pre-Flight Check"
echo "=============================================="
echo ""

# -------------------------------------------------------
# Check 1: OpenProdoc Web UI reachable
# -------------------------------------------------------
echo -n "[1/5] OpenProdoc Web UI (${OPD_URL}/ProdocWeb2/)... "
if curl -sf -o /dev/null "${OPD_URL}/ProdocWeb2/" 2>/dev/null; then
    echo "OK"
else
    echo "FAIL"
    echo "      Cannot reach OpenProdoc at ${OPD_URL}/ProdocWeb2/"
    ERRORS=$((ERRORS + 1))
fi

# -------------------------------------------------------
# Check 2: REST API reachable
# -------------------------------------------------------
echo -n "[2/5] REST API (${OPD_URL}/ProdocWeb2/APIRest/session)... "
REST_RESP=$(curl -sf "${OPD_URL}/ProdocWeb2/APIRest/session" 2>/dev/null || echo "")
if [ -n "${REST_RESP}" ]; then
    echo "OK"
else
    echo "FAIL"
    echo "      REST API not responding. Make sure ProdocWeb2 is deployed with APIRest."
    ERRORS=$((ERRORS + 1))
fi

# -------------------------------------------------------
# Check 3: REST API login works
# -------------------------------------------------------
echo -n "[3/5] REST API login... "
OPD_USER="${OPD_ROOT_USER:-root}"
OPD_PASS="${OPD_ROOT_PASSWORD:-admin}"
LOGIN_RESP=$(curl -sf -X PUT "${OPD_URL}/ProdocWeb2/APIRest/session" \
    -H "Content-Type: application/json" \
    -d "{\"Name\":\"${OPD_USER}\",\"Password\":\"${OPD_PASS}\"}" 2>/dev/null || echo "")

if echo "${LOGIN_RESP}" | grep -q '"Token"'; then
    echo "OK"
    # Logout
    TOKEN=$(echo "${LOGIN_RESP}" | sed 's/.*"Token":"\([^"]*\)".*/\1/')
    curl -sf -X DELETE "${OPD_URL}/ProdocWeb2/APIRest/session" \
        -H "Authorization: Bearer ${TOKEN}" >/dev/null 2>&1 || true
else
    echo "FAIL"
    echo "      Login failed with user '${OPD_USER}'. Check credentials."
    ERRORS=$((ERRORS + 1))
fi

# -------------------------------------------------------
# Check 4: Database reachable
# -------------------------------------------------------
echo -n "[4/5] PostgreSQL (${DB_HOST}:${DB_PORT}/${DB_NAME})... "
if command -v pg_isready >/dev/null 2>&1; then
    if PGPASSWORD="${DB_PASS}" pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" >/dev/null 2>&1; then
        echo "OK"
    else
        echo "FAIL"
        echo "      Cannot connect to PostgreSQL. Check host, port, and credentials."
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "SKIP (pg_isready not installed)"
    echo "      Install postgresql-client to enable this check."
fi

# -------------------------------------------------------
# Check 5: Task scheduler configuration
# -------------------------------------------------------
echo -n "[5/5] Task scheduler tables... "
if command -v psql >/dev/null 2>&1; then
    TABLE_CHECK=$(PGPASSWORD="${DB_PASS}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -t -A -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'pd_tasksdefeven';" 2>/dev/null || echo "0")
    if [ "${TABLE_CHECK}" -gt 0 ] 2>/dev/null; then
        echo "OK"
    else
        echo "FAIL"
        echo "      Table pd_tasksdefeven not found. Is this an OpenProdoc database?"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "SKIP (psql not installed)"
fi

# -------------------------------------------------------
# Summary
# -------------------------------------------------------
echo ""
echo "----------------------------------------------"
if [ "${ERRORS}" -eq 0 ]; then
    echo "  All checks passed! You can proceed with the upgrade."
    echo ""
    echo "  Next steps:"
    echo "    1. Copy .env.example to .env and edit values"
    echo "    2. Run: ./start-linux.sh (or start-windows.bat)"
    echo "    3. Wait for initialization (check: docker compose logs -f rag-init)"
    echo "    4. Add task scheduler settings to Prodoc.properties (see README.md)"
    echo "    5. Restart your OpenProdoc"
else
    echo "  ${ERRORS} check(s) failed. Please fix the issues above before proceeding."
fi
echo "----------------------------------------------"
exit ${ERRORS}

#!/bin/sh
# rag-init.sh — One-shot init script for OpenProdoc RAG CustomTask
#
# 1. Waits for core-engine and Open WebUI to be ready
# 2. Creates the watcher admin account in Open WebUI
# 3. Uploads the CustomTask JAR to OpenProdoc via REST API
# 4. Inserts event + cron task definitions via direct SQL
#
# Environment variables (all required):
#   OPENPRODOC_URL        - Core engine URL (e.g., http://core-engine:8080)
#   OPENWEBUI_URL         - Open WebUI URL (e.g., http://openwebui:8080)
#   OPENWEBUI_ADMIN_EMAIL - Admin email for Open WebUI
#   OPENWEBUI_ADMIN_PASSWORD - Admin password for Open WebUI
#   OPD_ROOT_USER         - OpenProdoc root user (default: root)
#   OPD_ROOT_PASSWORD     - OpenProdoc root password
#   POSTGRES_HOST         - PostgreSQL host
#   POSTGRES_PORT         - PostgreSQL port (default: 5432)
#   POSTGRES_DB           - OpenProdoc database name
#   POSTGRES_USER         - PostgreSQL user
#   POSTGRES_PASSWORD     - PostgreSQL password
#   JAR_PATH              - Path to the CustomTask JAR file
#   SCIM_TOKEN            - SCIM API token for Open WebUI

set -e

# Install curl if not present (postgres:alpine doesn't include it)
if ! command -v curl >/dev/null 2>&1; then
    echo "Installing curl..."
    apk add --no-cache curl >/dev/null 2>&1
fi

# Defaults
OPD_ROOT_USER="${OPD_ROOT_USER:-root}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
JAR_PATH="${JAR_PATH:-/jar/openprodoc-ragtask.jar}"
SYNC_INTERVAL_MINS="${SYNC_INTERVAL_MINS:-1}"
MARKER_TABLE="pd_tasksdefeven"
MARKER_NAME="RAG_DocIns"

echo "=== OpenProdoc RAG CustomTask Init ==="
echo "Core Engine: ${OPENPRODOC_URL}"
echo "Open WebUI:  ${OPENWEBUI_URL}"
echo ""

# -------------------------------------------------------
# Utility: wait for HTTP endpoint to return 200
# -------------------------------------------------------
wait_for_http() {
    local url="$1"
    local name="$2"
    local max_attempts="${3:-60}"
    local attempt=0

    echo "Waiting for ${name} at ${url}..."
    while [ "$attempt" -lt "$max_attempts" ]; do
        if curl -sf -o /dev/null "${url}" 2>/dev/null; then
            echo "${name} is ready."
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 5
    done
    echo "ERROR: ${name} not ready after $((max_attempts * 5))s"
    exit 1
}

# -------------------------------------------------------
# Utility: wait for PostgreSQL
# -------------------------------------------------------
wait_for_postgres() {
    local max_attempts="${1:-60}"
    local attempt=0

    echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
    while [ "$attempt" -lt "$max_attempts" ]; do
        if PGPASSWORD="${POSTGRES_PASSWORD}" pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null 2>&1; then
            echo "PostgreSQL is ready."
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 3
    done
    echo "ERROR: PostgreSQL not ready after $((max_attempts * 3))s"
    exit 1
}

# -------------------------------------------------------
# Utility: run SQL
# -------------------------------------------------------
run_sql() {
    PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -t -A -c "$1"
}

# -------------------------------------------------------
# Step 0: Check idempotency — skip if already initialized
# -------------------------------------------------------
wait_for_postgres

EXISTING=$(run_sql "SELECT COUNT(*) FROM ${MARKER_TABLE} WHERE name = '${MARKER_NAME}';" 2>/dev/null || echo "0")
if [ "${EXISTING}" -gt 0 ] 2>/dev/null; then
    echo "RAG CustomTask already initialized (found ${MARKER_NAME} in ${MARKER_TABLE}). Skipping."
    exit 0
fi
echo "No existing RAG tasks found. Proceeding with initialization."

# -------------------------------------------------------
# Step 1: Wait for services
# -------------------------------------------------------
wait_for_http "${OPENPRODOC_URL}/ProdocWeb2/" "OpenProdoc Core Engine"
wait_for_http "${OPENWEBUI_URL}/health" "Open WebUI"

# -------------------------------------------------------
# Step 2: Create watcher admin account in Open WebUI
# -------------------------------------------------------
echo ""
echo "--- Creating watcher admin account in Open WebUI ---"

# Check if user already exists by trying to sign in
SIGNIN_RESP=$(curl -sf -X POST "${OPENWEBUI_URL}/api/v1/auths/signin" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"${OPENWEBUI_ADMIN_EMAIL}\",\"password\":\"${OPENWEBUI_ADMIN_PASSWORD}\"}" 2>/dev/null || echo "")

if echo "${SIGNIN_RESP}" | grep -q '"token"'; then
    echo "Watcher admin already exists in Open WebUI."
else
    echo "Creating watcher admin account..."
    SIGNUP_RESP=$(curl -sf -X POST "${OPENWEBUI_URL}/api/v1/auths/signup" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"${OPENWEBUI_ADMIN_EMAIL}\",\"password\":\"${OPENWEBUI_ADMIN_PASSWORD}\",\"name\":\"RAG Watcher Admin\"}" 2>/dev/null || echo "")

    if echo "${SIGNUP_RESP}" | grep -q '"token"'; then
        echo "Watcher admin created successfully."
    else
        echo "WARNING: Could not create watcher admin. Response: ${SIGNUP_RESP}"
        echo "This may be OK if signup is disabled and the account was created manually."
    fi
fi

# -------------------------------------------------------
# Step 3: Login to OpenProdoc REST API
# -------------------------------------------------------
echo ""
echo "--- Logging in to OpenProdoc REST API ---"

LOGIN_RESP=$(curl -sf -X PUT "${OPENPRODOC_URL}/ProdocWeb2/APIRest/session" \
    -H "Content-Type: application/json" \
    -d "{\"Name\":\"${OPD_ROOT_USER}\",\"Password\":\"${OPD_ROOT_PASSWORD}\"}" 2>/dev/null || echo "")

if [ -z "${LOGIN_RESP}" ]; then
    echo "ERROR: Could not connect to OpenProdoc REST API."
    echo "The API might be disabled or the server not fully started."
    echo "Falling back to SQL-only initialization (JAR must be uploaded manually)."

    # SQL-only fallback: insert tasks with a placeholder PDId
    # The admin will need to upload the JAR and update the Description fields
    echo ""
    echo "WARNING: Cannot upload JAR without REST API. Tasks will NOT be created."
    echo "Please upload the JAR manually and create tasks via the admin UI."
    exit 1
fi

# Extract token from response: {"Res":"OK","Token":"xxxx"}
OPD_TOKEN=$(echo "${LOGIN_RESP}" | sed 's/.*"Token":"\([^"]*\)".*/\1/')

if [ -z "${OPD_TOKEN}" ] || [ "${OPD_TOKEN}" = "${LOGIN_RESP}" ]; then
    echo "ERROR: Login failed. Response: ${LOGIN_RESP}"
    exit 1
fi

echo "Logged in to OpenProdoc (token: ${OPD_TOKEN:0:8}...)"

# -------------------------------------------------------
# Step 4: Upload JAR to OpenProdoc (System folder)
# -------------------------------------------------------
echo ""
echo "--- Uploading CustomTask JAR to OpenProdoc ---"

if [ ! -f "${JAR_PATH}" ]; then
    echo "ERROR: JAR file not found at ${JAR_PATH}"
    exit 1
fi

TODAY=$(date -u +%Y-%m-%d)
UPLOAD_RESP=$(curl -sf -X POST "${OPENPRODOC_URL}/ProdocWeb2/APIRest/documents" \
    -H "Authorization: Bearer ${OPD_TOKEN}" \
    -H "Content-Type: multipart/form-data" \
    -F "Binary=@${JAR_PATH}" \
    -F "Metadata={\"Name\":\"openprodoc-ragtask.jar\",\"Type\":\"PD_DOCS\",\"Idparent\":\"RootFolder\",\"Title\":\"RAG CustomTask\",\"DocDate\":\"${TODAY}\"}" 2>/dev/null || echo "")

if [ -z "${UPLOAD_RESP}" ]; then
    echo "ERROR: Upload failed — no response from server."
    exit 1
fi

# Extract PDId from response: {"Res":"OK","Msg":"Created=xxxx"}
# or plain: Created=xxxx
PDID=$(echo "${UPLOAD_RESP}" | sed -n 's/.*Created=\([^"]*\).*/\1/p')

if [ -z "${PDID}" ]; then
    echo "ERROR: Could not extract PDId from upload response: ${UPLOAD_RESP}"
    exit 1
fi

echo "JAR uploaded successfully. PDId=${PDID}"

# -------------------------------------------------------
# Step 5: Logout from OpenProdoc
# -------------------------------------------------------
curl -sf -X DELETE "${OPENPRODOC_URL}/ProdocWeb2/APIRest/session" \
    -H "Authorization: Bearer ${OPD_TOKEN}" \
    -H "Content-Type: application/json" >/dev/null 2>&1 || true

# -------------------------------------------------------
# Step 6: Insert task definitions via SQL
# -------------------------------------------------------
echo ""
echo "--- Inserting task definitions into OpenProdoc database ---"

DOC_DESC="${PDID}|openprodoc.ragtask.RAGEventDoc"
FOLD_DESC="${PDID}|openprodoc.ragtask.RAGEventFold"
CRON_DESC="${PDID}|openprodoc.ragtask.RAGSyncCron"
PDDATE=$(date -u +%Y%m%d%H%M%S)

# Event tasks for documents (TaskType=210 = CUSTOM_DOC)
# evenorder=2 because built-in full-text index tasks use evenorder=1
echo "Creating document event tasks..."
run_sql "
INSERT INTO pd_tasksdefeven
    (name, category, description, tasktype, objtype, objfilter,
     taskparam, taskparam2, taskparam3, taskparam4,
     active, transact, pdautor, pddate, eventype, evenorder)
VALUES
    ('RAG_DocIns', '', '${DOC_DESC}', 210, 'PD_DOCS', '',
     '${OPENWEBUI_URL}', '${OPENWEBUI_ADMIN_EMAIL}', '${OPENWEBUI_ADMIN_PASSWORD}', '',
     1, 0, 'root', '${PDDATE}', 'INS', 2),
    ('RAG_DocUpd', '', '${DOC_DESC}', 210, 'PD_DOCS', '',
     '${OPENWEBUI_URL}', '${OPENWEBUI_ADMIN_EMAIL}', '${OPENWEBUI_ADMIN_PASSWORD}', '',
     1, 0, 'root', '${PDDATE}', 'UPD', 2),
    ('RAG_DocDel', '', '${DOC_DESC}', 210, 'PD_DOCS', '',
     '${OPENWEBUI_URL}', '${OPENWEBUI_ADMIN_EMAIL}', '${OPENWEBUI_ADMIN_PASSWORD}', '',
     1, 0, 'root', '${PDDATE}', 'DEL', 2);
"

# Event tasks for folders (TaskType=211 = CUSTOM_FOLD)
echo "Creating folder event tasks..."
run_sql "
INSERT INTO pd_tasksdefeven
    (name, category, description, tasktype, objtype, objfilter,
     taskparam, taskparam2, taskparam3, taskparam4,
     active, transact, pdautor, pddate, eventype, evenorder)
VALUES
    ('RAG_FoldIns', '', '${FOLD_DESC}', 211, 'PD_FOLDERS', '',
     '${OPENWEBUI_URL}', '${OPENWEBUI_ADMIN_EMAIL}', '${OPENWEBUI_ADMIN_PASSWORD}', '',
     1, 0, 'root', '${PDDATE}', 'INS', 1),
    ('RAG_FoldUpd', '', '${FOLD_DESC}', 211, 'PD_FOLDERS', '',
     '${OPENWEBUI_URL}', '${OPENWEBUI_ADMIN_EMAIL}', '${OPENWEBUI_ADMIN_PASSWORD}', '',
     1, 0, 'root', '${PDDATE}', 'UPD', 1),
    ('RAG_FoldDel', '', '${FOLD_DESC}', 211, 'PD_FOLDERS', '',
     '${OPENWEBUI_URL}', '${OPENWEBUI_ADMIN_EMAIL}', '${OPENWEBUI_ADMIN_PASSWORD}', '',
     1, 0, 'root', '${PDDATE}', 'DEL', 1);
"

# Cron task for user/group sync (TaskType=8 = TASK_CUSTOMDOC)
echo "Creating user/group sync cron task..."
run_sql "
INSERT INTO pd_tasksdefcron
    (name, category, description, tasktype, objtype, objfilter,
     taskparam, taskparam2, taskparam3, taskparam4,
     active, transact, pdautor, pddate,
     nextdate, addmonth, adddays, addhours, addmins)
VALUES
    ('RAG_Sync', '', '${CRON_DESC}', 8, 'PD_DOCS', '',
     '${OPENWEBUI_URL}', '${OPENWEBUI_ADMIN_EMAIL}', '${OPENWEBUI_ADMIN_PASSWORD}', '',
     1, 0, 'root', '${PDDATE}',
     '${PDDATE}', 0, 0, 0, ${SYNC_INTERVAL_MINS});
"

# -------------------------------------------------------
# Done
# -------------------------------------------------------
echo ""
echo "=== RAG CustomTask initialization complete ==="
echo "  JAR PDId:        ${PDID}"
echo "  Doc events:      RAG_DocIns, RAG_DocUpd, RAG_DocDel"
echo "  Fold events:     RAG_FoldIns, RAG_FoldUpd, RAG_FoldDel"
echo "  Cron task:       RAG_Sync (every 5 minutes)"
echo "  Watcher admin:   ${OPENWEBUI_ADMIN_EMAIL}"
echo ""
echo "Note: The core-engine will pick up these tasks on next session initialization."
echo "      No restart is required if no sessions have been created yet."

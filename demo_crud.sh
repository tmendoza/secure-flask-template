#!/usr/bin/env bash
set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────
KEYCLOAK_URL="http://localhost:8080"
REALM="dev"
CLIENT_ID="todo-svc"
USER="testuser"
PASS="testpass"

# No trailing slash here
API_BASE="http://localhost:5000/v1/todos"
CONTENT_HEADER="Content-Type: application/json"

# ─── 1) Fetch a Bearer token from Keycloak ────────────────────────────────────
echo "→ Fetching OIDC token from Keycloak..."
TOKEN=$(curl -s -X POST "${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=${CLIENT_ID}" \
  -d "username=${USER}" \
  -d "password=${PASS}" \
| jq -r .access_token)

echo "→ Got token: ${TOKEN:0:20}…"

# Helper for authenticated curl
_auth_curl() {
  curl -s -H "Authorization: Bearer $TOKEN" -H "$CONTENT_HEADER" "$@"
}

# ─── 2) CREATE ───────────────────────────────────────────────────────────────
echo
echo "→ Creating a new todo..."
CREATE_RESP=$(_auth_curl -X POST "${API_BASE}/" -d '{"title":"Test from script"}')
echo "   Response: $CREATE_RESP"

# Extract the new ID
TODO_ID=$(jq -r .id <<<"$CREATE_RESP")
echo "→ Created todo with ID = $TODO_ID"

# ─── 3) LIST ─────────────────────────────────────────────────────────────────
echo
echo "→ Listing all todos..."
_auth_curl "${API_BASE}/" | jq

# ─── 4) READ ─────────────────────────────────────────────────────────────────
echo
echo "→ Reading todo ${TODO_ID}..."
_auth_curl "${API_BASE}/${TODO_ID}" | jq

# ─── 5) UPDATE ───────────────────────────────────────────────────────────────
echo
echo "→ Marking todo ${TODO_ID} as completed..."
UPDATE_RESP=$(_auth_curl -X PATCH "${API_BASE}/${TODO_ID}" -d '{"completed":true}')
echo "   Response: $UPDATE_RESP"

# ─── 6) READ UPDATED ─────────────────────────────────────────────────────────
echo
echo "→ Reading updated todo ${TODO_ID}..."
_auth_curl "${API_BASE}/${TODO_ID}" | jq

# ─── 7) DELETE ───────────────────────────────────────────────────────────────
echo
echo "→ Deleting todo ${TODO_ID}..."
_auth_curl -X DELETE "${API_BASE}/${TODO_ID}"
echo "   Deleted."

# ─── 8) FINAL LIST ───────────────────────────────────────────────────────────
echo
echo "→ Final list of todos (should no longer include ID ${TODO_ID}):"
_auth_curl "${API_BASE}/" | jq

echo
echo "✅ CRUD demo complete."

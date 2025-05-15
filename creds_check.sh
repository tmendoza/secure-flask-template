#!/usr/bin/env bash
# Ensure these are set (or replace with literals)
KEYCLOAK_URL="http://localhost:8080"
REALM="dev"
CLIENT_ID="todo-svc"
USER="testuser"
PASS="testpass"

# Fetch and store the token
export TOKEN=$(
  curl -s -X POST "${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/token" \
       -H "Content-Type: application/x-www-form-urlencoded" \
       -d "grant_type=password" \
       -d "client_id=${CLIENT_ID}" \
       -d "username=${USER}" \
       -d "password=${PASS}" \
  | jq -r '.access_token'
)

echo "Got token: $TOKEN"

echo "Running curl test..."

curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/v1/todos/

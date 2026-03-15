#!/usr/bin/env bash
#
# Integration Smoke Test
#
# WHY THIS EXISTS:
# Unit tests mock system boundaries (database, auth, external APIs). Those tests pass
# even when the real integration is broken. This script tests the actual running services
# talking to each other. Run it after every implementation phase.
#
# EXTENDING THIS SCRIPT:
# Add new checks by calling the check() function. Each check tests one integration point.
# When adding new features (e.g., file uploads, webhooks), add a corresponding check.
#
# Usage: ./scripts/integration-smoke-test.sh
# Prerequisites: docker compose stack must be running (docker compose up -d)

set -euo pipefail

# --- Configuration ---
# [CUSTOMIZE] Update these URLs and endpoints to match your project.
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
TEST_EMAIL="smoketest-$(date +%s)@example.com"
TEST_PASSWORD="SmokeTest123!"

# --- Counters ---
PASS_COUNT=0
FAIL_COUNT=0
TOTAL_COUNT=0

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# --- Helper Functions ---

check() {
    # Usage: check "Test Name" "actual_value" "expected_value"
    local name="$1"
    local actual="$2"
    local expected="$3"
    TOTAL_COUNT=$((TOTAL_COUNT + 1))

    if [ "$actual" = "$expected" ]; then
        echo -e "  ${GREEN}PASS${NC}  $name"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo -e "  ${RED}FAIL${NC}  $name (expected: $expected, got: $actual)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

echo ""
echo "========================================"
echo "  Integration Smoke Test"
echo "========================================"
echo ""

# --- 1. Service Health ---
echo "--- Service Health ---"

# Backend health check
BACKEND_STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$BACKEND_URL/api/health" 2>/dev/null || echo "000")
check "Backend health endpoint" "$BACKEND_STATUS" "200"

# Frontend loads
FRONTEND_STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$FRONTEND_URL" 2>/dev/null || echo "000")
check "Frontend serves pages" "$FRONTEND_STATUS" "200"

# --- 2. Authentication ---
# [CUSTOMIZE] Adjust the auth endpoints and cookie handling to match your auth provider.
echo ""
echo "--- Authentication ---"

# Register a test user
REGISTER_RESPONSE=$(curl -s -w '\n%{http_code}' \
    -X POST "$FRONTEND_URL/api/auth/sign-up/email" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\", \"name\": \"Smoke Test\"}" \
    2>/dev/null || echo -e "\n000")
REGISTER_STATUS=$(echo "$REGISTER_RESPONSE" | tail -1)
check "User registration" "$REGISTER_STATUS" "200"

# Log in and capture session cookie
LOGIN_RESPONSE=$(curl -s -w '\n%{http_code}' -c /tmp/smoke-cookies.txt \
    -X POST "$FRONTEND_URL/api/auth/sign-in/email" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\"}" \
    2>/dev/null || echo -e "\n000")
LOGIN_STATUS=$(echo "$LOGIN_RESPONSE" | tail -1)
check "User login" "$LOGIN_STATUS" "200"

# Verify session cookie exists
if [ -f /tmp/smoke-cookies.txt ] && grep -q "session" /tmp/smoke-cookies.txt 2>/dev/null; then
    check "Session cookie set" "present" "present"
else
    check "Session cookie set" "missing" "present"
fi

# --- 3. CRUD Operations ---
# [CUSTOMIZE] Replace with your primary entity's CRUD endpoints.
echo ""
echo "--- CRUD Operations ---"

# Create a task
CREATE_RESPONSE=$(curl -s -w '\n%{http_code}' -b /tmp/smoke-cookies.txt \
    -X POST "$BACKEND_URL/api/tasks" \
    -H "Content-Type: application/json" \
    -d '{"title": "Smoke test task", "priority": "medium"}' \
    2>/dev/null || echo -e "\n000")
CREATE_STATUS=$(echo "$CREATE_RESPONSE" | tail -1)
CREATE_BODY=$(echo "$CREATE_RESPONSE" | head -n -1)
check "Create task" "$CREATE_STATUS" "201"

# Extract task ID from response (assumes JSON with "id" field)
TASK_ID=$(echo "$CREATE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null || echo "")

if [ -n "$TASK_ID" ]; then
    # Read the task
    READ_STATUS=$(curl -s -o /dev/null -w '%{http_code}' -b /tmp/smoke-cookies.txt \
        "$BACKEND_URL/api/tasks/$TASK_ID" 2>/dev/null || echo "000")
    check "Read task" "$READ_STATUS" "200"

    # Update the task
    UPDATE_STATUS=$(curl -s -o /dev/null -w '%{http_code}' -b /tmp/smoke-cookies.txt \
        -X PATCH "$BACKEND_URL/api/tasks/$TASK_ID" \
        -H "Content-Type: application/json" \
        -d '{"status": "in_progress"}' 2>/dev/null || echo "000")
    check "Update task" "$UPDATE_STATUS" "200"

    # Delete the task
    DELETE_STATUS=$(curl -s -o /dev/null -w '%{http_code}' -b /tmp/smoke-cookies.txt \
        -X DELETE "$BACKEND_URL/api/tasks/$TASK_ID" 2>/dev/null || echo "000")
    check "Delete task" "$DELETE_STATUS" "200"
else
    check "Read task" "skipped (no ID)" "200"
    check "Update task" "skipped (no ID)" "200"
    check "Delete task" "skipped (no ID)" "200"
fi

# --- 4. Page Load Checks ---
# [CUSTOMIZE] Add checks for every page in your application.
echo ""
echo "--- Page Loads ---"

declare -a PAGES=(
    "/,Home"
    "/dashboard,Dashboard"
    "/login,Login"
    "/register,Register"
)

for page_entry in "${PAGES[@]}"; do
    IFS=',' read -r page_path page_name <<< "$page_entry"
    PAGE_STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$FRONTEND_URL$page_path" 2>/dev/null || echo "000")
    check "Page: $page_name" "$PAGE_STATUS" "200"
done

# --- 5. Authenticated API via Frontend Proxy ---
# [CUSTOMIZE] Verify that the frontend proxy forwards API calls correctly.
echo ""
echo "--- Frontend API Proxy ---"

PROXY_STATUS=$(curl -s -o /dev/null -w '%{http_code}' -b /tmp/smoke-cookies.txt \
    "$FRONTEND_URL/api/tasks?limit=1" 2>/dev/null || echo "000")
check "Frontend API proxy" "$PROXY_STATUS" "200"

# --- Cleanup ---
rm -f /tmp/smoke-cookies.txt

# --- Summary ---
echo ""
echo "========================================"
echo "  Results: $PASS_COUNT passed, $FAIL_COUNT failed (out of $TOTAL_COUNT)"
echo "========================================"
echo ""

if [ "$FAIL_COUNT" -gt 0 ]; then
    echo -e "${RED}SMOKE TEST FAILED${NC} -- fix failures before proceeding."
    exit 1
else
    echo -e "${GREEN}ALL CHECKS PASSED${NC}"
    exit 0
fi

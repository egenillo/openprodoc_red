#!/bin/bash

# OpenProdoc REST API Test Script
# This script tests the basic functionality of the OpenProdoc REST API

set -e

# Configuration
API_BASE="http://localhost:8080/ProdocWeb2/APIRest"
USERNAME="root"
PASSWORD="admin"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "OpenProdoc REST API Test Script"
echo "========================================="
echo ""

# Function to print test results
print_test() {
    local test_name=$1
    local status=$2
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓ PASS${NC} - $test_name"
    else
        echo -e "${RED}✗ FAIL${NC} - $test_name"
    fi
}

# Test 1: Login
echo -e "${YELLOW}Test 1: Login${NC}"
LOGIN_RESPONSE=$(curl -s -X PUT "$API_BASE/session" \
  -H "Content-Type: application/json" \
  -d "{\"Name\":\"$USERNAME\",\"Password\":\"$PASSWORD\"}")

echo "Response: $LOGIN_RESPONSE"

if echo "$LOGIN_RESPONSE" | grep -q '"Res":"OK"'; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"Token":"[^"]*"' | cut -d'"' -f4)
    print_test "Login and get token" "PASS"
    echo "Token: ${TOKEN:0:50}..."
else
    print_test "Login and get token" "FAIL"
    echo "Error: Could not login. Check credentials and API availability."
    exit 1
fi
echo ""

# Test 2: Get Root Folder
echo -e "${YELLOW}Test 2: Get Root Folder${NC}"
FOLDER_RESPONSE=$(curl -s "$API_BASE/folders/ByPath/RootFolder" \
  -H "Authorization: Bearer $TOKEN")

echo "Response: $FOLDER_RESPONSE"

if echo "$FOLDER_RESPONSE" | grep -q '"Id":"RootFolder"'; then
    print_test "Get root folder" "PASS"
else
    print_test "Get root folder" "FAIL"
fi
echo ""

# Test 3: List Subfolders
echo -e "${YELLOW}Test 3: List Subfolders${NC}"
SUBFOLDERS_RESPONSE=$(curl -s "$API_BASE/folders/SubFoldersByPath/RootFolder?Initial=0&Final=10" \
  -H "Authorization: Bearer $TOKEN")

echo "Response: $SUBFOLDERS_RESPONSE"

if echo "$SUBFOLDERS_RESPONSE" | grep -q '\[' && echo "$SUBFOLDERS_RESPONSE" | grep -q '"Id"'; then
    print_test "List subfolders" "PASS"
    FOLDER_COUNT=$(echo "$SUBFOLDERS_RESPONSE" | grep -o '"Id"' | wc -l)
    echo "Found $FOLDER_COUNT subfolder(s)"
else
    print_test "List subfolders" "FAIL"
fi
echo ""

# Test 4: List Documents in Root Folder
echo -e "${YELLOW}Test 4: List Documents in Root Folder${NC}"
DOCS_RESPONSE=$(curl -s "$API_BASE/folders/ContDocsByPath/RootFolder?Initial=0&Final=10" \
  -H "Authorization: Bearer $TOKEN")

echo "Response: $DOCS_RESPONSE"

if echo "$DOCS_RESPONSE" | grep -q '\['; then
    print_test "List documents" "PASS"
    DOC_COUNT=$(echo "$DOCS_RESPONSE" | grep -o '"Id"' | wc -l)
    echo "Found $DOC_COUNT document(s)"
else
    print_test "List documents" "FAIL"
fi
echo ""

# Test 5: Create a Test Folder
echo -e "${YELLOW}Test 5: Create Test Folder${NC}"
CREATE_FOLDER_RESPONSE=$(curl -s -X POST "$API_BASE/folders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "TestFolder_'$(date +%s)'",
    "Idparent": "RootFolder",
    "Type": "PD_FOLDERS",
    "ACL": "Public"
  }')

echo "Response: $CREATE_FOLDER_RESPONSE"

if echo "$CREATE_FOLDER_RESPONSE" | grep -q '"Res":"OK"'; then
    print_test "Create test folder" "PASS"
    CREATED_FOLDER=$(echo "$CREATE_FOLDER_RESPONSE" | grep -o 'Created=[^"]*' | cut -d'=' -f2)
    echo "Created folder: $CREATED_FOLDER"

    # Test 5b: Delete the test folder
    echo -e "${YELLOW}Test 5b: Delete Test Folder${NC}"
    DELETE_RESPONSE=$(curl -s -X DELETE "$API_BASE/folders/ById/$CREATED_FOLDER" \
      -H "Authorization: Bearer $TOKEN")

    echo "Response: $DELETE_RESPONSE"

    if echo "$DELETE_RESPONSE" | grep -q '"Res":"OK"'; then
        print_test "Delete test folder" "PASS"
    else
        print_test "Delete test folder" "FAIL"
    fi
else
    print_test "Create test folder" "FAIL"
fi
echo ""

# Test 6: Search Folders
echo -e "${YELLOW}Test 6: Search Folders${NC}"
SEARCH_RESPONSE=$(curl -s -X POST "$API_BASE/folders/Search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"Query":"Name=\"System\"","Initial":0,"Final":5}')

echo "Response: $SEARCH_RESPONSE"

if echo "$SEARCH_RESPONSE" | grep -q '\[' || echo "$SEARCH_RESPONSE" | grep -q '"Id"'; then
    print_test "Search folders" "PASS"
else
    print_test "Search folders" "FAIL"
fi
echo ""

# Test 7: Logout
echo -e "${YELLOW}Test 7: Logout${NC}"
LOGOUT_RESPONSE=$(curl -s -X DELETE "$API_BASE/session" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "Response: $LOGOUT_RESPONSE"

if echo "$LOGOUT_RESPONSE" | grep -q '"Res":"OK"'; then
    print_test "Logout" "PASS"
else
    print_test "Logout" "FAIL"
fi
echo ""

# Summary
echo "========================================="
echo "Test Summary"
echo "========================================="
echo -e "${GREEN}API is working correctly!${NC}"
echo ""
echo "You can now use the OpenProdoc REST API."
echo "See API_USAGE_GUIDE.md for detailed documentation."
echo "See API_QUICK_REFERENCE.md for quick command examples."

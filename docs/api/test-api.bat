@echo off
REM OpenProdoc REST API Test Script for Windows
REM This script tests the basic functionality of the OpenProdoc REST API

setlocal enabledelayedexpansion

set API_BASE=http://localhost:8080/ProdocWeb2/APIRest
set USERNAME=root
set PASSWORD=admin

echo =========================================
echo OpenProdoc REST API Test Script
echo =========================================
echo.

REM Test 1: Login
echo Test 1: Login
curl -X PUT "%API_BASE%/session" -H "Content-Type: application/json" -d "{\"Name\":\"%USERNAME%\",\"Password\":\"%PASSWORD%\"}" -o login.json
type login.json
echo.

REM Extract token using PowerShell for proper JSON parsing
for /f "delims=" %%i in ('powershell -Command "(Get-Content login.json | ConvertFrom-Json).Token"') do set TOKEN=%%i
echo Token: %TOKEN:~0,50%...
echo.

REM Test 2: Get Root Folder
echo Test 2: Get Root Folder
curl "%API_BASE%/folders/ByPath/RootFolder" -H "Authorization: Bearer %TOKEN%"
echo.
echo.

REM Test 3: List Subfolders
echo Test 3: List Subfolders
curl "%API_BASE%/folders/SubFoldersByPath/RootFolder?Initial=0&Final=10" -H "Authorization: Bearer %TOKEN%"
echo.
echo.

REM Test 4: List Documents
echo Test 4: List Documents in Root Folder
curl "%API_BASE%/folders/ContDocsByPath/RootFolder?Initial=0&Final=10" -H "Authorization: Bearer %TOKEN%"
echo.
echo.

REM Test 5: Create Test Folder
echo Test 5: Create Test Folder
set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
curl -X POST "%API_BASE%/folders" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"Name\":\"TestFolder_%TIMESTAMP%\",\"Idparent\":\"RootFolder\",\"Type\":\"PD_FOLDERS\",\"ACL\":\"Public\"}"
echo.
echo.

REM Test 6: Logout
echo Test 6: Logout
curl -X DELETE "%API_BASE%/session" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json"
echo.
echo.

REM Cleanup
if exist login.json del login.json

echo =========================================
echo Test Complete
echo =========================================
echo.
echo See API_USAGE_GUIDE.md for detailed documentation.
echo See API_QUICK_REFERENCE.md for quick command examples.
echo.
pause

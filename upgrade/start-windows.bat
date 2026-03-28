@echo off
setlocal

:: OpenProdoc Red — External Upgrade Start Script (Windows)
::
:: Usage:
::   start-windows.bat           Auto-detect GPU
::   start-windows.bat --light   Force CPU-light mode (alpine/ollama, ~70 MB)
::   start-windows.bat --cpu     Force standard CPU mode (ollama/ollama, ~3.86 GB)
::   start-windows.bat --nvidia  Force NVIDIA GPU mode

echo OpenProdoc Red - External Upgrade Start Script
echo.

set MODE=%~1

if "%MODE%"=="--light" goto :light
if "%MODE%"=="--cpu" goto :cpu
if "%MODE%"=="--nvidia" goto :nvidia

:: Auto-detect GPU
echo Detecting GPU...

nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo Detected GPU: NVIDIA
    goto :nvidia
)

:: No GPU detected — use CPU-light mode
echo Detected GPU: none
echo No GPU detected, using CPU-light mode (alpine/ollama ~70 MB)
echo Note: AMD ROCm GPU passthrough is only supported on Linux hosts.
goto :light

:light
echo Starting with CPU-light Ollama (alpine/ollama)...
docker compose -f docker-compose.yml -f docker-compose.cpu-light.yml up -d
goto :end

:nvidia
echo Starting with NVIDIA GPU support...
docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up -d
goto :end

:cpu
echo Starting with standard CPU Ollama (ollama/ollama)...
docker compose -f docker-compose.yml up -d
goto :end

:end
echo.
echo RAG services starting. Check status with: docker compose logs -f
echo Open WebUI will be available at: http://localhost:8082
endlocal

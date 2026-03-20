@echo off
setlocal

echo Detecting GPU...

:: Check for NVIDIA GPU
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo Detected GPU: NVIDIA
    docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up -d
    goto :end
)

:: No GPU detected on Windows (AMD ROCm is Linux-only in Docker)
echo Detected GPU: none (CPU mode)
echo Note: AMD ROCm GPU passthrough is only supported on Linux hosts.
docker compose -f docker-compose.yml up -d

:end
endlocal

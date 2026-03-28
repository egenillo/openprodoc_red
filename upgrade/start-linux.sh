#!/bin/bash
# OpenProdoc Red — External Upgrade Start Script (Linux)
#
# Usage:
#   ./start-linux.sh           Auto-detect GPU
#   ./start-linux.sh --light   Force CPU-light mode (alpine/ollama, ~70 MB)
#   ./start-linux.sh --cpu     Force standard CPU mode (ollama/ollama, ~3.86 GB)
#   ./start-linux.sh --nvidia  Force NVIDIA GPU mode
#   ./start-linux.sh --amd     Force AMD GPU mode

detect_gpu() {
  if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null; then
    echo "nvidia"
  elif ls /dev/kfd &>/dev/null; then
    echo "amd"
  else
    echo "cpu"
  fi
}

MODE="${1}"

if [ -z "$MODE" ]; then
  GPU=$(detect_gpu)
  echo "Detected GPU: $GPU"
  if [ "$GPU" = "cpu" ]; then
    MODE="--light"
    echo "No GPU detected, using CPU-light mode (alpine/ollama ~70 MB)"
  elif [ "$GPU" = "nvidia" ]; then
    MODE="--nvidia"
  elif [ "$GPU" = "amd" ]; then
    MODE="--amd"
  fi
fi

case $MODE in
  --light)
    echo "Starting with CPU-light Ollama (alpine/ollama)..."
    docker compose -f docker-compose.yml -f docker-compose.cpu-light.yml up -d
    ;;
  --nvidia)
    echo "Starting with NVIDIA GPU support..."
    docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up -d
    ;;
  --amd)
    echo "Starting with AMD GPU support (ROCm)..."
    docker compose -f docker-compose.yml -f docker-compose.amd.yml up -d
    ;;
  --cpu)
    echo "Starting with standard CPU Ollama (ollama/ollama)..."
    docker compose -f docker-compose.yml up -d
    ;;
  *)
    echo "Unknown option: $MODE"
    echo "Usage: $0 [--light|--cpu|--nvidia|--amd]"
    exit 1
    ;;
esac

echo ""
echo "RAG services starting. Check status with: docker compose logs -f"
echo "Open WebUI will be available at: http://localhost:8082"

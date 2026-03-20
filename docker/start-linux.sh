#!/bin/bash

detect_gpu() {
  if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null; then
    echo "nvidia"
  elif ls /dev/kfd &>/dev/null; then
    echo "amd"
  else
    echo "cpu"
  fi
}

GPU=$(detect_gpu)
echo "Detected GPU: $GPU"

case $GPU in
  nvidia)
    docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up -d
    ;;
  amd)
    docker compose -f docker-compose.yml -f docker-compose.amd.yml up -d
    ;;
  *)
    docker compose -f docker-compose.yml up -d
    ;;
esac

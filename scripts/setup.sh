#!/usr/bin/env bash
set -euo pipefail

command -v docker >/dev/null 2>&1 || { echo "Docker is required. Install Docker Engine first."; exit 1; }

echo "==> Starting Rishi AI services..."
docker compose up -d --build

echo "==> Downloading Qwen3 4B locally (first run may take a while)..."
docker exec rishi-ai-ollama ollama pull qwen3:4b

echo
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo "Rishi AI is ready."
echo "Local: http://localhost:8080"
[ -n "${IP:-}" ] && echo "LAN:   http://${IP}:8080"


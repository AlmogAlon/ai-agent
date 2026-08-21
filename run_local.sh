#!/usr/bin/env bash
# Run the agent directly on the host (not in Docker) for debugging.
# Redis still runs via docker-compose so state matches the containerized setup.
set -euo pipefail
cd "$(dirname "$0")"

docker compose up -d redis

source .venv/bin/activate
pip install --quiet -r requirements.txt

export REDIS_URL="redis://localhost:6379/0"
export OPENAI_MODEL="${OPENAI_MODEL:-gpt-5-mini}"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY must be set before running the agent." >&2
  exit 1
fi

uvicorn app.main:app --reload --host 0.0.0.0 --port "${PORT:-5002}"

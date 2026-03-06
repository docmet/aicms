#!/bin/sh
# Run DB migrations then start the server.
# Used as the production entrypoint so deployments always apply pending migrations.
set -e

echo "[startup] Running database migrations..."
uv run alembic upgrade head

echo "[startup] Seeding required data..."
uv run python seeds/seed_required.py

echo "[startup] Starting server..."
exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

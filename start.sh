#!/bin/bash
set -e

PORT=${PORT:-10000}

echo "=== Initializing Suvarna Nadi Web Application ==="
echo "Listening Port: $PORT"

exec uvicorn web_app.main:app --host 0.0.0.0 --port $PORT

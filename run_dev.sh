#!/usr/bin/env bash

# Set absolute paths to be safe
BASE_DIR=$(pwd)
VENV_PYTHON="$HOME/hlm_env/bin/python"

# 1. Start Backend
echo "Starting backend..."
(
    cd "$BASE_DIR/backend"
    export FLASK_ENV=development # Matching your VS Code config
    $VENV_PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8000
) &
BACKEND_PID=$!

# 2. Start Frontend
DETECTED_IP=$(hostname -I | awk '{print $1}')
echo "Detected Server IP: $DETECTED_IP"

# Pass it to the frontend build/dev process
# export VITE_BACKEND_URL="http://$DETECTED_IP:8000"
echo "Starting frontend..."
(
    cd "$BASE_DIR/frontend"
    npm run dev
) &
FRONTEND_PID=$!

# Cleanup on exit
trap "echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID" SIGINT SIGTERM

wait
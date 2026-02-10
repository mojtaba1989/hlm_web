#!/usr/bin/env bash

source ~/hlm_env/bin/activate

set -e

echo "Starting backend (FastAPI)..."
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Starting frontend (React)..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

trap "echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID" SIGINT SIGTERM

wait

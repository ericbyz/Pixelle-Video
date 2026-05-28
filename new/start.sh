#!/bin/bash
# Start both backend and frontend

echo "Starting Pixelle-Video..."

# Start backend
echo "Starting backend on port 8000..."
cd "$(dirname "$0")"
uv run python backend/main.py --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend on port 3000..."
cd frontend
npm run dev -- --port 3000 &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait

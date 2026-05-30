#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OLD_DIR="$REPO_DIR/old"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
BACKEND_ENTRY="$SCRIPT_DIR/backend/main.py"
BRIDGE_ENTRY="$SCRIPT_DIR/backend/bridge_server.mjs"
LOG_DIR="$SCRIPT_DIR/logs"

HOST="${HOST:-127.0.0.1}"
CHECK_HOST="${CHECK_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
UV_CACHE_DIR="${UV_CACHE_DIR:-/private/tmp/uv-cache}"
SKIP_PORT_CLEANUP="${SKIP_PORT_CLEANUP:-0}"
BACKEND_MODE="${BACKEND_MODE:-auto}"

BACKEND_PID=""
FRONTEND_PID=""

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
}

stop_port() {
  local port="$1"

  if [ "$SKIP_PORT_CLEANUP" = "1" ]; then
    return 0
  fi

  local pids
  pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [ -z "$pids" ]; then
    return 0
  fi

  echo "Stopping existing process on port $port: $(echo "$pids" | tr '\n' ' ')"
  kill $pids 2>/dev/null || true

  for _ in 1 2 3 4 5; do
    sleep 1
    pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
    if [ -z "$pids" ]; then
      return 0
    fi
  done

  echo "Force stopping process on port $port: $(echo "$pids" | tr '\n' ' ')"
  kill -9 $pids 2>/dev/null || true

  sleep 1
  pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [ -n "$pids" ]; then
    echo "Port $port is still occupied: $(echo "$pids" | tr '\n' ' ')" >&2
    echo "Stop those processes manually or rerun with different FRONTEND_PORT/BACKEND_PORT." >&2
    exit 1
  fi
}

wait_for_url() {
  local name="$1"
  local url="$2"
  local pid="$3"
  local attempts="${4:-60}"
  local i

  for ((i = 1; i <= attempts; i++)); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi

    if ! kill -0 "$pid" 2>/dev/null; then
      echo "$name exited before it became ready." >&2
      return 1
    fi

    sleep 1
  done

  echo "$name did not become ready: $url" >&2
  return 1
}

start_backend() {
  if [ "$BACKEND_MODE" = "bridge" ]; then
    exec node "$BRIDGE_ENTRY"
  fi

  if [ -x "$OLD_DIR/.venv/bin/python" ]; then
    (
      cd "$SCRIPT_DIR"
      exec "$OLD_DIR/.venv/bin/python" "$BACKEND_ENTRY" --host "$HOST" --port "$BACKEND_PORT"
    )
    return
  fi

  if command -v uv >/dev/null 2>&1; then
    (
      cd "$OLD_DIR"
      exec env UV_CACHE_DIR="$UV_CACHE_DIR" uv run --no-sync python "$BACKEND_ENTRY" --host "$HOST" --port "$BACKEND_PORT"
    )
    return
  fi

  echo "No backend runtime found. Install uv or create old/.venv first." >&2
  exit 1
}

start_bridge_backend() {
  exec node "$BRIDGE_ENTRY"
}

ensure_frontend_deps() {
  if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "Installing frontend dependencies..."
    (
      cd "$FRONTEND_DIR"
      npm install
    )
  fi
}

cleanup() {
  trap - EXIT INT TERM
  echo ""
  echo "Stopping Pixelle-Video..."

  if [ -n "${FRONTEND_PID:-}" ]; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi

  if [ -n "${BACKEND_PID:-}" ]; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi

  if [ -n "${FRONTEND_PID:-}" ]; then
    wait "$FRONTEND_PID" 2>/dev/null || true
  fi

  if [ -n "${BACKEND_PID:-}" ]; then
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT
trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM

require_cmd curl
require_cmd npm
require_cmd node
if [ "$SKIP_PORT_CLEANUP" != "1" ]; then
  require_cmd lsof
fi

mkdir -p "$LOG_DIR"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"
: > "$BACKEND_LOG"
: > "$FRONTEND_LOG"

echo "Starting Pixelle-Video..."
echo "Logs:"
echo "  Backend:  $BACKEND_LOG"
echo "  Frontend: $FRONTEND_LOG"
echo ""

stop_port "$FRONTEND_PORT"
stop_port "$BACKEND_PORT"
ensure_frontend_deps

echo "Starting backend on $HOST:$BACKEND_PORT..."
start_backend > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

if ! wait_for_url "Backend" "http://$CHECK_HOST:$BACKEND_PORT/health" "$BACKEND_PID" 20; then
  echo ""
  echo "Backend did not start in direct mode. Falling back to the Node development bridge..."
  echo "" >> "$BACKEND_LOG"
  echo "----- Falling back to Node development bridge -----" >> "$BACKEND_LOG"

  if [ -n "${BACKEND_PID:-}" ]; then
    wait "$BACKEND_PID" 2>/dev/null || true
  fi

  start_bridge_backend >> "$BACKEND_LOG" 2>&1 &
  BACKEND_PID=$!

  wait_for_url "Backend bridge" "http://$CHECK_HOST:$BACKEND_PORT/health" "$BACKEND_PID" 60 || {
    echo ""
    echo "Backend log tail:"
    tail -n 120 "$BACKEND_LOG" || true
    exit 1
  }
fi

echo "Starting frontend on $HOST:$FRONTEND_PORT..."
(
  cd "$FRONTEND_DIR"
  BACKEND_HOST="$CHECK_HOST" \
  BACKEND_PORT="$BACKEND_PORT" \
  VITE_BACKEND_HOST="$CHECK_HOST" \
  VITE_BACKEND_PORT="$BACKEND_PORT" \
  npm run dev -- --host "$HOST" --port "$FRONTEND_PORT" --strictPort
) > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

wait_for_url "Frontend" "http://$CHECK_HOST:$FRONTEND_PORT/" "$FRONTEND_PID" 60 || {
  echo ""
  echo "Frontend log tail:"
  tail -n 80 "$FRONTEND_LOG" || true
  exit 1
}

echo ""
echo "Pixelle-Video is ready."
echo "Backend:  http://$CHECK_HOST:$BACKEND_PORT"
echo "Frontend: http://$CHECK_HOST:$FRONTEND_PORT"
echo ""
echo "Press Ctrl+C to stop both servers."

while true; do
  if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "Backend stopped unexpectedly. See $BACKEND_LOG" >&2
    exit 1
  fi

  if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
    echo "Frontend stopped unexpectedly. See $FRONTEND_LOG" >&2
    exit 1
  fi

  sleep 2
done

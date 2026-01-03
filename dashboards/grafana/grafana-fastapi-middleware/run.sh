#!/bin/bash

set -e

echo "FastAPI Grafana Middleware Service Manager"

# =============================================================================
# Configuration
# =============================================================================
PID_FILE="logs/pids.txt"
LOG_DIR="logs"
SERVICE_NAME="grafana_middleware"
VENV_PATH="venv/bin/activate"
START_CMD="uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload"

mkdir -p "$LOG_DIR"
touch "$PID_FILE"

# =============================================================================
# Utility Functions
# =============================================================================
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

is_running() {
    local pid=$1
    if [ -z "$pid" ]; then
        return 1
    fi
    kill -0 "$pid" 2>/dev/null
}

# =============================================================================
# Start Service
# =============================================================================
start_service() {
    local name=$1
    local cmd=$2
    local log_file="$LOG_DIR/${name}.log"

    # Check existing PID
    if grep -q "^${name}:" "$PID_FILE" 2>/dev/null; then
        local old_pid
        old_pid=$(grep "^${name}:" "$PID_FILE" | cut -d: -f2)

        if is_running "$old_pid"; then
            log "$name already running (PID: $old_pid)"
            return 0
        else
            log "Removing stale PID for $name"
            sed -i.bak "/^${name}:/d" "$PID_FILE"
        fi
    fi

    log "Starting $name..."
    source "$VENV_PATH"

    eval "PYTHONPATH=\"$PYTHONPATH\" $cmd >> $log_file 2>&1 &"
    local pid=$!

    echo "${name}:${pid}" >> "$PID_FILE"
    log "$name started successfully (PID: $pid)"
}

# =============================================================================
# Stop Service
# =============================================================================
stop_service() {
    local name=$1

    if ! grep -q "^${name}:" "$PID_FILE" 2>/dev/null; then
        log "$name is not running"
        return 0
    fi

    local pid
    pid=$(grep "^${name}:" "$PID_FILE" | cut -d: -f2)

    if is_running "$pid"; then
        log "Stopping $name (PID: $pid)..."
        kill "$pid"

        # Graceful shutdown wait
        for i in {1..10}; do
            if ! is_running "$pid"; then
                break
            fi
            sleep 1
        done

        # Force kill if needed
        if is_running "$pid"; then
            log "Force killing $name (PID: $pid)"
            kill -9 "$pid"
        fi
    else
        log "Process not running, cleaning PID"
    fi

    sed -i.bak "/^${name}:/d" "$PID_FILE"
    log "$name stopped"
}

# =============================================================================
# Status
# =============================================================================
status_service() {
    if ! grep -q "^${SERVICE_NAME}:" "$PID_FILE" 2>/dev/null; then
        echo "$SERVICE_NAME is NOT running"
        return
    fi

    local pid
    pid=$(grep "^${SERVICE_NAME}:" "$PID_FILE" | cut -d: -f2)

    if is_running "$pid"; then
        echo "$SERVICE_NAME is RUNNING (PID: $pid)"
    else
        echo "$SERVICE_NAME is NOT running (stale PID)"
    fi
}

# =============================================================================
# Command Handler
# =============================================================================
case "$1" in
    start)
        start_service "$SERVICE_NAME" "$START_CMD"
        ;;
    stop)
        stop_service "$SERVICE_NAME"
        ;;
    restart)
        stop_service "$SERVICE_NAME"
        sleep 2
        start_service "$SERVICE_NAME" "$START_CMD"
        ;;
    status)
        status_service
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

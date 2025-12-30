#!/bin/bash

echo "Starting FastAPI server..."

set -e

# Service configuration
PID_FILE="logs/pids.txt"
LOG_DIR="logs"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Start service (UNCHANGED)
start_service() {
    local name=$1
    local cmd=$2
    local log_file="$LOG_DIR/${name}.log"

    if [ -f "$PID_FILE" ] && grep -q "^${name}:" "$PID_FILE" 2>/dev/null; then
        local old_pid=$(grep "^${name}:" "$PID_FILE" | cut -d: -f2)
        if is_running "$old_pid"; then
            log "$name is already running (PID: $old_pid)"
            return 0
        fi
    fi

    log "Starting $name..."
    eval "PYTHONPATH=\"$PYTHONPATH\" $cmd >> $log_file 2>&1 &"
    local pid=$!
    echo "${name}:${pid}" >> "$PID_FILE"
    log "$name started (PID: $pid)"
}

# Activate virtual environment
source venv/bin/activate

# Start FastAPI
start_service "grafana_middleware" "uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload"

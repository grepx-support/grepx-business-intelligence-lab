#!/bin/bash

echo "Starting FastAPI server..."

set -e

# Activate virtual environment
source venv/Scripts/activate

# Start FastAPI
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 5000 \
  --reload

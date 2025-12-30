#!/bin/bash

echo "Starting FastAPI project setup..."

set -e  # stop on error

# Check Python
if ! command -v python &> /dev/null; then
  echo "Python is not installed"
  exit 1
fi

python --version

# Create virtual environment
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python -m venv venv
else
  echo "Virtual environment already exists"
fi

# Activate venv (Windows Git Bash)
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
if [ -f "requirements.txt" ]; then
  echo "Installing dependencies..."
  pip install -r requirements.txt
else
  echo "requirements.txt not found"
  exit 1
fi

# Validate .env
if [ ! -f ".env" ]; then
  echo ".env file not found"
  exit 1
fi

if ! grep -q "CONNECTION_STRING" .env; then
  echo "CONNECTION_STRING missing in .env"
  exit 1
fi

echo "Setup completed successfully"

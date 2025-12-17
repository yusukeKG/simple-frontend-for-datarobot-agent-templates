#!/bin/bash
set -e

echo "=== DataRobot Agent Chat Startup ==="
echo "Starting at: $(date)"
echo "Working directory: $(pwd)"
echo "PORT: ${PORT:-8080}"
echo "SCRIPT_NAME: ${SCRIPT_NAME:-/}"
echo "PYTHONPATH: ${PYTHONPATH}"

# Check Python
echo "Python version: $(python --version 2>&1)"
echo "Python location: $(which python)"

# Check files in current directory
echo "Listing current directory contents:"
ls -la

echo "Listing src directory:"
ls -la src/ || echo "No src directory"

# Install dependencies
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Set environment - use current working directory
export PYTHONPATH=$(pwd):${PYTHONPATH}

# Start application
echo "Starting Flask application..."
exec python -m src.backend.app

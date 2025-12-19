#!/bin/bash
set -e

echo "=== DataRobot Agent Chat Startup ==="
echo "Starting at: $(date)"
echo "Working directory: $(pwd)"
echo "PORT: ${PORT:-8080}"
echo "SCRIPT_NAME: ${SCRIPT_NAME:-/}"
echo "PYTHONPATH: ${PYTHONPATH}"

# Debug: Check DataRobot environment variables
echo "=== DataRobot Environment Variables ==="
echo "DATAROBOT_API_TOKEN: ${DATAROBOT_API_TOKEN:+[SET, length=$(echo -n $DATAROBOT_API_TOKEN | wc -c)]}"
echo "DATAROBOT_ENDPOINT: ${DATAROBOT_ENDPOINT:-[NOT SET]}"
echo "DATAROBOT_DEPLOYMENT_ID: ${DATAROBOT_DEPLOYMENT_ID:-[NOT SET]}"
echo "========================================"

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

# DataRobot環境では常にGunicornを使用
# working directoryが/opt/codeの場合はDataRobot環境と判定
if [ "$(pwd)" = "/opt/code" ]; then
    echo "Detected DataRobot environment (/opt/code)"
    export PRODUCTION_MODE=1
fi

echo "Runtime mode: PRODUCTION_MODE=${PRODUCTION_MODE:-0}"

# Start application
if [ "${PRODUCTION_MODE}" = "1" ]; then
    echo "Starting with Gunicorn (production mode)..."
    exec gunicorn \
        --bind 0.0.0.0:${PORT:-8080} \
        --workers 1 \
        --timeout 300 \
        --access-logfile - \
        --error-logfile - \
        src.backend.app:app
else
    echo "Starting with Flask development server..."
    exec python -m src.backend.app
fi

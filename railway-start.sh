#!/bin/bash

# Railway start script for XSEMA
# This script handles the PORT environment variable properly

# Get the port from Railway environment variable
PORT=${PORT:-8000}

echo "Starting XSEMA on port $PORT"

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port $PORT

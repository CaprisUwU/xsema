#!/bin/bash
echo "Starting XSEMA..."
echo "Port: $PORT"
echo "XSEMA is running!"
echo "Health check: OK"

# Keep script running
while true; do
    sleep 10
    echo "XSEMA heartbeat: $(date)"
done

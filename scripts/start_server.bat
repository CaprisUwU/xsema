@echo off
set UVICORN_LOG_LEVEL=debug
set PYTHONUNBUFFERED=1

echo Starting server with debug logging...
python -u main.py > server.log 2>&1

echo.
echo Server stopped. Logs have been saved to server.log
type server.log

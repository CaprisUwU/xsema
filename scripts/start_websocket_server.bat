@echo off
echo Starting WebSocket Server on port 8001...
echo.
python minimal_ws_server.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Failed to start WebSocket server
    echo Make sure all required packages are installed:
    echo   pip install fastapi uvicorn websockets
)

pause

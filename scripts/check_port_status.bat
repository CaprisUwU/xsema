@echo off
echo Checking if port 8001 is in use...
python -c "import socket; exit(0 if socket.socket().connect_ex(('localhost', 8001)) == 0 else 1)"
if %ERRORLEVEL% EQU 0 (
    echo Port 8001 is in use
) else (
    echo Port 8001 is available
)
pause

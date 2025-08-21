@echo off
echo Finding all processes using port 8001...

:: First, list all processes using port 8001
netstat -ano | findstr :8001 > port_users.txt

if %ERRORLEVEL% NEQ 0 (
    echo No processes found using port 8001
    goto end
)

echo Found processes using port 8001:
type port_users.txt
echo.

:: Extract PIDs and stop each one
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    echo Attempting to stop process with PID: %%a
    taskkill /F /PID %%a
    if %ERRORLEVEL% EQU 0 (
        echo Successfully stopped process %%a
    ) else (
        echo Failed to stop process %%a
    )
    echo.
)

:end
del /q port_users.txt 2>nul
echo.
echo Verifying port 8001 status...
python -c "import socket; print('Port 8001 is', 'STILL IN USE' if socket.socket().connect_ex(('localhost', 8001)) == 0 else 'NOW AVAILABLE')"

pause

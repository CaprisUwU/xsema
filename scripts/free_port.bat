@echo off
echo ==================================================
echo Port 8000 Cleanup Tool
echo ==================================================

echo.
echo [1/3] Checking for processes using port 8000...
netstat -ano | findstr :8000 | findstr LISTENING >nul

if %ERRORLEVEL% EQU 0 (
    echo [INFO] Found process(es) using port 8000.
    echo.
    echo [2/3] Listing process details:
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
        set PID=%%a
        echo [INFO] Process found with PID: !PID!
        tasklist /FI "PID eq !PID!"
        
        echo.
        echo [3/3] Attempting to terminate process...
        taskkill /F /PID !PID! >nul 2>&1
        
        if %ERRORLEVEL% EQU 0 (
            echo [SUCCESS] Successfully terminated process with PID !PID!
        ) else (
            echo [ERROR] Failed to terminate process with PID !PID!
            echo [ADVICE] Try running this script as Administrator.
        )
    )
) else (
    echo [INFO] No processes found using port 8000.
)

echo.
echo ==================================================
echo Final check for port 8000:
netstat -ano | findstr :8000 | findstr LISTENING >nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Port 8000 is still in use!
) else (
    echo [SUCCESS] Port 8000 is now free!
)

echo.
echo Press any key to exit...
pause >nul

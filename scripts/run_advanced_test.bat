@echo off
cd /d "%~dp0"
echo 🚀 Running Advanced WebSocket Test...
echo This will test multiple WebSocket connections simultaneously
echo.
echo Usage: run_advanced_test.bat [num_clients] [duration_seconds]
echo Default: 3 clients for 10 seconds
echo.

set NUM_CLIENTS=3
set DURATION=10

if not "%~1"=="" set NUM_CLIENTS=%~1
if not "%~2"=="" set DURATION=%~2

echo Starting test with %NUM_CLIENTS% clients for %DURATION% seconds...
python test_ws_advanced.py %NUM_CLIENTS% %DURATION%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Test completed successfully!
) else (
    echo.
    echo ❌ Test failed or was interrupted.
)

pause

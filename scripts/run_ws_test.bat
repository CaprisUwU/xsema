@echo off
cd /d "%~dp0"
echo Running WebSocket test...
python test_ws_simple.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Test completed successfully!
) else (
    echo.
    echo ❌ Test failed. Check the error message above.
)
pause

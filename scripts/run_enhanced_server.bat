@echo off
setlocal enabledelayedexpansion

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup_environment.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .\venv\Scripts\activate

echo Installing minimal dependencies...
pip install -r minimal_requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Failed to install dependencies. Please check your Python environment.
    pause
    exit /b 1
)

echo.
echo Starting Enhanced WebSocket Server...
echo.
echo Server will be available at: ws://localhost:8001/ws/{client_id}
echo.
echo Press Ctrl+C to stop the server
echo.

python enhanced_ws_server.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Failed to start server. Please check the error above.
    echo Make sure all dependencies are installed by running:
    echo pip install -r requirements-updated.txt
    echo.
)

pause

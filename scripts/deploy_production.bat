@echo off
setlocal enabledelayedexpansion

echo ===================================
echo  NFT Event Streaming API - Production Deployment
echo ===================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python is installed

:: Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment exists
)

:: Activate virtual environment
call venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment activated

:: Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements-updated.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from .env.production...
    copy /y .env.production .env >nul
    echo ✓ .env file created
    echo ⚠️ Please edit the .env file with your configuration
) else (
    echo ✓ .env file exists
)

echo.
echo Starting NFT Event Streaming API in production mode...
echo Press Ctrl+C to stop the server
echo.

:: Start the server
python production_server.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Failed to start the server
    echo Check the logs directory for more information
    pause
    exit /b 1
)

@echo off
setlocal enabledelayedexpansion

echo ===================================
echo  Setting Up Python Environment
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

:: Create virtual environment if it doesn't exist
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
    echo ✓ Virtual environment already exists
)

:: Activate virtual environment
call venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment activated

echo.
echo ===================================
echo  Installing Dependencies
echo ===================================
echo.

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to upgrade pip
    pause
    exit /b 1
)

echo ✓ pip upgraded

:: Install requirements
echo Installing dependencies from requirements-updated.txt...
pip install -r requirements-updated.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install dependencies
    echo.
    echo Trying with --user flag...
    pip install --user -r requirements-updated.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install dependencies with --user flag
        pause
        exit /b 1
    )
)

echo ✓ Dependencies installed successfully

echo.
echo ===================================
echo  Environment Setup Complete!
echo ===================================
echo.
echo To activate the environment in a new terminal, run:
echo    .\venv\Scripts\activate
echo.
echo To start the server, run:
echo    run_enhanced_server.bat
echo.
pause

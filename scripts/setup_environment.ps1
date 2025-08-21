<#
.SYNOPSIS
    Sets up a clean Python virtual environment and installs all dependencies.
.DESCRIPTION
    This script creates a new virtual environment, activates it, and installs all
    required dependencies from requirements.txt. It also verifies the installation
    and provides instructions for running the server.
#>

# Stop on first error
$ErrorActionPreference = "Stop"

# Configuration
$venvName = "venv"
$requirementsFile = "requirements.txt"
$pythonVersion = "3.11"  # Using a stable Python version

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[✓] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "[✗] ERROR: $Message" -ForegroundColor Red
    exit 1
}

# Check if Python is installed
try {
    $pythonVersionOutput = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Python is not installed or not in PATH. Please install Python $pythonVersion or later."
    }
    Write-Step "Found Python: $pythonVersionOutput"
} catch {
    Write-Error "Failed to check Python version: $_"
}

# Create virtual environment
Write-Step "Creating virtual environment '$venvName'..."
if (Test-Path $venvName) {
    Write-Host "Virtual environment already exists. Removing it..."
    Remove-Item -Recurse -Force $venvName
}

python -m venv $venvName
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create virtual environment"
}
Write-Success "Virtual environment created successfully"

# Activate virtual environment
Write-Step "Activating virtual environment..."
$activateScript = ".\$venvName\Scripts\Activate.ps1"
if (-Not (Test-Path $activateScript)) {
    Write-Error "Failed to find activation script: $activateScript"
}

# Import the activation script to modify the current session
. $activateScript
Write-Success "Virtual environment activated"

# Upgrade pip
Write-Step "Upgrading pip..."
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to upgrade pip"
}
Write-Success "pip upgraded to the latest version"

# Install dependencies
if (-Not (Test-Path $requirementsFile)) {
    Write-Error "Requirements file not found: $requirementsFile"
}

Write-Step "Installing dependencies from $requirementsFile..."
python -m pip install -r $requirementsFile
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies"
}
Write-Success "Dependencies installed successfully"

# Verify installation
Write-Step "Verifying installation..."
try {
    $installed = python -m pip list
    Write-Success "Installed packages:`n$installed"
} catch {
    Write-Error "Failed to verify installation: $_"
}

# Print success message and next steps
Write-Host "`n" -NoNewline
Write-Host "=" * 60 -ForegroundColor Green
Write-Host " ENVIRONMENT SETUP COMPLETE " -BackgroundColor Green -ForegroundColor Black
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "`nTo activate this virtual environment in the future, run:"
Write-Host "    .\$venvName\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "`nTo start the server, run:"
Write-Host "    python -m uvicorn portfolio.main:app --host 0.0.0.0 --port 8001 --reload" -ForegroundColor Yellow
Write-Host "`nTo deactivate the virtual environment when done, run:"
Write-Host "    deactivate" -ForegroundColor Yellow
Write-Host "`n" -NoNewline
Write-Host "=" * 60 -ForegroundColor Green

# Check if we should start the server
$startServer = Read-Host "Do you want to start the server now? (y/N)"
if ($startServer -eq 'y' -or $startServer -eq 'Y') {
    Write-Step "Starting server..."
    python -m uvicorn portfolio.main:app --host 0.0.0.0 --port 8001 --reload
} else {
    Write-Host "`nServer not started. You can start it later with:"
    Write-Host "    python -m uvicorn portfolio.main:app --host 0.0.0.0 --port 8001 --reload" -ForegroundColor Yellow
}

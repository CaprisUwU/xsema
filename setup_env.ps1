# Setup Python Virtual Environment Script
# This script will create and configure a new Python virtual environment

# Create new virtual environment
Write-Host "Creating new virtual environment..." -ForegroundColor Green
python -m venv venv

# Activate the virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

# Upgrade pip and setuptools
Write-Host "`nUpgrading pip and setuptools..." -ForegroundColor Green
python -m pip install --upgrade pip setuptools wheel

# Install requirements
if (Test-Path "requirements.txt") {
    Write-Host "`nInstalling requirements from requirements.txt..." -ForegroundColor Green
    pip install -r requirements.txt
} else {
    Write-Host "`nrequirements.txt not found. Installing core dependencies..." -ForegroundColor Yellow
    pip install fastapi uvicorn pydantic python-dotenv websockets
    pip install pandas numpy python-multipart
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "`nCreating .env file from .env.example..." -ForegroundColor Green
    if (Test-Path ".env.example") {
        Copy-Item -Path ".env.example" -Destination ".env"
        Write-Host "Please edit the .env file with your configuration" -ForegroundColor Yellow
    } else {
        Write-Host "No .env.example found. Please create a .env file manually." -ForegroundColor Red
    }
}

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Green
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"
python -c "import uvicorn; print(f'Uvicorn version: {uvicorn.__version__}')"
python -c "import pandas as pd; print(f'Pandas version: {pd.__version__}')"

Write-Host "`nEnvironment setup complete!" -ForegroundColor Green
Write-Host "To activate the environment, run: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "To start the server, run: python -m uvicorn main:app --reload" -ForegroundColor Cyan

# Fix Pydantic Installation Script
# This script will reinstall pydantic and related packages with compatible versions

# Print current Python and pip versions
Write-Host "Python Version:" -ForegroundColor Green
python --version
Write-Host "`nPip Version:" -ForegroundColor Green
pip --version

# Uninstall existing pydantic packages
Write-Host "`nUninstalling existing pydantic packages..." -ForegroundColor Yellow
pip uninstall -y pydantic pydantic-core pydantic-settings

# Install specific versions that work well together
Write-Host "`nInstalling pydantic and dependencies..." -ForegroundColor Yellow
pip install "pydantic>=2.0.0,<3.0.0" "pydantic-core>=2.0.0,<3.0.0" "pydantic-settings>=2.0.0,<3.0.0"

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Green
python -c "import pydantic; print(f'Pydantic version: {pydantic.__version__}'); import pydantic_core; print(f'Pydantic Core version: {pydantic_core.__version__}'); from pydantic_settings import BaseSettings; print('Pydantic Settings imported successfully')"

Write-Host "`nDone! Try running the server again with: python -m uvicorn main:app --reload" -ForegroundColor Green

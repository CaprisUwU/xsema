# PowerShell script to run check_env_simple.py and save output to a file
$outputFile = "env_check_ps_output.txt"
$pythonScript = ".\venv\Scripts\python.exe"
$scriptArgs = "check_env_simple.py"

# Run the Python script and capture output
$output = & $pythonScript $scriptArgs 2>&1

# Write output to file
$output | Out-File -FilePath $outputFile -Encoding utf8

# Display completion message
Write-Host "Environment check completed. Output saved to $outputFile"

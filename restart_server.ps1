# Stop any running Python processes that might be using the port
try {
    $process = Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
    if ($process) {
        Write-Host "Stopping existing FastAPI server (PID: $($process.Id))..."
        Stop-Process -Id $process.Id -Force
    }
} catch {
    Write-Host "No running FastAPI server found or error stopping process: $_"
}

# Start the FastAPI server
Write-Host "Starting FastAPI server..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "main.py"

# Wait a moment for the server to start
Start-Sleep -Seconds 2

# Check if the server is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ FastAPI server is running and healthy!"
        Write-Host "Access the API at: http://localhost:8000/api/v1"
    } else {
        Write-Host "❌ Server returned status code: $($response.StatusCode)"
        Write-Host $response.Content
    }
} catch {
    Write-Host "❌ Failed to connect to the FastAPI server. Error: $_"
    Write-Host "Check if the server started correctly and is accessible on port 8000."
}

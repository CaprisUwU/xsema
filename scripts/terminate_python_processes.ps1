# PowerShell script to terminate all Python processes using port 8001

# Display a header
Write-Host "=== Terminating Python Processes Using Port 8001 ===" -ForegroundColor Red

# Find all processes using port 8001
$processes = netstat -ano | findstr :8001 | ForEach-Object { 
    $parts = $_ -split '\s+' 
    $pid = $parts[-1]
    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($process -and $process.ProcessName -like "python*") {
        $process
    }
}

if ($processes) {
    Write-Host "Found the following Python processes using port 8001:" -ForegroundColor Yellow
    $processes | Format-Table Id, ProcessName, Path -AutoSize
    
    $confirm = Read-Host "Do you want to terminate these processes? (y/n)"
    if ($confirm -eq 'y') {
        foreach ($process in $processes) {
            try {
                Write-Host "Terminating process $($process.Id) ($($process.ProcessName))..." -ForegroundColor Yellow
                Stop-Process -Id $process.Id -Force -ErrorAction Stop
                Write-Host "Successfully terminated process $($process.Id)" -ForegroundColor Green
            } catch {
                Write-Host "Failed to terminate process $($process.Id): $_" -ForegroundColor Red
            }
        }
        
        # Verify the port is now available
        Write-Host "`n=== Verifying Port 8001 Status ===" -ForegroundColor Cyan
        $portInUse = netstat -ano | findstr :8001
        if ($portInUse) {
            Write-Host "Port 8001 is still in use. You may need to restart your computer to release the port." -ForegroundColor Red
        } else {
            Write-Host "Port 8001 is now available!" -ForegroundColor Green
        }
    } else {
        Write-Host "Process termination cancelled." -ForegroundColor Yellow
    }
} else {
    Write-Host "No Python processes found using port 8001." -ForegroundColor Green
    
    # Show all Python processes for reference
    Write-Host "`n=== All Running Python Processes ===" -ForegroundColor Cyan
    Get-Process python* -ErrorAction SilentlyContinue | Format-Table Id, ProcessName, Path -AutoSize
}

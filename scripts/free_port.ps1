# PowerShell script to free port 8000
Write-Host "=== Port 8000 Cleanup Tool ===" -ForegroundColor Cyan
Write-Host "`n[1/3] Checking for processes using port 8000..."

# Find the process using port 8000
$process = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | 
           Select-Object -ExpandProperty OwningProcess -First 1

if ($process) {
    $processInfo = Get-Process -Id $process -ErrorAction SilentlyContinue
    
    Write-Host "`n[2/3] Found process using port 8000:" -ForegroundColor Yellow
    Write-Host "Process ID: $($process)"
    Write-Host "Process Name: $($processInfo.ProcessName)"
    Write-Host "Process Path: $($processInfo.Path)"
    
    $confirm = Read-Host "`n[?] Do you want to terminate this process? (Y/N)"
    
    if ($confirm -eq 'Y' -or $confirm -eq 'y') {
        Write-Host "`n[3/3] Attempting to terminate process $process..." -ForegroundColor Yellow
        try {
            Stop-Process -Id $process -Force -ErrorAction Stop
            Write-Host "[SUCCESS] Process terminated successfully!" -ForegroundColor Green
        } catch {
            Write-Host "[ERROR] Failed to terminate process: $_" -ForegroundColor Red
            Write-Host "[ADVICE] Try running PowerShell as Administrator" -ForegroundColor Yellow
        }
    } else {
        Write-Host "`n[INFO] Process termination cancelled." -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[INFO] No processes found using port 8000." -ForegroundColor Green
}

# Final check
Write-Host "`n=== Final Check ===" -ForegroundColor Cyan
$finalCheck = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($finalCheck) {
    Write-Host "[WARNING] Port 8000 is still in use!" -ForegroundColor Red
} else {
    Write-Host "[SUCCESS] Port 8000 is now free!" -ForegroundColor Green
}

Write-Host "`nPress any key to exit..."
[Console]::ReadKey($true) | Out-Null

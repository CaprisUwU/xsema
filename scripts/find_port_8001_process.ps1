# PowerShell script to find and display information about the process using port 8001

# Display a header
Write-Host "=== Process Using Port 8001 ===" -ForegroundColor Cyan

# Find the process ID (PID) using the port
$processInfo = netstat -ano | findstr :8001

if ($processInfo) {
    # Extract the PID from the netstat output
    $processInfo = $processInfo -replace '\s+', ' ' -split ' '
    $pid = $processInfo[-1]
    
    # Get process details
    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
    
    if ($process) {
        Write-Host "Process ID (PID): $($process.Id)" -ForegroundColor Green
        Write-Host "Process Name: $($process.ProcessName)" -ForegroundColor Green
        Write-Host "Process Path: $($process.Path)" -ForegroundColor Green
        Write-Host "Command Line: $(Get-WmiObject Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine" -ForegroundColor Green
        
        Write-Host "`n=== Process Tree ===" -ForegroundColor Cyan
        Get-Process -Id $pid | Format-Table Id, ProcessName, Path -AutoSize
        
        Write-Host "`n=== Network Connections ===" -ForegroundColor Cyan
        netstat -ano | findstr $pid
    } else {
        Write-Host "Found process with PID $pid, but could not retrieve process details." -ForegroundColor Yellow
        Write-Host "This might be a system process or you may need elevated privileges." -ForegroundColor Yellow
    }
} else {
    Write-Host "No process found using port 8001." -ForegroundColor Green
}

Write-Host "`n=== All Python Processes ===" -ForegroundColor Cyan
Get-Process python* | Format-Table Id, ProcessName, Path -AutoSize

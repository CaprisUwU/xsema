# Force Free Port 8000 Script
# This script will find and terminate all processes using port 8000

# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Function to display colored messages
function Write-Status {
    param(
        [string]$Message,
        [string]$Status = "INFO"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    switch ($Status.ToUpper()) {
        "SUCCESS" { $color = "Green" }
        "WARNING" { $color = "Yellow" }
        "ERROR"   { $color = "Red" }
        default   { $color = "Cyan" }
    }
    
    Write-Host "[$timestamp] [$Status] $Message" -ForegroundColor $color
}

# Clear the screen and show header
Clear-Host
Write-Host "=== FORCE FREE PORT 8000 TOOL ===" -ForegroundColor Cyan
Write-Host "This script will find and terminate all processes using port 8000"
Write-Host "=" * 50

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Status -Message "This script requires administrator privileges. Please run as Administrator." -Status "ERROR"
    Write-Host "`nRight-click on the script and select 'Run as Administrator'`n" -ForegroundColor Yellow
    Pause
    exit 1
}

# Function to get process information
function Get-ProcessInfo {
    param($ProcessId)
    try {
        $process = Get-Process -Id $ProcessId -ErrorAction Stop
        return @{
            Name = $process.ProcessName
            Path = $process.Path
            StartTime = $process.StartTime
            CPU = "{0:N2}%" -f ($process.CPU * 100 / (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors)
            Memory = "{0:N2} MB" -f ($process.WorkingSet64 / 1MB)
        }
    } catch {
        return $null
    }
}

# Main execution
do {
    Write-Status -Message "Scanning for processes using port 8000..."
    $processes = @()
    
    # Find all processes using port 8000
    $connections = Get-NetTCPConnection -LocalPort 8000 -State Listen,Established -ErrorAction SilentlyContinue
    
    if ($connections) {
        foreach ($conn in $connections) {
            $processId = $conn.OwningProcess
            $processInfo = Get-ProcessInfo -ProcessId $processId
            
            if ($processInfo) {
                $processes += [PSCustomObject]@{
                    PID = $processId
                    Name = $processInfo.Name
                    Path = $processInfo.Path
                    StartTime = $processInfo.StartTime
                    CPU = $processInfo.CPU
                    Memory = $processInfo.Memory
                }
            } else {
                $processes += [PSCustomObject]@{
                    PID = $processId
                    Name = "Unknown"
                    Path = ""
                    StartTime = $null
                    CPU = ""
                    Memory = ""
                }
            }
        }
        
        # Display found processes
        Write-Status -Message "Found $($processes.Count) process(es) using port 8000:" -Status "WARNING"
        $processes | Format-Table -AutoSize | Out-String -Stream | ForEach-Object {
            Write-Host "  $_"
        }
        
        # Ask for confirmation
        $confirm = Read-Host "`nDo you want to terminate ALL these processes? (Y/N)"
        
        if ($confirm -eq 'Y' -or $confirm -eq 'y') {
            $killed = 0
            foreach ($proc in $processes) {
                try {
                    Stop-Process -Id $proc.PID -Force -ErrorAction Stop
                    Write-Status -Message "Terminated process $($proc.PID) ($($proc.Name))" -Status "SUCCESS"
                    $killed++
                } catch {
                    Write-Status -Message "Failed to terminate process $($proc.PID): $_" -Status "ERROR"
                }
            }
            
            Write-Status -Message "Successfully terminated $killed of $($processes.Count) processes" -Status "SUCCESS"
            
            # Wait a moment and check again
            Start-Sleep -Seconds 1
            $remaining = @(Get-NetTCPConnection -LocalPort 8000 -State Listen,Established -ErrorAction SilentlyContinue).Count
            
            if ($remaining -eq 0) {
                Write-Status -Message "Port 8000 is now free!" -Status "SUCCESS"
                $allCleared = $true
            } else {
                Write-Status -Message "Port 8000 is still in use by $remaining process(es)" -Status "WARNING"
                $allCleared = $false
            }
        } else {
            Write-Status -Message "Process termination cancelled by user" -Status "WARNING"
            $allCleared = $false
            break
        }
    } else {
        Write-Status -Message "No processes found using port 8000" -Status "SUCCESS"
        $allCleared = $true
    }
    
    if (-not $allCleared) {
        $retry = Read-Host "`nDo you want to scan again? (Y/N)"
    } else {
        $retry = 'N'
    }
    
} while ($retry -eq 'Y' -or $retry -eq 'y')

# Final check
Write-Host "`n=== FINAL STATUS ===" -ForegroundColor Cyan
$finalCheck = @(Get-NetTCPConnection -LocalPort 8000 -State Listen,Established -ErrorAction SilentlyContinue)
if ($finalCheck.Count -eq 0) {
    Write-Status -Message "Port 8000 is now free and ready to use!" -Status "SUCCESS"
} else {
    Write-Status -Message "Port 8000 is still in use by $($finalCheck.Count) process(es)" -Status "ERROR"
    Write-Status -Message "You may need to restart your computer to free the port" -Status "WARNING"
}

Write-Host "`nPress any key to exit..." -NoNewline
[Console]::ReadKey($true) | Out-Null

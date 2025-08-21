@echo off
echo Finding process using port 8001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do set PID=%%a

if "%PID%"=="" (
    echo No process found using port 8001
) else (
    echo Process with PID %PID% is using port 8001
    echo Attempting to terminate process...
    taskkill /F /PID %PID%
    if %ERRORLEVEL% EQU 0 (
        echo Successfully terminated process %PID%
    ) else (
        echo Failed to terminate process %PID%
    )
)
pause

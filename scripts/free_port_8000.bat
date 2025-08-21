@echo off
echo Finding process using port 8000...

REM Find the PID of the process using port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do set PID=%%a

if "%PID%"=="" (
    echo No process found using port 8000.
) else (
    echo Found process with PID %PID% using port 8000.
    echo Process details:
    tasklist /FI "PID eq %PID%"
    
    set /p KILL=Do you want to kill this process? (Y/N): 
    if /I "%KILL%"=="Y" (
        echo Killing process %PID%...
        taskkill /F /PID %PID%
        echo Process %PID% has been terminated.
    ) else (
        echo Process not killed.
    )
)

pause

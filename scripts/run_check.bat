@echo off
.\venv\Scripts\python.exe check_env_simple.py > env_check_output.txt 2>&1
echo Environment check completed. Output saved to env_check_output.txt

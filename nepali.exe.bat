@echo off
REM Fixed batch script that works from any directory

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Run the Python script with arguments
python "%SCRIPT_DIR%main.py" %*
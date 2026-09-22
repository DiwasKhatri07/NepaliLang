@echo off
REM NepaliLang runner wrapper
REM Calls main.py with Python

setlocal enabledelayedexpansion

if "%~1"=="" (
    python main.py
) else (
    python main.py "%~1"
)

exit /b !ERRORLEVEL!
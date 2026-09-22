@echo off
REM NepaliLang runner for VS Code
REM Handles file paths with spaces properly

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Usage: run_np.bat filename.np
    exit /b 1
)

set "FILE=%~1"
set "SCRIPT_DIR=%~dp0"

REM Try python main.py (most reliable fallback)
if exist "%SCRIPT_DIR%main.py" (
    python "%SCRIPT_DIR%main.py" "%FILE%"
    exit /b !ERRORLEVEL!
)

REM Try nepali.bat
if exist "%SCRIPT_DIR%nepali.bat" (
    call "%SCRIPT_DIR%nepali.bat" "%FILE%"
    exit /b !ERRORLEVEL!
)

REM Try nepali.exe (may be blocked by Windows security)
if exist "%SCRIPT_DIR%d nepali.exe" (
    "%SCRIPT_DIR%d nepali.exe" "%FILE%"
    exit /b !ERRORLEVEL!
)

echo Error: NepaliLang executable not found
echo Please ensure nepali.exe, nepali.bat, or main.py exists in the project directory
exit /b 1
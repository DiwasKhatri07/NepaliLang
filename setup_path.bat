@echo off
echo Adding NepaliLang to system PATH...
echo.

REM Get current directory
set "CURRENT_DIR=%~dp0"
REM Remove trailing backslash
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

echo Adding %CURRENT_DIR% to PATH...

REM Add to user PATH
setx PATH "%PATH%;%CURRENT_DIR%" /M

echo.
echo NepaliLang has been added to your system PATH.
echo Please restart your terminal or VS Code to use 'nepali' command from anywhere.
echo.
pause
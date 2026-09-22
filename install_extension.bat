@echo off
echo Installing NepaliLang VS Code Extension...
echo.

REM Check if vsce is installed
where vsce >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo vsce not found. Installing...
    call npm install -g @vscode/vsce
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install vsce. Please install Node.js first.
        pause
        exit /b 1
    )
)

echo Packaging extension...
cd vscode-extension
call vsce package
if %ERRORLEVEL% NEQ 0 (
    echo Failed to package extension.
    pause
    exit /b 1
)

echo.
echo Extension packaged successfully!
echo.
echo To install in VS Code:
echo 1. Open VS Code
echo 2. Go to Extensions
echo 3. Click the three dots menu
echo 4. Select "Install from VSIX..."
echo 5. Choose the nepalilang-*.vsix file
echo.
pause
@echo off
echo Installing NepaliLang VS Code Extension...
echo.

REM Check VS Code extensions directory
set "VSCODE_EXTENSIONS=%USERPROFILE%\.vscode\extensions"
if not exist "%VSCODE_EXTENSIONS%" (
    echo VS Code extensions directory not found.
    echo Please install VS Code first.
    pause
    exit /b 1
)

echo VS Code extensions directory: %VSCODE_EXTENSIONS%
echo.

REM Create extension folder
set "EXTENSION_DIR=%VSCODE_EXTENSIONS%\nepalilang-0.1.0"
if exist "%EXTENSION_DIR%" (
    echo Extension directory already exists. Removing old version...
    rmdir /s /q "%EXTENSION_DIR%"
)

echo Creating extension directory...
mkdir "%EXTENSION_DIR%"

REM Copy extension files
echo Copying extension files...
xcopy /E /I /Y "%~dp0*" "%EXTENSION_DIR%"

echo.
echo Installation complete!
echo.
echo Please restart VS Code to activate the extension.
echo.
echo After restart:
echo 1. Create a .np file
echo 2. You should see the NP logo
echo 3. Syntax highlighting should work
echo 4. Press F5 to run .np files
echo.
pause
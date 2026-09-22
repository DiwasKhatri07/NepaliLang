@echo off
echo ========================================
echo NepaliLang All-in-One Setup
echo ========================================
echo.

REM Step 1: Test Python
echo Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python first.
    pause
    exit /b 1
)
echo Python found!
echo.

REM Step 2: Test NepaliLang
echo Testing NepaliLang...
python main.py --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: NepaliLang test failed.
    pause
    exit /b 1
)
echo NepaliLang working!
echo.

REM Step 3: Add to PATH
echo Adding NepaliLang to system PATH...
powershell -Command "$env:Path = [System.Environment]::GetEnvironmentVariable('Path','User') + ';%CD%'; [System.Environment]::SetEnvironmentVariable('Path', $env:Path, 'User')"
echo Added to PATH!
echo.

REM Step 4: Install VS Code Extension
echo Installing VS Code extension...
cd vscode-extension
call INSTALL.bat
cd ..
echo VS Code extension installed!
echo.

REM Step 5: Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\NepaliCode.lnk'); $Shortcut.TargetPath = '%CD%\nepalicode.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'NepaliLang Editor'; $Shortcut.Save()"
echo Desktop shortcut created!
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo What's been installed:
echo 1. NepaliLang CLI (nepali.bat)
echo 2. NepaliCode Editor (nepalicode.bat)
echo 3. VS Code Extension
echo 4. Desktop Shortcut
echo 5. Added to system PATH
echo.
echo To use:
echo - Run from anywhere: nepali.bat yourfile.np
echo - Open editor: NepaliCode from desktop
echo - Use in VS Code: .np files will have NP logo
echo.
echo Please restart your terminal and VS Code for changes to take effect.
echo.
pause
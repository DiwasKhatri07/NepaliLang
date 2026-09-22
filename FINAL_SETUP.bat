@echo off
echo ========================================
echo NepaliLang Final Setup
echo ========================================
echo.

echo Step 1: Testing nepali.exe...
if exist nepali.exe (
    echo nepali.exe found!
    nepali.exe --version
) else (
    echo ERROR: nepali.exe not found.
    pause
    exit /b 1
)
echo.

echo Step 2: Adding to system PATH...
powershell -Command "$env:Path = [System.Environment]::GetEnvironmentVariable('Path','User') + ';%CD%'; [System.Environment]::SetEnvironmentVariable('Path', $env:Path, 'User')"
echo Added to PATH!
echo.

echo Step 3: Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\NepaliLang.lnk'); $Shortcut.TargetPath = '%CD%\nepali.exe'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'NepaliLang Programming Language'; $Shortcut.Save()"
echo Desktop shortcut created!
echo.

echo Step 4: Installing VS Code extension...
cd vscode-extension
call INSTALL.bat
cd ..
echo VS Code extension installed!
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo What's now available:
echo 1. nepali.exe - Standalone executable
echo 2. nepali.bat - Batch script wrapper
echo 3. Desktop shortcut - NepaliLang icon
echo 4. VS Code extension - NP logo + syntax highlighting
echo 5. System PATH - Use nepali from anywhere
echo.
echo To use:
echo - Double-click NepaliLang on desktop
echo - Run from anywhere: nepali.exe yourfile.np
echo - In VS Code: Create .np files (NP logo), press F5 to run
echo.
echo Please restart VS Code for extension changes.
echo.
pause
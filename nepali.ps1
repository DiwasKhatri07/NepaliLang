# NepaliLang PowerShell Script
param(
    [Parameter(Position=0)]
    [string]$FilePath
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "main.py"

if ($FilePath) {
    & python $PythonScript $FilePath
} else {
    & python $PythonScript
}
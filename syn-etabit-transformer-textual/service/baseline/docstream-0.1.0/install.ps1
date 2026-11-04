[CmdletBinding()]
param(
    [string]$PythonCommand = "py"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VirtualEnvironment = Join-Path $ProjectRoot ".venv"
$PythonExe = Join-Path $VirtualEnvironment "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $PythonExe)) {
    & $PythonCommand -m venv $VirtualEnvironment
}

& $PythonExe -m pip install --upgrade pip
& $PythonExe -m pip install $ProjectRoot

$DocstreamExe = Join-Path $VirtualEnvironment "Scripts\docstream.exe"
Write-Output "Installed Docstream: $DocstreamExe"
& $DocstreamExe --version


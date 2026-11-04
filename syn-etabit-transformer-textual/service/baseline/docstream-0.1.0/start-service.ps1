[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$DocumentRoot,
    [int]$Port = 8765,
    [string]$BindAddress = "127.0.0.1",
    [ValidateSet("auto", "pandoc", "native")]
    [string]$Backend = "auto",
    [string]$Pandoc
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$DocstreamExe = Join-Path $ProjectRoot ".venv\Scripts\docstream.exe"

if (-not (Test-Path -LiteralPath $DocstreamExe)) {
    throw "Docstream is not installed. Run .\install.ps1 first."
}

$Arguments = @(
    "serve",
    "--root", (Resolve-Path -LiteralPath $DocumentRoot).Path,
    "--host", $BindAddress,
    "--port", $Port,
    "--backend", $Backend
)
if ($Pandoc) {
    $Arguments += @("--pandoc", $Pandoc)
}

& $DocstreamExe @Arguments

# Development Startup Script
# Opens the main dev launcher in a separate PowerShell window

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$devScript = Join-Path $repoRoot "dev.ps1"

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", $devScript
)

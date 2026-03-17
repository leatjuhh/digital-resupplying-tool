$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "common.ps1")

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot "frontend"
$nodeExe = Resolve-NodeExecutable
$nextCli = Join-Path $frontendRoot "node_modules\next\dist\bin\next"

if (-not (Test-Path $nextCli)) {
    throw "Frontend dependencies ontbreken: $nextCli"
}

Push-Location $frontendRoot
try {
    & $nodeExe $nextCli dev --hostname 127.0.0.1 --port 3000
}
finally {
    Pop-Location
}

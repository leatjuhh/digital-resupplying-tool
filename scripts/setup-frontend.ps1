$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "common.ps1")

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot "frontend"
$npmExe = Resolve-NpmExecutable

Push-Location $frontendRoot
try {
    if ($npmExe -like "*.js") {
        $nodeExe = Resolve-NodeExecutable
        & $nodeExe $npmExe install
    }
    else {
        & $npmExe install
    }
}
finally {
    Pop-Location
}

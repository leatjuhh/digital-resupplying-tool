$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "common.ps1")

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot "frontend"
$nodeExe = Resolve-NodeExecutable
$nextCli = Join-Path $frontendRoot "node_modules\next\dist\bin\next"
$nextCacheDir = Join-Path $frontendRoot ".next"

if (-not (Test-Path $nextCli)) {
    throw "Frontend dependencies ontbreken: $nextCli"
}

# OneDrive Files On-Demand can mark .next artifacts as reparse points.
# Next.js then crashes during its own cleanup with EINVAL on readlink.
# Clearing the cache up front keeps local dev startup predictable.
if (Test-Path $nextCacheDir) {
    Write-Host "Frontend cache gevonden, opruimen voor schone dev-start..." -ForegroundColor Yellow
    try {
        Remove-Item -LiteralPath $nextCacheDir -Recurse -Force -ErrorAction Stop
    }
    catch {
        Write-Host "Standaard verwijdering van .next mislukte, fallback via cmd /c rd..." -ForegroundColor Yellow
        cmd /c "rd /s /q `"$nextCacheDir`""
        if (Test-Path $nextCacheDir) {
            throw "Kon frontend cache niet verwijderen: $nextCacheDir"
        }
    }
}

Push-Location $frontendRoot
try {
    & $nodeExe $nextCli dev --hostname 127.0.0.1 --port 3000
}
finally {
    Pop-Location
}

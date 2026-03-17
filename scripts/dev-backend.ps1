$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot "backend\venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    throw "Backend virtual environment ontbreekt: $pythonExe"
}

Push-Location (Join-Path $repoRoot "backend")
try {
    & $pythonExe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
}
finally {
    Pop-Location
}

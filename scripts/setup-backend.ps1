$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"

Push-Location $backendRoot
try {
    if (-not (Test-Path "venv\Scripts\python.exe")) {
        python -m venv venv
    }

    & ".\venv\Scripts\python.exe" -m pip install -r requirements.txt

    if (-not (Test-Path "database.db")) {
        & ".\venv\Scripts\python.exe" seed_database.py
    }
}
finally {
    Pop-Location
}

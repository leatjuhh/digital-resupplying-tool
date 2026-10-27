$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"

function Test-PythonCandidate {
    param([string[]]$CommandParts)

    # Een kandidaat is bruikbaar als hij daadwerkelijk draait EN Python 3.11+ is.
    # We controleren de exit-code expliciet: `py -3.13` op een machine zonder 3.13
    # print een fout maar levert (afhankelijk van PowerShell-versie) geen exception
    # op, dus alleen op exit-code vertrouwen is niet genoeg -> exit-code checken.
    try {
        Invoke-CommandParts -CommandParts $CommandParts -ExtraArgs @(
            "-c", "import sys; sys.exit(0 if sys.version_info[:2] >= (3, 11) else 1)"
        ) 2>$null | Out-Null
    }
    catch {
        return $false
    }
    return ($LASTEXITCODE -eq 0)
}

function Get-BootstrapPythonCommand {
    $candidates = @()
    if (Get-Command py -ErrorAction SilentlyContinue) {
        # Meerdere expliciete versies plus generieke selectors, zodat een
        # ontbrekende specifieke versie netjes doorvalt naar een aanwezige.
        $candidates += ,@("py", "-3.13")
        $candidates += ,@("py", "-3.12")
        $candidates += ,@("py", "-3.11")
        $candidates += ,@("py", "-3")
        $candidates += ,@("py")
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $candidates += ,@("python")
    }
    if (Get-Command python3 -ErrorAction SilentlyContinue) {
        $candidates += ,@("python3")
    }

    foreach ($candidate in $candidates) {
        if (Test-PythonCandidate -CommandParts $candidate) {
            return $candidate
        }
    }

    throw "Geen werkende Python 3.11+ gevonden om de backend-venv op te bouwen. Installeer Python 3.11 of nieuwer (bijv. 'winget install Python.Python.3.12' of via python.org, met 'Add to PATH')."
}

function Invoke-CommandParts {
    param(
        [string[]]$CommandParts,
        [string[]]$ExtraArgs = @()
    )

    $command = $CommandParts[0]
    $baseArgs = @()
    if ($CommandParts.Length -gt 1) {
        $baseArgs = $CommandParts[1..($CommandParts.Length - 1)]
    }

    & $command @baseArgs @ExtraArgs
}

function Test-VenvPython {
    param([string]$PythonExe)

    if (-not (Test-Path $PythonExe)) {
        return $false
    }

    try {
        & $PythonExe -c "import sys" | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

Push-Location $backendRoot
try {
    $venvPython = Join-Path $backendRoot "venv\Scripts\python.exe"

    if (-not (Test-VenvPython -PythonExe $venvPython)) {
        $venvPath = Join-Path $backendRoot "venv"
        if (Test-Path $venvPath) {
            $resolvedVenvPath = (Resolve-Path $venvPath).Path
            if ($resolvedVenvPath -ne $venvPath) {
                $venvPath = $resolvedVenvPath
            }

            if (-not $venvPath.StartsWith($backendRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
                throw "Veilige cleanup geweigerd: venv-pad valt buiten backend-root ($venvPath)."
            }

            Remove-Item -LiteralPath $venvPath -Recurse -Force
        }

        $pythonCommand = Get-BootstrapPythonCommand
        Invoke-CommandParts -CommandParts $pythonCommand -ExtraArgs @("-m", "venv", "venv")
    }

    & ".\venv\Scripts\python.exe" -m pip install -r requirements.txt

    if (-not (Test-Path "database.db")) {
        $previousPythonIoEncoding = $env:PYTHONIOENCODING
        try {
            $env:PYTHONIOENCODING = "utf-8"
            & ".\venv\Scripts\python.exe" seed_database.py
        }
        finally {
            $env:PYTHONIOENCODING = $previousPythonIoEncoding
        }
    }
}
finally {
    Pop-Location
}

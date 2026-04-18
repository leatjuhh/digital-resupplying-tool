$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"

function Get-BootstrapPythonCommand {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $candidates = @(
            @("py", "-3.13"),
            @("py", "-3"),
            @("py")
        )

        foreach ($candidate in $candidates) {
            try {
                Invoke-CommandParts -CommandParts $candidate -ExtraArgs @("-c", "import sys") | Out-Null
                return $candidate
            }
            catch {
            }
        }
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @("python")
    }

    throw "Geen werkende Python-installatie gevonden om de backend-venv opnieuw op te bouwen."
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

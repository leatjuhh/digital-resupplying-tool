function Resolve-NodeExecutable {
    $commands = @("node", "node.exe")
    foreach ($command in $commands) {
        $resolved = Get-Command $command -ErrorAction SilentlyContinue
        if ($resolved) {
            return $resolved.Source
        }
    }

    $candidates = @(
        (Join-Path $env:ProgramFiles "nodejs\node.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "nodejs\node.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\nodejs\node.exe"),
        "C:\Program Files\cursor\resources\app\resources\helpers\node.exe",
        "C:\Program Files\Cursor\resources\app\resources\helpers\node.exe"
    ) | Where-Object { $_ }

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    throw "Node.js niet gevonden. Installeer Node.js 20 LTS of voeg node.exe toe aan PATH."
}

function Resolve-NpmExecutable {
    $commands = @("npm.cmd", "npm", "npm.exe")
    foreach ($command in $commands) {
        $resolved = Get-Command $command -ErrorAction SilentlyContinue
        if ($resolved) {
            return $resolved.Source
        }
    }

    $nodePath = Resolve-NodeExecutable
    $nodeDir = Split-Path -Parent $nodePath
    $candidates = @(
        (Join-Path $nodeDir "npm.cmd"),
        (Join-Path $nodeDir "npm"),
        (Join-Path $nodeDir "node_modules\npm\bin\npm-cli.js")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    throw "npm niet gevonden. Installeer Node.js met npm of voeg npm.cmd toe aan PATH."
}

function Resolve-RepoRoot {
    param([string]$ScriptPath)

    return Split-Path -Parent (Split-Path -Parent $ScriptPath)
}

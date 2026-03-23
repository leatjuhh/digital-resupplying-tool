param(
    [switch]$Restart
)

# Digital Resupplying Tool - Smart Dev Launcher for Cursor
# Runs pre-flight checks then starts servers in current terminal

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "scripts\common.ps1")

# Colors
function Write-Color {
    param([string]$Text, [string]$Color = 'White', [switch]$NoNewline)
    Write-Host $Text -ForegroundColor $Color -NoNewline:$NoNewline
}

function Show-Header {
    Clear-Host
    $width = 60

    Write-Color ("=" * $width) 'Cyan'
    Write-Host ""
    Write-Color "  Digital Resupplying Tool - Dev Launcher" 'Cyan'
    Write-Host ""
    Write-Color ("=" * $width) 'Cyan'
    Write-Host ""
}

function Get-PortListeners {
    param([int]$Port)

    try {
        return @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
    }
    catch {
        return @()
    }
}

function Test-PortInUse {
    param([int]$Port)
    return (Get-PortListeners -Port $Port).Count -gt 0
}

function Get-ProcessesForPorts {
    param([int[]]$Ports)

    $processIds = New-Object System.Collections.Generic.HashSet[int]

    foreach ($port in $Ports) {
        foreach ($listener in (Get-PortListeners -Port $port)) {
            if ($listener.OwningProcess -gt 0) {
                [void]$processIds.Add([int]$listener.OwningProcess)
            }
        }
    }

    return @($processIds)
}

function Stop-ProcessesForPorts {
    param([int[]]$Ports)

    $processIds = Get-ProcessesForPorts -Ports $Ports

    if ($processIds.Count -eq 0) {
        return $true
    }

    Write-Host ""
    Write-Color " Restart requested: stopping processes on dev ports..." 'Yellow'

    foreach ($processId in $processIds) {
        try {
            $process = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
            if ($null -ne $process) {
                Write-Color "     Stopping PID " 'Yellow' -NoNewline
                Write-Color "$processId" 'Cyan' -NoNewline
                if ($process.Name) {
                    Write-Color " ($($process.Name))" 'Gray'
                }
                else {
                    Write-Host ""
                }
            }

            cmd /c "taskkill /PID $processId /T /F" | Out-Null
        }
        catch {
            Write-Color "     Failed to stop PID ${processId}: $($_.Exception.Message)" 'Red'
            return $false
        }
    }

    Start-Sleep -Seconds 2

    $remaining = Get-ProcessesForPorts -Ports $Ports
    if ($remaining.Count -gt 0) {
        Write-Color "     One or more dev ports are still in use after restart attempt." 'Red'
        return $false
    }

    Write-Color "     Existing dev servers stopped." 'Green'
    return $true
}

function Show-RestartHint {
    Write-Host ""
    Write-Color "     Tip: herstart direct vanuit dit script met " 'Yellow' -NoNewline
    Write-Color ".\dev.ps1 -Restart" 'Cyan'
}

function Show-PreflightChecks {
    Write-Color " Pre-flight Checks" 'Yellow'
    Write-Host ""

    # Check 1: Backend venv
    Write-Color "  [1] Backend Virtual Environment: " 'White' -NoNewline
    if (Test-Path "backend/venv/Scripts/activate.ps1") {
        Write-Color "OK" 'Green'
    }
    else {
        Write-Color "MISSING" 'Red'
        Write-Host ""
        Write-Color "     Run: " 'Yellow' -NoNewline
        Write-Color "npm run setup:backend" 'Cyan'
        return $false
    }

    # Check 2: Database
    Write-Color "  [2] Database: " 'White' -NoNewline
    if (Test-Path "backend/database.db") {
        Write-Color "OK" 'Green'
    }
    else {
        Write-Color "NOT INITIALIZED" 'Yellow'
        Write-Host ""
        Write-Color "     Initializing database..." 'Yellow'
        Write-Host ""

        Push-Location backend
        try {
            & .\venv\Scripts\python.exe seed_database.py
            Write-Color "     Database initialized!" 'Green'
        }
        catch {
            Write-Color "     Failed to initialize database!" 'Red'
            Pop-Location
            return $false
        }
        Pop-Location
        Write-Host ""
    }

    # Check 3: Frontend node_modules
    Write-Color "  [3] Frontend Dependencies: " 'White' -NoNewline
    if (Test-Path "frontend/node_modules/next/dist/bin/next") {
        Write-Color "OK" 'Green'
    }
    else {
        Write-Color "MISSING" 'Red'
        Write-Host ""
        Write-Color "     Run: " 'Yellow' -NoNewline
        Write-Color "npm run setup:frontend" 'Cyan'
        return $false
    }

    # Check 3b: Node executable
    Write-Color "  [3b] Node.js Runtime: " 'White' -NoNewline
    try {
        $script:NodeExe = Resolve-NodeExecutable
        Write-Color "OK" 'Green'
    }
    catch {
        Write-Color "MISSING" 'Red'
        Write-Host ""
        Write-Color "     $_" 'Yellow'
        return $false
    }

    # Check 4: Ports
    Write-Color "  [4] Port Availability: " 'White' -NoNewline
    $backendPort = Test-PortInUse -Port 8000
    $frontendPort = Test-PortInUse -Port 3000

    if ($backendPort -or $frontendPort) {
        if ($Restart) {
            Write-Color "RESTARTING" 'Yellow'
            $stopped = Stop-ProcessesForPorts -Ports @(8000, 3000)
            if (-not $stopped) {
                return $false
            }

            Write-Color "     Re-checking ports..." 'Yellow'
            $backendPort = Test-PortInUse -Port 8000
            $frontendPort = Test-PortInUse -Port 3000
            if ($backendPort -or $frontendPort) {
                Write-Color "     Ports are still in use" 'Red'
                return $false
            }

            Write-Color "     Ports cleared" 'Green'
        }
        else {
            Write-Color "IN USE" 'Red'
            Write-Host ""
            if ($backendPort) {
                Write-Color "     Port 8000 (Backend) is already in use" 'Red'
            }
            if ($frontendPort) {
                Write-Color "     Port 3000 (Frontend) is already in use" 'Red'
            }
            Write-Host ""
            Write-Color "     Stop running servers first" 'Yellow'
            Show-RestartHint
            return $false
        }
    }
    else {
        Write-Color "OK" 'Green'
    }

    Write-Host ""
    return $true
}

function Show-ServerInfo {
    Write-Host ""
    Write-Color " Server Information" 'Yellow'
    Write-Host ""
    Write-Color "  Backend:  " 'Cyan' -NoNewline
    Write-Host "http://localhost:8000"
    Write-Color "  API Docs: " 'Cyan' -NoNewline
    Write-Host "http://localhost:8000/docs"
    Write-Color "  Frontend: " 'Green' -NoNewline
    Write-Host "http://localhost:3000"
    Write-Host ""
    Write-Color " Logs" 'Yellow'
    Write-Host ""
    Write-Color "  [BACKEND]  " 'Cyan' -NoNewline
    Write-Host "Backend server logs"
    Write-Color "  [FRONTEND] " 'Green' -NoNewline
    Write-Host "Frontend server logs"
    Write-Host ""
    Write-Color ("=" * 60) 'Cyan'
    Write-Host ""
}

# Main execution
Show-Header

$checksOk = Show-PreflightChecks

if (-not $checksOk) {
    Write-Host ""
    Write-Color " Pre-flight checks failed. Fix the issues above first." 'Red'
    Write-Host ""
    exit 1
}

Write-Host ""
if ($Restart) {
    Write-Color " Restart completed. Starting fresh servers..." 'Green'
}
else {
    Write-Color " All checks passed! Starting servers..." 'Green'
}
Show-ServerInfo

Write-Color " Starting in 2 seconds..." 'Gray'
Start-Sleep -Seconds 2

# Start the servers using the local concurrently binary and PowerShell launchers
$concurrentlyCli = Join-Path $PSScriptRoot "node_modules\concurrently\dist\bin\concurrently.js"
if (-not (Test-Path $concurrentlyCli)) {
    Write-Host ""
    Write-Color " Missing dependency: node_modules/concurrently" 'Red'
    Write-Host ""
    Write-Color " Run: npm run setup:frontend" 'Yellow'
    exit 1
}

& $NodeExe $concurrentlyCli `
    "--names" "BACKEND,FRONTEND" `
    "--prefix-colors" "cyan,green" `
    "powershell -NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\scripts\dev-backend.ps1`"" `
    "powershell -NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\scripts\dev-frontend.ps1`""

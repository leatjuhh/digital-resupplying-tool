# Digital Resupplying Tool - Smart Dev Launcher for Cursor
# Runs pre-flight checks then starts servers in current terminal

$ErrorActionPreference = "Stop"

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

function Test-PortInUse {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        return $null -ne $connection
    }
    catch { return $false }
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
    if (Test-Path "frontend/node_modules") {
        Write-Color "OK" 'Green'
    }
    else {
        Write-Color "MISSING" 'Red'
        Write-Host ""
        Write-Color "     Run: " 'Yellow' -NoNewline
        Write-Color "npm run setup:frontend" 'Cyan'
        return $false
    }
    
    # Check 4: Ports
    Write-Color "  [4] Port Availability: " 'White' -NoNewline
    $backend_port = Test-PortInUse -Port 8000
    $frontend_port = Test-PortInUse -Port 3000
    
    if ($backend_port -or $frontend_port) {
        Write-Color "IN USE" 'Red'
        Write-Host ""
        if ($backend_port) {
            Write-Color "     Port 8000 (Backend) is already in use" 'Red'
        }
        if ($frontend_port) {
            Write-Color "     Port 3000 (Frontend) is already in use" 'Red'
        }
        Write-Host ""
        Write-Color "     Stop running servers first" 'Yellow'
        return $false
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
Write-Color " All checks passed! Starting servers..." 'Green'
Show-ServerInfo

Write-Color " Starting in 2 seconds..." 'Gray'
Start-Sleep -Seconds 2

# Start the servers using npm run dev (concurrently)
npm run dev

# Digital Resupplying Tool - Mobile Network Setup Script
# Configures the app for access from mobile devices on the same network

$ErrorActionPreference = "Stop"

function Write-Color {
    param([string]$Text, [string]$Color = 'White', [switch]$NoNewline)
    Write-Host $Text -ForegroundColor $Color -NoNewline:$NoNewline
}

function Show-Header {
    Clear-Host
    $line = "=" * 70
    Write-Color $line 'Cyan'
    Write-Host ""
    Write-Color "  Digital Resupplying Tool - Mobile Network Setup" 'Cyan'
    Write-Host ""
    Write-Color $line 'Cyan'
    Write-Host ""
}

function Get-LocalIPAddress {
    # Get the local IP address (excluding localhost)
    $adapters = Get-NetIPAddress -AddressFamily IPv4 | 
                Where-Object { $_.IPAddress -ne '127.0.0.1' -and $_.InterfaceAlias -notlike '*Loopback*' }
    
    # Prefer wireless or ethernet adapters
    $preferredAdapter = $adapters | 
                        Where-Object { $_.InterfaceAlias -like '*Wi-Fi*' -or $_.InterfaceAlias -like '*Ethernet*' } |
                        Select-Object -First 1
    
    if ($preferredAdapter) {
        return $preferredAdapter.IPAddress
    }
    
    # Fallback to any adapter
    if ($adapters) {
        return $adapters[0].IPAddress
    }
    
    return $null
}

Show-Header

Write-Color " Detecting network configuration..." 'Yellow'
Write-Host ""

$localIP = Get-LocalIPAddress

if (-not $localIP) {
    Write-Color " ERROR: Could not detect local IP address!" 'Red'
    Write-Host ""
    Write-Color " Make sure you're connected to a network." 'Yellow'
    Write-Host ""
    exit 1
}

Write-Color " Local IP Address: " 'Green' -NoNewline
Write-Color $localIP 'White'
Write-Host ""

# Update frontend .env.local
$envContent = @"
# Frontend Configuration
# Configured for mobile network access

NEXT_PUBLIC_API_URL=http://${localIP}:8000
"@

Write-Color " Updating frontend configuration..." 'Yellow'
Set-Content -Path "frontend/.env.local" -Value $envContent
Write-Color " ✓ frontend/.env.local updated" 'Green'
Write-Host ""

$separator = "=" * 70
Write-Color $separator 'Cyan'
Write-Host ""
Write-Color " Setup Complete!" 'Green'
Write-Host ""
Write-Color " Your app is now configured for mobile access." 'White'
Write-Host ""
Write-Color " Next Steps:" 'Yellow'
Write-Host ""
Write-Color "  1. Start the development servers:" 'White'
Write-Color "     .\dev.ps1" 'Cyan'
Write-Host ""
Write-Color "  2. On your iOS device, navigate to:" 'White'
Write-Color "     http://${localIP}:3000" 'Green'
Write-Host ""
Write-Color "  3. Make sure your iOS device is on the same network!" 'Yellow'
Write-Host ""
Write-Host " To switch back to localhost edit frontend/.env.local"
Write-Host ""
Write-Color $separator 'Cyan'
Write-Host ""

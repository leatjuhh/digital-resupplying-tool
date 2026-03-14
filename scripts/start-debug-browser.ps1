param(
    [string]$Url = "http://127.0.0.1:3000",
    [int]$Port = 9222,
    [string]$ProfileDir = ".browser-debug-profile"
)

$ErrorActionPreference = "Stop"

function Resolve-BrowserPath {
    $candidates = @(
        "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "C:\Program Files\Google\Chrome\Application\chrome.exe",
        "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    throw "Geen ondersteunde browser gevonden. Installeer Microsoft Edge of Google Chrome."
}

$projectRoot = Split-Path -Parent $PSScriptRoot
$resolvedProfileDir = Join-Path $projectRoot $ProfileDir
$browserPath = Resolve-BrowserPath

New-Item -ItemType Directory -Force -Path $resolvedProfileDir | Out-Null

$arguments = @(
    "--remote-debugging-port=$Port",
    "--user-data-dir=$resolvedProfileDir",
    "--new-window",
    $Url
)

Write-Host "Starting debug browser..." -ForegroundColor Cyan
Write-Host "Browser: $browserPath" -ForegroundColor White
Write-Host "Debug port: $Port" -ForegroundColor White
Write-Host "Profile: $resolvedProfileDir" -ForegroundColor White
Write-Host "URL: $Url" -ForegroundColor White

Start-Process -FilePath $browserPath -ArgumentList $arguments | Out-Null

Write-Host ""
Write-Host "Browser ready for remote debugging." -ForegroundColor Green
Write-Host "Next step: npm run browser:watch" -ForegroundColor Yellow

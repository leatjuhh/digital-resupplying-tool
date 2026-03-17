$ErrorActionPreference = "Stop"

& (Join-Path $PSScriptRoot "setup-backend.ps1")
& (Join-Path $PSScriptRoot "setup-frontend.ps1")

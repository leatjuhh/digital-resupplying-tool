# Test Auth Flow
Write-Host "=== TESTING AUTH FLOW ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Login
Write-Host "1. Testing login..." -ForegroundColor Yellow
$loginBody = "username=admin&password=Admin123!"
$loginResponse = curl -X POST "http://localhost:8000/api/auth/login" `
    -H "Content-Type: application/x-www-form-urlencoded" `
    -d $loginBody `
    2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "   Login response received" -ForegroundColor Green
    Write-Host $loginResponse
    
    # Parse token (simplified)
    $tokens = $loginResponse | ConvertFrom-Json
    $accessToken = $tokens.access_token
    
    Write-Host ""
    Write-Host "2. Testing /me endpoint..." -ForegroundColor Yellow
    $meResponse = curl -X GET "http://localhost:8000/api/auth/me" `
        -H "Authorization: Bearer $accessToken" `
        2>$null
    
    Write-Host $meResponse
} else {
    Write-Host "   Login failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== TEST COMPLETE ===" -ForegroundColor Cyan

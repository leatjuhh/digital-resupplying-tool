# Development Startup Script
# Starts both backend and frontend in separate windows

Write-Host "🚀 Starting Digital Resupplying Tool..." -ForegroundColor Green
Write-Host ""

# Check if backend database exists
if (-not (Test-Path "backend/database.db")) {
    Write-Host "⚠️  Database not found. Running seed script first..." -ForegroundColor Yellow
    
    # Start backend setup in same window
    Push-Location backend
    & .\venv\Scripts\activate
    python seed_database.py
    Pop-Location
    
    Write-Host "✓ Database initialized!" -ForegroundColor Green
    Write-Host ""
}

# Start Backend in new window
Write-Host "🔷 Starting Backend Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\venv\Scripts\activate; Write-Host '🔷 BACKEND SERVER' -ForegroundColor Cyan; Write-Host 'API: http://localhost:8000' -ForegroundColor Green; Write-Host 'Docs: http://localhost:8000/docs' -ForegroundColor Green; Write-Host ''; uvicorn main:app --reload --port 8000"

# Wait a bit for backend to start
Start-Sleep -Seconds 2

# Start Frontend in new window  
Write-Host "🟢 Starting Frontend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host '🟢 FRONTEND SERVER' -ForegroundColor Green; Write-Host 'App: http://localhost:3000' -ForegroundColor Cyan; Write-Host 'Test: http://localhost:3000/test' -ForegroundColor Cyan; Write-Host ''; npm run dev"

Write-Host ""
Write-Host "✅ Both servers starting in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 URLs:" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "To stop: Close the terminal windows or press Ctrl+C in each" -ForegroundColor Gray
Write-Host ""

# Quick Start Guide

## Starting the Development Servers

### Method 1: Using dev.ps1 (Recommended)

Simply run in your Cursor terminal:

```powershell
.\dev.ps1
```

**What it does:**
1. ✅ Checks if backend virtual environment exists
2. ✅ Checks if database is initialized (auto-initializes if needed)
3. ✅ Checks if frontend dependencies are installed
4. ✅ Checks if ports 8000 and 3000 are available
5. 🚀 Starts both servers in the **current Cursor terminal**

**Output:**
- All logs appear in the same terminal with color-coded prefixes:
  - `[BACKEND]` (cyan) - Backend server logs
  - `[FRONTEND]` (green) - Frontend server logs

### Method 2: Using npm (Alternative)

```bash
npm run dev
```

This skips the pre-flight checks and directly starts both servers.

### Method 3: Manual Split (Advanced)

If you want completely separate terminals for each server:

**Terminal 1 (Backend):**
```bash
npm run dev:backend
```

**Terminal 2 (Frontend):**
```bash
npm run dev:frontend
```

## Access URLs

After servers start:

- **Frontend Application:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Stopping Servers

Press `Ctrl+C` in the terminal where servers are running.

## First-Time Setup

If you haven't set up the project yet:

```bash
# Install all dependencies and initialize database
npm run setup

# Or step by step:
npm run setup:backend
npm run setup:frontend
```

## Troubleshooting

### "Port already in use"

**Problem:** Ports 8000 or 3000 are already occupied.

**Solution:**
```powershell
# Kill processes on port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force

# Kill processes on port 3000
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process -Force
```

### "Virtual environment not found"

**Problem:** Backend virtual environment is missing.

**Solution:**
```bash
npm run setup:backend
```

### "Database not found"

**Problem:** Database hasn't been initialized.

**Solution:**
The dev.ps1 script will automatically initialize it, or run manually:
```bash
cd backend
.\venv\Scripts\python.exe seed_database.py
```

### Backend fails to start with "call is not recognized"

**Problem:** Old scripts trying to use CMD syntax in PowerShell.

**Solution:** This has been fixed in the latest version. Make sure you're using:
- `.\dev.ps1` (uses npm run dev internally)
- `npm run dev` (fixed scripts)

## Why This Setup?

✅ **All logs visible in Cursor** - Both backend and frontend logs appear in your terminal, so Cline (AI assistant) can read error messages and help debug.

✅ **Pre-flight checks** - dev.ps1 validates everything before starting, preventing common startup issues.

✅ **Easy to use** - One command starts everything with proper initialization.

✅ **Color-coded output** - Easy to distinguish between backend and frontend logs.

# Development Management Guide

> 💡 **Voor de optimale Cursor workflow:** Zie **[[CURSOR_WORKFLOW]]** voor gedetailleerde instructies over hoe je de console combineert met aparte terminals voor volledige AI zichtbaarheid!

## Quick Start

### Methode 1: NPM Script (Aanbevolen voor Cursor) ⭐

Start de interactieve console direct vanuit Cursor:

```bash
npm run dev:console
```

**Voordelen:**
- Start direct vanuit Cursor terminal
- Interactieve status monitoring
- API testing & database checks
- Quick browser links

**Aanbevolen gebruik:**
- **Terminal 1:** `npm run dev:console` (monitoring)
- **Terminal 2:** `npm run dev:backend` (backend logs)
- **Terminal 3:** `npm run dev:frontend` (frontend logs)

**Waarom 3 terminals?** Zo kan zowel jij als de AI alle output zien en direct helpen bij errors!

📖 **Zie [[CURSOR_WORKFLOW]] voor complete setup instructies**

**Hoe te gebruiken in Cursor:**
1. Open terminal: `Ctrl + `` (backtick)
2. Type: `npm run dev:console`
3. De interactieve console start automatisch!

### Methode 2: Direct PowerShell

Start de console direct via PowerShell:

```powershell
.\dev.ps1
```

**Interactieve commando's in de console:**
- `1` of `start` - Start beide servers (opent 2 nieuwe terminal vensters)
- `2` of `stop` - Stop beide servers
- `3` of `restart` - Restart servers
- `4` of `test` - Test API endpoints
- `5` of `db` - Check database status
- `r` of `refresh` - Force refresh status
- `b/d/f/t` - Open browsers (Backend/Docs/Frontend/Test)
- `q` of `quit` - Sluit console

**Let op:** Wanneer je servers start, openen er 2 aparte PowerShell vensters:
- 🔷 **Backend Terminal** (Cyan) - Toont backend logs op poort 8000
- 🟢 **Frontend Terminal** (Green) - Toont frontend logs op poort 3000

Deze vensters blijven open zodat je real-time de server output kunt volgen en eventuele errors direct kunt zien.

## Commands

### Start
```powershell
.\dev.ps1 start
```
- Starts both backend (port 8000) and frontend (port 3000) servers
- Automatically initializes database if not present
- Opens separate terminal windows for each server
- Validates that servers started successfully
- Shows error messages if startup fails

### Status
```powershell
.\dev.ps1 status
```
- Shows real-time status of both servers
- Displays health check results
- Indicates if servers are RUNNING, STARTING, or STOPPED
- Detects unexpected process termination
- Alerts you to check terminal windows for errors

### Restart
```powershell
.\dev.ps1 restart
```
- Gracefully stops both servers
- Waits 2 seconds
- Starts both servers again
- Useful after making configuration changes

### Stop
```powershell
.\dev.ps1 stop
```
- Stops both backend and frontend servers
- Kills processes on ports 8000 and 3000
- Cleans up process tracking data

## Features

### ✅ Status Indicators

The script provides visual status indicators:

- 🟢 **RUNNING** - Server is running and responding
- 🟡 **STARTING** - Server is initializing
- 🔴 **STOPPED** - Server is not running
- ✅ **HEALTHY** - Server passed health check
- ⏳ **INITIALIZING** - Server is starting up

### ✅ Error Monitoring

The script monitors for errors and alerts you:

```
⚠️  IMPORTANT: Watch for error messages below
   If you see errors, the CLI needs to be checked!
```

Each terminal window displays:
- Clear server identification (Backend/Frontend)
- URLs and endpoints
- **Error warnings prominently displayed**
- Crash detection with error messages

### ✅ Process Tracking

The script tracks running processes to detect unexpected termination:

```
📝 Process Info:
   Started: 2025-10-31 21:00:00
   ⚠️  Backend process terminated unexpectedly
      💡 Check backend terminal for errors
```

### ✅ Port Conflict Detection

Prevents starting servers if ports are already in use:

```
⚠️  Servers already running!
```

### ✅ Database Initialization

Automatically initializes the database if missing:

```
⚠️  Database not found. Initializing...
✅ Database initialized!
```

## Terminal Windows

When you run `.\dev.ps1 start`, two separate PowerShell windows open:

### Backend Terminal (Blue)
```
═══════════════════════════════════════════════════════
  🔷 BACKEND SERVER - Digital Resupplying Tool
═══════════════════════════════════════════════════════

📍 API:  http://localhost:8000
📖 Docs: http://localhost:8000/docs

⚠️  IMPORTANT: Watch for error messages below
   If you see errors, the CLI needs to be checked!

═══════════════════════════════════════════════════════
```

### Frontend Terminal (Green)
```
═══════════════════════════════════════════════════════
  🟢 FRONTEND SERVER - Digital Resupplying Tool
═══════════════════════════════════════════════════════

🌐 App:  http://localhost:3000
🧪 Test: http://localhost:3000/test

⚠️  IMPORTANT: Watch for error messages below
   If you see errors, the CLI needs to be checked!

═══════════════════════════════════════════════════════
```

## Error Detection

### What to Watch For

The terminal windows will display:
- ❌ **Error codes** - Python/Node.js errors
- ⚠️ **Warnings** - Configuration issues
- 🔴 **Crashes** - Server crashes with stack traces

### When Errors Occur

1. **Check the terminal window** - Errors are displayed in real-time
2. **Run status command** - `.\dev.ps1 status` to check server health
3. **Read error messages** - They provide clues about what went wrong
4. **Fix the issue** - Address the error in your code
5. **Restart** - Use `.\dev.ps1 restart` to reload

### Common Errors

**Backend won't start:**
```
❌ Database initialization failed!
   💡 Check the error messages above
```
→ Check Python environment and database permissions

**Frontend won't start:**
```
Error: Cannot find module 'next'
```
→ Run `npm install` in the frontend directory

**Port already in use:**
```
⚠️  Servers already running!
```
→ Use `.\dev.ps1 stop` first, then `.\dev.ps1 start`

## URLs

### Backend
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Frontend
- Application: http://localhost:3000
- Test Page: http://localhost:3000/test

## Tips

### Monitor Server Health
Run status checks regularly:
```powershell
.\dev.ps1 status
```

### Keep Terminal Windows Open
Don't close the backend/frontend terminal windows - they show real-time logs and errors.

### Use Status Before Start
Always check status before starting:
```powershell
.\dev.ps1 status
.\dev.ps1 start
```

### Quick Restart After Changes
After making backend/frontend changes:
```powershell
.\dev.ps1 restart
```

### Stop Before Major Changes
Stop servers before making database schema changes:
```powershell
.\dev.ps1 stop
# Make your changes
.\dev.ps1 start
```

## Comparison with Old Method

### Old Method (start-dev.ps1)
- ✅ Simple to use
- ❌ No status checking
- ❌ No easy way to stop servers
- ❌ No restart functionality
- ❌ Manual port cleanup needed
- ❌ No error monitoring

### New Method (dev.ps1)
- ✅ Simple to use
- ✅ Real-time status checking
- ✅ Easy stop command
- ✅ One-command restart
- ✅ Automatic port cleanup
- ✅ Built-in error monitoring
- ✅ Process tracking
- ✅ Health checks

## Troubleshooting

### "Servers already running" but nothing responds
```powershell
.\dev.ps1 stop
.\dev.ps1 start
```

### Process tracking shows terminated processes
```powershell
# Check the terminal windows for error messages
.\dev.ps1 status

# Then restart
.\dev.ps1 restart
```

### Can't stop servers
```powershell
# Manually kill processes on ports
Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess | Stop-Process -Force
Get-NetTCPConnection -LocalPort 3000 | Select-Object -ExpandProperty OwningProcess | Stop-Process -Force
```

### Database issues
```powershell
# Reset database
cd backend
python reset_database.py
python seed_database.py
cd ..

# Start servers
.\dev.ps1 start
```

## System Requirements

- Windows PowerShell 5.1 or later
- Python 3.8+ with venv
- Node.js 16+ with npm
- Git (optional)

## Files Created

The script creates a tracking file:
- `.dev-processes.json` - Stores process IDs for monitoring

This file is automatically managed and can be safely deleted if needed.

## Legacy Script

The old `start-dev.ps1` script is still available if needed, but we recommend using the new `dev.ps1` script for better control and monitoring.

---

**Need Help?** Run `.\dev.ps1 help` for a quick reference guide.

# Cursor Development Workflow Guide

## 🎯 Aanbevolen Setup voor Development met AI Assistance

Deze gids beschrijft de optimale manier om te werken in Cursor, zodat zowel jij als de AI (Cline) volledige zichtbaarheid hebben op alle server output.

## 🚀 Quick Start: 3-Terminal Setup

### Terminal 1: Monitoring Console ⭐
```bash
npm run dev:console
```
**Wat doet het:**
- Interactieve management console
- Real-time status monitoring (auto-refresh elke 3 sec)
- Server control commands
- API testing tools
- Database checks
- Quick browser links

### Terminal 2: Backend Server
```bash
npm run dev:backend
```
**Wat doet het:**
- Start FastAPI backend op poort 8000
- Hot-reload enabled
- Volledige error output zichtbaar in Cursor
- AI kan meelezen en helpen bij errors

### Terminal 3: Frontend Server
```bash
npm run dev:frontend
```
**Wat doet het:**
- Start Next.js frontend op poort 3000
- Hot-reload enabled
- Volledige build output zichtbaar
- AI kan meelezen en helpen bij errors

## 📋 Stap-voor-Stap Setup

### 1. Open Cursor Terminal
`Ctrl + `` (backtick) of View → Terminal

### 2. Start Monitoring Console
```bash
npm run dev:console
```

Je ziet nu de interactieve console:
```
===============================================================================
  DIGITAL RESUPPLYING TOOL - DEVELOPMENT CONSOLE v2.0
===============================================================================

 BACKEND:  [STOPPED] Port 8000
 FRONTEND: [STOPPED] Port 3000
 DATABASE: [EXISTS] database.db

Commands: [1] Start | [2] Stop | [3] Restart | [4] API Test | [5] DB Check
Quick Links: [B] Backend | [D] Docs | [F] Frontend | [T] Test | [Q] Quit
```

### 3. Open Nieuwe Terminal Tab
`Ctrl + Shift + `` of klik op het + icoon

### 4. Start Backend
```bash
npm run dev:backend
```

Output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 5. Open Nog Een Terminal Tab
`Ctrl + Shift + ``

### 6. Start Frontend
```bash
npm run dev:frontend
```

Output:
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- Local: http://localhost:3000
```

### 7. Check Status in Console
Ga terug naar Terminal 1 (dev:console) en zie de status automatisch updaten:
```
 BACKEND:  [RUNNING] Port 8000 - HEALTHY ✅
 FRONTEND: [RUNNING] Port 3000 - HEALTHY ✅
```

## 🎨 Terminal Layout Voorbeeld

```
┌─────────────────────────────────────────────────────────┐
│ Terminal 1: npm run dev:console                         │
│ [Monitoring & Control - Interactieve commands]          │
├─────────────────────────────────────────────────────────┤
│ Terminal 2: npm run dev:backend                         │
│ [Backend logs - FastAPI/Uvicorn output]                 │
├─────────────────────────────────────────────────────────┤
│ Terminal 3: npm run dev:frontend                        │
│ [Frontend logs - Next.js build output]                  │
└─────────────────────────────────────────────────────────┘
```

## 💡 Console Commands (Terminal 1)

Terwijl de servers draaien in Terminal 2 & 3, kun je in Terminal 1:

| Command | Actie |
|---------|-------|
| `4` of `test` | Test alle API endpoints |
| `5` of `db` | Check database status |
| `r` of `refresh` | Force refresh status |
| `b` | Open backend in browser |
| `d` | Open API docs in browser |
| `f` | Open frontend in browser |
| `t` | Open test page in browser |
| `q` | Quit console (servers blijven draaien!) |

**Let op:** Commands `1` (start), `2` (stop), en `3` (restart) werken niet optimaal in deze setup omdat servers handmatig gestart zijn. Gebruik deze alleen als je servers via externe terminals wilt beheren.

## 🔄 Alternatieve Workflow: Alles in Eén Terminal

Als je liever alles in één terminal ziet:

```bash
npm run dev:all
```

of gewoon:

```bash
npm run dev
```

**Output:**
```
[BACKEND] INFO:     Uvicorn running on http://127.0.0.1:8000
[FRONTEND] - ready started server on 0.0.0.0:3000
[BACKEND] INFO:     Application startup complete
[FRONTEND] - Local: http://localhost:3000
```

**Voordelen:**
- ✅ Alles in één venster
- ✅ Beide servers met één commando

**Nadelen:**
- ❌ Output van beide servers gemixed
- ❌ Moeilijker om individuele server output te volgen
- ❌ Geen interactieve console voor management

## 🤖 Werken met AI (Cline)

### Waarom deze setup ideaal is:

1. **Volledige Zichtbaarheid**
   - AI kan alle terminal output zien
   - Direct helpen bij errors
   - Code suggesties gebaseerd op werkelijke output

2. **Interactieve Debugging**
   ```
   Jij: "Er is een error in de backend"
   AI: *leest Terminal 2*
   AI: "Ik zie een ImportError op regel 45. Laat me dat fixen..."
   ```

3. **Real-time Monitoring**
   - Console toont status
   - Terminals tonen details
   - AI heeft context van beide

### Best Practices:

**✅ DO:**
- Laat alle 3 terminals open tijdens development
- Gebruik console voor quick checks
- Bekijk backend/frontend terminals bij errors
- Tag @terminal2 of @terminal3 in Cline chat bij vragen

**❌ DON'T:**
- Sluit terminals niet af bij errors (AI kan output niet meer zien)
- Mix niet te veel output in één terminal
- Restart servers niet via console als ze handmatig gestart zijn

## 🛠️ Troubleshooting

### Server reageert niet
```bash
# Terminal 2 (Backend): Check output
# Als gestopt: Ctrl+C en herstart
npm run dev:backend
```

### Port al in gebruik
```bash
# Check wat er op de poort draait
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Stop het proces (gebruik PID uit output)
taskkill /PID <PID> /F

# Of gebruik console stop command
# In Terminal 1: Type "2" of "stop"
```

### Database errors
```bash
# Terminal 1 (Console): Type "5" of "db"
# Check database status

# Als needed:
cd backend
python seed_database.py
```

## 📚 NPM Scripts Overzicht

| Script | Commando | Gebruik |
|--------|----------|---------|
| `dev:console` | `npm run dev:console` | Monitoring console |
| `dev:backend` | `npm run dev:backend` | Backend alleen |
| `dev:frontend` | `npm run dev:frontend` | Frontend alleen |
| `dev:all` | `npm run dev:all` | Beide servers (gemixed) |
| `dev` | `npm run dev` | Alias voor dev:all |

## 🎯 Workflow Scenarios

### Scenario 1: Normale Development
```bash
Terminal 1: npm run dev:console    # Monitoring
Terminal 2: npm run dev:backend    # Backend logs
Terminal 3: npm run dev:frontend   # Frontend logs
```

### Scenario 2: Backend Development Focus
```bash
Terminal 1: npm run dev:backend    # Volledige focus
Terminal 2: npm run dev:console    # Quick status checks
# Frontend niet nodig
```

### Scenario 3: Quick Test
```bash
Terminal 1: npm run dev:all        # Alles in één keer
# Open browser, test, klaar
```

### Scenario 4: Debugging met AI
```bash
Terminal 1: npm run dev:console    # Status monitoring
Terminal 2: npm run dev:backend    # Error output hier
Terminal 3: npm run dev:frontend   # Build issues hier

# In chat: "@terminal2 er is een error, zie je wat er mis is?"
# AI leest Terminal 2 en helpt direct
```

## 📖 Meer Informatie

- **[[DEV_MANAGEMENT]]** - Volledige dev.ps1 console documentatie
- **[[GETTING_STARTED]]** - Eerste setup en installatie
- **[[TROUBLESHOOTING]]** - Veelvoorkomende problemen

---

**Pro Tip:** Gebruik Cursor's terminal splitting (rechtsklik op terminal → Split Terminal) om terminals naast elkaar te zien! 🚀

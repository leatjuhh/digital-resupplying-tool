---
tags: [documentation, getting-started, setup, tutorial]
type: guide
related: [[README]], [[BATCH_SYSTEM]], [[DATABASE]], [[TROUBLESHOOTING]]
---

# 🚀 Getting Started - Digital Resupplying Tool

Complete gids om de app te starten en te gebruiken.

> 💡 **Tip:** Zie [[README]] voor project overzicht

---

## 📋 Snelle Index

- [Voor Cursor Gebruikers](#cursor-method) ⭐ AANBEVOLEN
- [PowerShell Script Method](#powershell-method)
- [NPM Concurrently Method](#npm-method)
- [URLs & Endpoints](#urls)
- [Batch Systeem Testen](#testing)
- [Troubleshooting](#troubleshooting)

---

## <a id="cursor-method"></a>⭐ Voor Cursor Gebruikers (AANBEVOLEN)

Gebruik de **geïntegreerde terminal** van Cursor voor betere debugging en troubleshooting.

### Voordelen
✅ **Betere debugging** - Zie errors direct in Cursor  
✅ **AI hulp** - Cline kan meekijken met errors  
✅ **Overzichtelijk** - Tabs in plaats van losse vensters  
✅ **Copy/paste** - Makkelijk errors delen  

### Stap 1: Open 2 Terminals in Cursor
- Klik op "+" in terminal panel (of Ctrl+Shift+`)
- Je hebt nu 2 tabs in Cursor

### Stap 2: Terminal 1 - Backend
```powershell
cd backend
venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

**Je ziet:**
```
INFO: Started server process [...]
INFO: Application startup complete.
```

✅ Backend draait nu op **http://localhost:8000**

### Stap 3: Terminal 2 - Frontend  
```powershell
cd frontend
npm run dev
```

**Je ziet:**
```
- Local:        http://localhost:3000
```

✅ Frontend draait nu op **http://localhost:3000**

### Stap 4: Test (Optioneel - Terminal 3)
```powershell
cd backend
venv\Scripts\python.exe test_batch_api.py
```

### Stoppen
In elke terminal: **Ctrl+C**

---

## <a id="powershell-method"></a>📜 PowerShell Script Method

Opent 2 aparte vensters (buiten Cursor).

### Run Script:
**In Windows Explorer:**
- Ga naar project root folder
- Dubbelklik `start-dev.ps1`

**Of in terminal:**
```powershell
.\start-dev.ps1
```

### Wat gebeurt er:
1. ✅ Check of database bestaat (maakt aan als nodig)
2. 🔷 Start backend in nieuw venster (poort 8000)
3. 🟢 Start frontend in nieuw venster (poort 3000)
4. 📝 Toont alle URLs

### Resultaat:
- **2 terminal vensters** openen
- Backend venster: blauw, toont uvicorn logs
- Frontend venster: groen, toont Next.js logs

### Stoppen:
- Sluit beide terminal vensters, OF
- Druk Ctrl+C in elk venster

⚠️ **Let op:** Vensters openen buiten Cursor - moeilijker voor troubleshooting.

---

## <a id="npm-method"></a>📦 NPM Concurrently Method

Start beide in 1 terminal.

### Eerst installeer concurrently:
```powershell
npm install
```

### Dan start de app:
```powershell
npm run dev
```

### Wat gebeurt er:
- Backend en frontend starten **in 1 terminal**
- Gekleurd output:
  - [BACKEND] in blauw
  - [FRONTEND] in groen
- Alle logs door elkaar (maar wel te volgen)

### Stoppen:
- Druk Ctrl+C (stopt alles tegelijk)

### Bonus NPM Scripts:
```powershell
npm run dev              # Start beide servers
npm run dev:backend      # Alleen backend
npm run dev:frontend     # Alleen frontend
npm run setup            # Setup alles (eenmalig)
```

---

## 📋 Methode Vergelijking

| Feature | Cursor ⭐ | PowerShell | NPM |
|---------|----------|------------|-----|
| Setup | Geen | Geen | `npm install` |
| Vensters | In Cursor | Buiten Cursor | 1 terminal |
| Debugging | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| AI Help | ✅ Ja | ❌ Nee | ⚙️ Soms |
| Logs | Apart per tab | Apart per venster | Door elkaar |
| Stoppen | Per tab Ctrl+C | Sluit vensters | 1x Ctrl+C |
| **Aanbevolen** | ✅ **JA** | Als backup | Als voorkeur |

---

## <a id="urls"></a>🧪 URLs na Starten

### Frontend
- **Main App:** http://localhost:3000
- **Test Page:** http://localhost:3000/test

### Backend
- **API Root:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs ⭐ **Interactief testen!**
- **Health Check:** http://localhost:8000/health

### API Endpoints

#### Article Endpoints
- `GET /api/articles` - Alle artikelen ophalen

#### Batch Endpoints (v1.1)
- `POST /api/batches/create` - Nieuwe batch aanmaken
- `POST /api/batches/{id}/upload` - PDF uploaden naar batch
- `GET /api/batches/{id}` - Batch details ophalen
- `GET /api/batches` - Alle batches bekijken

💡 **Tip:** Test de endpoints interactief op http://localhost:8000/docs

---

## <a id="testing"></a>🧪 Batch Systeem Testen

### Optie A: Automatisch Test Script ⭐
```powershell
# Start eerst de app (zie boven)
# Dan in nieuwe terminal (of Terminal 3 in Cursor):
cd backend
venv\Scripts\python.exe test_batch_api.py
```

**Dit test script:**
- ✅ Maakt een nieuwe batch aan
- ✅ Upload een dummy PDF (`dummyinfo/Interfiliaalverdeling vooraf - 423264.pdf`)
- ✅ Haalt batch details op
- ✅ Toont geëxtraheerde artikelnummers

### Optie B: Swagger UI (Aanbevolen voor exploratie)
1. Start de app
2. Ga naar **http://localhost:8000/docs**
3. Test endpoints interactief:
   - Klik op endpoint
   - Klik "Try it out"
   - Vul parameters in
   - Klik "Execute"
   - Zie response

### Optie C: cURL Commands
```bash
# Batch aanmaken
curl -X POST http://localhost:8000/api/batches/create \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test Batch\"}"

# Batches ophalen
curl http://localhost:8000/api/batches

# Batch details
curl http://localhost:8000/api/batches/1
```

---

## <a id="troubleshooting"></a>⚙️ Troubleshooting

### "ModuleNotFoundError: No module named 'pdfplumber'"
Dependencies zijn niet geïnstalleerd in backend venv:

```powershell
cd backend
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### "Port already in use" (8000 of 3000)
Er draait nog een server:

**Optie 1: Stop alle servers**
1. Druk Ctrl+C in alle terminals
2. Sluit eventuele aparte vensters
3. Probeer opnieuw

**Optie 2: Kill process (Windows)**
```powershell
# Vind process op poort 8000
netstat -ano | findstr :8000
# Kill met PID (vervang 1234 met echte PID)
taskkill /PID 1234 /F

# Of voor poort 3000
netstat -ano | findstr :3000
taskkill /PID 5678 /F
```

### "Execution policy" error (PowerShell)
PowerShell script wordt geblokkeerd:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Database niet gevonden (eerste keer)
```powershell
cd backend
venv\Scripts\python.exe seed_database.py
```

Je ziet:
```
✅ Database seeding completed!
Database file: database.db
```

### Frontend "npm: command not found"
Node.js niet geïnstalleerd:
1. Download: https://nodejs.org/
2. Installeer LTS versie
3. Herstart terminal
4. Test: `node --version`

### Backend start maar crash meteen
Check de logs in terminal. Meestal:
1. **Import errors** → Dependencies installeren (zie boven)
2. **Port in use** → Andere server stoppen
3. **Database error** → Run seed_database.py

### Meer hulp nodig?
Zie **[[TROUBLESHOOTING]]** voor uitgebreide troubleshooting.

---

## 🎯 Quick Reference

### Cursor Method (Aanbevolen)
```powershell
# Terminal 1
cd backend
venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000

# Terminal 2
cd frontend
npm run dev
```

### PowerShell Script
```powershell
.\start-dev.ps1
```

### NPM Concurrently
```powershell
npm install  # Eenmalig
npm run dev  # Elke keer
```

### Test Batch Systeem
```powershell
cd backend
venv\Scripts\python.exe test_batch_api.py
```

---

## 📖 Meer Informatie

- **[[BATCH_SYSTEM]]** - Uitgebreide batch systeem documentatie
- **[[DATABASE]]** - Database setup en management
- **[[INTEGRATION]]** - Frontend-backend integratie
- **[[TROUBLESHOOTING]]** - Alle troubleshooting oplossingen
- **[[README]]** - Project overzicht en architectuur

---

**Veel succes met ontwikkelen! 🚀**

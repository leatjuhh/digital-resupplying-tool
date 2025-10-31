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

- [Dev.ps1 Script (AANBEVOLEN)](#devps1-method) ⭐ NIEUW!
- [NPM Direct Method](#npm-method)
- [Handmatige Methode](#manual-method)
- [URLs & Endpoints](#urls)
- [Batch Systeem Testen](#testing)
- [Troubleshooting](#troubleshooting)

---

## <a id="devps1-method"></a>⭐ Dev.ps1 Script Method (AANBEVOLEN)

De **nieuwe en aanbevolen manier** om de app te starten binnen Cursor.

### Voordelen
✅ **Pre-flight checks** - Valideert alles voor je start  
✅ **Auto database init** - Maakt database aan indien nodig  
✅ **Alle logs in Cursor** - Beide servers in 1 terminal  
✅ **AI hulp** - Cline kan alle errors lezen en helpen  
✅ **Gekleurde output** - `[BACKEND]` en `[FRONTEND]` prefixes  

### Gebruik

**Eenvoudig in Cursor terminal:**
```powershell
.\dev.ps1
```

### Wat gebeurt er:

**Pre-flight Checks:**
1. ✅ Controleert backend virtual environment
2. ✅ Controleert database (maakt aan indien nodig)
3. ✅ Controleert frontend dependencies
4. ✅ Controleert of poorten 8000 en 3000 vrij zijn

**Als alles OK is:**
- 🚀 Start beide servers via `npm run dev`
- 📊 Toont alle logs in dezelfde terminal
- 🎨 Gekleurde prefixes: `[BACKEND]` (cyan) en `[FRONTEND]` (groen)

### Output Voorbeeld:
```
  Digital Resupplying Tool - Dev Launcher

 Pre-flight Checks

  [1] Backend Virtual Environment: OK
  [2] Database: OK
  [3] Frontend Dependencies: OK
  [4] Port Availability: OK

 All checks passed! Starting servers...

[BACKEND] INFO: Uvicorn running on http://127.0.0.1:8000
[FRONTEND] ▲ Next.js 14.2.16
[FRONTEND]   - Local:        http://localhost:3000
```

### Stoppen
**Ctrl+C** in de terminal (stopt beide servers)

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

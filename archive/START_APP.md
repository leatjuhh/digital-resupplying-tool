# 🚀 App Starten - Simpel Gemaakt

## ⭐ NIEUW: Cursor Gebruikers

**Gebruik je Cursor?** Zie **[CURSOR_START_GUIDE.md](CURSOR_START_GUIDE.md)** voor de beste methode!

Voordelen:
- ✅ Terminals in Cursor (geen aparte vensters)
- ✅ Cline kan meekijken met errors
- ✅ Betere debugging
- ✅ Makkelijk troubleshooting

---

## Andere Manieren

Je hebt ook **2 andere manieren** om de app te starten:

---

## Optie 1: PowerShell Script ⭐ MAKKELIJKST

### Dubbelklik of run commando:

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
- Overzichtelijk, aparte logs

### Stoppen:
- Sluit beide terminal vensters, OF
- Druk Ctrl+C in elk venster

---

## Optie 2: NPM Concurrently (1 Terminal)

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

---

## 📋 Vergelijking

| Feature | PowerShell Script | NPM Concurrently |
|---------|------------------|------------------|
| Setup | Geen | `npm install` eerst |
| Vensters | 2 aparte | 1 terminal |
| Overzicht | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Logs | Apart | Door elkaar |
| Stoppen | 2x Ctrl+C of sluit vensters | 1x Ctrl+C |
| Makkelijkst | ✅ Ja | Nee |

---

## 💡 Aanbeveling

**Start met PowerShell script** (`start-dev.ps1`)
- Makkelijkst
- Overzichtelijkst
- Geen extra installatie

**Gebruik NPM als je:**
- Alles in 1 terminal wilt
- Gewend bent aan concurrently
- Minder vensters wilt

---

## 🧪 URLs na Starten

### Frontend
- **Main App:** http://localhost:3000
- **Test Page:** http://localhost:3000/test

### Backend
- **API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs ⭐ **Interactief testen!**
- **Health:** http://localhost:8000/health

### Nieuwe Batch Endpoints (v1.1)
- **POST** `/api/batches/create` - Nieuwe batch aanmaken
- **POST** `/api/batches/{id}/upload` - PDF uploaden naar batch
- **GET** `/api/batches/{id}` - Batch details ophalen
- **GET** `/api/batches` - Alle batches bekijken

💡 **Tip:** Test de batch endpoints interactief op http://localhost:8000/docs

---

## ❌ Troubleshooting

### "Execution policy" error (PowerShell)
Run dit eerst:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Port already in use"
Er draait nog een oude server:
1. Sluit alle terminal vensters
2. Of kill processen op poort 3000 en 8000
3. Probeer opnieuw

### "npm: command not found"
Node.js niet geïnstalleerd - gebruik PowerShell script

### Backend start niet
Check of venv bestaat en database.db:
```powershell
cd backend
.\venv\Scripts\activate
pip list  # Check packages
python seed_database.py  # Re-initialize DB
```

---

## 🎯 Quick Reference

### PowerShell Script
```powershell
.\start-dev.ps1
```

### NPM Concurrently
```powershell
npm install    # Eenmalig
npm run dev    # Elke keer
```

### Handmatig (Oude Manier)
```powershell
# Terminal 1:
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000

# Terminal 2:
cd frontend
npm run dev
```

---

## ✨ Bonus NPM Scripts

Als je concurrently hebt geïnstalleerd:

```powershell
npm run dev              # Start beide servers
npm run dev:backend      # Alleen backend
npm run dev:frontend     # Alleen frontend
npm run setup            # Setup alles (eenmalig)
```

---

## 🧪 Batch Systeem Testen (Nieuw!)

### Optie A: Automatisch Test Script
```powershell
# Start eerst de server (met een van bovenstaande methodes)
# Dan in een andere terminal:
cd backend
python test_batch_api.py
```

Dit test script:
- ✅ Maakt een nieuwe batch aan
- ✅ Upload een dummy PDF
- ✅ Haalt batch details op
- ✅ Toont geëxtraheerde artikelnummers

### Optie B: Swagger UI (Aanbevolen)
1. Start de app (methode 1 of 2)
2. Ga naar http://localhost:8000/docs
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
```

📖 **Meer info:** Zie `BATCH_SYSTEM_STATUS.md` voor volledige batch systeem documentatie

---

**Veel plezier met ontwikkelen! 🚀**

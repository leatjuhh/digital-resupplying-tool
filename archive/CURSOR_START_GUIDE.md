# 🚀 App Starten in Cursor - Eenvoudig!

## Voor Cursor Gebruikers

Gebruik de **geïntegreerde terminal** van Cursor voor betere debugging en troubleshooting.

---

## ✅ Eenvoudigste Methode (Aanbevolen)

### Stap 1: Open 2 Terminals in Cursor
- Klik op "+" in terminal panel (of Ctrl+Shift+`)
- Je hebt nu 2 tabs in Cursor

### Stap 2: Terminal 1 - Backend
```powershell
cd backend
venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

Je ziet:
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

Je ziet:
```
- Local:        http://localhost:3000
```

✅ Frontend draait nu op **http://localhost:3000**

---

## 🧪 URLs na Starten

### Frontend
- **App:** http://localhost:3000
- **Test:** http://localhost:3000/test

### Backend
- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs ⭐ **Test hier je endpoints!**
- **Health:** http://localhost:8000/health

### Batch Endpoints (Nieuw!)
- POST `/api/batches/create`
- POST `/api/batches/{id}/upload`
- GET `/api/batches/{id}`
- GET `/api/batches`

---

## 🧪 Batch Systeem Testen

### Methode 1: Test Script (in 3e terminal)
```powershell
cd backend
venv\Scripts\python.exe test_batch_api.py
```

### Methode 2: Swagger UI (Aanbevolen)
1. Ga naar http://localhost:8000/docs
2. Klik op endpoint
3. Klik "Try it out"
4. Test interactief!

---

## 🛑 Stoppen

In elke terminal: **Ctrl+C**

---

## ⚙️ Troubleshooting

### "ModuleNotFoundError: No module named 'pdfplumber'"
Dependencies zijn niet geïnstalleerd in backend venv:

```powershell
cd backend
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### "Port already in use"
Er draait nog een server:
1. Druk Ctrl+C in alle terminals
2. Sluit Cursor en heropen
3. Probeer opnieuw

### Eerste keer opstart - Database niet gevonden
```powershell
cd backend
venv\Scripts\python.exe seed_database.py
```

---

## 💡 Waarom Cursor Terminal?

✅ **Betere debugging** - Zie errors direct in Cursor  
✅ **AI hulp** - Cline kan meekijken met errors  
✅ **Overzichtelijk** - Tabs in plaats van losse vensters  
✅ **Copy/paste** - Makkelijk errors delen  

---

## 🔄 Alternatief: PowerShell Script

Als je toch aparte vensters wilt:
```powershell
.\start-dev.ps1
```

⚠️ Opent vensters **buiten Cursor** - moeilijker voor troubleshooting.

---

## 📖 Meer Info

- **START_APP.md** - Alle start methodes
- **BATCH_SYSTEM_STATUS.md** - Batch systeem details
- **README.md** - Project overzicht

---

**Veel succes met ontwikkelen! 🚀**

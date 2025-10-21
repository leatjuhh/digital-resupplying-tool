# Fresh Start - Backend Setup

## 🔄 Volledige Herinstallatie Backend

### Stap 1: Stop Alle Running Terminals

Zorg dat er geen backend server meer draait:
- Klik in terminal venster
- Druk `Ctrl + C`
- Herhaal voor alle open terminals

---

### Stap 2: Verwijder Oude Virtual Environment

**In Windows Explorer:**
1. Ga naar `backend` folder
2. Verwijder de `venv` folder (hele folder)
3. Als het niet lukt: sluit Cursor eerst, dan verwijderen

**Of via PowerShell:**
```powershell
cd backend
Remove-Item -Recurse -Force venv
```

---

### Stap 3: Maak Nieuwe Virtual Environment

```powershell
cd backend
python -m venv venv
```

**Dit duurt ~30 seconden**

Je zou moeten zien dat er een nieuwe `venv` folder wordt aangemaakt.

---

### Stap 4: Activeer Virtual Environment

```powershell
.\venv\Scripts\activate
```

**Je ziet nu `(venv)` voor je prompt:**
```
(venv) PS C:\...\backend>
```

---

### Stap 5: Upgrade Pip (Belangrijk!)

```powershell
python -m pip install --upgrade pip
```

**Output:**
```
Successfully installed pip-XX.X.X
```

---

### Stap 6: Installeer Dependencies

```powershell
pip install -r requirements.txt
```

**Je zou moeten zien:**
```
Installing collected packages: ...
Successfully installed fastapi-0.115.5 uvicorn-0.34.0 python-dotenv-1.0.1 pydantic-2.10.3 sqlalchemy-2.0.23
```

---

### Stap 7: Verify Installatie

```powershell
pip list
```

**Check dat je deze packages ziet:**
- fastapi
- uvicorn
- python-dotenv
- pydantic
- sqlalchemy ✅

---

### Stap 8: Initialiseer Database

```powershell
python seed_database.py
```

**Expected output:**
```
🌱 Starting database seeding...

Creating database tables...
✓ Tables created

Seeding stores...
✓ Added store: Amsterdam
✓ Added store: Rotterdam
✓ Added store: Utrecht
✓ Added store: Den Haag

Seeding articles...
✓ Added article: ART-001 - Winter Jacket - Blue
[...]

✅ Database seeding completed!
```

---

### Stap 9: Start Backend

```powershell
uvicorn main:app --reload --port 8000
```

**Je zou moeten zien:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Stap 10: Test!

Open browser: **http://localhost:8000/docs**

Je zou nu moeten zien:
- 5 endpoints voor /api/articles
- Werkende API documentatie
- Geen errors

---

## ❌ Troubleshooting

### "python not found"
**Oplossing:** Check Python installatie
```powershell
python --version
```
Zou iets als `Python 3.11.x` moeten tonen

### "Cannot remove venv folder"
**Oplossing:** 
1. Sluit Cursor/VSCode volledig
2. Verwijder folder via Windows Explorer
3. Heropen Cursor

### "pip install fails"
**Oplossing:** Probeer zonder cache:
```powershell
pip cache purge
pip install --no-cache-dir -r requirements.txt
```

### "Module not found" bij seed script
**Oplossing:** Check of venv actief is
```powershell
# Je zou (venv) moeten zien voor je prompt
# Zo niet:
.\venv\Scripts\activate
```

---

## ✅ Success Checklist

Na deze stappen zou je moeten hebben:
- [ ] Nieuwe venv folder in backend/
- [ ] (venv) zichtbaar in terminal
- [ ] `pip list` toont alle 5 packages
- [ ] database.db file bestaat
- [ ] Backend draait op :8000
- [ ] http://localhost:8000/docs werkt
- [ ] Geen errors in terminal

---

## 🎯 Volgende Stap

Als alles werkt:
- **Frontend testen:** http://localhost:3000/test
- **CRUD operaties testen** in API docs
- **Verder bouwen** aan de applicatie!

Als het nog steeds niet werkt, laat me weten:
1. Bij welke stap het fout ging
2. Wat de error message was
3. Output van `python --version` en `pip --version`

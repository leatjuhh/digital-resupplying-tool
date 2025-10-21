# Database Setup - Quick Start Guide

## ✅ Wat is er Klaar

Je hebt nu een complete database setup:
- ✅ SQLite database configuratie
- ✅ Database models (Store, Article)
- ✅ Seed script met test data
- ✅ CRUD endpoints (Create, Read, Update, Delete)

## 🚀 Installatie & Setup (5 minuten)

### Stap 1: Installeer SQLAlchemy

Stop de backend server (Ctrl+C) en run:

```powershell
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Je zou moeten zien:**
```
Installing collected packages: sqlalchemy
Successfully installed sqlalchemy-2.0.23
```

---

### Stap 2: Initialiseer Database

Run het seed script:

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
✓ Added article: ART-002 - Summer T-Shirt - White
✓ Added article: ART-003 - Denim Jeans - Black
✓ Added article: ART-004 - Sneakers - Red
✓ Added article: ART-005 - Baseball Cap - Green

✅ Database seeding completed!

Database file: database.db
You can now start the API server.
```

✅ **Check:** Je hebt nu een `database.db` file in de backend folder!

---

### Stap 3: Start Backend

```powershell
uvicorn main:app --reload --port 8000
```

**Server start normaal, maar nu met database!**

---

### Stap 4: Test Database Endpoints

Open browser: http://localhost:8000/docs

**Je ziet nu deze nieuwe endpoints:**

#### GET /api/articles
Haal alle artikelen op (uit database!)

#### GET /api/articles/{artikelnummer}
Haal specifiek artikel op (bijv. ART-001)

#### POST /api/articles
Maak nieuw artikel aan

#### PUT /api/articles/{artikelnummer}
Update artikel

#### DELETE /api/articles/{artikelnummer}
Verwijder artikel

---

### Stap 5: Test in Frontend

Met backend draaiend, ga naar: **http://localhost:3000/test**

**Het verschil:**
- ❌ VOOR: Dummy data hardcoded in code
- ✅ NU: Echte data uit database!

De test pagina zou nog steeds dezelfde 5 artikelen moeten tonen, maar nu komen ze uit `database.db` in plaats van hardcoded!

---

## 🧪 Test CRUD Operaties

### In de browser (http://localhost:8000/docs):

**1. GET alle artikelen**
- Click "GET /api/articles" → Try it out → Execute
- Je ziet 5 artikelen

**2. GET één artikel**
- Click "GET /api/articles/{artikelnummer}" → Try it out
- Voer in: `ART-001` → Execute
- Je ziet één artikel

**3. POST nieuw artikel**
- Click "POST /api/articles" → Try it out
- Voer in:
```json
{
  "artikelnummer": "ART-006",
  "omschrijving": "Test Product",
  "voorraad_per_winkel": {
    "Amsterdam": 10,
    "Rotterdam": 5
  }
}
```
- Execute → Status 201 Created!

**4. Refresh frontend test page**
- Ga naar http://localhost:3000/test
- Click "Ververs"
- Je ziet nu 6 artikelen! (incl. je nieuwe artikel)

**5. UPDATE artikel**
- Click "PUT /api/articles/{artikelnummer}" → Try it out
- artikelnummer: `ART-006`
- Body:
```json
{
  "artikelnummer": "ART-006",
  "omschrijving": "Updated Test Product",
  "voorraad_per_winkel": {
    "Amsterdam": 20,
    "Rotterdam": 15
  }
}
```
- Execute → Artikel is updated!

**6. DELETE artikel**
- Click "DELETE /api/articles/{artikelnummer}" → Try it out
- artikelnummer: `ART-006` → Execute
- Status 204 No Content → Artikel verwijderd!

---

## 📊 Verificatie Checklist

- [ ] database.db file bestaat in backend folder
- [ ] `pip install -r requirements.txt` succesvol
- [ ] Seed script runt zonder errors
- [ ] Backend start zonder errors
- [ ] http://localhost:8000/docs toont 5 endpoints
- [ ] GET /api/articles retourneert 5 artikelen
- [ ] Frontend test page toont dezelfde data
- [ ] POST nieuwe artikel werkt
- [ ] Nieuwe artikel zichtbaar in frontend

---

## 🎉 Success!

Je hebt nu:
✅ SQLite database
✅ CRUD operaties
✅ Test data
✅ Frontend die database data toont
✅ API documentatie

## 🚀 Volgende Stappen

Nu de database werkt, kunnen we bouwen:
1. **Stores endpoints** - CRUD voor winkels
2. **Voorraad updates** - Wijzig voorraad per winkel
3. **Proposals systeem** - Bouw de core feature
4. **Authenticatie** - Beveilig de endpoints

**Laat me weten wanneer je klaar bent met testen!** 🎯

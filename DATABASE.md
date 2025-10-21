---
tags: [documentation, database, sqlite, sqlalchemy, setup]
type: technical-doc
related: [[README]], [[BATCH_SYSTEM]], [[GETTING_STARTED]]
---

# Database - Complete Gids

Complete documentatie over de SQLite database setup en management.

> 💡 **Quick Start:** Zie [[GETTING_STARTED]] voor app setup

---

## 📋 Snelle Index

- [Overzicht](#overview)
- [Quick Start](#quickstart)
- [Database Schema](#schema)
- [CRUD Operaties](#crud)
- [Seed Data](#seeding)
- [Troubleshooting](#troubleshooting)

---

## <a id="overview"></a>📊 Overzicht

### Wat We Gebruiken

**Database:** SQLite  
**ORM:** SQLAlchemy 2.0  
**Locatie:** `backend/database.db`  

### Waarom SQLite?

✅ **Geen extra installatie** - Komt met Python  
✅ **Perfect voor development** - File-based, simpel  
✅ **Makkelijk te migreren** - Later naar PostgreSQL  
✅ **Type-safe** - SQLAlchemy ORM  

### Database Models

```python
# backend/db_models.py

Store:
- id (Integer, Primary Key)
- name (String, Unique)
- city (String)
- code (String, Unique)

Article:
- id (Integer, Primary Key)
- artikelnummer (String, Unique)
- omschrijving (String)
- voorraad_per_winkel (JSON)

Batch:
- id (Integer, Primary Key)
- name (String)
- status (String)
- pdf_count (Integer)
- processed_count (Integer)
- created_at (DateTime)

BatchPDF:
- id (Integer, Primary Key)
- batch_id (Integer, Foreign Key)
- filename (String)
- file_path (String)
- status (String)
- parsed_data (JSON)
- error_message (Text)
- uploaded_at (DateTime)
- processed_at (DateTime)

Proposal:
- id (Integer, Primary Key)
- batch_id (Integer, Foreign Key)
- artikelnummer (String)
- article_name (String)
- current_distribution (JSON)
- proposed_distribution (JSON)
- status (String)
- reason (Text)
- applied_rules (JSON)
- created_at (DateTime)
- reviewed_at (DateTime)
- rejection_reason (Text)

Feedback:
- id (Integer, Primary Key)
- proposal_id (Integer, Foreign Key)
- category (String)
- rating (Integer)
- comment (Text)
- sentiment (String)
- created_at (DateTime)
```

---

## <a id="quickstart"></a>🚀 Quick Start (5 minuten)

### Stap 1: Dependencies Installeren

```powershell
cd backend
venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Belangrijk packages:**
- sqlalchemy==2.0.36
- python-dotenv==1.0.1

### Stap 2: Database Initialiseren

```powershell
venv\Scripts\python.exe seed_database.py
```

**Expected Output:**
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
```

### Stap 3: Verify

```powershell
# Check of database.db bestaat
dir database.db
```

✅ **Success!** Database is ready.

---

## <a id="schema"></a>🗄️ Database Schema

### SQLite Schema

```sql
-- Stores (Winkels)
CREATE TABLE stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE
);

-- Articles (Producten)
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artikelnummer TEXT NOT NULL UNIQUE,
    omschrijving TEXT NOT NULL,
    voorraad_per_winkel TEXT NOT NULL  -- JSON stored as TEXT
);

-- Batches (PDF Upload Groepen)
CREATE TABLE batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'processing',
    pdf_count INTEGER NOT NULL DEFAULT 0,
    processed_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extra_data TEXT  -- JSON
);

-- Batch PDFs
CREATE TABLE batch_pdfs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    parsed_data TEXT,  -- JSON
    error_message TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES batches(id)
);

-- Proposals (Herverdelingsvoorstellen)
CREATE TABLE proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    artikelnummer TEXT NOT NULL,
    article_name TEXT NOT NULL,
    current_distribution TEXT NOT NULL,  -- JSON
    proposed_distribution TEXT NOT NULL,  -- JSON
    status TEXT NOT NULL DEFAULT 'pending',
    reason TEXT,
    applied_rules TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    rejection_reason TEXT,
    FOREIGN KEY (batch_id) REFERENCES batches(id)
);

-- Feedback
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT NOT NULL,
    sentiment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proposal_id) REFERENCES proposals(id)
);
```

### Indexes

```sql
CREATE INDEX idx_articles_artikelnummer ON articles(artikelnummer);
CREATE INDEX idx_stores_name ON stores(name);
CREATE INDEX idx_stores_code ON stores(code);
CREATE INDEX idx_batch_pdfs_batch_id ON batch_pdfs(batch_id);
CREATE INDEX idx_proposals_batch_id ON proposals(batch_id);
CREATE INDEX idx_proposals_artikelnummer ON proposals(artikelnummer);
CREATE INDEX idx_feedback_proposal_id ON feedback(proposal_id);
```

---

## <a id="crud"></a>🔧 CRUD Operaties

### Via API (Swagger UI)

Ga naar: http://localhost:8000/docs

### Articles Endpoints

#### GET /api/articles
Haal alle artikelen op.

**Response:**
```json
[
  {
    "artikelnummer": "ART-001",
    "omschrijving": "Winter Jacket - Blue",
    "voorraad_per_winkel": {
      "Amsterdam": 15,
      "Rotterdam": 8,
      "Utrecht": 12
    }
  }
]
```

#### GET /api/articles/{artikelnummer}
Haal specifiek artikel op.

**Response:**
```json
{
  "artikelnummer": "ART-001",
  "omschrijving": "Winter Jacket - Blue",
  "voorraad_per_winkel": {
    "Amsterdam": 15,
    "Rotterdam": 8,
    "Utrecht": 12
  }
}
```

#### POST /api/articles
Maak nieuw artikel aan.

**Request:**
```json
{
  "artikelnummer": "ART-006",
  "omschrijving": "New Product",
  "voorraad_per_winkel": {
    "Amsterdam": 10,
    "Rotterdam": 5
  }
}
```

#### PUT /api/articles/{artikelnummer}
Update artikel.

**Request:**
```json
{
  "artikelnummer": "ART-006",
  "omschrijving": "Updated Product",
  "voorraad_per_winkel": {
    "Amsterdam": 20,
    "Rotterdam": 15
  }
}
```

#### DELETE /api/articles/{artikelnummer}
Verwijder artikel.

**Response:** `204 No Content`

### Via Python Code

```python
from sqlalchemy.orm import Session
from database import get_db
import db_models

# Get alle artikelen
db = next(get_db())
articles = db.query(db_models.Article).all()

# Get één artikel
article = db.query(db_models.Article).filter(
    db_models.Article.artikelnummer == "ART-001"
).first()

# Create nieuw artikel
new_article = db_models.Article(
    artikelnummer="ART-006",
    omschrijving="New Product",
    voorraad_per_winkel={"Amsterdam": 10}
)
db.add(new_article)
db.commit()

# Update artikel
article.voorraad_per_winkel["Amsterdam"] = 20
db.commit()

# Delete artikel
db.delete(article)
db.commit()
```

---

## <a id="seeding"></a>🌱 Seed Data

### Wat Zit Er in Seed Data?

**4 Stores:**
- Amsterdam (AMS)
- Rotterdam (RTM)
- Utrecht (UTR)
- Den Haag (DHG)

**5 Articles:**
- ART-001: Winter Jacket - Blue
- ART-002: Summer T-Shirt - White
- ART-003: Denim Jeans - Black
- ART-004: Sneakers - Red
- ART-005: Baseball Cap - Green

### Database Opnieuw Seeden

⚠️ **Dit verwijdert alle data!**

```powershell
cd backend

# Verwijder oude database
del database.db

# Maak nieuwe met seed data
venv\Scripts\python.exe seed_database.py
```

### Custom Seed Data

Bewerk `backend/seed_database.py`:

```python
# Voeg meer stores toe
new_store = Store(
    name="Eindhoven",
    city="Eindhoven",
    code="EIN"
)
db.add(new_store)

# Voeg meer artikelen toe
new_article = Article(
    artikelnummer="ART-010",
    omschrijving="Custom Product",
    voorraad_per_winkel={
        "Amsterdam": 5,
        "Rotterdam": 3
    }
)
db.add(new_article)

db.commit()
```

---

## <a id="troubleshooting"></a>⚙️ Troubleshooting

### "database.db not found"

**Oplossing:**
```powershell
cd backend
venv\Scripts\python.exe seed_database.py
```

### "table already exists" error

Database is al aangemaakt maar niet compleet.

**Oplossing:**
```powershell
cd backend
del database.db
venv\Scripts\python.exe seed_database.py
```

### "no such table: articles"

Database bestaat maar heeft geen tabellen.

**Oplossing:**
```powershell
cd backend
venv\Scripts\python.exe seed_database.py
```

### "UNIQUE constraint failed"

Je probeert duplicate data toe te voegen.

**Oplossing:**
- Check artikelnummer/store naam is uniek
- Of delete oude record eerst

### Database is locked

Meerdere processen proberen te schrijven.

**Oplossing:**
1. Stop backend server (Ctrl+C)
2. Run seed script opnieuw
3. Start server opnieuw

### Database file corrumpeerd

**Oplossing:**
```powershell
cd backend
del database.db
venv\Scripts\python.exe seed_database.py
```

### Migration naar PostgreSQL

Later als je naar productie gaat:

```python
# backend/.env
# DATABASE_URL=postgresql://user:pass@localhost/dbname

# In database.py wijzig:
# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
```

Geen code changes nodig! SQLAlchemy handelt dit af.

---

## 📖 Zie Ook

- **[[GETTING_STARTED]]** - App starten
- **[[BATCH_SYSTEM]]** - Batch systeem docs
- **[[INTEGRATION]]** - Frontend-backend integratie
- **[[README]]** - Project overzicht

---

## 🎯 Next Steps

Nu de database werkt:

1. ✅ **CRUD operaties** - Volledig werkend
2. ✅ **Batch systeem** - PDF uploads & parsing
3. ⏳ **Proposals** - Generatie uit batch data
4. ⏳ **Frontend UI** - Batch/proposal management
5. ⏳ **Authenticatie** - User management
6. ⏳ **PostgreSQL** - Production ready

---

**Database Status:** ✅ Volledig operationeel!

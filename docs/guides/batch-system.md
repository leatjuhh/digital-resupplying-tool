---
tags: [documentation, batch-system, api, pdf-parsing]
type: technical-doc
related: [[README]], [[DATABASE]], [[GETTING_STARTED]]
version: 1.1
---

# Batch Systeem - Complete Documentatie

Complete overzicht van het batch upload en PDF parsing systeem.

> 💡 **Quick Start:** Zie [[GETTING_STARTED]] voor app setup

---

## 📋 Snelle Index

- [Status & Features](#status)
- [Architectuur](#architecture)
- [API Endpoints](#endpoints)
- [Hoe Te Testen](#testing)
- [Volgende Stappen](#next-steps)
- [Code Referentie](#code)

---

## <a id="status"></a>✅ Status & Features

### Wat is Klaar (v1.1)

#### 1. Database Models ✅
**Bestand:** `backend/db_models.py`

Nieuwe tabellen toegevoegd:
- **Batch** - Groepeert meerdere PDF uploads
  - id, name, status, pdf_count, processed_count, created_at
- **BatchPDF** - Individuele PDF binnen een batch
  - id, batch_id, filename, file_path, status, parsed_data, error_message
- **Proposal** - Herverdelingsvoorstellen
  - id, batch_id, artikelnummer, current_distribution, proposed_distribution, status
- **Feedback** - Gebruiker feedback op voorstellen
  - id, proposal_id, category, rating, comment, sentiment

#### 2. PDF Parser ✅
**Bestand:** `backend/pdf_parser.py`

- Gebruikt **pdfplumber** (bewezen in oud project)
- Functie: `parse_voorraad_pdf(pdf_path)` 
- Extraheert artikelnummers (5-6 cijfers)
- Returns: dict met success, artikelnummers, page_count, etc.

```python
# Voorbeeld gebruik
from pdf_parser import parse_voorraad_pdf

result = parse_voorraad_pdf("path/to/pdf.pdf")
# Returns:
# {
#     "success": True,
#     "artikelnummers": ["423264", "423265", ...],
#     "raw_text": "...",
#     "page_count": 3,
#     "total_lines": 150,
#     "extracted_count": 45
# }
```

#### 3. API Endpoints ✅
**Bestand:** `backend/routers/batches.py`

Endpoints geïmplementeerd:
- `POST /api/batches/create` - Nieuwe batch aanmaken
- `POST /api/batches/{id}/upload` - PDF uploaden naar batch
- `GET /api/batches/{id}` - Batch details + PDF lijst
- `GET /api/batches` - Alle batches (nieuwste eerst)

Features:
- ✅ PDF validatie (type check, pdfplumber validate)
- ✅ Automatische parsing na upload
- ✅ Batch status tracking (processing/completed/failed)
- ✅ Foutafhandeling
- ✅ Per-batch file organization (`uploads/batch_{id}/`)

#### 4. Pydantic Models ✅
**Bestand:** `backend/models.py`

Modellen toegevoegd:
- BatchCreate, BatchResponse
- PDFUploadResponse, BatchDetailResponse
- ProposalResponse, FeedbackCreate

#### 5. Dependencies ✅
**Geïnstalleerd:**
- pdfplumber==0.11.0
- python-multipart==0.0.9 (voor file uploads)
- sqlalchemy==2.0.36 (upgrade)

#### 6. Database Migratie ✅
- Nieuwe tabellen aangemaakt via `seed_database.py`
- Bestaande data behouden (stores, articles)

#### 7. Test Script ✅
**Bestand:** `backend/test_batch_api.py`

Test script om te verifiëren:
1. Batch aanmaken
2. PDF uploaden
3. Batch details ophalen

---

## <a id="architecture"></a>🏗️ Architectuur

### Data Flow

```
1. User → Frontend: Maak nieuwe batch aan
2. Frontend → Backend: POST /api/batches/create
3. Backend: Batch record in database

4. User → Frontend: Upload PDF(s)
5. Frontend → Backend: POST /api/batches/{id}/upload
6. Backend: 
   - Save PDF to uploads/batch_{id}/
   - Validate PDF
   - Parse met pdfplumber
   - Extract artikelnummers
   - Save parsed data in database
   - Update batch status

7. User → Frontend: Bekijk batch details
8. Frontend → Backend: GET /api/batches/{id}
9. Backend: Return batch + alle PDF's + parsed data
```

### File Structure

```
backend/
├── uploads/                    # PDF storage (gitignored)
│   ├── batch_1/               # Batch 1 PDF's
│   │   ├── 20250119_180000_file1.pdf
│   │   └── 20250119_180030_file2.pdf
│   ├── batch_2/               # Batch 2 PDF's
│   └── ...
├── routers/
│   ├── batches.py             # Batch endpoints
│   ├── proposals.py           # TODO: Proposals
│   └── feedback.py            # TODO: Feedback
├── pdf_parser.py              # PDF parsing logic
├── db_models.py               # Database schemas
└── models.py                  # API models
```

---

## <a id="endpoints"></a>📡 API Endpoints

### POST /api/batches/create
Maak nieuwe batch aan.

**Request Body:**
```json
{
  "name": "Week 42 - Interfiliaal"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Week 42 - Interfiliaal",
  "status": "processing",
  "pdf_count": 0,
  "processed_count": 0,
  "created_at": "2025-01-19T18:00:00"
}
```

### POST /api/batches/{id}/upload
Upload PDF naar batch.

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file`: PDF file

**Response:**
```json
{
  "batch_id": 1,
  "filename": "voorraad.pdf",
  "status": "completed",
  "message": "Extracted 45 artikelnummers"
}
```

### GET /api/batches/{id}
Haal batch details op.

**Response:**
```json
{
  "id": 1,
  "name": "Week 42 - Interfiliaal",
  "status": "completed",
  "pdf_count": 2,
  "processed_count": 2,
  "created_at": "2025-01-19T18:00:00",
  "pdfs": [
    {
      "id": 1,
      "filename": "voorraad1.pdf",
      "status": "completed",
      "uploaded_at": "2025-01-19T18:01:00",
      "processed_at": "2025-01-19T18:01:05",
      "extracted_count": 45,
      "error": null
    },
    {
      "id": 2,
      "filename": "voorraad2.pdf",
      "status": "completed",
      "uploaded_at": "2025-01-19T18:02:00",
      "processed_at": "2025-01-19T18:02:03",
      "extracted_count": 38,
      "error": null
    }
  ]
}
```

### GET /api/batches
Haal alle batches op (nieuwste eerst).

**Response:**
```json
[
  {
    "id": 2,
    "name": "Week 43 - Interfiliaal",
    "status": "processing",
    "pdf_count": 1,
    "processed_count": 0,
    "created_at": "2025-01-20T10:00:00"
  },
  {
    "id": 1,
    "name": "Week 42 - Interfiliaal",
    "status": "completed",
    "pdf_count": 2,
    "processed_count": 2,
    "created_at": "2025-01-19T18:00:00"
  }
]
```

---

## <a id="testing"></a>🧪 Hoe Te Testen

### Automatisch Test Script

```powershell
# Start app eerst (zie GETTING_STARTED.md)
cd backend
venv\Scripts\python.exe test_batch_api.py
```

**Het script test:**
1. Batch aanmaken
2. PDF uploaden (gebruikt `dummyinfo/Interfiliaalverdeling vooraf - 423264.pdf`)
3. Batch details ophalen
4. Parsed data verifiëren

### Swagger UI (Interactief)

1. Start app
2. Ga naar http://localhost:8000/docs
3. Test endpoints:
   - **POST /api/batches/create** → Input: `{"name": "Test Batch"}`
   - **POST /api/batches/{id}/upload** → Upload een PDF
   - **GET /api/batches/{id}** → Zie parsed data
   - **GET /api/batches** → Zie alle batches

### Handmatig met cURL

```bash
# Batch aanmaken
curl -X POST http://localhost:8000/api/batches/create \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test Batch\"}"

# PDF uploaden (vervang {id} met batch ID)
curl -X POST http://localhost:8000/api/batches/1/upload \
  -F "file=@path/to/your.pdf"

# Batch details
curl http://localhost:8000/api/batches/1

# Alle batches
curl http://localhost:8000/api/batches
```

### Wat We Nu Kunnen

✅ **Batches aanmaken** met een naam  
✅ **Meerdere PDF's uploaden** naar één batch  
✅ **PDF's automatisch parsen** (artikelnummers extraheren)  
✅ **Status bijhouden** per PDF en per batch  
✅ **Foutmeldingen opslaan** als parsing mislukt  
✅ **Batch details opvragen** met alle PDF's en parsed data  

### Voorbeeld Flow

```
1. User maakt batch aan: "Week 42 - Interfiliaal"
   → Batch ID: 1, Status: processing

2. User upload PDF #1 → Parse → 50 artikelnummers geëxtraheerd
   → PDF status: completed, extracted_count: 50

3. User upload PDF #2 → Parse → 45 artikelnummers geëxtraheerd
   → PDF status: completed, extracted_count: 45

4. Batch status automatisch = completed (alle PDF's verwerkt)
   → pdf_count: 2, processed_count: 2

5. User vraagt batch details op
   → Ziet beide PDF's + extracted counts + parsed data
```

---

## <a id="next-steps"></a>🚧 Volgende Stappen

### Prioriteit 1: Proposals Generatie (Hoog)
**Doel:** Van parsed PDF data → Herverdelingsvoorstellen

**Geschatte Tijd:** ~2 uur

**Stappen:**

1. **Rules Engine Basis** (`backend/rules/`)
   - `rules_engine.py` - Hoofd logica
   - `rules_schema.py` - Pydantic schemas voor regels
   - Basis regels implementeren:
     * Minimum voorraad per winkel
     * Geen dubbele maten
     * Prioriteit voor goedverkopende winkels

2. **Proposals Router** (`backend/routers/proposals.py`)
   - `POST /api/proposals/generate` - Genereer voorstellen van batch
   - `GET /api/proposals/{id}` - Voorstel details
   - `POST /api/proposals/{id}/approve` - Goedkeuren
   - `POST /api/proposals/{id}/reject` - Afkeuren
   - `PUT /api/proposals/{id}/edit` - Voorstel aanpassen

3. **Test met Dummy Data**
   - Create test scenarios
   - Verify proposal generation
   - Check edge cases

### Prioriteit 2: Frontend Integration (Medium)
**Doel:** UI voor batch management

**Geschatte Tijd:** ~2 uur

**Pagina's toevoegen:**
- `/batches` - Overzicht van alle batches
- `/batches/create` - Nieuwe batch + upload UI
- `/batches/[id]` - Batch details met PDF's
- `/proposals` - Gegenereerde voorstellen bekijken

**Components:**
- BatchList - Lijst van batches
- BatchCreate - Form + file uploader
- BatchDetail - Details + PDF lijst
- ProposalViewer - Voorstel weergave & acties

### Prioriteit 3: Feedback Router (Medium)
**Doel:** Gebruiker feedback verzamelen

**Geschatte Tijd:** ~30 minuten

**Endpoints:**
- `POST /api/feedback` - Feedback indienen
- `GET /api/feedback` - Alle feedback (admin)
- `GET /api/feedback/stats` - Feedback statistieken

### Prioriteit 4: ChatGPT Integration (Laag/Optioneel)
**Doel:** AI-verbeterde regels

**Geschatte Tijd:** ~1 uur

**Features:**
- API key management
- Dynamic rules mode
- Feedback → ChatGPT prompt → Verbeterde regels
- AI-gegenereerde redenen voor voorstellen

### Totale Geschatte Tijd voor Compleet Systeem
**~5-6 uur** (zonder ChatGPT)  
**~6-7 uur** (met ChatGPT)

---

## 📝 Code Kwaliteit

### Wat Goed Is
✅ **Nederlandse comments** overal  
✅ **Type hints** (Pydantic models)  
✅ **Error handling** proper exception handling  
✅ **Database foreign keys** referential integrity  
✅ **Status tracking** duidelijke state management  
✅ **Herbruikbaar** beproefd PDF parser uit oud project  

### Aandachtspunten (Toekomstige Verbeteringen)

⚠️ **Sync processing** (kan slow worden bij veel PDF's)
- **Later:** Async met Celery/background tasks
- **Nu:** Acceptabel voor < 10 PDF's per batch

⚠️ **Geen authenticatie yet**
- **Later:** JWT tokens, user roles
- **Nu:** Lokaal development, niet kritisch

⚠️ **File cleanup** (uploads blijven staan)
- **Later:** Cleanup job of TTL
- **Nu:** Handmatig verwijderen indien nodig

⚠️ **Geen progress tracking tijdens parsing**
- **Later:** WebSockets voor real-time updates
- **Nu:** Status polling via GET endpoints

---

## <a id="code"></a>📚 Code Referentie

### Belangrijke Bestanden

```
backend/
├── db_models.py              # Database schemas
│   ├── Batch
│   ├── BatchPDF
│   ├── Proposal
│   └── Feedback
│
├── models.py                 # API request/response models
│   ├── BatchCreate
│   ├── BatchResponse
│   ├── PDFUploadResponse
│   └── BatchDetailResponse
│
├── pdf_parser.py            # PDF parsing logica
│   ├── parse_voorraad_pdf()
│   ├── parse_interfiliaal_pdf()
│   └── validate_pdf()
│
├── routers/
│   ├── batches.py           # Batch endpoints ✅
│   ├── proposals.py         # TODO: Proposals endpoints
│   └── feedback.py          # TODO: Feedback endpoints
│
├── rules/                   # TODO: Rules engine
│   ├── rules_engine.py
│   └── rules_schema.py
│
├── test_batch_api.py        # Test script
└── seed_database.py         # Database initialization

uploads/                     # PDF storage (gitignored)
└── batch_{id}/             # Per-batch directories
```

### Database Schema (SQLite)

```sql
-- Batches
CREATE TABLE batches (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'processing',
    pdf_count INTEGER NOT NULL DEFAULT 0,
    processed_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extra_data JSON
);

-- Batch PDFs
CREATE TABLE batch_pdfs (
    id INTEGER PRIMARY KEY,
    batch_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    parsed_data JSON,
    error_message TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES batches(id)
);

-- Proposals
CREATE TABLE proposals (
    id INTEGER PRIMARY KEY,
    batch_id INTEGER NOT NULL,
    artikelnummer TEXT NOT NULL,
    article_name TEXT NOT NULL,
    current_distribution JSON NOT NULL,
    proposed_distribution JSON NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    reason TEXT,
    applied_rules JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    rejection_reason TEXT,
    FOREIGN KEY (batch_id) REFERENCES batches(id)
);

-- Feedback
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY,
    proposal_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT NOT NULL,
    sentiment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proposal_id) REFERENCES proposals(id)
);
```

---

## 💡 Tips

### Voor Development
1. **Test incrementeel** - Na elke stap testen
2. **Begin simpel** - Statische regels eerst, AI later
3. **Focus op rules engine** - Dit is het hart van het systeem
4. **Use Swagger UI** - Makkelijkste manier om te testen

### Voor Volgende Sessie
1. **Start met test** - Run `test_batch_api.py` om te verifiëren dat alles nog werkt
2. **Check database** - Verify `backend/database.db` bestaat
3. **Check dependencies** - `pip list` in backend venv
4. **Start servers** - Zie GETTING_STARTED.md

---

## ✨ Conclusie

In 1 uur hebben we een solide fundament gelegd:
- ✅ Database schema uitgebreid
- ✅ PDF parsing werkend (beproefd)
- ✅ API endpoints voor batch management
- ✅ Ready voor proposals generatie

**Volgende stap:** Rules engine + Proposals systeem implementeren!

---

## 📖 Zie Ook

- **[[GETTING_STARTED]]** - App starten en testen
- **[[DATABASE]]** - Database setup details
- **[[INTEGRATION]]** - Frontend-backend integratie
- **[[TROUBLESHOOTING]]** - Troubleshooting hulp
- **[[README]]** - Project overzicht

---

**Status:** Foundation compleet - Ready voor proposals! 🎉

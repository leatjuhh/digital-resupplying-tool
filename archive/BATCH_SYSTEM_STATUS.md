# Batch Systeem - Implementatie Status

## ✅ Wat is Klaar (Vanavond - 1 uur werk)

### 1. Database Models ✅
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

### 2. PDF Parser ✅
**Bestand:** `backend/pdf_parser.py`

- Gebruikt **pdfplumber** (bewezen in oud project)
- Functie: `parse_voorraad_pdf(pdf_path)` 
- Extraheert artikelnummers (5-6 cijfers)
- Returns: dict met success, artikelnummers, page_count, etc.

### 3. API Endpoints ✅
**Bestand:** `backend/routers/batches.py`

Endpoints geïmplementeerd:
- `POST /api/batches/create` - Nieuwe batch aanmaken
- `POST /api/batches/{id}/upload` - PDF uploaden naar batch
- `GET /api/batches/{id}` - Batch details + PDF lijst
- `GET /api/batches` - Alle batches (nieuwste eerst)

Features:
- PDF validatie (type check, pdfplumber validate)
- Automatische parsing na upload
- Batch status tracking (processing/completed/failed)
- Foutafhandeling

### 4. Pydantic Models ✅
**Bestand:** `backend/models.py`

Modellen toegevoegd:
- BatchCreate, BatchResponse
- PDFUploadResponse, BatchDetailResponse
- ProposalResponse, FeedbackCreate

### 5. Dependencies ✅
**Geïnstalleerd:**
- pdfplumber==0.11.0
- python-multipart==0.0.9 (voor file uploads)
- sqlalchemy==2.0.36 (upgrade)

### 6. Database Migratie ✅
- Nieuwe tabellen aangemaakt via `seed_database.py`
- Bestaande data behouden (stores, articles)

### 7. Test Script ✅
**Bestand:** `backend/test_batch_api.py`

Test script om te verifiëren:
1. Batch aanmaken
2. PDF uploaden
3. Batch details ophalen

## 🔄 Hoe te Testen

### 📖 Volledige Start Instructies
**Zie: `START_APP.md`** voor complete instructies om de app te starten!

Twee makkelijke manieren:
1. **PowerShell Script** (Aanbevolen): `.\start-dev.ps1`
2. **NPM Concurrently**: `npm run dev`

### Snelle Test van Batch Systeem

#### Optie 1: Automatisch Test Script ⭐
```bash
# In terminal 1: Start de app (zie START_APP.md)
.\start-dev.ps1

# In terminal 2: Run test
cd backend
python test_batch_api.py
```

Het script gebruikt de dummy PDF: `dummyinfo/Interfiliaalverdeling vooraf - 423264.pdf`

Dit test:
- ✅ Batch aanmaken
- ✅ PDF uploaden
- ✅ Parsing (artikelnummers extraheren)
- ✅ Batch details ophalen

#### Optie 2: Interactief met Swagger UI
1. Start de app (zie START_APP.md)
2. Ga naar: **http://localhost:8000/docs**
3. Test endpoints interactief:
   - POST `/api/batches/create` → Body: `{"name": "Test Batch"}`
   - POST `/api/batches/{id}/upload` → Upload PDF bestand
   - GET `/api/batches/{id}` → Zie details + parsed data

## 📊 Wat We Nu Kunnen

### Backend kan nu:
- ✅ Batches aanmaken met een naam
- ✅ Meerdere PDF's uploaden naar één batch
- ✅ PDF's automatisch parsen (artikelnummers extraheren)
- ✅ Status bijhouden per PDF en per batch
- ✅ Foutmeldingen opslaan als parsing mislukt
- ✅ Batch details opvragen met alle PDF's en parsed data

### Voorbeeld Flow:
```
1. User maakt batch aan: "Week 42 - Interfiliaal"
2. User upload PDF #1 → Parse → 50 artikelnummers geëxtraheerd
3. User upload PDF #2 → Parse → 45 artikelnummers geëxtraheerd
4. Batch status = completed (alle PDF's verwerkt)
5. User vraagt batch details op → Ziet beide PDF's + extracted counts
```

## 🚧 Wat Nog Moet (Volgende Sessie)

### Prioriteit 1: Proposals Generatie
**Doel:** Van parsed PDF data → Herverdelingsvoorstellen

Stappen:
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

3. **Feedback Router** (`backend/routers/feedback.py`)
   - `POST /api/feedback` - Feedback indienen
   - `GET /api/feedback` - Alle feedback (admin)

### Prioriteit 2: Frontend Integration
Pagina's toevoegen:
- `/batches` - Overzicht van alle batches
- `/batches/create` - Nieuwe batch + upload UI
- `/batches/[id]` - Batch details met PDF's
- `/proposals` - Gegenereerde voorstellen bekijken

### Prioriteit 3: ChatGPT Integration (Optioneel)
- API key management
- Dynamic rules mode
- Feedback → ChatGPT prompt → Verbeterde regels

## 📝 Code Kwaliteit

### Wat Goed Is:
- ✅ Nederlandse comments overal
- ✅ Type hints (Pydantic models)
- ✅ Error handling
- ✅ Database foreign keys
- ✅ Status tracking
- ✅ Herbruikbaar (beproefd PDF parser)

### Aandachtspunten:
- ⚠️ Sync processing (kan slow worden bij veel PDF's)
  - Later: Async met Celery/background tasks
- ⚠️ Geen authenticatie yet
  - Later: JWT tokens, user roles
- ⚠️ File cleanup (uploads blijven staan)
  - Later: Cleanup job of TTL

## 🎯 Geschatte Tijd voor Volgende Stappen

| Stap | Tijd | Prioriteit |
|------|------|-----------|
| Rules Engine Basis | 1 uur | 🔴 Hoog |
| Proposals Router | 45 min | 🔴 Hoog |
| Test met Dummy Data | 15 min | 🔴 Hoog |
| Feedback Router | 30 min | 🟡 Medium |
| Frontend Batches UI | 1 uur | 🟡 Medium |
| Frontend Proposals UI | 1 uur | 🟡 Medium |
| ChatGPT Integration | 1 uur | 🟢 Laag (optioneel) |

**Totaal voor werkend systeem:** ~3-4 uur

## 🚀 Snel Starten (Voor Volgende Sessie)

### ⭐ Aanbevolen: Cursor Terminal Methode
**Zie: [CURSOR_START_GUIDE.md](CURSOR_START_GUIDE.md)**

```powershell
# Terminal 1 in Cursor:
cd backend
venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000

# Terminal 2 in Cursor:
cd frontend
npm run dev
```

**Voordelen:** Cline kan meekijken, betere debugging, overzichtelijk in Cursor

### Alternatief: PowerShell Script
```powershell
.\start-dev.ps1
```
Opent 2 vensters buiten Cursor (poort 8000 + 3000)

### Alternatief: NPM Concurrently
```powershell
npm run dev
```
Start beide in 1 terminal

### Test het Batch Systeem
```bash
# In 3e Cursor terminal:
cd backend
venv\Scripts\python.exe test_batch_api.py
```

### Of gebruik Swagger UI
Open: **http://localhost:8000/docs**

📖 **Volledige instructies:** Zie `CURSOR_START_GUIDE.md` of `START_APP.md`

## 📚 Relevante Bestanden

```
backend/
├── db_models.py          # Database schemas (Batch, Proposal, etc.)
├── models.py             # API request/response models
├── pdf_parser.py         # PDF parsing logica
├── routers/
│   ├── batches.py        # Batch endpoints ✅
│   ├── proposals.py      # TODO: Proposals endpoints
│   └── feedback.py       # TODO: Feedback endpoints
├── rules/                # TODO: Rules engine
│   ├── rules_engine.py
│   └── rules_schema.py
└── test_batch_api.py     # Test script

uploads/                  # PDF storage (gitignored)
└── batch_{id}/          # Per-batch directories
```

---

## 💡 Tips voor Volgende Sessie

1. **Start met test** - Run `test_batch_api.py` om te verifiëren dat alles nog werkt
2. **Focus op rules engine** - Dit is het hart van het systeem
3. **Begin simpel** - Statische regels eerst, AI later
4. **Test incrementeel** - Na elke stap testen

## ✨ Conclusie

In 1 uur hebben we een solide fundament gelegd:
- Database schema uitgebreid
- PDF parsing werkend (beproefd)
- API endpoints voor batch management
- Ready voor proposals generatie

**Volgende keer:** Rules engine + Proposals systeem implementeren!

**Goed werk! 🎉**

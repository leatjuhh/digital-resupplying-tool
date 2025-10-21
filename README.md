---
tags: [project, overview, main]
type: index
version: 1.1
status: active
---

# Digital Resupplying Tool

Een geautomatiseerde tool voor het beheren van voorraadherverdelingen tussen verschillende winkellocaties.

## 📋 Snelle Links

- **[[GETTING_STARTED]]** - ⭐ Start hier! App starten en testen
- **[[BATCH_SYSTEM]]** - Batch upload & PDF parsing systeem
- **[[DATABASE]]** - Database setup en management
- **[[INTEGRATION]]** - Frontend-backend integratie
- **[[TROUBLESHOOTING]]** - Troubleshooting hulp

## 🎯 Project Status

**Versie:** 1.1  
**Status:** ✅ Batch Systeem Operationeel

### Wat Werkt
- ✅ Backend API (FastAPI) met SQLite database
- ✅ Frontend (Next.js) met shadcn/ui components
- ✅ Batch upload systeem voor PDF's
- ✅ PDF parsing (pdfplumber) met artikelnummer extractie
- ✅ CRUD operaties voor articles en batches
- ✅ Swagger API documentation

### In Development
- ⏳ Proposals generatie (rules engine)
- ⏳ Frontend batch management UI
- ⏳ Feedback systeem

### Roadmap
- 🔜 Rules engine voor herverdelingsvoorstellen
- 🔜 Proposal approval workflow
- 🔜 AI-powered suggestions (ChatGPT)
- 🔜 User authenticatie

## 🚀 Quick Start

**Aanbevolen methode (Cursor):**
```powershell
# Terminal 1 - Backend
cd backend
venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

📖 **Zie [[GETTING_STARTED]] voor alle start methodes**

## 📊 Project Structuur

```
digital-resupplying-tool/
├── frontend/              # Next.js frontend applicatie
├── backend/               # FastAPI backend applicatie
│   ├── routers/          # API endpoints
│   │   ├── articles.py   # Articles CRUD
│   │   └── batches.py    # Batch upload & PDF parsing
│   ├── db_models.py      # Database schemas
│   ├── models.py         # Pydantic API models
│   ├── pdf_parser.py     # PDF parsing logica
│   ├── database.py       # Database configuratie
│   └── seed_database.py  # Database initialisatie
├── archive/              # Oude documentatie (referentie)
└── dummyinfo/            # Test PDF bestanden
```

## 🧪 URLs & Testing

Na starten:
- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs ⭐ Test endpoints hier!
- **Test Page:** http://localhost:3000/test

### Test Batch Systeem
```powershell
# Start app eerst, dan in nieuwe terminal:
cd backend
venv\Scripts\python.exe test_batch_api.py
```

## 🛠️ Technologie Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Python-dotenv** - Environment variable management
- **SQLAlchemy** - Database ORM
- **pdfplumber** - PDF parsing

### Frontend
- **Next.js** - React framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - UI component library

## ⚙️ Environment Variables

### Backend (.env)
```env
BACKEND_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📚 Documentatie

### Hoofd Documentatie
- **[[GETTING_STARTED]]** - Complete start gids
- **[[BATCH_SYSTEM]]** - Batch systeem features & API
- **[[DATABASE]]** - Database setup & schema
- **[[INTEGRATION]]** - Frontend-backend integratie
- **[[TROUBLESHOOTING]]** - Veelvoorkomende problemen

### Specifieke Docs
- Backend API: http://localhost:8000/docs (Swagger UI)
- Frontend: `frontend/PROJECT-OVERVIEW.md`
- Backend: `backend/README.md`

### Archive
Oude documentatie (voor referentie): `archive/`

## 🎯 Voor Ontwikkelaars

### Database Schema
Zie [[DATABASE]] voor complete schema en CRUD operaties.

**Models:**
- Store, Article (basis)
- Batch, BatchPDF (upload systeem)
- Proposal, Feedback (workflow)

### API Endpoints
Zie [[BATCH_SYSTEM]] voor API documentatie.

**Routes:**
- `/api/articles` - Articles CRUD
- `/api/batches` - Batch management
- `/api/batches/{id}/upload` - PDF upload

### PDF Parsing
Zie `backend/pdf_parser.py` voor parsing logica.

**Features:**
- pdfplumber-based extraction
- Artikelnummer detection (5-6 cijfers)
- Error handling & validation

## 📦 GitHub Repository

Dit project wordt actief onderhouden op GitHub met volledige versiebeheer en backup.

**Repository:** Digital Resupplying Tool  
**Branch:** `main` (stabiele code)  
**Workflow:** Zie [[DEVELOPMENT_GUIDE]] voor complete Git workflow

### Belangrijke Links
- **[[CHANGELOG.md]]** - Versiegeschiedenis en wijzigingen
- **[[DEVELOPMENT_GUIDE.md]]** - Development workflow en conventies
- **GitHub Issues** - Bug reports en feature requests

## 🤝 Contributing

Wij verwelkomen bijdragen aan dit project! Volg deze stappen:

1. **Setup Development Environment**
   - Zie [[GETTING_STARTED]] voor complete setup
   - Installeer Git, Python 3.11+, Node.js 18+

2. **Development Workflow**
   - Clone de repository
   - Maak een feature branch (optioneel voor kleine wijzigingen)
   - Commit regelmatig met duidelijke messages
   - Test lokaal voor elke push
   - Push naar GitHub

3. **Code Standards**
   - Python: PEP8, type hints verplicht
   - TypeScript: Prettier formatting
   - Zie [[DEVELOPMENT_GUIDE]] voor complete conventies

4. **Pull Requests**
   - Beschrijf wat je hebt veranderd
   - Link naar relevante issues
   - Zorg dat tests slagen

Voor vragen of suggesties, neem contact op met het development team.

## 📝 License

MIT License - Zie [[LICENSE]] voor details

Copyright (c) 2025 Digital Resupplying Automation Team

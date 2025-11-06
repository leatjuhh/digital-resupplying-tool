# Digital Resupplying Tool

Een geautomatiseerde tool voor het beheren van voorraadherverdelingen tussen verschillende winkellocaties.

---

## 📢 Recent Updates

**Latest Version: v1.5.0** (2025-11-02) 

### ✨ What's New

**🔴 CRITICAL FIX - Authentication Working!**
- ✅ JWT Authentication bug resolved
- ✅ Complete login → protected routes → logout flow functional
- ✅ Mobile network access support added

**📚 New Documentation**
- ✅ Authentication Testing Guide (60+ test scenarios)
- ✅ Mobile Network Access Guide (iOS/Android setup)

**🔧 Latest Improvements** (Since v1.5.0)
- ✅ Filialen sorting fixes - Numerieke sortering in alle tabellen
- ✅ Proposals detail/edit UI verbeteringen
- ✅ Backend sorting utilities geïmplementeerd

[📖 View Full Changelog →](CHANGELOG.md)

---

## 📋 Snelle Links

### Getting Started
- ⭐ **[Quick Start](docs/getting-started/quick-start.md)** - Snel aan de slag
- 📖 **[Installation Guide](docs/getting-started/installation.md)** - Complete setup instructies
- 📱 **[Mobile Network Access](docs/getting-started/mobile-network-access.md)** - iOS/Android testing setup (NIEUW!)
- 🔧 **[Troubleshooting](docs/getting-started/troubleshooting.md)** - Hulp bij problemen

### Guides
- 🚀 **[Cursor Workflow](docs/guides/cursor-workflow.md)** - Optimale AI workflow (AANBEVOLEN!)
- 🔐 **[Authentication Testing](docs/guides/authentication-testing.md)** - Complete test guide (NIEUW!)
- 📦 **[Batch System](docs/guides/batch-system.md)** - PDF upload & parsing
- 🗄️ **[Database Guide](docs/guides/database.md)** - Database management
- 🔗 **[Integration](docs/guides/integration.md)** - Frontend-backend koppeling
- 🎯 **[Redistribution Algorithm](docs/guides/redistribution-algorithm.md)** - Herverdelingslogica

## 🎯 Project Status

**Versie:** 1.3.0  
**Status:** ✅ Herverdelingsalgoritme Compleet! 🎉

### Wat Werkt
- ✅ Backend API (FastAPI) met SQLite database
- ✅ Frontend (Next.js) met shadcn/ui components
- ✅ Batch upload systeem voor PDF's
- ✅ PDF parsing (pdfplumber) met artikelnummer extractie
- ✅ CRUD operaties voor articles en batches
- ✅ Swagger API documentation
- ✅ **Herverdelingsalgoritme** (NIEUW! 🎉)
  - BV consolidatie logica
  - Demand-based allocation
  - Move scoring & optimization
  - Size sequence detection
- ✅ **Proposal Detail & Edit UI** (NIEUW! 🎉)
  - Complete read/write views
  - Live balance validation
  - Visual feedback systeem

### In Development (Quick Wins - 1-2 uur)
- ⏳ Proposals API router (backend/routers/proposals.py)
- ⏳ Database Proposals table
- ⏳ Frontend-backend integratie voor updates
- ⏳ "Genereer Voorstellen" knop in batch view

### Roadmap
- 🔜 Rules engine voor herverdelingsvoorstellen
- 🔜 Proposal approval workflow
- 🔜 AI-powered suggestions (ChatGPT)
- 🔜 User authenticatie

## 🚀 Quick Start

**Aanbevolen: Gebruik dev.ps1 in Cursor terminal** ⭐
```powershell
.\dev.ps1
```

**Dit script:**
- ✅ Voert pre-flight checks uit (venv, database, dependencies, poorten)
- ✅ Initialiseert database automatisch indien nodig
- 🚀 Start beide servers in **dezelfde Cursor terminal**
- 📊 Toont alle logs met gekleurde prefixes: `[BACKEND]` (cyan) en `[FRONTEND]` (groen)

**Alternatief: Direct via npm:**
```bash
npm run dev
```

**URLs na starten:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

📖 **Zie [Quick Start Guide](docs/getting-started/quick-start.md) voor complete start gids & troubleshooting**

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

### Getting Started
- [Quick Start](docs/getting-started/quick-start.md) - Snel beginnen
- [Installation Guide](docs/getting-started/installation.md) - Complete setup
- [Troubleshooting](docs/getting-started/troubleshooting.md) - Problemen oplossen

### User & Developer Guides
- [Cursor Workflow](docs/guides/cursor-workflow.md) - AI-powered development
- [Batch System](docs/guides/batch-system.md) - PDF upload & parsing
- [Database](docs/guides/database.md) - Database management
- [Integration](docs/guides/integration.md) - Frontend-backend koppeling
- [Redistribution Algorithm](docs/guides/redistribution-algorithm.md) - Herverdelingslogica
- [SQL-Based Generation Plan](todo/sql_connection_and_sizedisplay_logic-old-CHATGPT_logic.md) - Automatische generatie uit EasyVoras SQL ⭐ NEW!

### Technical Documentation
- [PDF Extraction System](docs/technical/pdf-extraction-system.md) - PDF parsing details
- [GUI Overview](docs/technical/gui-overview.md) - Frontend architectuur
- [Frontend Consolidation](docs/technical/frontend-consolidation.md) - Frontend refactoring
- Backend API: http://localhost:8000/docs (Swagger UI)
- Frontend: `frontend/PROJECT-OVERVIEW.md`
- Backend: `backend/README.md`

### Contributing
- [Contributing Guidelines](CONTRIBUTING.md) - Hoe bij te dragen
- [Documentation Guidelines](docs/DOCUMENTATION_GUIDELINES.md) - Documentatie regels
- [Changelog](CHANGELOG.md) - Versiegeschiedenis

### Archive
Oude documentatie (referentie): `archive/`

## 🎯 Voor Ontwikkelaars

### Database Schema
Zie [Database Guide](docs/guides/database.md) voor complete schema en CRUD operaties.

**Models:**
- Store, Article (basis)
- Batch, BatchPDF (upload systeem)
- Proposal, Feedback (workflow)

### API Endpoints
Zie [Batch System Guide](docs/guides/batch-system.md) voor API documentatie.

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
**Workflow:** Zie [Contributing Guidelines](CONTRIBUTING.md) voor complete Git workflow

### Belangrijke Links
- **[Changelog](CHANGELOG.md)** - Versiegeschiedenis en wijzigingen
- **[Contributing Guidelines](CONTRIBUTING.md)** - Development workflow en conventies
- **[Documentation Guidelines](docs/DOCUMENTATION_GUIDELINES.md)** - Documentatie regels
- **GitHub Issues** - Bug reports en feature requests

## 🤝 Contributing

Wij verwelkomen bijdragen aan dit project! Volg deze stappen:

1. **Setup Development Environment**
   - Zie [Installation Guide](docs/getting-started/installation.md) voor complete setup
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
   - Zie [Contributing Guidelines](CONTRIBUTING.md) voor complete conventies

4. **Pull Requests**
   - Beschrijf wat je hebt veranderd
   - Link naar relevante issues
   - Zorg dat tests slagen

Voor vragen of suggesties, neem contact op met het development team.

## 📝 License

MIT License - Zie [LICENSE](LICENSE) voor details

Copyright (c) 2025 Digital Resupplying Automation Team

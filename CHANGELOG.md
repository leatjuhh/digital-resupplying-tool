# Changelog

Alle belangrijke wijzigingen aan dit project worden gedocumenteerd in dit bestand.

Het formaat is gebaseerd op [Keep a Changelog](https://keepachangelog.com/nl/1.0.0/),
en dit project volgt [Semantic Versioning](https://semver.org/lang/nl/).

## [1.2.0] - 2025-10-28

### Added
- ✅ **Visual PDF Test Tool** - Comprehensive HTML test report generator
  - Tests alle PDFs in dummyinfo folder
  - Genereert visueel HTML rapport met volledige data tabellen
  - JSON export voor programmatisch gebruik
  - Color-coded status indicatoren (SUCCESS, PARTIAL_SUCCESS, FAILED)
  - Negatieve voorraad detectie en reporting
  - Metadata en voorraad data visualisatie per PDF
- ✅ **PDF Extraction Testing** - Validated extractie accuratesse
  - 7 dummy PDFs succesvol getest (86% success rate)
  - Text-based fallback parser werkend
  - Negatieve voorraad business rules gevalideerd
  - Complete voorraad data extractie met alle filialen en maten

### Testing Results
- 📊 **6/7 PDFs** succesvol geëxtraheerd
- ⚠️ **1/7 PDFs** gedeeltelijk succesvol (negatieve voorraad correct afgehandeld)
- ✅ **100% data volledigheid** - alle filialen, maten en verkocht cijfers
- ✅ **Fallback systeem** functioneert perfect

## [1.1.0] - 2025-10-21

### Features
- ✅ **Batch upload systeem** voor PDF's volledig operationeel
- ✅ **PDF parsing** met pdfplumber voor artikelnummer extractie
- ✅ **FastAPI backend** met SQLite database
- ✅ **Next.js frontend** met shadcn/ui component library
- ✅ **Complete CRUD operaties** voor articles en batches
- ✅ **Swagger API documentation** op `/docs` endpoint
- ✅ **Database seeding** systeem voor development
- ✅ **PowerShell start script** voor eenvoudige development setup

### Backend
- FastAPI framework met uvicorn server
- SQLAlchemy ORM voor database operaties
- Pydantic models voor data validatie
- Router structuur voor API endpoints
- PDF upload en parsing functionaliteit
- CORS configuratie voor frontend integratie

### Frontend
- Next.js 15 met App Router
- TypeScript voor type-safe development
- Tailwind CSS voor styling
- shadcn/ui component library
- Dark/Light mode ondersteuning
- Responsive sidebar navigatie
- Upload interface voor batch PDF's

### Documentatie
- Complete README met project overview
- GETTING_STARTED gids voor nieuwe ontwikkelaars
- BATCH_SYSTEM documentatie
- DATABASE schema documentatie
- INTEGRATION gids voor frontend-backend
- TROUBLESHOOTING handleiding
- SESSION logs voor development tracking

### In Development
- ⏳ **Proposals generatie** met rules engine
- ⏳ **Frontend batch management** UI
- ⏳ **Feedback systeem** voor herverdelingsvoorstellen

### Roadmap
- 🔜 **Rules engine** voor intelligente herverdelingsvoorstellen
- 🔜 **Proposal approval workflow**
- 🔜 **AI-powered suggestions** via ChatGPT integratie
- 🔜 **User authenticatie** systeem
- 🔜 **Email notificaties**
- 🔜 **Export functionaliteit** (PDF rapporten)

## [1.0.0] - 2025-10-20

### Initial Release
- ✅ Basis backend setup (FastAPI)
- ✅ Frontend structuur (Next.js)
- ✅ Database models (SQLAlchemy)
- ✅ API endpoints structuur
- ✅ Development environment setup
- ✅ Project documentatie initialisatie

---

## Versie Nummering

**Format:** MAJOR.MINOR.PATCH

- **MAJOR:** Breaking changes (incompatibele API wijzigingen)
- **MINOR:** Nieuwe features (backwards compatible)
- **PATCH:** Bug fixes (backwards compatible)

## Change Types

- **Added:** Nieuwe features
- **Changed:** Wijzigingen in bestaande functionaliteit
- **Deprecated:** Features die binnenkort verwijderd worden
- **Removed:** Verwijderde features
- **Fixed:** Bug fixes
- **Security:** Security patches

# Changelog

Alle belangrijke wijzigingen aan dit project worden gedocumenteerd in dit bestand.

Het formaat is gebaseerd op [Keep a Changelog](https://keepachangelog.com/nl/1.0.0/),
en dit project volgt [Semantic Versioning](https://semver.org/lang/nl/).

## [Unreleased]

### Fixed - COMBINATIE-MAATBALK ONDERSTEUNING (2026-04-20)

- **`backend/pdf_extract/extract_settings.py`** — nieuw regex-patroon `^(X{0,3}[SML])\/(X{0,3}[SML])$` in `KNOWN_SIZE_PATTERNS`; de table-parser herkent nu `XS/S`, `S/M`, `M/L`, `L/XL`, `XL/XX`, `XL/XXL` als geldige maatkolommen.

- **`backend/pdf_extract/text_parser.py`** — drie fixes:
  - Early-return bij niet-gevonden maatregelrij gaf 4-tuple terug terwijl pipeline een 5-tuple verwacht → `not enough values to unpack (expected 5, got 4)` opgelost
  - Header-detectie: combo-maatpatroon als eerste check toegevoegd (`XS/S|S/M|M/L|L/XL|XL/XX`)
  - `extract_sizes_from_line()`: detecteert en sorteert combo-maten vóór de overige letter-/numeriek-logica

- **`backend/redistribution/constraints.py`** — `COMBO_LETTER_SIZE_ORDER` lijst toegevoegd en `get_size_order()` uitgebreid met een branch die combo-maten correct ordent (`XS/S → S/M → M/L → L/XL → XL/XX`)

- Hiermee verwerkt DRT nu ook voorraadoverzichten met combinatie-maatbalken (bijv. artikel 425462)

### Added - BUNDLE-PLANNER MET HARDE MIN-3 REGEL (2026-04-20)

- **Nieuwe artikel-level bundle-planner** in `backend/redistribution/algorithm.py` — vervangt per-maat greedy voor de receiver-assignment:
  - `generate_moves_for_article(article, params, working_inv)` als entrypoint; schakelbaar via `params.enable_bundle_planner` (default `True`)
  - `_rank_receivers`: composite sort-key `(-total_sales, -series_width, -sum_inv, store_total_inventory, store_code)` garandeert deterministische keuze
  - `_assign_bundle`: feedt elke receiver tot `min_items_per_receiver` (default 3), prefereert ontbrekende maten in de serie
  - `_drain_non_receivers`: forceert non-pick winkels naar 0 om de ≥3-of-0 regel structureel af te dwingen
  - `_consolidate_all_to_top`: R1-uitzondering voor pools < 3 stuks → alles naar top-ranked winkel
  - BV-grenzen gerespecteerd: elke BV-groep wordt onafhankelijk gepland wanneer `enforce_bv_separation=True`

- **Harde bedrijfsregel**: elke winkel eindigt per artikel op **0 stuks of ≥ 3 stuks** (valide maatreeks). Dit lost de issue op dat voorraad werd uitgesmeerd over 9 winkels met 1-2 stuks elk (zichtbaar op proposal 29, artikel 56490).

- **Tiebreaker bij verkoop-gelijkspel**: winkel met lagere totale winkelvoorraad (som álle artikelen) blijft receiver; winkel met hogere totaalvoorraad wordt leeggehaald.

- **`backend/redistribution/constraints.py`** — nieuwe parameters:
  - `min_items_per_receiver: int = 3` (harde drempel voor de bundle-planner)
  - `enable_bundle_planner: bool = True` (feature-flag; op `False` valt het algoritme terug op het legacy per-maat pad)

- **`backend/redistribution/domain.py`** — `StoreInventory.store_total_inventory` veld toegevoegd; `calculate_metrics` accepteert nu een `store_total`-parameter.

- **`backend/db_models.py` + migratie `migrate_add_extra_data.py`** — `pdf_batches.extra_data` (JSON) kolom toegevoegd; slaat `{"store_total_inventory": {...}, "captured_at": <iso>}` op per batch.

- **`backend/routers/pdf_ingest.py`** — `/api/pdf/ingest` endpoint uitgebreid met optionele `store_total_inventory` form-parameter (JSON-string); wordt opgeslagen in `PDFBatch.extra_data`.

- **`backend/redistribution/algorithm.py`** — `load_article_data` en `generate_redistribution_proposals_for_batch` lezen de totals uit `batch.extra_data` en zetten ze per store via `calculate_metrics(store_total=...)`.

- **Frontend — batch-aanmaak uitgebreid met totale-voorraad-invoer:**
  - `frontend/lib/stores.ts` (nieuw): `STORE_LIST` constante met de 8 MC Company filialen (6, 8, 9, 11, 12, 13, 31, 38)
  - `frontend/components/uploads/store-totals-form.tsx` (nieuw): grid met 8 numerieke inputs + `parseStoreTotals()` validator
  - `frontend/components/uploads/uploads-page-client.tsx`: integreert het formulier; submit wordt geblokkeerd tot alle 8 waardes ≥ 0 zijn ingevuld; waardes worden meegestuurd in `api.pdf.uploadPDFs(files, name, storeTotalInventory)`

- **Tests** — `backend/test_bundle_planner.py` (9 tests, allen groen):
  - `test_min_3_hard_rule_no_store_ends_with_1_or_2` — R1 afgedwongen
  - `test_under_3_total_all_to_one_store` — R1-uitzondering
  - `test_sales_tie_lower_store_total_wins_as_receiver` — R3 tiebreaker
  - `test_bv_scope_respected_no_cross_bv_moves` — R5 BV-grens
  - `test_top_seller_gets_most_inventory` — R2 ranking
  - `test_pool_divides_into_correct_number_of_receivers` — pool/3 caps
  - `test_isolated_bv_with_under_3_consolidates_within_bv` — BV-isolatie bij consolidatie
  - `test_total_moves_conserve_inventory` — geen stuks verloren
  - `test_feature_flag_off_falls_back_to_legacy` — feature-flag werkt

### Removed - DEAD RULES-SETTINGS (2026-04-20)

- **`frontend/components/settings/settings-rules.tsx`** verwijderd — de 4 velden (`min_stock_per_store=2`, `max_stock_per_store=10`, `min_stores_per_article=3`, `sales_period_days=30`) werden nergens in `backend/redistribution/` gelezen en conflicteerden visueel met de nieuwe harde min-3 regel (UI zei "min 2", algoritme dwong min 3 af).

- **`frontend/app/settings/settings-page-client.tsx`** — tabblad "Regels" verwijderd, inclusief `canManageRules` permission-check.

- **`frontend/lib/api.ts`** — `RulesSettings` interface + `api.settings.getRules/updateRules` endpoints verwijderd.

- **`backend/routers/settings.py`** — `/api/settings/rules/all` endpoint + rules-category permissiecheck verwijderd.

- **`backend/seed_database.py`** — 4 rules-rows uit settings-seed verwijderd.

- **Migratie `backend/migrate_drop_rules_settings.py`** — verwijdert bestaande `category='rules'` rows uit de settings-tabel van actieve databases.

### Added - STORE-EXCLUSIELIJST & UI-POLISH (2026-04-18)

- **`backend/redistribution/store_config.py`** (nieuw) — centrale exclusielijst voor niet-herverdeelbare filialen:
  - `NON_REDISTRIBUTION_STORES`: outlet-filialen (14, 15, 16, 39), administratieve filialen (0, 2, 3, 27, 99) en gesloten filiaal (35)
  - `is_redistribution_candidate(store_code)` als enkelvoudige toegangspoort voor het algoritme
  - Filialen in deze lijst worden volledig uitgesloten als bron én bestemming; hun voorraad telt niet mee in batch-totalen

- **`backend/redistribution/algorithm.py`** — integreert `is_redistribution_candidate()`:
  - `calculate_batch_store_totals`: filtert niet-kandidaten uit bij groeperen van batch-voorraad
  - `load_article_data`: slaat records van uitgesloten filialen over bij het opbouwen van store-data

- **`frontend/components/proposals/proposal-detail.tsx`** — rijkere metadataweergave:
  - `parseHoofdgroep()`: strippt `Artikelgroep : X` suffix uit ruwe Hoofdgroep-string
  - `parseSeizoenjaarInfo()`: splitst seizoenjaar-veld in jaar, collectie en bestelcode
  - `getColorSwatch()`: vertaalt kleurnaam naar hex-achtergrond voor visueel kleurindicatortje
  - `MetaField` component: consistent label+waarde blokje met truncatie
  - Bestelcode-resolutie: eigen veld → parsed seizoenjaar → artikelnummer als fallback

- **`frontend/app/proposals/[id]/page.tsx`** — Tabs in proposal-header:
  - Voorstel / Analyse tabs naast de actieknoppen in de header
  - `DashboardHeader` ontvangt nu de tabs en acties als één gegroepeerde kindcomponent

- **`frontend/app/login/login-page-client.tsx`** — LiveStat widget op loginpagina:
  - `LiveStat` component met flash-animatie bij update
  - Toont live telling van verdelingen, filialen en trends

- **`frontend/components/auth/network-background.tsx`** — achtergrondanimatie herschreven:
  - Magazijn + artikel-nodes vervangen door algoritme-node + winkelknopen
  - Herverdelingsflows gevisualiseerd als oranje balken (surplus → shortage)
  - Surplus en shortage als gekleurde ringindicatoren per winkelknoop

### Fixed - DB SCHEMA MISMATCH FEEDBACK (2026-04-18)

- **`feedback.rating` en `feedback.comment`** waren `NOT NULL` in de database maar `nullable=True` in het SQLAlchemy-model — dit blokkeerde proposal-approval met een 500-fout
  - Database gemigreerd via eenmalig script (tabel gerecreëerd, bestaande data behouden)
  - Fout: `sqlite3.IntegrityError: NOT NULL constraint failed: feedback.rating` bij `POST /api/pdf/proposals/{id}/approve`

### Changed - ALGORITME VEREENVOUDIGD (2026-03-30)

- **Herverdelingsalgoritme vereenvoudigd** van ~2.800 naar ~1.400 LOC
  - `optimizer.py` verwijderd (339 LOC) — move-consolidatie via swap-iteraties is overkill bij 8 filialen
  - Multi-factor scoring (demand 70% / series 20% / efficiency 10%) vervangen door puur demand-gebaseerde scoring
  - Size sequence detectie en penalties/bonussen verwijderd (onbewezen waarde)
  - `OptimizationParams` en 20+ ongebruikte configuratieparameters verwijderd
  - `ConsolidationMetrics`, `OptimizationExplanation`, `SwapDetail`, `SizeSequence` domain types verwijderd
  - `/front/` directory verwijderd (1 bestand, volledig dood)

- **Behouden kernlogica:**
  - Greedy matching per maat (surplus → shortage, gesorteerd op demand)
  - BV-constraint en BV-consolidatie
  - Situatieclassificatie shadow mode (LOW/MEDIUM/HIGH/PARTIJ)
  - Volledige API-compatibiliteit (alle endpoints en response-velden werken)

- **Motivatie:** De codebase was nodeloos complex gegroeid voor de huidige schaal (8 filialen, 2 BV's). Het vereenvoudigde algoritme is transparanter, makkelijker te valideren tegen echte herverdeeldata, en vormt een betere basis voor toekomstige iteraties.

### Added - SQL-BASED GENERATION DOCUMENTATION 📚

- 📋 **SQL-Based Generation Specificatie** - Complete implementatie plan voor automatische generatie
  - Document: `todo/sql_connection_and_sizedisplay_logic-old-CHATGPT_logic.md`
  - 50+ pagina's uitgebreide technische specificatie
  - Bridge tussen oude GPT-4o inzichten en huidige implementatie
  - Complete architectuur voor SQL → ArtikelVoorraad transformatie
  - Maatbalk systeem met learning via PDF uploads
  - 7-fase implementatie roadmap (~9 weken)

- 🗄️ **Database Schema Planning**
  - Nieuwe tabel: `maatbalk_mappings` met 13 positie kolommen
  - Seed data voor 7 bekende maatbalken (1, 2, 7, 9, 10, 20, 21)
  - ArtikelVoorraad uitbreidingen: `source` ('pdf'/'sql') en `maatbalk_id`
  - PDF learning systeem voor auto-detectie nieuwe maatbalken

- 🔌 **Backend Services Specificatie**
  - `backend/sql_extract/evoras_connector.py` - SSH + MySQL connector
  - `backend/sql_extract/transformer.py` - VOORRAAD1-13 → maat labels
  - `backend/routers/sql_ingest.py` - `/api/sql-ingest/generate` endpoint
  - Complete SQL queries met alle Interfiliaalverdeling velden

- 🎨 **Frontend Implementation Plan**
  - Update `generate-proposals.tsx` met echte API calls
  - Tekstinvoer voor artikelnummers (newline-separated)
  - Progress tracking via polling
  - Error handling voor onbekende maatbalken

- 🔐 **Security Architecture**
  - Intern netwerk: Read-only SQL user setup scripts
  - Toekomstige internet deployment: VPN + API gateway architectuur
  - Connection pooling en query sanitization
  - Audit logging voor SQL operations

- 🧪 **Testing Strategie**
  - Unit tests voor maatbalk mappings en transformers
  - Integration tests voor end-to-end SQL flow
  - Validation tests: SQL vs PDF output vergelijking
  - Performance benchmarks voor batch operations

### Implementation Phases
**Fase 1: Foundation** (Week 1-2)
- Create `maatbalk_mappings` tabel + seed data
- Migrate `ArtikelVoorraad` schema
- Setup read-only SQL user
- Test SSH + MySQL connectie

**Fase 2: Backend Core** (Week 3-4)
- Implementeer `EvorasConnector` class
- Implementeer `SQLDataTransformer` class
- Test met bekende artikelen (423423, 54448)
- Unit tests voor transformer

**Fase 3: API Integration** (Week 5)
- Implementeer `/api/sql-ingest/generate` endpoint
- Error handling voor onbekende maatbalken
- Logging en monitoring
- Integration tests

**Fase 4: Frontend** (Week 6)
- Update `generate-proposals.tsx` met API call
- Tekstinvoer UI voor artikelnummers
- Progress tracking (real-time)
- Error weergave

**Fase 5: Maatbalk Learning** (Week 7)
- Extract maat labels uit PDF header
- Auto-create maatbalk mappings
- UI waarschuwing bij onbekende maatbalk

**Fase 6: Testing & Validation** (Week 8)
- Test 20+ artikelen SQL vs PDF
- Edge cases testing
- Performance optimalisatie
- Security audit

**Fase 7: Deployment** (Week 9)
- Production deployment
- Monitor eerste SQL generations
- User training
- Feedback verzameling

### Key Architecture Decisions
| Beslissing | Rationale |
|-----------|-----------|
| **Parallel systems (PDF + SQL)** | Beide blijven beschikbaar voor flexibiliteit |
| **Dezelfde ArtikelVoorraad structuur** | Algoritme blijft ongewijzigd, minimale impact |
| **Maatbalk learning via PDF** | Automatisch nieuwe maatbalken "trainen" |
| **Error bij onbekende maatbalk** | Gebruiker moet eerst PDF uploaden |
| **Source kolom in UI** | Transparantie over databron (PDF/SQL) |
| **Read-only SQL user** | Security best practice |
| **Tekstinvoer artikelnummers** | Eenvoudig kopiëren uit Excel/tekst |

### SQL Query Specification
- Volledige query met ALLE Interfiliaalverdeling velden
- JOIN van evlgfil + efiliaal + eplu tabellen
- Fallback strategie voor lege `eplu` tabel
- Parameterized queries met PyMySQL
- MAATBALK veld KRITIEK voor maat interpretatie

### Data Flow
```
[EasyVoras SQL] → [SQL Connector] → [Maatbalk Mapping] 
    → [Data Transformer] → [ArtikelVoorraad + source='sql'] 
    → [Bestaand Algoritme] → [Proposals] → [Zelfde UI]
```

### Historical Context
- Oude GPT-4o gesprekken over SQL connectie behouden
- Basis SQL queries gedocumenteerd (evlgfil + efiliaal)
- BV-grenzen en maatbalk logica uitgebreid beschreven
- SSH → MySQL workflow gedocumenteerd

### Open Questions
- [ ] Maatbalk fallback als `eplu` leeg blijft?
- [ ] Batch size limit voor SQL generatie?
- [ ] Caching strategie voor herhaalde artikelen?
- [ ] Sync frequency tussen EasyVoras en DRT?
- [ ] Top 40 integratie in v2.1?

### Document Status
**Van:** Oude chatgeschiedenis (historisch, 15 pagina's)  
**Naar:** Complete v2.0 implementatie spec (50+ pagina's)  
**Status:** ✅ Compleet en klaar voor implementatie

### Added - BASELINE HERVERDELINGSALGORITME PLANNING 🎯

- 📋 **Baseline Implementatie Plan** - Complete roadmap voor geavanceerd algoritme
  - 6-fase implementatie plan in `docs/technical/baseline-implementation-plan.md`
  - Gap analyse tussen huidig en gewenst algoritme
  - Gedetailleerde technische specificaties per fase
  - Success criteria en testing strategie
  - ~4 weken implementatie tijdlijn

- 📝 **Fase 1: Situatie Classificatie** (2-3 dagen) ⭐ CRITICAL PATH
  - Todo: `todo/baseline-phase-1-situation-classifier.md`
  - Detecteert automatisch HIGH_STOCK (40-56), LOW_STOCK (<25), MEDIUM_STOCK, PARTIJ (>56)
  - `SituationThresholds` configureerbaar per omgeving
  - Basis voor situatie-specifieke strategieën
  - Dependencies: Geen (kan direct starten)

- 📝 **Fase 2: Strategieën Implementatie** (4-5 dagen) ⭐ CRITICAL PATH
  - Todo: `todo/baseline-phase-2-strategies.md`
  - Strategy Pattern architectuur met 4 strategieën:
    - `HighStockStrategy` - Behoud series in veel winkels
    - `LowStockStrategy` - Concentreer op top-X winkels
    - `PartijStrategy` - Agressievere herverdeling
    - `DefaultStrategy` - Fallback (huidig greedy)
  - Dependencies: Fase 1 (situatie classificatie)

- 📝 **Fase 3: Artikel Categorie System** (2-3 dagen)
  - Todo: `todo/baseline-phase-3-categories.md`
  - Keyword-based detectie (jassen, broeken, jurken, shirts, etc.)
  - Categorie-specifiek beleid (jassen blijven in meer winkels)
  - `CategoryPolicy` per artikel type
  - Dependencies: Fase 2 (strategies moeten category-aware zijn)

- 📝 **Fase 4: Intelligente Prioritering** (2-3 dagen)
  - Todo: `todo/baseline-phase-4-priority.md`
  - Multi-factor priority scoring:
    - Verkoop ratio (40%) - klasieke demand
    - Absolute verkoop (25%) - top sellers voorkeur
    - Serie compleetheid (20%) - bijna-complete serie bonus
    - Categorie modifier (10%) - jassen vs shirts
    - BV relatief (5%) - prestatie binnen BV
  - BV-level priority ranking
  - Dependencies: Fase 3 (gebruikt category policies)

- 📝 **Fase 5: Maat Compensatie** (1-2 dagen)
  - Todo: `todo/baseline-phase-5-compensation.md`
  - Compensatie voor ontbrekende maten in LOW_STOCK situaties
  - Voorkeur volgorde:
    1. Dubbele toewijzing naburige maat
    2. Buitenliggende maat (S/XXL)
    3. Één maat verder
  - Alleen voor top-X winkels met incomplete series
  - Dependencies: Fase 4 (gebruikt priority ranking)

- 📝 **Fase 6: Feedback & Iteratie System** (3-4 dagen) 🔴 HIGH PRIORITY
  - Todo: `todo/baseline-phase-6-feedback.md`
  - Human-in-the-loop feedback systeem
  - Database schema: `ProposalFeedback`, `AlgorithmConfig` tables
  - Config versioning en activation systeem
  - Manuele analyse en parameter tuning (minimale AI)
  - Admin UI voor feedback review en config management
  - Dependencies: Fase 5 (complete baseline eerst)

### Baseline Architecture
**Nieuwe Modules:**
```
backend/redistribution/
├── situation_classifier.py      # Fase 1
├── article_categories.py        # Fase 3
├── size_compensation.py         # Fase 5
├── feedback_analyzer.py         # Fase 6
└── strategies/                  # Fase 2
    ├── base.py
    ├── high_stock.py
    ├── low_stock.py
    ├── partij.py
    └── default.py
```

**Updates:**
- `algorithm.py` - Strategy pattern integration
- `constraints.py` - Nieuwe thresholds en params
- `scoring.py` - Enhanced multi-factor scoring
- `domain.py` - Priority score tracking

### Success Criteria
**Baseline V1.0 (Na Fase 1-2):** ⭐ MVP - 2 weken
- Algoritme detecteert situaties correct
- HIGH_STOCK: behoudt series in veel winkels
- LOW_STOCK: concentreert op top-X
- Output vergelijkbaar met manuele beslissingen

**Baseline V2.0 (Na Fase 3-4):** +1 week
- Jassen worden anders behandeld dan shirts
- Multi-factor priority scoring
- Categorie beleid configureerbaar

**Baseline V3.0 (Na Fase 5-6):** +1 week
- Maat compensatie werkend
- Feedback capture operationeel
- Iteratieve verbetering framework

**Total: ~4 weken voor volledige baseline**

### Design Principles
- 🎯 **Manuele werkwijze als referentie** - Algoritme volgt ervaren gebruiker
- 🔧 **Configureerbaar** - Parameters aanpasbaar via settings
- 📊 **Testbaar** - Elke fase met unit en integration tests
- 🔄 **Iteratief** - Verbetering via user feedback
- 🏗️ **Modulair** - Strategy pattern voor flexibiliteit

### Test Strategy
- Unit tests per module (>80% coverage)
- Integration tests met `/dummyinfo/*.pdf` data
- User acceptance testing per fase
- Performance benchmarks (geen regressies)

### Added
- ✅ **Filialen Sortering** - Numerieke sortering van filialen in alle tabellen
  - Backend sorting utilities in `backend/utils.py`
  - Drie helper functies: `extract_store_code_numeric()`, `sort_stores_by_code()`, `sort_store_ids()`
  - Integr atie in API endpoint `/api/pdf/proposals/{proposal_id}/full`
  - Consistente sortering aan de bron (API level)
  - Voorkomt lexicografische bug (10 voor 2)
  - Geen frontend wijzigingen nodig - backend levert gesorteerde data
  - Test suite met 100% pass rate (`test_store_sorting_simple.py`)
  - Volledige documentatie in `docs/sorting-filialen.md`

- 📚 **Proposals Documentatie** - Uitgebreide diagnostische documentatie
  - `docs/proposals_status.md` - Status inventarisatie en diagnose
  - `docs/proposals_changes.md` - Wijzigingen overzicht
  - `docs/proposals_tests.md` - Test resultaten
  - Root cause analyse voor proposal visibility issues

- 🧪 **Testing & Verificatie Scripts**
  - `backend/test_store_sorting.py` - Uitgebreid sorting test
  - `backend/test_store_sorting_simple.py` - Compacte sorting test
  - `backend/check_proposals_db.py` - Database proposals checker
  - `backend/check_proposal_detail.py` - Proposal detail verificatie

- 📝 **Todo Items** - Planning en bug tracking
  - `todo/bug_verkocht_kolom_summing_instead_of_source.md` - Verkocht kolom bug
  - `todo/verify_proposals_use_extracted_sales.md` - Sales data verificatie
  - `todo/review_proposal_optimaal_verdeeld_422557.md` - Optimaal verdeelde proposal review
  - `todo/next_session_checklist.md` - Next session planning

### Changed
- 🔧 **Backend API Updates** - `backend/routers/pdf_ingest.py`
  - Import van `sort_stores_by_code` en `sort_store_ids` utilities
  - Implementatie van numerieke sortering in proposal endpoints
  - Improved data consistency in API responses

- 🎨 **Frontend Proposal Components** - UI verbeteringen
  - `frontend/components/proposals/proposal-detail.tsx` - Enhanced read-only view
  - `frontend/components/proposals/editable-proposal-detail.tsx` - Improved edit functionality
  - Better data handling en error states
  - Improved user feedback en visual cues

### Technical Details
**Sorting Implementation:**
- O(n log n) sorting performance (<1ms voor typische dataset)
- Handles edge cases: leading zeros, invalid codes, whitespace
- Primary sort: numerieke waarde (1, 2, 10, 100)
- Secondary sort: alfabetisch op naam
- Backwards compatible - geen breaking changes

**Impact:**
- Betere user experience door consistente volgorde
- Voorkomt verwarring bij filiaal herkenning
- Professional appearance in alle tabellen
- Foundation voor toekomstige sorting features

### Testing
- ✅ 100% test pass rate voor sorting utilities
- ✅ Database queries verified
- ✅ API endpoints validated
- ✅ Frontend components render correct

### Documentation
- Complete technical documentation in `docs/sorting-filialen.md`
- Proposals diagn ose documentatie in `docs/`
- Todo items voor bug tracking en planning
- Session log bijgewerkt in `docs/sessions/2025-11-02.md`

## [1.5.0] - 2025-11-02

### Fixed - CRITICAL BUG 🔴
- ✅ **JWT Authentication Bug** - Login flow nu volledig werkend
  - **Probleem:** Login succesvol maar `/api/auth/me` gaf 401 "Token kon niet gevalideerd worden"
  - **Oorzaak:** JWT "sub" claim was integer in plaats van string (RFC 7519 vereist string)
  - **Oplossing:** Conversie naar string bij token creatie, terug naar int bij validatie
  - **Bestanden:** `backend/routers/auth.py`, `backend/auth.py`
  - **Impact:** Volledige auth flow werkt nu end-to-end (login → protected routes → logout)
  - **Test Script:** `backend/test_complete_auth.py` voor validatie

### Added - NEW FEATURES & DOCUMENTATION 📚
- ✅ **Authentication Testing Guide** (`docs/guides/authentication-testing.md`)
  - 60+ test scenarios met step-by-step instructies
  - Test credentials voor admin/user/store roles
  - Login/logout flow tests
  - Session management tests (Remember Me, auto-refresh, expiry)
  - Role-based access control tests
  - Error handling en edge case tests
  - Visual/UX tests (loading states, toasts, modals)
  - Testing best practices en bug reporting guidelines
  
- ✅ **Mobile Network Access** (`docs/getting-started/mobile-network-access.md`)
  - Complete guide voor iOS/Android toegang vanaf lokaal netwerk
  - Handmatige en geautomatiseerde setup instructies
  - Uitgebreide troubleshooting sectie
  - Network security notes
  - Tips voor stabiel IP address
  - FAQ sectie
  
- ✅ **Mobile Setup Automation** (`setup-mobile.ps1`)
  - PowerShell script voor automatische configuratie
  - Detecteert lokaal IP address automatisch
  - Update frontend `.env.local` met correcte API URL
  - Color-coded output met duidelijke instructies
  - Gebruiksvriendelijke setup in 3 stappen

### Changed - TECHNICAL IMPROVEMENTS 🔧
- 🔧 **Backend Host Binding** - Backend luistert nu op `0.0.0.0` (alle interfaces)
  - File: `backend/.env` → `BACKEND_HOST=0.0.0.0`
  - Maakt mobiele toegang mogelijk

- 🔧 **CORS Configuration** - Uitgebreid voor lokale netwerk IP's
  - Regex pattern: `http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.\d+\.\d+\.\d+):3000`
  - Support voor alle private network ranges (192.168.x.x, 10.x.x.x, 172.x.x.x)
  
- 🔧 **Frontend API Configuration** - Dynamische API URL via environment variable
  - File: `frontend/lib/api-client.ts`
  - Variable: `NEXT_PUBLIC_API_URL` (defaults to localhost:8000)
  - Configureerbaar via `frontend/.env.local`

### Testing
- ✅ End-to-end auth flow gevalideerd met `test_complete_auth.py`
- ✅ Mobile network access getest op iOS/Android devices
- ✅ All test scenarios in authentication-testing.md gedocumenteerd

### Documentation Structure
**Nieuwe Documentatie:**
```
docs/
├── guides/
│   └── authentication-testing.md    (NEW - 600+ lines)
└── getting-started/
    └── mobile-network-access.md     (NEW - 400+ lines)
    
Root:
└── setup-mobile.ps1                 (NEW - 80 lines)
```

### Impact
🎊 **Production-Ready Authentication!**
- Login/logout flow volledig functioneel
- Session management met auto-refresh
- Role-based access control werkend
- Mobile/tablet testing nu mogelijk
- Comprehensive testing documentatie

### Security Notes
⚠️ **Mobile Network Access:**
- Development configuratie ALLEEN voor local testing
- NIET geschikt voor productie zonder HTTPS/SSL
- Backend luistert op alle interfaces (0.0.0.0)
- CORS staat lokale netwerk origins toe
- Voor productie: gebruik specifieke IP whitelisting + HTTPS

### Related Files Changed
**Backend:**
- `backend/routers/auth.py` - JWT sub claim fix (3 locaties)
- `backend/auth.py` - Token validation fix
- `backend/test_complete_auth.py` - Nieuwe test suite
- `backend/.env` - Host binding op 0.0.0.0
- `backend/main.py` - CORS regex update

**Frontend:**
- `frontend/lib/api-client.ts` - Configureerbare API URL
- `frontend/.env.local` - API URL configuratie (created by setup script)

**Documentation:**
- `docs/guides/authentication-testing.md` - Nieuwe testing guide
- `docs/getting-started/mobile-network-access.md` - Nieuwe setup guide
- `backend/AUTH_FIX_SUMMARY.md` - Technical write-up van JWT fix

**Scripts:**
- `setup-mobile.ps1` - Nieuwe automation script

### Breaking Changes
Geen breaking changes - backwards compatible

### Migration Notes
Voor mobile access:
1. Run `.\setup-mobile.ps1` (automatisch)
2. Of handmatig edit `frontend/.env.local` met je lokale IP
3. Start servers met `.\dev.ps1`
4. Toegang via `http://[JE-IP]:3000` op mobile device

Om terug te gaan naar localhost:
- Edit `frontend/.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Of verwijder het bestand

---

## [1.4.0] - 2025-10-31

### Added - MAJOR DOCUMENTATION REORGANIZATION 📚
- ✅ **Documentation Guidelines** (`docs/DOCUMENTATION_GUIDELINES.md`)
  - Strikte regels om wildgroei te voorkomen
  - Maximum 4 .md bestanden in root (README, CHANGELOG, CONTRIBUTING, LICENSE)
  - Template voor nieuwe documentatie met YAML frontmatter
  - Bestandsnaming conventies (lowercase-with-dashes.md)
  - Periodic maintenance checklist

- ✅ **Contributing Guidelines** (`CONTRIBUTING.md`)
  - Samenvoeging van DEV_MANAGEMENT.md en DEVELOPMENT_GUIDE.md
  - Code of Conduct
  - Development workflow instructies
  - Code conventions (Python & TypeScript)
  - Commit guidelines met types
  - Testing instructies
  - Pull request proces
  - Dependency management
  - Database migratie instructies

- ✅ **Gestructureerde docs/ folder**
  - `docs/getting-started/` - Voor nieuwe gebruikers
    - quick-start.md
    - installation.md (was GETTING_STARTED.md)
    - troubleshooting.md
  - `docs/guides/` - User & developer guides
    - cursor-workflow.md
    - batch-system.md
    - database.md
    - integration.md
    - redistribution-algorithm.md
  - `docs/technical/` - Technische documentatie
    - pdf-extraction-system.md
    - gui-overview.md (was GUI-COMPLETE-OVERVIEW.md)
    - frontend-consolidation.md (was FRONTEND_CONSOLIDATIE_RAPPORT.md)
    - dummy-data-audit.md
    - next-steps-analysis.md
  - `docs/sessions/` - Development session logs
    - 2025-10-20.md (was SESSION_20_OKT_2025.md)
    - 2025-10-29.md (was SESSION_29_OKT_2025.md)

### Changed
- 📝 **README.md** - Volledig geüpdatet met nieuwe documentatie links
  - Wiki-style [[links]] vervangen door relatieve markdown links
  - Georganiseerd in secties (Getting Started, Guides, Technical, Contributing)
  - Alle links verwijzen nu naar docs/ structuur
  
- 📁 **Root Directory** - Van 19 naar 4 .md bestanden
  - Voor: 19 markdown bestanden verspreid over root
  - Na: 4 markdown bestanden (README, CHANGELOG, CONTRIBUTING, LICENSE)
  - 15 bestanden verplaatst naar gestructureerde docs/ folders

- 🗂️ **Bestandsnaming** - Geconsistentiseerd naar lowercase-with-dashes
  - GUI-COMPLETE-OVERVIEW.md → gui-overview.md
  - FRONTEND_CONSOLIDATIE_RAPPORT.md → frontend-consolidation.md
  - SESSION_20_OKT_2025.md → 2025-10-20.md
  - GETTING_STARTED.md → installation.md

### Removed
- ❌ DEV_MANAGEMENT.md (geïntegreerd in CONTRIBUTING.md)
- ❌ DEVELOPMENT_GUIDE.md (geïntegreerd in CONTRIBUTING.md)
- ❌ Alle ongeorganiseerde .md bestanden uit root

### Impact
🎊 **Van Wildgroei → Professionele Structuur!**
- Clean root directory (GitHub best practice)
- Duidelijke categorisatie van documentatie
- Gemakkelijker navigeren voor nieuwe developers
- Schaalbare documentatie structuur
- Preventie systeem tegen toekomstige wildgroei
- Beter voor GitHub presentatie
- Makkelijker te onderhouden

### Preventie
⚠️ **Belangrijk voor Toekomstige Wijzigingen:**
- Lees ALTIJD `docs/DOCUMENTATION_GUIDELINES.md` VOOR je nieuwe documentatie toevoegt
- Nieuwe .md bestanden NOOIT in root plaatsen (behalve de 4 toegestane)
- Gebruik lowercase-with-dashes.md naming
- Update README.md wanneer je nieuwe docs toevoegt
- Volg de YAML frontmatter template

## [1.3.1] - 2025-10-29

### Added
- ✅ **MC Company Branding**
  - MC Company logo toegevoegd aan sidebar met witte achtergrond voor contrast
  - Logo is klikbaar en linkt naar https://mc-company.nl/
  - Logo wordt gebruikt als favicon in browser tab
  - "DRT" afkorting prominent weergegeven met volledige uitleg "Digital Resupplying Tool"
  
- ✅ **Icon-Only Collapsible Sidebar**
  - Sidebar kan ingeklapt worden naar icon-only mode (~48px breed)
  - In collapsed state blijven alle navigatie iconen zichtbaar
  - Tooltips tonen bij hover over iconen
  - Keyboard shortcut: Ctrl+B / Cmd+B om te togglen
  - State wordt bewaard in cookie (blijft na refresh)
  
- ✅ **Responsive Layout Fixes**
  - `SidebarInset` component toegevoegd voor correcte content spacing
  - Content past automatisch aan bij collapsed/expanded sidebar
  - Smooth transitions tussen sidebar states
  - Geen overlap meer tussen sidebar en content

### Changed
- 🎨 **App Titel**: "Digital Resupplying Tool" → "DRT - Digital Resupplying Tool"
- 🎨 **Sidebar Logo**: Vergroot van 32x32 naar 48x48 pixels
- 🎨 **Sidebar Collapsible Mode**: Van "offcanvas" naar "icon" voor betere UX
- 🎨 **Branding Consistentie**: DRT naam doorheen hele applicatie

### Technical
- Updated `frontend/components/app-sidebar.tsx` met logo en branding
- Updated `frontend/app/layout.tsx` met SidebarInset en favicon metadata
- Copied `dummyinfo/applogo/smalltransp.png` → `frontend/public/mc-company-logo.png`

## [1.3.0] - 2025-10-29

### Added - MAJOR RELEASE 🎉
- ✅ **Herverdelingsalgoritme Volledig Geïmplementeerd** (CRITICAL FEATURE!)
  - Complete algoritme logica in `backend/redistribution/algorithm.py`
  - Analyseert voorraad per winkel en genereert optimale herverdelingen
  - Detecteert overschotten en tekorten op basis van gemiddelden
  - Greedy matching algoritme voor efficiënte herverdeling
  - Altijd proposals genereren (ook voor optimaal verdeelde artikelen)

- ✅ **BV Consolidatie Logica**
  - Detecteert gefragmenteerde BV's (≤3 items totaal)
  - Consolideert automatisch naar best verkopende winkel binnen BV
  - Voorkomt onnodige fragmentatie van voorraad

- ✅ **Demand-Based Allocation**
  - Hoge verkoop winkels krijgen prioriteit bij herverdeling
  - Verkoop cijfers worden gewogen in allocatie beslissingen
  - Intelligente prioritering van moves

- ✅ **Size Sequence Detection**
  - Detecteert opeenvolgende maatreeksen (XXS-XXXL, 32-48)
  - Support voor letter maten, numerieke maten en custom maten
  - Gestructureerde maat volgorde voor alle artikelen

- ✅ **Move Scoring System** (`backend/redistribution/scoring.py`)
  - Kwaliteit score voor elke move (0.0 - 1.0)
  - Factoren: demand delta, stock balance, BV compliance, move efficiency
  - Filtering van lage kwaliteit moves (< 0.2 score)

- ✅ **Move Optimization** (`backend/redistribution/optimizer.py`)
  - Consolideert meerdere kleine moves tussen zelfde winkels
  - Reduceert totaal aantal transacties
  - Behoudt totale herverdeling effect

- ✅ **Constraint System** (`backend/redistribution/constraints.py`)
  - Configureerbare parameters voor algoritme
  - Oversupply/undersupply thresholds
  - Min/max move quantities
  - BV separation enforcement
  - Optimization toggles

- ✅ **Domain Models** (`backend/redistribution/domain.py`)
  - ArticleStock - Complete artikel voorraad en metadata
  - StoreInventory - Winkel voorraad + verkoop cijfers + metrics
  - Move - Individuele herverdeling (van → naar)
  - Proposal - Complete voorstel met alle moves
  - SizeSequence - Opeenvolgende maatreeks detectie

- ✅ **BV Configuration** (`backend/redistribution/bv_config.py`)
  - BV naar winkel mapping
  - Inter-BV move validatie
  - Separation rule enforcement

- ✅ **Proposal Detail UI** (`frontend/app/proposals/[id]/page.tsx`)
  - Complete read-only weergave van voorstellen
  - Visualisatie van alle moves (van → naar)
  - Status badges (pending/approved/rejected)
  - Batch context en navigatie
  - Approve/Reject/Edit actie knoppen

- ✅ **Editable Proposal UI** (`frontend/app/proposals/[id]/edit/page.tsx`)
  - Live balance validatie (totale voorraad moet gelijk blijven)
  - Visuele feedback (groene overlay bij opslaan)
  - Progress tracking binnen batch
  - Disabled state bij ongebalanceerde edits
  - Tooltips voor disabled states
  - Auto-navigate naar volgend voorstel

- ✅ **Proposal Components**
  - `proposal-detail.tsx` - Read-only voorstel weergave
  - `editable-proposal-detail.tsx` - Bewerkbare voorstel met inline editing
  - `proposal-actions.tsx` - Approve/Reject knoppen met confirmations

- ✅ **API Client Extensions** (`frontend/lib/api.ts`)
  - Nieuwe proposals endpoints (getAll, getById, getByBatch)
  - Approve/Reject functies
  - Type-safe interfaces voor Proposal en Move

- ✅ **Test Scripts**
  - `backend/test_generate_proposals.py` - Algoritme validatie
  - Edge case testing
  - Performance testing

### Changed
- 📝 **Project Status**: Van 70% → 95% compleet
- 📝 **Architecture**: Volledige separation tussen algoritme, UI en API
- 📝 **Type Safety**: Complete TypeScript/Python type coverage

### Technical Debt Identified
- ⚠️ **TODO**: Proposals API router moet aangemaakt worden (`backend/routers/proposals.py`)
- ⚠️ **TODO**: Database Proposals table moet geïmplementeerd worden
- ⚠️ **TODO**: Frontend-backend integratie voor proposal updates (regel 77-78 in edit page)
- ⚠️ **TODO**: "Genereer Voorstellen" knop in batch view

### In Development
- ⏳ **Proposals API Integration** - UI is klaar, backend endpoints nodig
- ⏳ **Database Schema Updates** - Proposals table design klaar
- ⏳ **Batch Proposal Generation** - Algoritme werkt, UI trigger nodig

### Impact
🎊 **Van PDF Parser → Complete Herverdelingstool!**
- Core functionaliteit nu volledig werkend
- Intelligente besluitvorming gebaseerd op verkoop en voorraad
- Business rules embedded (BV constraints, demand prioriteit)
- Flexible en configureerbaar systeem

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

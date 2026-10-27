---
title: Production Readiness Audit
category: technical
tags: [engineering, production-readiness, security, audit, power-of-ten]
last_updated: 2026-08-12
related:
  - docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md
  - docs/engineering/PRODUCTION_READINESS_PLAN.md
  - docs/DOCUMENTATION_GUIDELINES.md
status: draft
---

# Production Readiness Audit

## Doel

Dit document geeft een momentopname van de production-readiness van
`digital-resupplying-tool` op **2026-07-13**, uitsluitend gebaseerd op
aantoonbare informatie uit deze repository: broncode (pad:regelnummer),
configuratiebestanden, git-geschiedenis, en daadwerkelijk uitgevoerde
verificatiecommando's (pytest, `tsc`, ESLint, `npm run build`, `npm audit`).

## Scope

- Backend: `backend/` (FastAPI/SQLAlchemy/SQLite).
- Frontend: `frontend/` (Next.js 14 App Router, TypeScript).
- Repository-hygiëne: git-geschiedenis, `.gitignore`, getrackte artefacten.
- Buiten scope: `tools/baseline-pipeline/` (offline ML-pipeline), diepgaand
  performance- of belastingsonderzoek, penetratietesten.

## Methode

1. Read-only verkenning van de repository (broncode, configuratie,
   git-log) — elke bevinding hieronder is opnieuw geopend en gecontroleerd
   op het genoemde pad:regelnummer vlak vóór opname in dit document.
2. Uitgevoerde verificatiechecks in een geïsoleerde Linux-container
   (geen mutatie van getrackte bestanden of van een bestaande productie-
   database):
   - Backend: nieuwe virtualenv, `pip install -r backend/requirements.txt
     pytest`, daarna `pytest` op de losstaande testbestanden.
   - Frontend: `npm ci`, `npx tsc --noEmit`, `CI=true npm run lint`,
     `npm run build`, `npm audit`.
   - Root: `npm ci`, `npm audit`.
   - Git: `git log`, `git ls-files`, bestandsgroottes via
     `git cat-file -s`.
3. Niet uitgevoerd (met reden, zie ook
   `docs/engineering/AI_SESSION_HANDOFF.md` voor het volledige overzicht):
   Playwright-smoke (vereist draaiende app + geseede database),
   `test_auth_flow.py` / `test_batch_api.py` / `test_complete_auth.py`
   (vereisen een live server op `localhost:8000`), en elk seed/reset/
   migratiescript (bewuste veiligheidsregel: geen databasemutatie tijdens
   deze audit).

## Disclaimer

Er wordt in dit document **geen enkele uitspraak gedaan over algehele
productiegeschiktheid** ("is dit klaar voor productie") zonder dat de
onderliggende claim is onderbouwd met een concreet pad:regelnummer of een
daadwerkelijk uitgevoerde verificatiecheck. Waar een regelnummer bij
verificatie niet meer exact bleek te kloppen, is dit gecorrigeerd en expliciet
vermeld. Waar geen sluitend bewijs kon worden vastgesteld, staat "Niet
vastgesteld" in plaats van een aanname. Dit document vervangt geen
security-review door een gespecialiseerde partij en geen penetratietest.

De canonieke engineeringstandaard waarnaar de Power of Ten-regels in dit
document verwijzen staat in
`docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md`.

---

## Statusreconciliatie (2026-08-12)

> Deze audit is een momentopname van **2026-07-13**. Sindsdien is een reeks
> bevindingen opgelost via PR #1–#9 op `main`. Onderstaande tabel geeft de
> **actuele status**; de oorspronkelijke bevindingsteksten verderop blijven als
> historisch record staan. Bevindingen die hier **niet** als "deze sessie
> geverifieerd" staan, zijn niet opnieuw gecontroleerd — daarvoor blijft de
> oorspronkelijke tekst leidend (geen aanname van "opgelost").

| ID | Status | Toelichting (geverifieerd 2026-08 tenzij anders vermeld) |
|---|---|---|
| PR-001 | ✅ Opgelost | Auth (`require_permission`) aanwezig op de ingest/approve-endpoints. |
| PR-002 | ✅ Opgelost (fallback) | `SECRET_KEY = os.getenv("SECRET_KEY")` zónder fallback. (De `check_secret_key.py`-print is niet apart herzien.) |
| PR-003 | 🟡 Deels — jouw actie | Tracking verwijderd; secret roteren + git-historie herschrijven vereist eigenaarsactie. |
| PR-004 | ✅ Opgelost | Veilige bestandsnaam (`safe_name`) bij opslag (sanitisatie-detail niet diepgaand herzien). |
| PR-005 | ✅ Opgelost | `save_upload_within_limit()` dwingt een groottelimiet af vóór wegschrijven. |
| PR-006 | ✅ Opgelost | Idempotentie op approve én reject; niet-negatief- + unieke-constraints op `ArtikelVoorraad`. ⚠ Zie kanttekeningen hieronder. |
| PR-007 | 🟡 Deels — productkeuze | Per-bestand-sessieherstel verbeterd (PR #6/#9); de transactiegrens-keuze bij multi-file blijft open. |
| PR-009 | ✅ Opgelost | CORS gebruikt nu `allow_origins` uit de omgeving. |
| PR-010 | ✅ Opgelost | `ignoreBuildErrors` verwijderd; frontend-build faalt bij typefouten. |
| PR-011 | ✅ Opgelost | CI-pipeline met ruff/mypy/pytest + frontend tsc/lint/build. |
| PR-012 | ✅ Opgelost | `requirements-dev.txt` bevat de testafhankelijkheden. |
| PR-013 | ✅ Opgelost | Rate limiting (`rate_limit.py`). |
| PR-015 | 🟡 Deels | Edit-pad valideert `moves` via Pydantic; lees-consumenten gebruiken defensieve `.get()`, nog geen model. |
| PR-019 | ✅ Opgelost | Eén centrale `logging.basicConfig` in `main.py`; `/health` doet een DB-check (503 bij uitval). |
| PR-020 | ✅ Opgelost | Config-singletons → dependency injection (PR #2). |
| PR-021 | 🔴 Open — Fase 4 | Nog geen Alembic; ad-hoc `ensure_runtime_schema` blijft tussenoplossing. |
| PR-022 | ✅ Opgelost | `algorithm.py` (922→197 r.) + `pdf_ingest.py` opgesplitst (PR #3 e.a.). |
| Audit trail (§6/§8) | ✅ Opgelost | `Proposal.reviewed_by` + `Feedback.user_id` (PR #7/#8). |

**Niet opnieuw geverifieerd deze sessie** (oorspronkelijke tekst blijft leidend): PR-008, PR-014, PR-016, PR-017, PR-018, PR-023, PR-024.

### Nieuwe/uitgebreide kanttekeningen (uit code-review 2026-08-12)

- **Constraints gelden alleen op een verse DB (PR-006):** de `CheckConstraint`s en de `UniqueConstraint` op `ArtikelVoorraad` worden toegepast bij `create_all` op een verse database. `ensure_runtime_schema()` voegt wél kolommen toe aan bestaande SQLite-DB's, maar géén constraints (SQLite kan dat niet zonder tabel-herbouw). Op een bestaande productie-/dev-DB zijn de dubbeltelling- en negatief-beschermingen daarom **inert** tot een echte migratie (Fase 4 / PR-021). Dit is de belangrijkste openstaande beperking van PR-006.
- **Alles-of-niets per bestand (PR-006):** één dubbele of ongeldige rij in een PDF laat de commit van dat héle bestand falen (bestand → `FAILED`, geen enkele rij opgeslagen). Verdedigbaar (een duplicaat ís fout), maar een zware faalmodus; deduplicatie binnen één bestand is een mogelijke verfijning.
- **Tijdzone-naïeve audit-tijdstempels:** `reviewed_at`/`created_at` gebruiken `datetime.now()` (tz-naïef) in tijdzone-bewuste kolommen; audit-tijdstempels missen een offset. Bestaand patroon, aandachtspunt voor opschoning naar `datetime.now(timezone.utc)`.
- **Verweesde winkel-assignments (gevonden 2026-08-13 via code-review, opgelost in PR #10):** de assignment-sync (`assignment_service.py`) máákte alleen aan en verwijderde nooit. Daardoor bleven bij een goedgekeurd-daarna-afgekeurd voorstel én bij een edit die een route weghaalde, uitvoerbare winkelopdrachten staan die niet meer klopten. Opgelost: `reject_proposal` én `update_proposal` (edit) ruimen de nog-openstaande assignments op via `remove_assignments_for_proposal`; `approve` ruimt bij re-sync stale routes op (`cleanup_stale=True`). Reeds uitgevoerde/afgehandelde opdrachten (`completed`/`failed`) blijven als auditrecord behouden, en het brede read-path-sync verwijdert nooit (geen destructieve neveneffecten op een GET). Compenserende controle: `backend/test_assignment_sync_cleanup.py` (6 tests). **Resterend, pre-bestaand (uit de code-review, nog niet opgelost):**
  - *Upsert reset geen terminale status:* bij her-goedkeuring na een edit wordt een bestaand item met een terminale status (`completed`/`failed`) ge-upsert met nieuwe aantallen zonder de status, `completed_at` of de `failure_*`-velden te resetten — de winkel kan zo een 'voltooide'/'gefaalde' opdracht met nieuwe aantallen zien. Dit vereist een productbeslissing (nieuw item vs. reset), mede omdat `uq_assignment_item_proposal_route` maar één item per (voorstel, route) toestaat.
  - *`delete_batch` ruimt niet volledig op:* `backend/routers/pdf_ingest.py::delete_batch` verwijdert voorraad/logs/batch maar niet de bijbehorende `Proposal`s en `AssignmentSeries`/`AssignmentItem`s (die via FK naar de batch verwijzen). Omdat SQLite FK's niet afdwingt (geen `PRAGMA foreign_keys=ON`), levert dit stil verweesde assignments op — dezelfde integriteitsklasse als hierboven. Aparte fix nodig.

---

## Samenvattingstabel

| ID | Ernst | Component | Titel |
|---|---|---|---|
| PR-001 | Critical | backend/routers (pdf_ingest, batches, articles, redistribution) | Muterende endpoints zonder authenticatie |
| PR-002 | Critical | backend/auth.py, backend/check_secret_key.py | Hardcoded SECRET_KEY-fallback + key wordt geprint |
| PR-003 | Critical | backend/database.db.backup_* (git-geschiedenis) | Databasebackups met echte data getrackt in git |
| PR-004 | Critical | backend/routers/pdf_ingest.py | Path traversal via client-filename bij upload |
| PR-005 | High | backend/routers/pdf_ingest.py | Geen upload-size-limit of content-type-check |
| PR-006 | High | backend/routers/pdf_ingest.py, backend/db_models.py | Geen idempotentie op approve/ingest |
| PR-007 | High | backend/routers/pdf_ingest.py | Per-file commits midden in verwerkingslus |
| PR-008 | High | backend/routers/auth.py | Refresh-endpoint maskeert alle serverfouten als 401 |
| PR-009 | High | backend/main.py | CORS `ALLOWED_ORIGINS`-omgevingsvariabele wordt genegeerd |
| PR-010 | High | frontend/next.config.mjs | `ignoreBuildErrors: true` verbergt reële TypeScript-fouten |
| PR-011 | High | repository-breed | Geen Python-lint/typecheck-config, geen werkende ESLint-config, geen CI |
| PR-012 | High | backend/requirements.txt | Testafhankelijkheden (pytest, httpx) ontbreken |
| PR-013 | High | backend/routers/auth.py | Geen rate limiting/lockout op login |
| PR-014 | Medium | backend/routers/batches.py | Interne fouttekst gelekt naar client |
| PR-015 | Medium | backend/routers/pdf_ingest.py | Ongevalideerde `moves`-payload (`List[dict]`) |
| PR-016 | Medium | frontend/lib/api.ts, frontend/lib/api-client.ts | Twee divergerende API-base-mechanismen |
| PR-017 | Medium | frontend/lib/api-client.ts | Fetch zonder timeout/AbortController |
| PR-018 | Medium | backend/routers/settings.py | OpenAI-sleutel onversleuteld opgeslagen |
| PR-019 | Medium | backend/routers/pdf_ingest.py, backend/main.py | Geen centrale/gestructureerde logging, health check zonder DB-check |
| PR-020 | Medium | backend/redistribution/bv_config.py, backend/redistribution/store_profiles.py | Module-level mutable singletons |
| PR-021 | Medium | backend/database.py | Geen Alembic; ad-hoc schemamigraties, deels onvolledig |
| PR-022 | Medium | backend/routers/pdf_ingest.py, backend/redistribution/algorithm.py | Grote modules met gemengde verantwoordelijkheid |
| PR-023 | Medium | frontend/, root | npm audit meldt kwetsbaarheden |
| PR-024 | Medium | backend/pdf_extraction_data.json, backend/pdf_extraction_report.html | Gegenereerde artefacten getrackt in git |
| ~~PR-029~~ | ~~Medium~~ | backend/redistribution/algorithm.py | **Ingetrokken** — testartefact, geen defect (zie hieronder en POS-011) |
| PR-025 | Low | backend/test_situation_classifier.py | 2 falende tests door test-isolatie (geen productiebug) |
| PR-026 | Low | backend/test_*.py | Meerderheid van root-testbestanden zonder assertions |
| PR-027 | Low | frontend/pnpm-lock.yaml | Verdwaald, vrijwel leeg lockbestand naast package-lock.json |
| PR-028 | Low | frontend/package.json | Dependencies gepind op `latest` |

Positieve bevindingen: zie sectie "Wat behouden moet blijven" (POS-001 t/m POS-011).

---

## Critical

### PR-001 — Muterende endpoints zonder authenticatie

- **Ernst**: Critical
- **Component**: `backend/routers/pdf_ingest.py`, `backend/routers/batches.py`, `backend/routers/articles.py`, `backend/routers/redistribution.py`
- **Bewijs**:
  - Geverifieerd door elke `@router.`-decorator in deze vier bestanden te doorlopen en te controleren op `Depends(get_current_user)`, `Depends(get_current_active_user)` of `Depends(require_permission(...))`.
  - `backend/routers/pdf_ingest.py`: geen van de endpoints heeft een auth-dependency, o.a. `POST /api/pdf/ingest` (regel 95-101), `DELETE /batches/{batch_id}` (regel 533-534), `POST /proposals/{proposal_id}/approve` (regel 764-765), `POST /proposals/{proposal_id}/reject` (regel 808-813), `PUT /proposals/{proposal_id}` (regel 858-863).
  - `backend/routers/batches.py`: `POST /batches/create` (regel 25-26), `POST /batches/{batch_id}/upload` (regel 48-53) — beide zonder auth-dependency.
  - `backend/routers/articles.py`: `POST /articles` (regel 58-59), `PUT /articles/{artikelnummer}` (regel 94-99), `DELETE /articles/{artikelnummer}` (regel 129-130) — geen auth.
  - `backend/routers/redistribution.py`: `POST /redistribution/generate/{batch_id}` (regel 22-28) — geen auth.
  - Contrast: `backend/routers/users.py`, `roles.py`, `settings.py`, `assignments.py`, `dashboard.py`, `feedback.py`, `algorithm_import.py` en `auth.py` (endpoints `/me`, `/logout`) hebben op ieder endpoint wél `Depends(get_current_active_user)` of `Depends(require_permission(...))` (bv. `users.py:124`, `roles.py:61`, `settings.py:80`, `assignments.py:98`, `dashboard.py:214`, `feedback.py:69`, `algorithm_import.py:18`).
- **Risico**: Iedereen met netwerktoegang tot de API kan zonder inloggen PDF's uploaden, batches en proposals verwijderen/goedkeuren/afwijzen, artikelen aanmaken/wijzigen/verwijderen en herverdelingsvoorstellen genereren. Dit is zowel een integriteits- als een beschikbaarheidsrisico (bv. willekeurige `DELETE /batches/{id}` door een niet-geauthenticeerde partij).
- **Power of Ten-regel**: Uitbreiding hoofdstuk 9 (Security) van de standaard; raakt ook regel 7 (retourwaarden/parameters controleren — hier ontbreekt de controle op wie de aanroeper is) en regel 10 (statische/automatische controle had dit kunnen signaleren).
- **Aanbevolen oplossing**: Voeg op elk state-changing endpoint in deze vier routers een passende `Depends(require_permission("..."))` of minimaal `Depends(get_current_active_user)` toe, consistent met het patroon dat al in `users.py`/`roles.py`/`settings.py` bestaat. Geen nieuwe autorisatiearchitectuur — hergebruik de bestaande `require_permission`/`require_role` uit `backend/auth.py:194-249`.
- **Verificatiemethode**: Voor elk endpoint een geautomatiseerde test die aantoont dat een aanroep zonder geldig token `401`/`403` retourneert, plus een positieve test met geldig token en juiste permissie. Handmatig: `curl` zonder `Authorization`-header tegen elk endpoint in een lokale dev-omgeving.
- **Veranderomvang**: Medium (veel bestanden, maar elke wijziging is mechanisch dezelfde dependency-toevoeging).
- **Afhankelijkheden/blokkades**: Vereist dat de juiste permissienamen al bestaan in de rollen-tabel (lijkt het geval te zijn gezien het gebruik in andere routers); geen blokkade richting CI, maar dit werk moet vóór PR-013 (rate limiting) niet per se, wel vóór elke publieke deployment.

### PR-002 — Hardcoded SECRET_KEY-fallback + key wordt geprint

- **Ernst**: Critical
- **Component**: `backend/auth.py`, `backend/check_secret_key.py`
- **Bewijs**: `backend/auth.py:26`: `SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")`. Identieke fallback gedupliceerd in `backend/check_secret_key.py:15`. Dat script print de sleutel expliciet naar stdout op `check_secret_key.py:18`: `print(f"🔑 SECRET_KEY from env: {secret_key}")`.
- **Risico**: Als `SECRET_KEY` niet in de omgeving is gezet, gebruikt de applicatie stilzwijgend een publiek bekende, in de repository zichtbare waarde om JWT's te ondertekenen — elke aanvaller kan dan geldige tokens vervalsen voor elke gebruiker/rol. Het diagnosescript maakt het risico groter door de actieve sleutel (indien wel custom) naar console/logs te lekken.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 9 (Security); raakt regel 5 (assert/precondition-check: hier ontbreekt een expliciete "fail fast als secret ontbreekt"-check) en regel 7 (parameter/omgevingscontrole).
- **Aanbevolen oplossing**: `SECRET_KEY` verplicht uit de omgeving lezen zonder fallback-string; bij ontbreken de applicatie direct laten falen bij opstart (`raise RuntimeError(...)` of gelijkwaardig) in plaats van stilzwijgend een onveilige default te gebruiken. In `check_secret_key.py` de regel die de sleutel print verwijderen of vervangen door alleen lengte/aanwezigheid te tonen.
- **Verificatiemethode**: Applicatie starten zonder `SECRET_KEY` in de omgeving → verwacht een startfout (geen draaiende server). Met `SECRET_KEY` gezet → normale start. Handmatige code-review dat `check_secret_key.py` de waarde niet meer print.
- **Veranderomvang**: Small.
- **Afhankelijkheden/blokkades**: Vereist dat elke deployment/dev-omgeving vooraf een `SECRET_KEY` in `.env` heeft (er is al een `backend/.env.example` aanwezig als sjabloon); moet gecommuniceerd worden vóór deze wijziging live gaat, anders faalt de app onverwacht bij collega's.

### PR-003 — Databasebackups met echte data getrackt in git

- **Ernst**: Critical
- **Component**: git-geschiedenis (`backend/database.db.backup_*`)
- **Bewijs**: `git ls-files` toont drie getrackte bestanden: `backend/database.db.backup_20251029_002226` (241.664 bytes, geverifieerd via `git cat-file -s`), `backend/database.db.backup_20251029_002437` (0 bytes) en `backend/database.db.backup_20251029_002506` (0 bytes). Ze zijn toegevoegd in commit `f977cfe` (2025-10-29). De `.gitignore`-regel `*.db.backup_*` is pas op 2025-11-05 toegevoegd (commit `b9984ab`, geverifieerd via `git log -S "db.backup" -- .gitignore`) — dus zeven dagen ná het committen van de bestanden, waardoor de regel de reeds getrackte bestanden niet met terugwerkende kracht verwijdert.
- **Risico**: Het 241 KB-bestand is een reële SQLite-databasekopie in de git-geschiedenis (permanent terugvindbaar, ook na latere verwijdering van de bestandsinhoud uit HEAD, tenzij de geschiedenis wordt herschreven). Gezien het schema (`users.hashed_password`, `settings`-tabel die o.a. de OpenAI-sleutel bevat, zie PR-018) is dit een potentieel datalek van wachtwoordhashes en API-sleutels in versiebeheer, met name als de repository ooit publiek wordt of breder gedeeld dan bedoeld.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 9 (Security) / hoofdstuk 6 (Data-integriteit) van de standaard.
- **Aanbevolen oplossing**: `git rm --cached` op de drie bestanden (bestandsinhoud blijft lokaal staan, verdwijnt uit toekomstige commits); de `.gitignore`-regel is al aanwezig en voorkomt herhaling. Geschiedenis-herschrijving (bv. `git filter-repo`) is een aparte, zwaardere beslissing die buiten deze audit valt maar wel als vervolgstap gedocumenteerd moet worden. Alle in de backup aanwezige secrets (wachtwoorden, API-sleutels) moeten als gecompromitteerd worden beschouwd en geroteerd.
- **Verificatiemethode**: `git ls-files | grep "database.db.backup"` geeft na de fix geen resultaat meer voor nieuwe commits; bevestig met een test-clone dat de bestanden niet meer in de working tree verschijnen bij een nieuwe checkout van de nieuwste commit (de historische aanwezigheid blijft totdat een geschiedenis-herschrijving plaatsvindt — dat apart benoemen).
- **Veranderomvang**: Small (het verwijderen zelf); Large als ook geschiedenis-herschrijving en secret-rotatie worden meegenomen.
- **Afhankelijkheden/blokkades**: Secret-rotatie (wachtwoorden resetten, OpenAI-sleutel vervangen) is een operationele vervolgstap buiten de code-wijziging; moet met de repository-eigenaar worden afgestemd vóórdat de repository breder wordt gedeeld.

### PR-004 — Path traversal via client-filename bij upload

- **Ernst**: Critical
- **Component**: `backend/routers/pdf_ingest.py`
- **Bewijs**: `backend/routers/pdf_ingest.py:169`: `file_path = os.path.join(batch_dir, file.filename)` — `file.filename` komt rechtstreeks van de client (multipart upload) en wordt ongesaneerd gebruikt in een pad dat vervolgens beschreven wordt (regel 170-171: `with open(file_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)`).
- **Risico**: Een kwaadwillende client kan een bestandsnaam sturen die `../`-sequenties bevat, waardoor het bestand buiten `batch_dir` (mogelijk buiten `UPLOAD_DIR`) weggeschreven wordt — potentieel overschrijven van willekeurige bestanden waartoe het serverproces schrijfrechten heeft. Dit endpoint heeft bovendien geen authenticatie (zie PR-001), wat de blootstelling vergroot.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 9 (Security); raakt regel 7 (invoer van buiten het systeem controleren vóór gebruik).
- **Aanbevolen oplossing**: Bestandsnaam saneren vóór gebruik in een pad, bijvoorbeeld met `os.path.basename(file.filename)` gecombineerd met een whitelist van toegestane tekens/extensie (`.pdf`), en het resulterende pad valideren dat het binnen `batch_dir` blijft (bv. via `Path.resolve()` en een prefix-check).
- **Verificatiemethode**: Test die een upload met filename `"../../evil.txt"` stuurt en verifieert dat het resulterende bestand binnen `batch_dir` blijft (of dat de request met een 4xx wordt geweigerd).
- **Veranderomvang**: Small.
- **Afhankelijkheden/blokkades**: Kan onafhankelijk van PR-001 worden opgelost, maar hoort logisch in dezelfde fase (Fase 1) omdat beide de ingest-flow raken.

---

## High

### PR-005 — Geen upload-size-limit of content-type-check

- **Ernst**: High
- **Component**: `backend/routers/pdf_ingest.py`
- **Bewijs**: `POST /api/pdf/ingest` (`pdf_ingest.py:95-101`) accepteert `files: List[UploadFile] = File(...)` zonder enige controle op bestandsgrootte of `content_type`/extensie vóór verwerking (geverifieerd: geen `content_type`-check, geen `MAX_`-constante en geen `Content-Length`-validatie in het volledige bestand — grep op deze termen levert geen relevante treffers op behalve ongerelateerde variabelenamen). Ter vergelijking bevat `backend/routers/batches.py:65` wél een extensiecontrole (`if not file.filename.endswith('.pdf')`) voor het parallelle upload-endpoint.
- **Risico**: Een client kan een willekeurig groot of willekeurig type bestand uploaden, wat schijfruimte kan uitputten (denial-of-service) of onverwachte bestandstypen in `backend/uploads/pdf_batches/` plaatst die later door de PDF-parser worden aangeroepen.
- **Power of Ten-regel**: Regel 2 (vaste bovengrens — hier ontbreekt een expliciete bovengrens op invoergrootte) en regel 3 (begrensd resourcegebruik).
- **Aanbevolen oplossing**: Expliciete maximale bestandsgrootte (bv. via `Content-Length`-check of streaming met een teller die afbreekt boven een limiet) en een extensie-/content-type-whitelist (`.pdf`), analoog aan de bestaande check in `batches.py:65`.
- **Verificatiemethode**: Test die een bestand groter dan de limiet of met een niet-toegestane extensie uploadt en een 4xx-response verwacht in plaats van verwerking.
- **Veranderomvang**: Small.
- **Afhankelijkheden/blokkades**: Geen.

### PR-006 — Geen idempotentie op approve/ingest

- **Ernst**: High
- **Component**: `backend/routers/pdf_ingest.py`, `backend/db_models.py`
- **Bewijs**:
  - Dubbele approve → dubbele Feedback-rijen: `pdf_ingest.py:785-794` maakt bij elke aanroep van `POST /proposals/{id}/approve` een nieuwe `Feedback`-rij per move aan zonder te controleren of `proposal.status` al `'approved'` is; een herhaalde aanroep (dubbele klik, retry) voegt dus telkens extra Feedback-records toe.
  - Dubbele ingest → dubbele voorraadrijen: `ArtikelVoorraad` (`backend/db_models.py:285-320`) heeft geen `UniqueConstraint` op de combinatie `batch_id`/`volgnummer`/`filiaal_code`/`maat` (geverifieerd door de volledige class-body te lezen); een herhaalde ingest van dezelfde PDF in een nieuwe batch levert dus nieuwe, niet-gededupliceerde rijen op (dit is deels inherent aan het batch-model, maar binnen één ingest-aanroep met retry ontstaat eveneens duplicatie zonder enige guard).
- **Risico**: Netwerk-retries, dubbele kliks in de UI of geautomatiseerde herhaling kunnen leiden tot dubbele feedback-data (vertekent eventuele ML-training/rapportage) en dubbele voorraadrecords (vertekent voorraadberekeningen in het herverdelingsalgoritme).
- **Power of Ten-regel**: Uitbreiding hoofdstuk 6 (Data-integriteit); raakt regel 5 (invariant-checks/preconditie: "is deze proposal al approved?" ontbreekt).
- **Aanbevolen oplossing**: In `approve_proposal` een expliciete check toevoegen (`if proposal.status == 'approved': raise HTTPException(409, ...)` of een no-op teruggeven). Voor `ArtikelVoorraad` een `UniqueConstraint` overwegen op de relevante kolommencombinatie, waarbij eerst moet worden vastgesteld of duplicaten binnen één batch functioneel gewenst kunnen zijn (dit vereist afstemming, geen blinde constraint-toevoeging).
- **Verificatiemethode**: Test die `approve` twee keer op dezelfde proposal aanroept en verifieert dat het aantal Feedback-rijen niet verdubbelt (of dat de tweede aanroep een 409 geeft).
- **Veranderomvang**: Small (approve-guard); Medium (unique constraint, vanwege mogelijke bestaande duplicaten in productiedata die eerst opgeschoond moeten worden).
- **Afhankelijkheden/blokkades**: De unique-constraint-wijziging vereist eerst een data-audit van bestaande `artikel_voorraad`-rijen op duplicaten (kan botsen met historische data).

### PR-007 — Per-file commits midden in verwerkingslus

- **Ernst**: High
- **Component**: `backend/routers/pdf_ingest.py`
- **Bewijs**: De hoofdlus in `ingest_pdfs` (`pdf_ingest.py:164-232`) roept per bestand `save_to_database(...)` aan (regel 199), en die functie commit tweemaal binnen zichzelf: `db.commit()` op regel 327 (na het opslaan van de voorraadrecords) en nogmaals op regel 342 (na het wegschrijven van een logregel). Er is geen omvattende transactie of rollback-mechanisme rond de volledige batchverwerking; bij een fout in een later bestand blijven de reeds gecommitte records van eerdere bestanden staan.
- **Risico**: Bij een fout halverwege een multi-file upload (bv. bestand 3 van 5 faalt) is de database in een deels-verwerkte toestand: bestanden 1-2 zijn al definitief opgeslagen, bestand 3 gefaald, bestanden 4-5 nog te verwerken. Dit is functioneel zichtbaar in de `PARTIAL_SUCCESS`-status, maar er is geen mogelijkheid om de hele batch atomair terug te draaien.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 6 (Data-integriteit); raakt regel 7 (foutafhandeling van tussenresultaten).
- **Aanbevolen oplossing**: Geen grote refactor binnen deze audit; als eerste stap de bestaande `PARTIAL_SUCCESS`-status expliciet documenteren als bewust ontwerp (per-bestand onafhankelijke verwerking) óf, indien atomaire verwerking gewenst is, een expliciete transactiegrens per batch introduceren met rollback bij falen. Deze keuze vereist een productbeslissing (is partial success gewenst gedrag?) voordat er code wijzigt.
- **Verificatiemethode**: Test die een batch van meerdere bestanden aanbiedt waarbij één bestand bewust faalt, en het resulterende aantal opgeslagen `ArtikelVoorraad`-rijen vergelijkt met de verwachte uitkomst (huidig gedrag: partiële opslag — vastleggen als baseline, dan pas beslissen of dit moet veranderen).
- **Veranderomvang**: Medium (afhankelijk van gekozen richting).
- **Afhankelijkheden/blokkades**: Vereist eerst een productbeslissing over gewenst transactiegedrag; geen technische blokkade.

### PR-008 — Refresh-endpoint maskeert alle serverfouten als 401

- **Ernst**: High
- **Component**: `backend/routers/auth.py`
- **Bewijs**: `backend/routers/auth.py:173-177`: `except Exception as e: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token kon niet vernieuwd worden")`. De variabele `e` wordt opgevangen maar nergens gebruikt (niet gelogd, niet in de detail-tekst).
- **Risico**: Elke onverwachte fout binnen de `try`-block (bv. een databasefout, een `AttributeError` als `role` `None` is op regel 154) wordt naar de client teruggegeven als "ongeldig token" (401), terwijl de daadwerkelijke oorzaak een serverfout (500-waardig) kan zijn. Dit maakt troubleshooting lastig en kan gebruikers ten onrechte laten denken dat ze opnieuw moeten inloggen.
- **Power of Ten-regel**: Regel 7 (retourwaarden en foutcondities expliciet en specifiek afhandelen, geen brede `except Exception` zonder logging/motivatie).
- **Aanbevolen oplossing**: De brede `except Exception` vervangen door specifieke excepties (bv. `JWTError` voor ongeldige tokens → 401) en overige onverwachte fouten laten propageren of expliciet als 500 loggen, in plaats van ze te maskeren als 401.
- **Verificatiemethode**: Unit-test die een scenario simuleert waarin `role` `None` is (regel 150-154) en verifieert dat de response een 500 (of specifieke foutcode) geeft in plaats van een misleidende 401; logging-assertie dat de fout ergens zichtbaar is.
- **Veranderomvang**: Small.
- **Afhankelijkheden/blokkades**: Geen.

### PR-009 — CORS `ALLOWED_ORIGINS`-omgevingsvariabele wordt genegeerd

- **Ernst**: High
- **Component**: `backend/main.py`
- **Bewijs**: `main.py:40-53` leest `ALLOWED_ORIGINS` uit de omgeving en bouwt een lijst `allowed_origins` op, maar die variabele wordt nergens doorgegeven aan de middleware. `main.py:55-61` configureert `CORSMiddleware` met een hardcoded `allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.\d+\.\d+\.\d+):3000"` in combinatie met `allow_credentials=True`. De eerder opgebouwde `allowed_origins`-lijst wordt dus feitelijk dode code.
- **Risico**: Operators die menen de toegestane origins via `ALLOWED_ORIGINS` te kunnen configureren (bv. voor een productiedomein) zien geen effect: alleen de hardcoded private-IP/localhost-regex geldt, ongeacht de omgevingsvariabele. Dit is zowel een configuratiebug (verrassend gedrag) als een potentieel security-risico wanneer de regex breder is dan bedoeld voor een productieomgeving (private-IP-ranges met credentials toegestaan).
- **Power of Ten-regel**: Uitbreiding hoofdstuk 9 (Security); raakt regel 7 (een geconfigureerde waarde die nooit wordt gebruikt is een vorm van genegeerd resultaat/parameter).
- **Aanbevolen oplossing**: De opgebouwde `allowed_origins`-lijst daadwerkelijk doorgeven aan `CORSMiddleware` (via `allow_origins=allowed_origins` i.p.v. alleen `allow_origin_regex`), of expliciet documenteren waarom de env-var momenteel genegeerd wordt als dit een bewuste tussenstap was.
- **Verificatiemethode**: Test/handmatige check die `ALLOWED_ORIGINS` op een niet-standaard waarde zet, de server herstart, en verifieert dat een CORS-preflight vanaf dat origin wordt geaccepteerd/geweigerd conform de env-var.
- **Veranderomvang**: Small.
- **Afhankelijkheden/blokkades**: Moet worden afgestemd met het (nog onbekende) deploymentdoel — zie Fase 4 in het verbeterplan.

### PR-010 — `ignoreBuildErrors: true` verbergt reële TypeScript-fouten

- **Ernst**: High
- **Component**: `frontend/next.config.mjs`
- **Bewijs**: `frontend/next.config.mjs` bevat `typescript: { ignoreBuildErrors: true }`. Uitgevoerde verificatie: `npx tsc --noEmit` (TypeScript 5.9.3) geeft exitcode 2 met exact 2 fouten (beide `TS2339`, "Property 'batch_name' does not exist on type 'BatchWithProposals'") in `frontend/app/proposals/[id]/edit/page.tsx:54` en `frontend/app/proposals/[id]/page.tsx:34`. Desondanks slaagt `npm run build` (exitcode 0) met de output "Skipping validation of types" — de build negeert deze fouten door de config-instelling.
- **Risico**: `tsconfig.json` staat op `strict: true`, maar die striktheid is cosmetisch zolang de build typefouten negeert: reële type-mismatches (hier: een niet-bestaand veld `batch_name`) belanden ongemerkt in productie en kunnen op runtime tot undefined-waarden of crashes leiden.
- **Power of Ten-regel**: Regel 10 (nul warnings/fouten toestaan in de build).
- **Aanbevolen oplossing**: Eerst de 2 onderliggende typefouten oplossen (het ontbrekende `batch_name`-veld op `BatchWithProposals` toevoegen of de toegang corrigeren), pas daarna `ignoreBuildErrors: true` verwijderen — in die volgorde, anders breekt de build onmiddellijk.
- **Verificatiemethode**: Na de fix: `npx tsc --noEmit` geeft exitcode 0; `npm run build` slaagt zonder de "Skipping validation of types"-melding.
- **Veranderomvang**: Small (de 2 typefouten zelf) + Small (config-wijziging), maar volgorde-afhankelijk.
- **Afhankelijkheden/blokkades**: De config-wijziging mag pas ná de typefix, anders faalt de build (zie Fase 2 in het verbeterplan).

### PR-011 — Geen Python-lint/typecheck-config, geen werkende ESLint-config, geen CI

- **Ernst**: High
- **Component**: repository-breed
- **Bewijs**: Geen `pyproject.toml`, geen ruff-/mypy-/flake8-/black-configuratiebestand gevonden in de repository (geverifieerd met een gerichte zoekopdracht op deze bestandsnamen). `frontend/package.json:12` bevat het script `"lint": "eslint ."`, maar er is geen `eslint.config.(js|mjs|cjs)` aanwezig; uitgevoerde verificatie `CI=true npm run lint` geeft exitcode 2 met de melding "ESLint couldn't find an eslint.config.(js|mjs|cjs) file." Een `.github/`-map ontbreekt volledig (geverifieerd: `ls .github` geeft "No such file or directory") — er is dus geen CI/CD-pipeline.
- **Risico**: Er is geen geautomatiseerde poort die code met stijl-, type- of lintfouten tegenhoudt vóór het samenvoegen; kwaliteitsbewaking is volledig afhankelijk van handmatige review. Dit is de grootste kloof ten opzichte van Power of Ten-regel 10.
- **Power of Ten-regel**: Regel 10 (nul-warnings-beleid + statische analyse als afdwingbare gate) — expliciet de grootste kloof volgens de vertaaltabel in de standaard.
- **Aanbevolen oplossing**: Gefaseerd invoeren zoals uitgewerkt in Fase 2 van het verbeterplan: eerst niet-destructieve configuratiebestanden toevoegen (ruff/mypy-config, ESLint flat config), dan een CI-workflow die deze gates afdwingt. Geen tooling "half" toevoegen zonder dat de bijbehorende commando's ook slagen.
- **Verificatiemethode**: `ruff check backend/`, `mypy backend/`, `npm run lint` en `npx tsc --noEmit` slagen allemaal lokaal en in CI met exitcode 0.
- **Veranderomvang**: Medium (meerdere configuratiebestanden + CI-workflow, maar elk op zichzelf klein en incrementeel).
- **Afhankelijkheden/blokkades**: PR-010 (typefouten) moet eerst opgelost zijn voordat `tsc`/build als gate kan worden ingezet.

### PR-012 — Testafhankelijkheden (pytest, httpx) ontbreken in requirements.txt

- **Ernst**: High
- **Component**: `backend/requirements.txt`
- **Bewijs**: `backend/requirements.txt` bevat geen `pytest`- of `httpx`-regel (geverifieerd door het volledige bestand te lezen: `fastapi`, `uvicorn[standard]`, `python-dotenv`, `pydantic`, `sqlalchemy`, `pdfplumber`, `python-multipart`, `passlib`, `bcrypt`, `python-jose[cryptography]`, `email-validator`). Uitgevoerde verificatie bevestigt het gevolg: 3 van de 9 losstaande testbestanden (`test_algorithm_import_router.py`, `test_dashboard_summary.py`, `test_user_store_assignments.py`) geven een collection error `ModuleNotFoundError: httpx`, omdat `fastapi.testclient.TestClient` (via Starlette) `httpx` als harde runtime-vereiste heeft.
- **Risico**: Zonder expliciete testafhankelijkheden is de testsuite niet reproduceerbaar op een schone omgeving; nieuwe bijdragers of CI-runners falen op ontbrekende dependencies in plaats van op echte testfouten.
- **Power of Ten-regel**: Regel 10 (reproduceerbare, geautomatiseerde verificatie als voorwaarde voor een sluitende quality gate).
- **Aanbevolen oplossing**: Een nieuw `backend/requirements-dev.txt` toevoegen met minimaal `pytest` en `httpx` (niet `requirements.txt` zelf wijzigen, dat blijft de productie-afhankelijkhedenlijst).
- **Verificatiemethode**: `pip install -r backend/requirements.txt -r backend/requirements-dev.txt` gevolgd door `pytest` op de drie eerder falende bestanden geeft geen collection error meer.
- **Veranderomvang**: Small.
- **Afhankelijkheden/blokkades**: Geen; dit is de eerste stap in Fase 0 van het verbeterplan.

### PR-013 — Geen rate limiting/lockout op login

- **Ernst**: High
- **Component**: `backend/routers/auth.py`
- **Bewijs**: `POST /login` (`auth.py:52-110`) bevat geen enkele vorm van pogingenteller, lockout of rate limiting; bij een onjuist wachtwoord wordt direct `401` teruggegeven (regel 65-70) zonder enige vertraging of blokkade-logica, ongeacht het aantal eerdere pogingen (geverifieerd door het volledige bestand te lezen — geen middleware of dependency die dit afhandelt is aanwezig, en er is geen relevante state in `db_models.py` zoals een `failed_login_count`-kolom).
- **Risico**: Het login-endpoint is kwetsbaar voor brute-force- en credential-stuffing-aanvallen; een aanvaller kan onbeperkt wachtwoorden proberen tegen bekende gebruikersnamen.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 9 (Security); raakt regel 2 (onbegrensde herhaling van een operatie zonder bovengrens).
- **Aanbevolen oplossing**: Eenvoudige, niet-destructieve maatregel: een teller/lockout-mechanisme per gebruikersnaam of IP (in-memory of DB-gebaseerd) dat na een X aantal mislukte pogingen een tijdelijke blokkade oplegt. Geen zware externe rate-limiting-infrastructuur binnen deze audit voorschrijven.
- **Verificatiemethode**: Test die N+1 mislukte loginpogingen doet en verifieert dat vanaf poging N+1 een 429 (of gelijkwaardige blokkade) wordt teruggegeven in plaats van een normale 401-verwerking.
- **Veranderomvang**: Medium.
- **Afhankelijkheden/blokkades**: Kan onafhankelijk van PR-001 t/m PR-004 worden opgepakt.

---

## Medium

### PR-014 — Interne fouttekst gelekt naar client

- **Ernst**: Medium
- **Component**: `backend/routers/batches.py`
- **Bewijs**: `batches.py:81-82`: `except Exception as e: raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")` — de ruwe exception-tekst wordt direct in de HTTP-response geplaatst.
- **Risico**: Interne implementatiedetails (bestandspaden, stacktrace-fragmenten, systeeminformatie) kunnen via de foutmelding aan de client lekken, wat aanvallers informatie kan geven voor verdere verkenning.
- **Power of Ten-regel**: Regel 7 (foutafhandeling zonder interne details te lekken).
- **Aanbevolen oplossing**: Generieke foutmelding naar de client, met de details (`str(e)`) alleen naar de server-log.
- **Verificatiemethode**: Test die een schrijffout simuleert (bv. read-only directory) en verifieert dat de response-body geen bestandspad of exception-klassenaam bevat, terwijl de log dat wel vastlegt.
- **Veranderomvang**: Small.
- **Afhankelijkheden/blokkades**: Geen.

### PR-015 — Ongevalideerde `moves`-payload (`List[dict]`)

- **Ernst**: Medium
- **Component**: `backend/routers/pdf_ingest.py`
- **Bewijs**: `UpdateProposalRequest.moves: List[dict]` (`pdf_ingest.py:90`) valideert geen structuur van de move-objecten. In `get_proposal_with_full_inventory` wordt vervolgens ongevalideerd op sleutel gelezen: `from_store = move["from_store"]`, `to_store = move["to_store"]`, `size = move["size"]`, `qty = move["qty"]` (`pdf_ingest.py:707-710`). Ook `update_proposal` gebruikt `move.get('qty', 0)`, `move.get('from_store')`, `move.get('to_store')` (regel 885, 890-891) op de ongevalideerde payload.
- **Risico**: Een move-dict zonder de verwachte sleutels (bv. via een handmatige API-aanroep of een bug in de frontend) leidt tot een `KeyError` op regel 707-710, wat een onbehandelde 500-fout oplevert in plaats van een nette validatiefout.
- **Power of Ten-regel**: Regel 7 (parameters/invoer controleren vóór gebruik) en regel 9 (vermijd ongetypeerde dicts over systeemgrenzen).
- **Aanbevolen oplossing**: Een getypeerd Pydantic-model voor een enkele move introduceren (met de velden `size`, `from_store`, `to_store`, `qty`, etc.) en `UpdateProposalRequest.moves: List[MoveModel]` gebruiken in plaats van `List[dict]`. Dit is een lokale, beperkte wijziging — geen bredere refactor van de proposal-flow.
- **Verificatiemethode**: Test die `PUT /proposals/{id}` aanroept met een move-dict zonder `from_store` en verifieert dat Pydantic een 422-validatiefout geeft in plaats van dat de server later op een `KeyError` crasht.
- **Veranderomvang**: Small tot Medium (afhankelijk van hoeveel plekken `moves` als dict aanspreken).
- **Afhankelijkheden/blokkades**: Raakt ook `generate_and_save_proposals` (regel 372-388) waar moves als dict worden opgebouwd — bij invoering van een getypeerd model moeten alle producenten/consumenten van `proposal.moves` worden meegenomen (zie Fase 3 in het verbeterplan).

### PR-016 — Twee divergerende API-base-mechanismen in de frontend

- **Ernst**: Medium
- **Component**: `frontend/lib/api.ts`, `frontend/lib/api-client.ts`
- **Bewijs**: `frontend/lib/api-client.ts:9`: `const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';` (omgevingsgestuurd, met fallback). `frontend/lib/api.ts:10`: `const API_BASE_URL = 'http://localhost:8000';` (volledig hardcoded, geen omgevingsvariabele). Beide bestanden bestaan naast elkaar (115 resp. 901 regels) en `api.ts` importeert zelfs `apiClient` uit `api-client.ts` (regel 7), maar definieert zijn eigen, hardcoded basis-URL.
- **Risico**: Bij het configureren van een niet-lokale backend-URL (bv. staging/productie) via `NEXT_PUBLIC_API_URL` werkt slechts een deel van de frontend-aanroepen correct; calls via `api.ts` blijven naar `localhost:8000` wijzen, wat tot stille, moeilijk te diagnosticeren fouten leidt in niet-lokale omgevingen.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 5 (Architectuur); raakt regel 6 (kleinste scope/geen dubbele bronnen van waarheid).
- **Aanbevolen oplossing**: Op korte termijn `api.ts` dezelfde omgevingsgestuurde constante laten gebruiken als `api-client.ts` (import in plaats van dupliceren). Volledige consolidatie tot één client is een grotere wijziging en hoort in Fase 3 van het verbeterplan, niet in deze audit.
- **Verificatiemethode**: `NEXT_PUBLIC_API_URL` op een afwijkende waarde zetten, build/dev-server starten, en verifiëren (via netwerktab of grep op de gecompileerde bundle) dat alle API-aanroepen naar die waarde gaan.
- **Veranderomvang**: Small (de env-var-fix) tot Large (volledige consolidatie, apart getraceerd in Fase 3).
- **Afhankelijkheden/blokkades**: Volledige consolidatie vereist het inventariseren van alle aanroepers van beide clients.

### PR-017 — Fetch zonder timeout/AbortController

- **Ernst**: Medium
- **Component**: `frontend/lib/api-client.ts`
- **Bewijs**: `apiFetch` (`api-client.ts:25-115`) roept `fetch(url, { ...options, headers })` aan op regel 43 en, bij een 401-retry, nogmaals op regel 59-62, zonder `AbortController`/`signal` of enige timeout-configuratie.
- **Risico**: Een hangende backend-request (bv. een trage PDF-parse of database-lock) laat de frontend-aanroep onbeperkt wachten, zonder gebruikersfeedback of automatische annulering.
- **Power of Ten-regel**: Regel 2/3 (begrensde uitvoering van I/O-operaties, geen onbegrensde wachttijd).
- **Aanbevolen oplossing**: Een standaard timeout toevoegen via `AbortController` met een redelijke default (bv. 30s), consistent toegepast in `apiFetch`.
- **Verificatiemethode**: Test (of handmatige simulatie met een kunstmatig vertraagde backend-response) die aantoont dat de fetch na de ingestelde timeout wordt geannuleerd in plaats van oneindig te wachten.
- **Veranderomvang**: Small.
- **Afhankelijkheden/blokkades**: Geen.

### PR-018 — OpenAI-sleutel onversleuteld opgeslagen

- **Ernst**: Medium
- **Component**: `backend/routers/settings.py`
- **Bewijs**: `settings.py:349-351`: `setting = db_models.Settings(key="openai_api_key", value={"key": api_key}, ...)` met de begeleidende comment `# Store as JSON for encryption later` (regel 351) — de sleutel wordt dus in platte tekst in de `settings`-tabel opgeslagen; "encryption later" is nooit geïmplementeerd (het endpoint zelf heeft overigens wél `require_permission("manage_api_settings")` op regel 327, dus dit is geen auth-gat, wel een opslagprobleem).
- **Risico**: Elke partij met leestoegang tot de database (inclusief de eerder genoemde gecommitte backup, PR-003) kan de OpenAI-sleutel in platte tekst uitlezen.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 9 (Security).
- **Aanbevolen oplossing**: De sleutel versleuteld opslaan (bv. met een applicatie-sleutel uit de omgeving, niet in de database zelf) vóórdat deze in `Settings.value` terechtkomt; dit is een gerichte wijziging in `settings.py`, geen bredere encryptie-architectuur.
- **Verificatiemethode**: Na de fix: directe inspectie van de `settings`-tabel toont geen leesbare sleutel meer in de `value`-kolom.
- **Veranderomvang**: Medium (vereist keuze van encryptiemechanisme en sleutelbeheer).
- **Afhankelijkheden/blokkades**: Vereist een beslissing over waar de encryptiesleutel zelf veilig wordt bewaard (bv. omgevingsvariabele) — dat mag zelf niet weer hardcoded worden (zie PR-002-patroon).

### PR-019 — Geen centrale/gestructureerde logging, health check zonder DB-check

- **Ernst**: Medium
- **Component**: `backend/routers/pdf_ingest.py`, `backend/main.py`
- **Bewijs**: `pdf_ingest.py:27`: `logging.basicConfig(level=logging.INFO)` wordt aangeroepen binnen een routermodule in plaats van centraal bij applicatiestart (`main.py`); andere modules configureren logging niet consistent op dezelfde manier (geen los `logging_config.py` of vergelijkbaar gevonden). `main.py:120-123`: `@app.get("/health") async def health_check(): return {"status": "healthy"}` — dit endpoint controleert geen databaseconnectie of andere afhankelijkheden, het retourneert altijd `"healthy"` ongeacht de werkelijke staat van de applicatie.
- **Risico**: Inconsistente logconfiguratie maakt troubleshooting in productie lastiger (geen request-ID's, geen gestructureerd formaat). Een health check die niets controleert geeft orchestration-tooling (bv. een load balancer of container-orchestrator) een vals gevoel van gezondheid, ook als de database onbereikbaar is.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 8 (Logging & observability).
- **Aanbevolen oplossing**: Logging-configuratie centraliseren in `main.py` bij opstart (eenmalig `logging.basicConfig`/`dictConfig`), en `health_check` uitbreiden met een lichte DB-ping (bv. `SELECT 1`) die bij falen een niet-200-statuscode teruggeeft. Geen volledige observability-stack binnen deze audit voorschrijven — dat hoort in Fase 4.
- **Verificatiemethode**: `/health` retourneert een niet-200 status wanneer de database-connectie wordt verbroken (handmatig te simuleren door de DB-bestandslocatie tijdelijk ontoegankelijk te maken in een testomgeving).
- **Veranderomvang**: Small (logging-centralisatie) tot Medium (health check met DB-ping).
- **Afhankelijkheden/blokkades**: Geen.

### PR-020 — Module-level mutable singletons

- **Ernst**: Medium
- **Component**: `backend/redistribution/bv_config.py`, `backend/redistribution/store_profiles.py`
- **Bewijs**: `bv_config.py:241`: `_global_bv_config: Optional[BVConfig] = None`, gemuteerd via `global _global_bv_config` in `get_bv_config()` (regel 251-256) en `reload_bv_config()` (regel 259-262). `store_profiles.py:35`: `_active_profiles: Dict[str, StoreProfile] = dict(_DEFAULT_PROFILES)`, gemuteerd via `global _active_profiles` in `set_store_profiles()` (regel 47-49). *(Correctie t.o.v. eerdere aantekening: het bestand staat op `backend/redistribution/store_profiles.py`, niet `backend/store_profiles.py`; de singleton wordt gedeclareerd op regel 35, niet regel 48 — regel 48 is de `global`-declaratie binnen de setter-functie.)*
- **Risico**: Module-level mutable state wordt gedeeld tussen alle requests binnen hetzelfde proces; bij gelijktijdige requests (of bij testparallellisatie) kan de ene request de configuratie van een andere beïnvloeden via `reload_bv_config()`/`set_store_profiles()`. In een single-worker dev-opstelling is dit onopvallend, maar het is een verborgen afhankelijkheid die niet expliciet via dependency injection loopt.
- **Power of Ten-regel**: Regel 6 (kleinste scope; geen nieuwe module-level mutable state).
- **Aanbevolen oplossing**: Binnen deze audit geen herontwerp voorschrijven (dat is een grotere architecturale wijziging, zie Fase 3); wel expliciet documenteren als bekende technische schuld met een duidelijke `# TODO`-referentie naar de standaard, zodat nieuwe code dit patroon niet herhaalt.
- **Verificatiemethode**: Code-review-checklist-item: geen nieuwe `global`-declaraties in nieuwe modules zonder expliciete motivatie in de PR-beschrijving.
- **Veranderomvang**: Large (echte oplossing = dependency injection door de hele redistribution-laag) — daarom in deze audit alleen gedocumenteerd, niet direct opgelost.
- **Afhankelijkheden/blokkades**: Vereist eerst Fase 2 (tests/CI) zodat een refactor van deze singletons veilig geverifieerd kan worden.

### PR-021 — Geen Alembic; ad-hoc schemamigraties, deels onvolledig

- **Ernst**: Medium
- **Component**: `backend/database.py`
- **Bewijs**: Schema wordt aangemaakt via `Base.metadata.create_all(bind=engine)` (`main.py:36`) gevolgd door `ensure_runtime_schema()` (`main.py:37`, gedefinieerd in `database.py:31-73`), die met losse `ALTER TABLE`-statements kolommen toevoegt (bv. regel 42-44, 68-70). De functie bevat zelf de bevestiging dat dit onvolledig is: `database.py:72-73`: `# rating en comment mogen NULL zijn (bestaande NOT NULL constraint verwijderen kan niet in SQLite zonder tabel herbouwen; nieuwe records slaan NULL correct op)`. Er is geen Alembic-configuratie in de repository (geen `alembic.ini`/`migrations/`-map gevonden); daarnaast bestaan losse `migrate_*.py`-scripts (buiten deze audit niet individueel geverifieerd op inhoud).
- **Risico**: Zonder versiebeheerd migratiesysteem is de exacte schemahistorie niet reproduceerbaar, en de eigen code-comment bevestigt dat minstens één constraint-wijziging (NOT NULL op `rating`/`comment` in `feedback`) niet daadwerkelijk op bestaande SQLite-bestanden wordt toegepast — bestaande databases kunnen dus afwijken van wat de modellen suggereren.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 6 (Data-integriteit) en hoofdstuk 12 (Deployment & herstel).
- **Aanbevolen oplossing**: Geen migratie van het bestaande ad-hoc-mechanisme binnen deze audit; wel als concrete stap in Fase 4 van het verbeterplan: Alembic invoeren voor nieuwe schemawijzigingen, met de huidige staat als baseline-migratie.
- **Verificatiemethode**: Een schone database, opgebouwd via `alembic upgrade head`, heeft een schema identiek aan een database die via het huidige `create_all` + `ensure_runtime_schema()`-pad is opgebouwd (te vergelijken via `sqlite3 .schema`).
- **Veranderomvang**: Large — bewust in Fase 4 geplaatst, niet in de kritieke fasen.
- **Afhankelijkheden/blokkades**: Vereist stabiele CI (Fase 2) om migraties te kunnen testen vóór ze worden ingevoerd.

### PR-022 — Grote modules met gemengde verantwoordelijkheid

- **Ernst**: Medium
- **Component**: `backend/routers/pdf_ingest.py`, `backend/redistribution/algorithm.py`
- **Bewijs**: `wc -l` bevestigt `backend/routers/pdf_ingest.py` = 913 regels en `backend/redistribution/algorithm.py` = 880 regels. `pdf_ingest.py` combineert binnen één bestand: HTTP-routing, bestandsopslag (regel 169-171), PDF-parsing-aanroep (regel 174), database-persistence (`save_to_database`, regel 279-344) en proposal-generatielogica (`generate_and_save_proposals`, regel 347-448) — vier duidelijk te onderscheiden verantwoordelijkheden in één module.
- **Risico**: Grote, multi-verantwoordelijkheid-modules zijn moeilijker te testen in isolatie, verhogen de kans op onbedoelde koppeling tussen HTTP-laag en domeinlogica, en maken code-review lastiger.
- **Power of Ten-regel**: Regel 4 (functie-/moduleomvang als richtlijn voor nieuwe code; bestaande overschrijdingen zijn technische schuld, geen reden voor een onmiddellijke herschrijving).
- **Aanbevolen oplossing**: Geen big-bang-refactor binnen deze audit. Zie Fase 3 van het verbeterplan voor een voorstel om `pdf_ingest.py` te splitsen in HTTP-laag, domeinlogica en persistence, ondersteund door de dan al aanwezige testdekking.
- **Verificatiemethode**: Na een toekomstige opsplitsing: elke nieuwe module blijft binnen de richtlijn van de standaard, en de bestaande tests (`test_bundle_planner.py`, `test_proposal_data_mapping.py`, e.a.) blijven slagen zonder aanpassing van hun assertions.
- **Veranderomvang**: Large — bewust niet in de kritieke fasen opgenomen.
- **Afhankelijkheden/blokkades**: Vereist eerst Fase 2 (tests/CI als vangnet) voordat een opsplitsing veilig kan plaatsvinden.

### PR-023 — npm audit meldt kwetsbaarheden

- **Ernst**: Medium
- **Component**: `frontend/`, root (`package.json`)
- **Bewijs**: Uitgevoerde verificatie: `frontend/` — `npm audit` na `npm ci` (271 packages) meldt 7 vulnerabilities (2 moderate, 5 high). Root — `npm audit` na `npm ci` (32 packages, alleen devDependencies `@playwright/test`/`concurrently`) meldt 1 critical severity vulnerability.
- **Risico**: Afhankelijk van de exacte kwetsbare packages (niet individueel herleid binnen deze audit — `npm audit` geeft alleen aantallen, geen namen zijn hier apart geverifieerd) kunnen dit build-tooling-kwetsbaarheden zijn met beperkte productie-impact, of kwetsbaarheden die daadwerkelijk in de gebundelde frontend terechtkomen. Dit onderscheid is **niet vastgesteld** binnen deze audit en vereist een aparte `npm audit`-detailanalyse.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 9 (Security) en hoofdstuk 11 (CI/CD & quality gates — een `npm audit`-gate ontbreekt).
- **Aanbevolen oplossing**: `npm audit` met detailoutput (`--json`) doorlopen, kwetsbaarheden classificeren (dev-only vs. productie-bundel), en waar mogelijk patchen via `npm audit fix` (niet `--force` zonder review, om breaking changes te vermijden).
- **Verificatiemethode**: Herhaal `npm audit` na patching; aantal high/critical bevindingen daalt naar het afgesproken acceptabele niveau (idealiter 0 voor productie-afhankelijkheden).
- **Veranderomvang**: Small tot Medium, afhankelijk van of patches breaking changes bevatten.
- **Afhankelijkheden/blokkades**: Geen directe blokkade; onafhankelijk uit te voeren.

### PR-024 — Gegenereerde artefacten getrackt in git

- **Ernst**: Medium
- **Component**: `backend/pdf_extraction_data.json`, `backend/pdf_extraction_report.html`
- **Bewijs**: `git ls-files | grep pdf_extraction` bevestigt dat `backend/pdf_extraction_data.json` en `backend/pdf_extraction_report.html` getrackt zijn (naast `backend/test_pdf_extraction.py`, dat wél broncode is en dus geen artefact).
- **Risico**: Gegenereerde output in versiebeheer leidt tot ruis in diffs, mogelijke merge-conflicten bij elke herverwerking, en een repository die groeit met data die reproduceerbaar is uit code.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 6/13 (Data-integriteit / Documentatie-hygiëne).
- **Aanbevolen oplossing**: `git rm --cached` op beide bestanden en toevoegen aan `.gitignore` indien ze door een testscript of handmatige run worden geregenereerd.
- **Verificatiemethode**: `git ls-files | grep pdf_extraction` geeft na de fix geen resultaat meer voor deze twee bestanden.
- **Veranderomvang**: Small.
- **Afhankelijkheden/blokkades**: Controleer eerst of `test_pdf_extraction.py` deze bestanden daadwerkelijk zelf regenereert (niet binnen deze audit geverifieerd — **niet vastgesteld**) voordat ze verwijderd worden, om te voorkomen dat een script stilzwijgend op een ontbrekend bestand faalt.

---

### PR-029 — INGETROKKEN: min-3-"schending" was een testartefact

- **Status**: **Ingetrokken op 2026-07-13** (zelfde dag toegevoegd en weer ingetrokken na nader onderzoek). Geen defect in de applicatiecode.
- **Oorspronkelijk vermoeden**: bij het opbouwen van het invariant-vangnet leek de min-3-regel in ~1% van willekeurige scenario's geschonden (een winkel op 1-2 stuks naast andere niet-lege winkels).
- **Oorzaak (vastgesteld)**: het testharnas was inconsistent, niet de algoritmecode. `generate_moves_for_article` groepeert winkels via `store.bv_name` (`_group_by_bv`), maar de move-gate `_bv_compatible` leidt de BV-groep af uit de *configuratie* op basis van winkel-CODE (`validate_bv_move`). In de synthetische scenario's kregen winkels een willekeurig `bv_name` dat níét overeenkwam met wat de configuratie voor die codes zegt (bijv. code `6` = "Lumitex B.V.", code `5` = "Panningen B.V."). Daardoor weigerde de planner terecht een cross-BV donor, waardoor een receiver onder-gevuld bleef — een artefact van de tegenstrijdige testopstelling, niet van de planner.
- **Verificatie**: met een consistente wereld (`enforce_bv_separation=False`, geen configuratie-afhankelijkheid) houdt de min-3-regel over **3000 willekeurige scenario's zonder enkele schending**. Deze invariant staat nu permanent geborgd in `backend/test_redistribution_invariants.py` (`test_min_3_rule_holds`). Zie POS-011.
- **Les**: BV-afhankelijke tests moeten winkelcodes gebruiken die consistent zijn met de configuratie (zoals `test_bundle_planner.py` doet), of `enforce_bv_separation=False` om de pure planner-logica te isoleren.

---

## Low

### PR-025 — 2 falende tests door test-isolatie (geen productiebug)

- **Ernst**: Low
- **Component**: `backend/test_situation_classifier.py`
- **Bewijs**: Uitgevoerde verificatie: gecombineerde pytest-run van 6 draaibare bestanden geeft "37 passed, 2 failed" (39 items, 1.41s). Beide failures zitten in `test_situation_classifier.py` met `sqlalchemy.exc.OperationalError: no such table: artikel_voorraad`. Oorzaak (vastgesteld tijdens verificatie): het testbestand importeert nooit `main` (waar `Base.metadata.create_all` wordt aangeroepen), waardoor de tabellen niet bestaan in de door pytest gebruikte lege database.
- **Risico**: Geen productierisico — dit is een test-isolatieprobleem (ontbrekende setup/fixture), geen bug in de applicatielogica zelf.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 10 (Teststrategie).
- **Aanbevolen oplossing**: Een pytest-fixture toevoegen die `Base.metadata.create_all` aanroept (of `main` importeert) vóórdat deze specifieke tests draaien, consistent met hoe andere testbestanden dat kennelijk al goed doen (die faalden niet op dezelfde tabel-fout).
- **Verificatiemethode**: Na de fix: `pytest backend/test_situation_classifier.py -v` geeft 7/7 passed (huidige stand: 5 passed, 2 failed).
- **Veranderomvang**: Small.
- **Afhankelijkheden/blokkades**: Vereist eerst PR-012 (pytest/httpx als reproduceerbare dependency) om dit consistent te kunnen verifiëren.

### PR-026 — Meerderheid van root-testbestanden zonder assertions

- **Ernst**: Low
- **Component**: `backend/test_*.py`
- **Bewijs**: 21 `test_*.py`-bestanden in `backend/` (geverifieerd via `ls test_*.py | wc -l`). Eigen verificatie (grep op `def test_`, `assert `, `assertEqual`/`assertTrue`/`assertFalse`/`assertRaises` per bestand) toont dat 11 van de 21 bestanden geen enkele assertion bevatten: `test_54448_negative.py`, `test_auth_flow.py`, `test_login_simple.py` (geen `def test_`-functie, puur procedureel top-level scriptcode die print-statements uitvoert), en `test_all_pdfs.py`, `test_batch_api.py`, `test_complete_auth.py`, `test_generate_proposals.py`, `test_negative_voorraad.py`, `test_pdf_extraction.py`, `test_redistribution_algo.py`, `test_verkocht_fix.py` (wél een `test_`-functie met een `if __name__ == "__main__":`-blok, maar zonder enige `assert`). De overige 10 bestanden bevatten wél assertions, waarvan 6 daadwerkelijk als pytest zijn uitgevoerd tijdens de verificatie (zie VERIFICATION_RESULTS) en 3 door de ontbrekende `httpx`-dependency niet konden draaien (PR-012).
- **Risico**: Deze 11 scripts geven bij handmatige uitvoering (`python test_x.py`) alleen visuele output; ze bewijzen niets automatisch en worden bij een toekomstige pytest-gebaseerde CI (Fase 2) ofwel genegeerd (indien niet pytest-conform) ofwel — omdat drie ervan (`test_54448_negative.py`, `test_auth_flow.py`, `test_login_simple.py`) top-level code zonder `if __name__` bevatten — bij *pytest-collectie* per ongeluk uitgevoerd als import-bijwerking, wat ongewenste side effects (bv. echte DB-queries in `test_login_simple.py:12`) kan veroorzaken tijdens een CI-run.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 10 (Teststrategie).
- **Aanbevolen oplossing**: Deze scripts niet in de pytest-collectiescope opnemen (bv. via `pytest.ini`/`pyproject.toml` `testpaths`/`--ignore`, of ze hernoemen zodat ze niet matchen op `test_*.py`), en waar de onderliggende controle nuttig blijft, deze omzetten naar een echte `assert`-gebaseerde test in een apart traject (geen onderdeel van deze audit).
- **Verificatiemethode**: `pytest --collect-only backend/` toont na de fix alleen bestanden met echte testfuncties; de procedurele scripts verschijnen niet meer in de collectie.
- **Veranderomvang**: Small (uitsluiten van collectie) tot Medium (omzetten naar echte tests).
- **Afhankelijkheden/blokkades**: Onderdeel van Fase 0 (tests reproduceerbaar maken) in het verbeterplan.

### PR-027 — Verdwaald, vrijwel leeg lockbestand naast package-lock.json

- **Ernst**: Low
- **Component**: `frontend/pnpm-lock.yaml`
- **Bewijs**: `frontend/pnpm-lock.yaml` bestaat naast `frontend/package-lock.json` en bevat uitsluitend `lockfileVersion: '9.0'` en een lege `settings`-sectie (geverifieerd door het volledige bestand te lezen — geen `packages:`-sectie, geen dependency-vergrendeling). Het project gebruikt aantoonbaar npm (`package-lock.json` is aanwezig en werd gebruikt tijdens de verificatie via `npm ci`).
- **Risico**: Gemengde signalen over welke package manager leidend is; een toekomstige bijdrager die `pnpm install` gebruikt op basis van dit bestand krijgt een inconsistente afhankelijkhedenboom t.o.v. `package-lock.json`.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 13 (Documentatie/tooling-hygiëne).
- **Aanbevolen oplossing**: `frontend/pnpm-lock.yaml` verwijderen, tenzij er een bewuste reden is om naar pnpm te migreren (dat zou dan `package-lock.json` juist moeten vervangen, niet ernaast bestaan).
- **Verificatiemethode**: `git ls-files frontend/ | grep lock` toont na de fix alleen `package-lock.json`.
- **Veranderomvang**: Small.
- **Afhankelijkheden/blokkades**: Geen.

### PR-028 — Dependencies gepind op `latest`

- **Ernst**: Low
- **Component**: `frontend/package.json`
- **Bewijs**: `frontend/package.json:49`: `"date-fns": "latest"`, regel 55: `"next-themes": "latest"` (geverifieerd via directe inspectie van het bestand).
- **Risico**: `"latest"` betekent dat elke nieuwe `npm install`/`npm ci` (zonder bestaande lockfile-entry) een andere versie kan ophalen dan eerder getest, wat reproduceerbaarheid van builds ondermijnt.
- **Power of Ten-regel**: Uitbreiding hoofdstuk 11 (CI/CD & quality gates — reproduceerbare builds).
- **Aanbevolen oplossing**: Vastzetten op de huidige geïnstalleerde versie (zoals vastgelegd in `package-lock.json`) met een expliciet semver-bereik (bv. `^3.6.0`) in plaats van `latest`.
- **Verificatiemethode**: `grep '"latest"' frontend/package.json` geeft na de fix geen resultaat meer.
- **Veranderomvang**: Small.
- **Afhankelijkheden/blokkades**: Geen.

---

## Wat behouden moet blijven

### POS-001 — Volledig gepinde productieafhankelijkheden

`backend/requirements.txt` pint elke afhankelijkheid met een exacte versie (`==`), bv. `fastapi==0.115.5`, `sqlalchemy==2.0.36`, `pydantic==2.10.3` (volledige lijst geverifieerd). Dit ondersteunt reproduceerbare backend-installaties.

### POS-002 — Pydantic-validatie en afgedwongen wachtwoordsterkte

De meeste JSON-request-bodies gebruiken Pydantic-modellen voor validatie. `validate_password_strength` (`backend/auth.py:50-96`) implementeert concrete OWASP-achtige regels (lengte, hoofdletter, kleine letter, cijfer, speciaal teken, geen gebruikersnaam-substring, geen bekende sequenties, geen herhalingen) en wordt daadwerkelijk aangeroepen bij zowel gebruikersaanmaak als wachtwoordwijziging: `backend/routers/users.py:241` (aanmaken) en `backend/routers/users.py:536` (wijzigen).

### POS-003 — Aanwezige RBAC-machinerie

`require_permission` en `require_role` (`backend/auth.py:194-249`) bieden een werkende, herbruikbare autorisatielaag, consequent toegepast in `users.py`, `roles.py`, `settings.py`, `assignments.py`, `dashboard.py`, `feedback.py` en `algorithm_import.py`. Dit is precies de machinerie die nodig is om PR-001 op te lossen — er hoeft niets nieuws ontworpen te worden.

### POS-004 — Guard-counter tegen oneindige lus

`backend/redistribution/algorithm.py:492-500` implementeert een expliciete guard-counter (`guard = 0`, `guard += 1`, `if guard > 200: ... break`, met een gelogde waarschuwing) rond een `while`-lus die theoretisch niet gegarandeerd termineert. Dit is precies het patroon dat Power of Ten-regel 2 (vaste lusbovengrens) voorschrijft, en dient als goed voorbeeld voor de rest van de codebase.

### POS-005 — Streaming upload in plaats van read-all

`backend/routers/pdf_ingest.py:171`: `shutil.copyfileobj(file.file, buffer)` streamt het geüploade bestand naar disk in plaats van het volledig in het geheugen te lezen (`file.read()`). Dit beperkt geheugengebruik bij grote uploads, ongeacht de ontbrekende size-limit uit PR-005.

### POS-006 — Doordachte `.gitignore`

De root-`.gitignore` dekt Python-artefacten, `node_modules/`, `.next/`, omgevingsbestanden (`.env*`), databasebestanden (`*.db`, `database.db`, `*.db.backup_*`), uploads en editor-/OS-specifieke bestanden. Dat de drie backup-bestanden uit PR-003 toch getrackt zijn komt doordat ze vóór de betreffende regel zijn gecommit (zie PR-003) — de regel zelf is inhoudelijk correct en voorkomt herhaling.

### POS-007 — Groene kernlogica-tests (bundle planner en store sorting)

Uitgevoerde verificatie: `test_bundle_planner.py` — 9 passed; `test_store_sorting.py` — 16 passed. Samen dekken deze de kritieke domeinlogica (bundel-/herverdelingsplanning en winkelsortering) die het hart van de applicatie vormt.

### POS-008 — Database-constraints: unieke sleutels en cascade-foreign keys

`backend/db_models.py` bevat op meerdere plekken bewuste constraints: `unique=True` op `Store.name`/`Store.code`, `Article.artikelnummer`, `User.username`/`User.email`, `Role.name`, `Permission.name`, `Settings.key`; expliciete `UniqueConstraint`s op `AssignmentSeries` (regel 174) en `AssignmentItem` (regel 204); en `ondelete='CASCADE'` op de foreign keys van `AssignmentItem.series_id` (regel 183) en de `role_permissions`-koppeltabel (regel 353-354).

### POS-009 — Documentgovernance

De repository bevat een expliciete documentatiestructuur (`docs/DOCUMENTATION_GUIDELINES.md`) met een root-bestandswhitelist en categorie-indeling, aangevuld met `docs/PROJECT_CONTEXT_INDEX.md` (conflictresolutie-volgorde tussen documenten) en Keep-a-Changelog-discipline in `CHANGELOG.md`. Dit is een goede basis om de nieuwe engineeringstandaard en dit auditrapport in op te nemen.

### POS-010 — Health-endpoints aanwezig

`backend/main.py:111-123` bevat zowel een root-endpoint (`GET /`) als een `GET /health`-endpoint. De inhoud van `/health` is beperkt (zie PR-019), maar het endpoint zelf — als aanknopingspunt voor orchestration-tooling — is al aanwezig en hoeft niet vanaf nul te worden opgezet.

### POS-011 — Kernalgoritme-invarianten geverifieerd en geborgd

Toegevoegd op 2026-07-13. `backend/test_redistribution_invariants.py` borgt met property-based tests (120 seeds) de kritieke invarianten van het herverdelingsalgoritme uit hoofdstuk 10: **voorraadbehoud**, **geen negatieve voorraad**, **min-3-regel** en **moves naar alleen bestaande winkels**. Verkenning over duizenden willekeurige scenario's toonde geen enkele schending van deze invarianten (de aanvankelijk vermoede min-3-afwijking bleek een testartefact, zie PR-029). Dit is zowel een bevestiging dat de kernlogica correct is, als een blijvend vangnet dat een toekomstige refactor (Fase 3) niet ongemerkt de invarianten mag breken.

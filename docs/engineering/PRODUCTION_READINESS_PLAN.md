---
title: Production Readiness Plan
category: technical
tags: [engineering, production-readiness, roadmap, power-of-ten]
last_updated: 2026-07-13
related:
  - docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md
  - docs/engineering/PRODUCTION_READINESS_AUDIT.md
  - docs/DOCUMENTATION_GUIDELINES.md
status: draft
---

# Production Readiness Plan

## Doel

Dit document beschrijft een gefaseerd, klein-committeerbaar pad van de
huidige repository-toestand naar production-ready, gebaseerd op de
bevindingen in `docs/engineering/PRODUCTION_READINESS_AUDIT.md` (audit-ID's
PR-001 t/m PR-028). Elke stap is bedoeld om afzonderlijk gereviewd en
gecommit te kunnen worden. De canonieke engineeringstandaard waaraan elke
stap moet voldoen staat in
`docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md`.

## Uitgangsprincipes

1. **Klein en review-baar.** Elke stap is beperkt tot een afgebakende
   wijziging die in één commit past en op zichzelf te beoordelen is. Grote
   refactors (bv. het opsplitsen van `pdf_ingest.py`) worden expliciet
   uitgesteld naar Fase 3, ná een vangnet van tests/CI.
2. **Nooit een gate uitschakelen om "groen" te halen.** Als een nieuwe
   check (lint, typecheck, test) faalt, wordt de onderliggende oorzaak
   opgelost — niet de check verzwakt, uitgezet of overgeslagen. Zie
   specifiek PR-010: de volgorde is eerst de typefouten fixen, dán pas
   `ignoreBuildErrors` verwijderen.
3. **Geen destructieve acties zonder expliciete, aparte goedkeuring.**
   Geschiedenis-herschrijving, secret-rotatie en productiedata-migraties
   worden als aparte, met de repository-eigenaar af te stemmen acties
   benoemd, niet stilzwijgend uitgevoerd als onderdeel van een stap.
4. **Elke stap is testbaar en terug te draaien.** Elke stap hieronder
   bevat concrete testcommando's en een expliciete rollback-optie.

## Fasen op hoofdlijnen

| Fase | Doel |
|---|---|
| Fase 0 | Baseline vastleggen en beschermen: git-hygiëne, reproduceerbare tests, tooling-inventaris. |
| Fase 1 | Kritieke risico's sluiten: auth, secrets, uploads, idempotentie, transacties, CORS. |
| Fase 2 | Quality gates invoeren: lint/typecheck/CI, zodat regressie in Fase 1 niet ongemerkt terugkeert. |
| Fase 3 | Architectuur en onderhoudbaarheid: modules opsplitsen, typering, dependency injection. |
| Fase 4 | Productievalidatie: deployment, database-robuustheid, observability, runbook. |

> **Voortgangsstand (2026-08-12):** Fase 0–2 zijn grotendeels afgerond en Fase 3
> is inhoudelijk klaar (PR #1–#9 op `main`): auth, secrets, uploadlimieten, CORS,
> rate limiting, idempotentie-guards en `ArtikelVoorraad`-constraints (Fase 1);
> CI met ruff/mypy/pytest + frontend tsc/lint/build (Fase 2); `algorithm.py` en
> `pdf_ingest.py` opgesplitst, config-dependency-injection en `mypy` blokkerend
> voor de Kritiek-domeinlaag (Fase 3). **Fase 4 is nog niet gestart** en blijft
> geblokkeerd op een bekend deployment-doel; ook PR-003 (secret-rotatie +
> git-historie) en PR-007 (transactiegrens) vragen een eigenaarsbeslissing. Zie
> de statusreconciliatie in `PRODUCTION_READINESS_AUDIT.md` voor de
> per-bevinding-stand.

---

## Fase 0 — Baseline en bescherming

**Doelstelling**: de huidige toestand reproduceerbaar en veilig maken om op
verder te bouwen, zonder nog functioneel gedrag te wijzigen. Dit is de
voorwaarde voor alle volgende fasen.

### Stap 0.1 — Git-hygiëne herstellen: databasebackups uit git verwijderen

- **Doel**: de drie getrackte `database.db.backup_*`-bestanden (PR-003) uit
  toekomstige commits verwijderen, zonder de bestaande `.gitignore`-regel
  (die al aanwezig is) te wijzigen.
- **Betrokken bestanden**: `backend/database.db.backup_20251029_002226`,
  `backend/database.db.backup_20251029_002437`,
  `backend/database.db.backup_20251029_002506`.
- **Gekoppelde bevinding(en)**: PR-003.
- **Risico**: `git rm --cached` verwijdert de bestanden alleen uit de
  index/toekomstige commits, niet uit de git-geschiedenis — de data blijft
  bereikbaar via oudere commits totdat een aparte geschiedenis-herschrijving
  plaatsvindt. Lokale werkkopieën van andere ontwikkelaars behouden de
  bestanden op disk tot hun volgende `git pull`/`fetch` + cleanup.
- **Afhankelijkheden**: geen.
- **Acceptatiecriteria**: `git ls-files | grep "database.db.backup"` geeft
  geen resultaat meer na de commit; `.gitignore` blijft ongewijzigd (de
  regel `*.db.backup_*` bestaat al).
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool
  git rm --cached backend/database.db.backup_20251029_002226 \
                   backend/database.db.backup_20251029_002437 \
                   backend/database.db.backup_20251029_002506
  git status --porcelain
  git ls-files | grep "database.db.backup"   # verwacht: leeg
  ```
- **Rollbackmogelijkheid**: `git reset HEAD -- backend/database.db.backup_*`
  vóór de commit; na de commit via `git revert <commit>`.

**Vervolgactie (buiten deze stap, apart te plannen)**: alle secrets die in
het 241.664-byte backupbestand kunnen staan (wachtwoordhashes, de OpenAI-
sleutel uit PR-018) als gecompromitteerd beschouwen en roteren. Dit is een
operationele beslissing die met de repository-eigenaar moet worden
afgestemd, geen automatische code-wijziging.

### Stap 0.2 — Gegenereerde artefacten uit git verwijderen

- **Doel**: `backend/pdf_extraction_data.json` en
  `backend/pdf_extraction_report.html` (PR-024) uit git verwijderen.
- **Betrokken bestanden**: bovengenoemde twee bestanden; eventueel
  `.gitignore` als blijkt dat ze door een script worden geregenereerd.
- **Gekoppelde bevinding(en)**: PR-024.
- **Risico**: laag; controleer eerst of `backend/test_pdf_extraction.py`
  deze bestanden verwacht te vinden (i.p.v. te genereren) voordat ze
  verwijderd worden, om een stille testfout te voorkomen.
- **Afhankelijkheden**: geen.
- **Acceptatiecriteria**: bestanden niet meer in `git ls-files`;
  `test_pdf_extraction.py` faalt niet nieuw door hun afwezigheid (of, als
  het wél afhankelijk blijkt, eerst het script aanpassen om ze te
  regenereren vóór verwijdering uit git).
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool
  grep -n "pdf_extraction_data.json\|pdf_extraction_report.html" backend/test_pdf_extraction.py
  git rm --cached backend/pdf_extraction_data.json backend/pdf_extraction_report.html
  git ls-files | grep pdf_extraction   # verwacht: alleen test_pdf_extraction.py
  ```
- **Rollbackmogelijkheid**: `git reset HEAD -- backend/pdf_extraction_*`
  vóór de commit; na de commit via `git revert`.

### Stap 0.3 — Testafhankelijkheden vastleggen in requirements-dev.txt

- **Doel**: `pytest` en `httpx` reproduceerbaar beschikbaar maken zonder
  `backend/requirements.txt` (de productie-afhankelijkhedenlijst) te
  wijzigen.
- **Betrokken bestanden**: nieuw bestand `backend/requirements-dev.txt`.
- **Gekoppelde bevinding(en)**: PR-012.
- **Risico**: laag; puur additief, raakt geen bestaande code.
- **Afhankelijkheden**: geen.
- **Acceptatiecriteria**: `pip install -r backend/requirements.txt -r
  backend/requirements-dev.txt` slaagt in een schone virtualenv; de drie
  eerder falende testbestanden (`test_algorithm_import_router.py`,
  `test_dashboard_summary.py`, `test_user_store_assignments.py`) geven geen
  `ModuleNotFoundError: httpx` meer bij collectie.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  python -m venv /tmp/pr-venv
  /tmp/pr-venv/bin/pip install -r requirements.txt -r requirements-dev.txt
  /tmp/pr-venv/bin/python -m pytest test_algorithm_import_router.py test_dashboard_summary.py test_user_store_assignments.py -v
  ```
- **Rollbackmogelijkheid**: nieuw bestand verwijderen; geen impact op
  bestaande installaties omdat `requirements.txt` ongewijzigd blijft.

### Stap 0.4 — Bestaande tests reproduceerbaar draaien en de 2 falende tests isoleren

- **Doel**: een reproduceerbare baseline-testrun vastleggen (huidige
  bevestigde stand: 37 passed, 2 failed op 39 verzamelde items over 6
  bestanden) en de 2 falende `test_situation_classifier.py`-tests (PR-025)
  te fixen via test-isolatie, niet via productiecode-wijziging.
- **Betrokken bestanden**: `backend/test_situation_classifier.py` (fixture
  toevoegen die het schema aanmaakt vóór de test draait, bv. door `main`
  te importeren of expliciet `Base.metadata.create_all` aan te roepen in
  een `conftest.py` of test-setup).
- **Gekoppelde bevinding(en)**: PR-025.
- **Risico**: een fixture die het schema aanmaakt moet een aparte,
  wegwerpbare testdatabase gebruiken (zie Stap 0.6) — niet de lokale
  `backend/database.db` van een ontwikkelaar aanraken.
- **Afhankelijkheden**: Stap 0.3 (pytest/httpx beschikbaar), Stap 0.6
  (aparte dev/test-database).
- **Acceptatiecriteria**: `pytest test_situation_classifier.py -v` geeft
  7/7 passed (huidige stand: 5 passed, 2 failed); de overige 8 al
  slagende bestanden blijven slagen.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  /tmp/pr-venv/bin/python -m pytest test_situation_classifier.py -v --tb=short
  /tmp/pr-venv/bin/python -m pytest test_bundle_planner.py test_store_sorting.py test_situation_classifier.py test_offline_situation_evaluation.py test_algorithm_import_service.py test_proposal_data_mapping.py test_algorithm_import_router.py test_dashboard_summary.py test_user_store_assignments.py -v
  ```
- **Rollbackmogelijkheid**: wijziging beperkt tot het testbestand/een
  nieuwe `conftest.py`; `git revert` volstaat.

### Stap 0.5 — Tooling-inventaris vastleggen

- **Doel**: expliciet documenteren welke tooling wél/niet aanwezig is
  (geen ruff/mypy/pyproject.toml, geen ESLint-config, geen `.github/`),
  zodat Fase 2 een concreet startpunt heeft in plaats van aannames.
- **Betrokken bestanden**: geen codewijziging; deze inventaris is al
  vastgelegd in PR-011 van de audit en dient als brontabel voor Fase 2.
- **Gekoppelde bevinding(en)**: PR-011.
- **Risico**: geen (documentatie-only, al opgenomen in de audit).
- **Afhankelijkheden**: geen.
- **Acceptatiecriteria**: n.v.t. — informatief; zie PR-011 in de audit.
- **Testcommando's**: n.v.t.
- **Rollbackmogelijkheid**: n.v.t.

### Stap 0.6 — Aparte dev/test-database om productiedata te beschermen

- **Doel**: voorkomen dat testruns of lokaal ontwikkelwerk de bestaande
  `backend/database.db` muteren (deze wordt door SQLite-pad in
  `backend/database.py:12` standaard gebruikt voor zowel dev als, mogelijk,
  productie-achtig gebruik).
- **Betrokken bestanden**: geen wijziging aan `database.py` zelf binnen
  deze stap; wel een expliciete afspraak/instructie (bv. in
  `backend/.env.example` of een test-`conftest.py`) om tijdens tests een
  losse databaselocatie (bv. `sqlite:///:memory:` of een tijdelijk bestand)
  te gebruiken.
- **Gekoppelde bevinding(en)**: ondersteunt PR-025 en algemene
  testveiligheid (hoofdstuk 10 van de standaard).
- **Risico**: als dit niet consequent wordt toegepast, kan een toekomstige
  testrun alsnog per ongeluk tegen de echte `database.db` draaien.
- **Afhankelijkheden**: geen.
- **Acceptatiecriteria**: een testrun met de nieuwe fixture laat
  `backend/database.db` (indien aanwezig) qua wijzigingstijdstip
  ongemoeid; `git status --porcelain` toont geen wijziging aan getrackte
  bestanden na een testrun.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool
  stat -c '%Y' backend/database.db 2>/dev/null || echo "geen lokaal database.db aanwezig"
  cd backend && /tmp/pr-venv/bin/python -m pytest test_bundle_planner.py -v
  stat -c '%Y' database.db 2>/dev/null || echo "nog steeds geen database.db"
  ```
- **Rollbackmogelijkheid**: n.v.t. (geen destructieve wijziging).

### Stap 0.7 — Backup-/herstelpunt bevestigen

- **Doel**: bevestigen dat er een terugvalpunt bestaat vóórdat verdere
  wijzigingen in latere fasen worden doorgevoerd.
- **Betrokken bestanden**: geen.
- **Gekoppelde bevinding(en)**: n.v.t. — procesbevestiging.
- **Risico**: geen.
- **Afhankelijkheden**: geen.
- **Acceptatiecriteria**: de git-tag `backup/pre-p10-standard` bestaat en
  wijst naar een commit vóór de wijzigingen uit dit plan.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool
  git tag -l "backup/pre-p10-standard"
  git log -1 --format="%H %ad %s" --date=short backup/pre-p10-standard
  ```
- **Rollbackmogelijkheid**: `git reset --hard backup/pre-p10-standard` (of
  `git checkout backup/pre-p10-standard`) herstelt de volledige toestand
  van vóór deze wijzigingen — alleen te gebruiken na expliciete
  bevestiging, dit is een destructieve operatie.

---

## Fase 1 — Kritieke risico's

**Doelstelling**: de Critical- en High-bevindingen sluiten die tot
dataverlies, corruptie, security-incidenten, onbegrensde uitvoering of
stilzwijgend gemaskeerde fouten kunnen leiden. Elke stap hieronder staat op
zichzelf en kan in willekeurige volgorde binnen deze fase worden
uitgevoerd, tenzij expliciet anders vermeld.

### Stap 1.1 — Authenticatie op muterende endpoints

- **Doel**: elk state-changing endpoint in `pdf_ingest.py`, `batches.py`,
  `articles.py` en `redistribution.py` van een auth-dependency voorzien,
  consistent met het bestaande patroon in `users.py`/`roles.py`.
- **Betrokken bestanden**: `backend/routers/pdf_ingest.py`,
  `backend/routers/batches.py`, `backend/routers/articles.py`,
  `backend/routers/redistribution.py`.
- **Gekoppelde bevinding(en)**: PR-001.
- **Risico**: kan bestaande, ongeauthenticeerde frontend-aanroepen breken
  als de frontend nog geen token meestuurt naar deze endpoints — vereist
  parallelle controle dat de frontend (via `apiFetch`/`api-client.ts`) al
  overal een `Authorization`-header meestuurt wanneer een gebruiker is
  ingelogd.
- **Afhankelijkheden**: geen technische afhankelijkheid; wel functionele
  afstemming met de frontend-auth-flow.
- **Acceptatiecriteria**: elke geïdentificeerde endpoint retourneert
  401/403 bij een aanroep zonder (of met onvoldoende) rechten, en 2xx bij
  een aanroep met een geldig token en de juiste permissie.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  /tmp/pr-venv/bin/python -m pytest test_algorithm_import_router.py test_dashboard_summary.py test_user_store_assignments.py -v
  # Nieuwe tests toevoegen naar analogie van deze bestanden voor pdf_ingest/batches/articles/redistribution
  ```
- **Rollbackmogelijkheid**: elke router afzonderlijk te reverten via
  `git revert` op het specifieke bestand/commit.

### Stap 1.2 — SECRET_KEY verplicht uit env, geen fallback

- **Doel**: de applicatie fail-fast laten starten wanneer `SECRET_KEY`
  ontbreekt, in plaats van stilzwijgend een publiek bekende default te
  gebruiken; `check_secret_key.py` niet langer de sleutel laten printen.
- **Betrokken bestanden**: `backend/auth.py` (regel 26),
  `backend/check_secret_key.py` (regel 15, 18).
- **Gekoppelde bevinding(en)**: PR-002.
- **Risico**: bestaande dev-omgevingen zonder `SECRET_KEY` in `.env`
  starten na deze wijziging niet meer — moet vooraf gecommuniceerd worden;
  `backend/.env.example` biedt al een sjabloon.
- **Afhankelijkheden**: geen.
- **Acceptatiecriteria**: opstarten zonder `SECRET_KEY` in de omgeving
  resulteert in een directe, duidelijke opstartfout; opstarten mét
  `SECRET_KEY` werkt ongewijzigd; `check_secret_key.py` toont niet langer
  de volledige sleutelwaarde.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  env -u SECRET_KEY /tmp/pr-venv/bin/python -c "import auth"   # verwacht: fout, geen stille fallback
  SECRET_KEY=test-key-1234567890 /tmp/pr-venv/bin/python -c "import auth; print('OK')"
  ```
- **Rollbackmogelijkheid**: `git revert` op het specifieke commit.

### Stap 1.3 — Upload-limieten en filename-sanitisering

- **Doel**: een maximale bestandsgrootte en content-type/extensie-check
  toevoegen aan `POST /api/pdf/ingest`, en de path-traversal via
  `file.filename` dichten.
- **Betrokken bestanden**: `backend/routers/pdf_ingest.py` (regel 95-101
  voor de limiet/check, regel 169 voor de filename-sanitisering).
- **Gekoppelde bevinding(en)**: PR-004, PR-005.
- **Risico**: te strikte limieten kunnen legitieme, grote PDF-batches
  blokkeren — de gekozen limiet moet worden afgestemd op realistische
  bestandsgroottes uit `dummyinfo/` of bestaande productie-uploads.
- **Afhankelijkheden**: geen.
- **Acceptatiecriteria**: een upload met een filename die `../`-sequenties
  bevat schrijft niet buiten `batch_dir`; een upload boven de limiet of met
  een niet-toegestane extensie geeft een 4xx-response in plaats van
  verwerking.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  # Nieuwe test: upload met filename "../../evil.txt" -> verifieer pad blijft binnen batch_dir
  # Nieuwe test: upload > limiet -> verwacht 4xx
  /tmp/pr-venv/bin/python -m pytest test_all_pdfs.py -v   # bestaande PDF-verwerkingsscript als regressie-smoke
  ```
- **Rollbackmogelijkheid**: `git revert` op het specifieke commit.

### Stap 1.4 — Idempotentie-guards op approve en ingest

- **Doel**: een dubbele `approve`-aanroep niet langer dubbele
  Feedback-rijen laten aanmaken; duplicatie bij herhaalde ingest expliciet
  onderzoeken vóór een constraint-wijziging.
- **Betrokken bestanden**: `backend/routers/pdf_ingest.py` (regel 764-805
  voor de approve-guard); eventueel `backend/db_models.py` (regel 285-320)
  voor een `UniqueConstraint`, ná data-audit.
- **Gekoppelde bevinding(en)**: PR-006.
- **Risico**: een `UniqueConstraint` op `ArtikelVoorraad` kan falen op
  bestaande, reeds gedupliceerde productiedata — daarom eerst alleen de
  approve-guard implementeren (laag risico), de unique-constraint pas na
  een aparte data-audit.
- **Afhankelijkheden**: de unique-constraint-stap is afhankelijk van een
  voorafgaande data-audit van bestaande `artikel_voorraad`-rijen.
- **Acceptatiecriteria**: een tweede `approve`-aanroep op dezelfde
  proposal verandert het aantal Feedback-rijen niet (of geeft een 409).
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  # Nieuwe test: approve tweemaal aanroepen, aantal Feedback-rijen vergelijken vóór/na
  /tmp/pr-venv/bin/python -m pytest test_proposal_data_mapping.py -v
  ```
- **Rollbackmogelijkheid**: `git revert`; de eventuele unique-constraint
  apart en pas na succesvolle data-audit toepassen, zodat deze stap
  onafhankelijk terug te draaien is.

### Stap 1.5 — Transactiegrens rond multi-step writes documenteren/expliciteren

- **Doel**: het huidige per-file-commit-gedrag in de ingest-loop expliciet
  vastleggen als bewust gedrag (partial success is toegestaan), of —
  indien de productbeslissing anders uitvalt — een omvattende
  transactiegrens invoeren.
- **Betrokken bestanden**: `backend/routers/pdf_ingest.py` (regel 164-232
  hoofdlus, regel 327/342 commits binnen `save_to_database`).
- **Gekoppelde bevinding(en)**: PR-007.
- **Risico**: het wijzigen naar één grote transactie kan het gedrag bij
  gedeeltelijk falen fundamenteel veranderen (nu: partial success bewaard;
  na wijziging: mogelijk alles-of-niets) — dit vereist een expliciete
  productbeslissing vóór implementatie.
- **Afhankelijkheden**: productbeslissing over gewenst transactiegedrag.
- **Acceptatiecriteria**: het gekozen gedrag (partial-success-bewust-
  gedocumenteerd, of atomaire transactie) is vastgelegd in zowel code-
  comments als (indien atomair) een test die een gefaalde batch volledig
  laat terugdraaien.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  /tmp/pr-venv/bin/python -m pytest test_generate_proposals.py -v
  ```
- **Rollbackmogelijkheid**: `git revert` op het specifieke commit.

### Stap 1.6 — Auth-refresh-handler smal maken

- **Doel**: de brede `except Exception` in `refresh_token` vervangen door
  specifieke foutafhandeling, zodat serverfouten niet meer als 401 worden
  gemaskeerd.
- **Betrokken bestanden**: `backend/routers/auth.py` (regel 113-177).
- **Gekoppelde bevinding(en)**: PR-008.
- **Risico**: als niet alle mogelijke exceptiepaden expliciet worden
  afgevangen, kan een onverwachte fout nu als 500 doorbreken in plaats van
  als 401 gemaskeerd te worden — dit is de bedoelde, betere uitkomst, maar
  moet met een test worden bevestigd.
- **Afhankelijkheden**: geen.
- **Acceptatiecriteria**: een ongeldig/verlopen refresh-token geeft nog
  steeds 401; een onverwachte serverfout (bv. `role is None`) geeft een
  server-foutcode (5xx) in plaats van 401, en wordt gelogd.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  /tmp/pr-venv/bin/python -m pytest test_complete_auth.py -v
  ```
- **Rollbackmogelijkheid**: `git revert` op het specifieke commit.

### Stap 1.7 — CORS ALLOWED_ORIGINS daadwerkelijk doorgeven

- **Doel**: de reeds opgebouwde `allowed_origins`-lijst uit de
  omgevingsvariabele daadwerkelijk aan `CORSMiddleware` doorgeven.
- **Betrokken bestanden**: `backend/main.py` (regel 40-61).
- **Gekoppelde bevinding(en)**: PR-009.
- **Risico**: een verkeerd geconfigureerde `ALLOWED_ORIGINS` kan de
  frontend blokkeren als de env-var niet overeenkomt met het daadwerkelijke
  frontend-origin — vereist afstemming met het (nog te bepalen)
  deploymentdoel uit Fase 4.
- **Afhankelijkheden**: geen technische afhankelijkheid; wel afstemming
  met Fase 4 (deploymentdoel).
- **Acceptatiecriteria**: het instellen van `ALLOWED_ORIGINS` op een
  aangepaste waarde heeft aantoonbaar effect op welke origins een
  CORS-preflight geaccepteerd krijgen.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  ALLOWED_ORIGINS="http://example.test:3000" SECRET_KEY=test-key /tmp/pr-venv/bin/python -c "
  import main
  print(main.app.user_middleware)
  "
  ```
- **Rollbackmogelijkheid**: `git revert` op het specifieke commit.

---

## Fase 2 — Quality gates

**Doelstelling**: geautomatiseerde poorten invoeren zodat de fixes uit
Fase 1 niet ongemerkt kunnen regresseren, en zodat Power of Ten-regel 10
(nul-warnings-beleid) daadwerkelijk afdwingbaar wordt.

### Stap 2.1 — requirements-dev.txt uitbreiden met ruff en mypy

- **Doel**: statische-analyse-tooling voor Python reproduceerbaar
  beschikbaar maken.
- **Betrokken bestanden**: `backend/requirements-dev.txt` (uit Stap 0.3).
- **Gekoppelde bevinding(en)**: PR-011.
- **Risico**: geen; additief.
- **Afhankelijkheden**: Stap 0.3.
- **Acceptatiecriteria**: `ruff --version` en `mypy --version` werken na
  installatie vanuit `requirements-dev.txt`.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  /tmp/pr-venv/bin/pip install -r requirements-dev.txt
  /tmp/pr-venv/bin/ruff --version
  /tmp/pr-venv/bin/mypy --version
  ```
- **Rollbackmogelijkheid**: regel(s) uit `requirements-dev.txt`
  verwijderen.

### Stap 2.2 — pyproject.toml met ruff/mypy-configuratie

- **Doel**: niet-destructieve, additieve configuratie voor ruff en mypy
  vastleggen, aansluitend bij de risicoclassificatie in de standaard
  (kritieke modules strenger dan experimentele).
- **Betrokken bestanden**: nieuw `backend/pyproject.toml` (of root
  `pyproject.toml` met `[tool.ruff]`/`[tool.mypy]`-secties, af te stemmen
  met de structuur die `PRODUCTION_ENGINEERING_STANDARD.md` voorschrijft).
- **Gekoppelde bevinding(en)**: PR-011.
- **Risico**: een te strikte eerste configuratie kan direct honderden
  bestaande meldingen opleveren — begin met een basisregelset en breid
  uit, in plaats van in één keer maximale striktheid af te dwingen.
- **Afhankelijkheden**: Stap 2.1.
- **Acceptatiecriteria**: `ruff check backend/` en `mypy backend/` draaien
  zonder configuratiefouten (het aantal inhoudelijke meldingen wordt apart
  vastgelegd als vertrekpunt, niet als blokkerende eis in deze stap).
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  /tmp/pr-venv/bin/ruff check .
  /tmp/pr-venv/bin/mypy .
  ```
- **Rollbackmogelijkheid**: `pyproject.toml` verwijderen/`git revert`.

### Stap 2.3 — Frontend ESLint flat config toevoegen

- **Doel**: `npm run lint` (`frontend/package.json:12`) daadwerkelijk laten
  werken door een `eslint.config.mjs` toe te voegen (Next.js flat config).
- **Betrokken bestanden**: nieuw `frontend/eslint.config.mjs`.
- **Gekoppelde bevinding(en)**: PR-011.
- **Risico**: de eerste lint-run kan een groot aantal bestaande meldingen
  opleveren; begin met de Next.js-aanbevolen basisconfiguratie.
- **Afhankelijkheden**: geen.
- **Acceptatiecriteria**: `CI=true npm run lint` geeft geen
  configuratiefout meer (huidige stand: exitcode 2, "couldn't find an
  eslint.config file").
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/frontend
  CI=true npm run lint
  ```
- **Rollbackmogelijkheid**: `eslint.config.mjs` verwijderen/`git revert`.

### Stap 2.4 — TypeScript-fouten oplossen, dan ignoreBuildErrors verwijderen

- **Doel**: de 2 bevestigde `TS2339`-fouten
  (`app/proposals/[id]/edit/page.tsx:54`, `app/proposals/[id]/page.tsx:34`,
  beide "Property 'batch_name' does not exist on type
  'BatchWithProposals'") oplossen, en pas dáárna
  `typescript.ignoreBuildErrors` uit `next.config.mjs` verwijderen.
- **Betrokken bestanden**: `frontend/app/proposals/[id]/edit/page.tsx`,
  `frontend/app/proposals/[id]/page.tsx`, het type `BatchWithProposals`
  (locatie te bepalen bij implementatie), `frontend/next.config.mjs`.
- **Gekoppelde bevinding(en)**: PR-010.
- **Risico**: **volgordekritiek** — als `ignoreBuildErrors` wordt
  verwijderd vóórdat de typefouten zijn opgelost, breekt de productie-build
  onmiddellijk. Deze stap moet als één samenhangende wijziging (of twee
  commits in de juiste volgorde binnen dezelfde PR) worden doorgevoerd.
- **Afhankelijkheden**: geen.
- **Acceptatiecriteria**: `npx tsc --noEmit` geeft exitcode 0; `npm run
  build` slaagt zonder de melding "Skipping validation of types".
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/frontend
  npx tsc --noEmit   # eerst: bevestig fix van de 2 fouten (exitcode 0)
  npm run build      # daarna pas: bevestig build slaagt met type-validatie aan
  ```
- **Rollbackmogelijkheid**: `git revert`; als de build na verwijdering van
  `ignoreBuildErrors` onverwacht faalt op andere, nog niet ontdekte
  typefouten, is het herstellen van `ignoreBuildErrors: true` een tijdelijke
  noodgreep — nooit als permanente oplossing, wel als expliciet
  gedocumenteerde, tijdelijke rollback-stap met een directe vervolgtaak om
  de nieuwe fouten alsnog op te lossen.

### Stap 2.5 — GitHub Actions CI-workflow

- **Doel**: een `.github/workflows/ci.yml` toevoegen die formatting/lint/
  typecheck/pytest/build als verplichte gates afdwingt op elke PR.
- **Betrokken bestanden**: nieuw `.github/workflows/ci.yml`.
- **Gekoppelde bevinding(en)**: PR-011.
- **Risico**: als de workflow te strikt wordt ingesteld vóórdat Stappen
  2.1-2.4 zijn afgerond, blokkeert CI onmiddellijk alle PR's — daarom pas
  invoeren nadat de andere Fase 2-stappen lokaal al slagen.
- **Afhankelijkheden**: Stap 0.3, 2.1, 2.2, 2.3, 2.4.
- **Acceptatiecriteria**: een PR met een introduceerde lint-/type-/
  testfout wordt door de workflow geblokkeerd (rode check); een PR zonder
  zulke fouten krijgt een groene check. Regel: een PR mag niet mergen bij
  een falende gate.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend && /tmp/pr-venv/bin/python -m pytest -v
  cd /home/user/digital-resupplying-tool/backend && /tmp/pr-venv/bin/ruff check . && /tmp/pr-venv/bin/mypy .
  cd /home/user/digital-resupplying-tool/frontend && npx tsc --noEmit && npm run lint && npm run build
  ```
- **Rollbackmogelijkheid**: workflow-bestand verwijderen/`git revert`;
  branch-protection-instellingen die de workflow als verplicht markeren
  moeten apart (buiten git) worden teruggedraaid in de GitHub-repo-
  instellingen.

---

## Fase 3 — Architectuur en onderhoudbaarheid

**Doelstelling**: de in de audit als Medium/Large aangemerkte
architecturale schuld gericht aanpakken, nu er een testvangnet en CI
(Fase 2) bestaat om regressies te detecteren.

### Stap 3.1 — pdf_ingest.py opsplitsen (HTTP vs domein vs persistence)

- **Doel**: `backend/routers/pdf_ingest.py` (913 regels) opsplitsen in een
  dunne HTTP-routinglaag, een domeinlogica-module (proposal-generatie) en
  een persistence-module (`save_to_database`), zonder het externe
  API-contract te wijzigen.
- **Betrokken bestanden**: `backend/routers/pdf_ingest.py` en nieuwe
  modules (bv. `backend/pdf_ingest_service.py`,
  `backend/pdf_ingest_persistence.py` — exacte indeling te bepalen bij
  implementatie).
- **Gekoppelde bevinding(en)**: PR-022.
- **Risico**: een opsplitsing zonder toereikende testdekking kan
  functionaliteit subtiel wijzigen (bv. impliciete volgordeafhankelijkheden
  tussen `save_to_database` en `generate_and_save_proposals`) — daarom pas
  na Fase 2.
- **Afhankelijkheden**: Fase 2 volledig afgerond (CI groen).
- **Acceptatiecriteria**: alle bestaande endpoints in `pdf_ingest.py`
  blijven functioneel identiek (zelfde request/response-contract); alle
  bestaande tests die deze module raken blijven slagen zonder aanpassing
  van hun assertions.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  /tmp/pr-venv/bin/python -m pytest test_bundle_planner.py test_proposal_data_mapping.py test_algorithm_import_service.py -v
  ```
- **Rollbackmogelijkheid**: `git revert` op de opsplitsings-commit(s);
  aanbevolen als reeks kleine commits (per geëxtraheerde functie) zodat
  gedeeltelijke rollback mogelijk is.

### Stap 3.2 — Getypeerde Pydantic-modellen voor moves

- **Doel**: `UpdateProposalRequest.moves: List[dict]` vervangen door een
  getypeerd `List[MoveModel]`, en de raw-key-toegang (`move["from_store"]`
  e.d.) elimineren.
- **Betrokken bestanden**: `backend/routers/pdf_ingest.py` (regel 89-92,
  707-720, 858-913, en `generate_and_save_proposals` regel 372-388).
- **Gekoppelde bevinding(en)**: PR-015.
- **Risico**: elke plek die `proposal.moves` als dict aanspreekt (ook
  buiten `pdf_ingest.py`, bv. in `algorithm_import/service.py` dat moves
  verrijkt) moet worden meegenomen, anders ontstaat een inconsistente
  mix van getypeerde en ongetypeerde toegang.
- **Afhankelijkheden**: Fase 2 (CI als vangnet); baat bij Stap 3.1
  (persistence-laag al gescheiden maakt dit overzichtelijker).
- **Acceptatiecriteria**: `PUT /proposals/{id}` met een move-payload zonder
  verplicht veld geeft een 422-Pydantic-validatiefout in plaats van een
  onbehandelde 500 (`KeyError`).
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  /tmp/pr-venv/bin/python -m pytest test_proposal_data_mapping.py test_algorithm_import_service.py -v
  ```
- **Rollbackmogelijkheid**: `git revert` op het specifieke commit.

### Stap 3.3 — Module-level singletons naar expliciete dependency-injection

- **Doel**: `_global_bv_config` (`backend/redistribution/bv_config.py:241`)
  en `_active_profiles`
  (`backend/redistribution/store_profiles.py:35`) vervangen door expliciet
  doorgegeven configuratie-objecten in plaats van module-level `global`-
  state.
- **Betrokken bestanden**: `backend/redistribution/bv_config.py`,
  `backend/redistribution/store_profiles.py`, en alle aanroepers
  (`backend/redistribution/algorithm.py` en gerelateerde modules).
- **Gekoppelde bevinding(en)**: PR-020.
- **Risico**: dit raakt de kernlogica van het herverdelingsalgoritme
  (`algorithm.py`, 880 regels) — een hoog-impact wijziging die zonder de
  bestaande 9 bundle-planner-tests en 16 store-sorting-tests als vangnet
  niet veilig is; ook risico op gemiste aanroeplocaties bij een dergelijke
  brede refactor.
- **Afhankelijkheden**: Fase 2 volledig afgerond; sterke aanbeveling om
  eerst de testdekking van `bv_config`/`store_profiles`-gedrag uit te
  breiden vóór de refactor start.
- **Acceptatiecriteria**: `test_bundle_planner.py` (9 tests) en
  `test_store_sorting.py` (16 tests) blijven slagen zonder aanpassing van
  hun assertions; geen `global`-statement meer in beide modules.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  /tmp/pr-venv/bin/python -m pytest test_bundle_planner.py test_store_sorting.py -v
  grep -n "^global \|    global " redistribution/bv_config.py redistribution/store_profiles.py   # verwacht: leeg na refactor
  ```
- **Rollbackmogelijkheid**: `git revert`; gezien de omvang aanbevolen als
  reeks kleine, onafhankelijk revertbare commits per module.

### Stap 3.4 — Frontend API-base consolideren

- **Doel**: `frontend/lib/api.ts` laten hergebruiken van dezelfde
  omgevingsgestuurde `API_BASE_URL` als `frontend/lib/api-client.ts`, als
  eerste stap naar één client.
- **Betrokken bestanden**: `frontend/lib/api.ts` (regel 10),
  `frontend/lib/api-client.ts` (regel 9).
- **Gekoppelde bevinding(en)**: PR-016.
- **Risico**: `api.ts` (901 regels) heeft mogelijk veel aanroeppunten door
  de hele frontend — een volledige consolidatie tot één client is groter
  dan deze stap; deze stap beperkt zich tot het delen van de
  basis-URL-constante, niet tot het samenvoegen van de volledige clients.
- **Afhankelijkheden**: geen harde afhankelijkheid, wel makkelijker met
  Fase 2 se typecheck-gate actief.
- **Acceptatiecriteria**: het instellen van `NEXT_PUBLIC_API_URL` op een
  afwijkende waarde heeft aantoonbaar effect op alle aanroepen via zowel
  `api.ts` als `api-client.ts`.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/frontend
  npx tsc --noEmit
  grep -n "API_BASE_URL" lib/api.ts lib/api-client.ts
  ```
- **Rollbackmogelijkheid**: `git revert` op het specifieke commit.

### Stap 3.5 — Functieomvang terugbrengen conform standaard (doorlopend)

- **Doel**: bij elke toekomstige wijziging aan `pdf_ingest.py`,
  `algorithm.py` en andere modules die de richtlijn uit de standaard
  overschrijden, de gelegenheid gebruiken om de geraakte functie dichter
  bij de richtlijn (≤ 60 regels) te brengen — geen aparte big-bang-actie,
  maar een doorlopende praktijk die in code review wordt bewaakt.
- **Betrokken bestanden**: n.v.t. (proces, geen specifiek bestand).
- **Gekoppelde bevinding(en)**: PR-022.
- **Risico**: geen (procesmaatregel).
- **Afhankelijkheden**: Fase 2 (CI als vangnet bij elke wijziging).
- **Acceptatiecriteria**: opgenomen als reviewrichtlijn in
  `PRODUCTION_ENGINEERING_STANDARD.md`, niet als eenmalig af te vinken
  taak.
- **Testcommando's**: n.v.t.
- **Rollbackmogelijkheid**: n.v.t.

---

## Fase 4 — Productievalidatie

**Doelstelling**: de repository geschikt maken voor een daadwerkelijke
deployment, inclusief database-robuustheid, observability en een
gedocumenteerde herstelprocedure. Deze fase vereist keuzes die buiten de
repository zelf liggen (deploymentdoel) en wordt daarom pas na Fase 1-3
uitgevoerd.

### Stap 4.1 — Deploymentdoel kiezen en reproduceerbare build

- **Doel**: een expliciet deploymentdoel vaststellen (dit is bij het
  opstellen van dit plan **niet vastgesteld** in de repository — er is
  geen Dockerfile, geen `.github/workflows/deploy.yml`, geen
  cloudconfiguratie gevonden) en een reproduceerbare build (bv.
  Dockerfile of CI-artifact) opzetten.
- **Betrokken bestanden**: nieuw `Dockerfile`(s) / CI-artifact-configuratie
  (exacte vorm afhankelijk van het gekozen deploymentdoel).
- **Gekoppelde bevinding(en)**: ondersteunt PR-009 (CORS-configuratie
  hangt af van het uiteindelijke domein/origin).
- **Risico**: een verkeerd gekozen deploymentmodel kan later kostbaar zijn
  om te wijzigen — dit is een bewuste, met de repository-eigenaar af te
  stemmen beslissing, geen technische auto-keuze.
- **Afhankelijkheden**: Fase 2 (CI) afgerond, zodat de build die
  gedeployed wordt ook de quality gates is gepasseerd.
- **Acceptatiecriteria**: een reproduceerbare build kan vanaf een schone
  checkout worden gemaakt zonder handmatige tussenstappen.
- **Testcommando's**: afhankelijk van gekozen doel, bv.
  ```bash
  docker build -t drt-backend ./backend
  docker build -t drt-frontend ./frontend
  ```
- **Rollbackmogelijkheid**: n.v.t. vóór eerste deployment; nadien
  standaard deployment-rollback van het gekozen platform.

### Stap 4.2 — SQLite → robuustere database overwegen bij concurrent gebruik

- **Doel**: expliciet beoordelen of SQLite (met
  `check_same_thread=False`, `backend/database.py:19`) toereikend is voor
  het verwachte gelijktijdige gebruik, of dat een overstap naar
  PostgreSQL/MySQL nodig is.
- **Betrokken bestanden**: `backend/database.py`.
- **Gekoppelde bevinding(en)**: gerelateerd aan PR-021 (migratiebeheer) en
  PR-007 (transactiegedrag).
- **Risico**: een databasewissel is een ingrijpende wijziging met impact
  op elke query in de codebase — dit is een beslissing, geen
  automatische actie binnen dit plan.
- **Afhankelijkheden**: Stap 4.1 (deploymentdoel bepaalt
  concurrency-eisen).
- **Acceptatiecriteria**: een expliciete, gedocumenteerde beslissing (blijf
  bij SQLite met beargumenteerde grenzen, of migreer) vastgelegd in de
  standaard of een apart ADR (architecture decision record).
- **Testcommando's**: n.v.t. (beslissingsstap).
- **Rollbackmogelijkheid**: n.v.t.

### Stap 4.3 — Alembic-migraties invoeren

- **Doel**: het ad-hoc `ensure_runtime_schema()`-mechanisme
  (`backend/database.py:31-73`) vervangen door versiebeheerde
  Alembic-migraties voor nieuwe schemawijzigingen, met de huidige staat
  als baseline.
- **Betrokken bestanden**: nieuw `backend/alembic.ini`,
  `backend/migrations/`; `backend/database.py` (aanroep van
  `ensure_runtime_schema()` uiteindelijk uit te faseren).
- **Gekoppelde bevinding(en)**: PR-021.
- **Risico**: bestaande lokale/productie-SQLite-bestanden moeten correct
  worden "gestempeld" als zijnde op de baseline-migratie, anders probeert
  Alembic tabellen opnieuw aan te maken die al bestaan.
- **Afhankelijkheden**: Stap 4.2 (databasekeuze), Fase 2 (CI).
- **Acceptatiecriteria**: `alembic upgrade head` op een schone database
  resulteert in een schema identiek aan het huidige
  `create_all`-gebaseerde schema; op een bestaande database resulteert
  `alembic stamp head` + toekomstige `alembic upgrade head` niet in
  dataverlies.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  /tmp/pr-venv/bin/alembic upgrade head
  sqlite3 database.db ".schema" > /tmp/alembic-schema.sql
  # Vergelijk met schema uit create_all + ensure_runtime_schema()
  ```
- **Rollbackmogelijkheid**: `alembic downgrade`; daarnaast blijft het
  oude `ensure_runtime_schema()`-pad tijdelijk als fallback gedocumenteerd
  totdat Alembic in alle omgevingen bevestigd werkt.

### Stap 4.4 — Geautomatiseerde databasebackups + geteste restore

- **Doel**: een reproduceerbaar backup- en restoreproces opzetten (in
  tegenstelling tot de ad-hoc, per ongeluk gecommitte
  `database.db.backup_*`-bestanden uit PR-003).
- **Betrokken bestanden**: nieuw backup-script/cron-configuratie (buiten
  git-tracked productiepaden, zie `.gitignore`-regel `*.db.backup_*`).
- **Gekoppelde bevinding(en)**: PR-003 (les geleerd), PR-021.
- **Risico**: een ongeteste restore-procedure is in een incident
  waardeloos — de restore moet minimaal één keer daadwerkelijk
  gedemonstreerd zijn.
- **Afhankelijkheden**: Stap 4.1 (deploymentdoel bepaalt waar backups
  worden opgeslagen — nooit in git).
- **Acceptatiecriteria**: een backup kan worden hersteld naar een werkende
  database, geverifieerd via een smoke-test (bv. login + batch-overzicht
  ophalen) tegen de herstelde database.
- **Testcommando's**: afhankelijk van het gekozen backup-mechanisme, bv.
  ```bash
  cp backend/database.db /tmp/backup-test.db
  sqlite3 /tmp/backup-test.db "PRAGMA integrity_check;"
  ```
- **Rollbackmogelijkheid**: n.v.t. (dit ís het rollback-mechanisme voor de
  rest van de applicatie).

### Stap 4.5 — Observability: gestructureerde logging, request-ID, health met DB-check, metrics

- **Doel**: `logging.basicConfig` centraliseren (uit `pdf_ingest.py:27`
  naar `main.py`), request-ID's introduceren, en `/health`
  (`main.py:120-123`) uitbreiden met een echte DB-connectiecheck.
- **Betrokken bestanden**: `backend/main.py`,
  `backend/routers/pdf_ingest.py` (regel 27 verwijderen/verplaatsen).
- **Gekoppelde bevinding(en)**: PR-019.
- **Risico**: laag; vooral additief, met uitzondering van het verplaatsen
  van de logging-configuratie (kan logniveau-gedrag in bestaande
  omgevingen beïnvloeden als daar stilzwijgend op vertrouwd werd).
- **Afhankelijkheden**: geen harde afhankelijkheid; logisch te combineren
  met Stap 4.1.
- **Acceptatiecriteria**: `/health` retourneert een niet-200-status
  wanneer de database onbereikbaar is; logregels van verschillende
  modules hebben een consistent formaat.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool/backend
  SECRET_KEY=test-key /tmp/pr-venv/bin/python -c "
  from fastapi.testclient import TestClient
  from main import app
  client = TestClient(app)
  r = client.get('/health')
  print(r.status_code, r.json())
  "
  ```
- **Rollbackmogelijkheid**: `git revert` op het specifieke commit.

### Stap 4.6 — Rollbackstrategie, deploymentchecklist en runbook

- **Doel**: een operationeel runbook (in `docs/`) vastleggen: hoe een
  deployment terug te draaien, welke stappen bij een incident te volgen,
  en een checklist vóór elke productie-release.
- **Betrokken bestanden**: nieuw `docs/technical/deployment-runbook.md`
  (of vergelijkbare, conform `docs/DOCUMENTATION_GUIDELINES.md`-categorie-
  indeling).
- **Gekoppelde bevinding(en)**: samenvattend voor Fase 4.
- **Risico**: geen (documentatie).
- **Afhankelijkheden**: Stap 4.1 t/m 4.5 (het runbook beschrijft wat
  daadwerkelijk is opgezet, geen aspiraties vooruitlopend op de techniek).
- **Acceptatiecriteria**: het runbook is door iemand anders dan de auteur
  te volgen om een testrollback daadwerkelijk uit te voeren.
- **Testcommando's**: n.v.t. (procesdocument; validatie door een
  droogoefening van de procedure).
- **Rollbackmogelijkheid**: n.v.t.

### Stap 4.7 — Playwright-smoke in CI tegen een testomgeving

- **Doel**: de bestaande `tests/browser/smoke.spec.ts` (7 smoke tests,
  aangestuurd via `npm run browser:smoke` in het root-`package.json`) in
  CI laten draaien tegen een opgezette test-instantie van backend +
  frontend + geseede database.
- **Betrokken bestanden**: `.github/workflows/ci.yml` (uitbreiding),
  mogelijk een apart `docker-compose`- of CI-service-configuratie voor de
  testomgeving.
- **Gekoppelde bevinding(en)**: ondersteunt algehele verificatie van
  Fase 1-3.
- **Risico**: een geseede test-database in CI mag nooit productiedata
  bevatten; moet volledig synthetisch zijn opgebouwd.
- **Afhankelijkheden**: Stap 4.1 (reproduceerbare build om tegen te
  draaien), Fase 2 (CI-infrastructuur bestaat al).
- **Acceptatiecriteria**: `npm run browser:smoke` slaagt in CI tegen de
  opgezette testomgeving, met alle 7 smoke-tests groen.
- **Testcommando's**:
  ```bash
  cd /home/user/digital-resupplying-tool
  npx playwright test tests/browser/smoke.spec.ts
  ```
- **Rollbackmogelijkheid**: CI-workflow-uitbreiding verwijderen/`git
  revert`; raakt geen productiecode.

---

## Aanbevolen volgorde & afhankelijkheden

| Fase | Stap | Kernafhankelijkheid | Veranderomvang (uit audit) |
|---|---|---|---|
| 0 | 0.1 Git-hygiëne: database-backups | geen | Small |
| 0 | 0.2 Git-hygiëne: gegenereerde artefacten | geen | Small |
| 0 | 0.3 requirements-dev.txt (pytest/httpx) | geen | Small |
| 0 | 0.4 Falende tests isoleren/fixen | 0.3, 0.6 | Small |
| 0 | 0.5 Tooling-inventaris | geen | n.v.t. |
| 0 | 0.6 Aparte dev/test-database | geen | n.v.t. |
| 0 | 0.7 Backup-/herstelpunt bevestigen | geen | n.v.t. |
| 1 | 1.1 Auth op muterende endpoints | geen | Medium |
| 1 | 1.2 SECRET_KEY verplicht | geen | Small |
| 1 | 1.3 Upload-limiet + filename-sanitisering | geen | Small |
| 1 | 1.4 Idempotentie-guards | data-audit (unique-constraint-deel) | Small–Medium |
| 1 | 1.5 Transactiegrens | productbeslissing | Medium |
| 1 | 1.6 Auth-refresh smal maken | geen | Small |
| 1 | 1.7 CORS ALLOWED_ORIGINS | Fase 4 (deploymentdoel voor definitieve waarde) | Small |
| 2 | 2.1 ruff/mypy in requirements-dev | 0.3 | Small |
| 2 | 2.2 pyproject.toml-config | 2.1 | Medium |
| 2 | 2.3 ESLint flat config | geen | Small |
| 2 | 2.4 TS-fouten fixen → ignoreBuildErrors weg | **volgorde-kritiek, intern** | Small |
| 2 | 2.5 GitHub Actions CI | 0.3, 2.1, 2.2, 2.3, 2.4 | Medium |
| 3 | 3.1 pdf_ingest.py opsplitsen | Fase 2 compleet | Large |
| 3 | 3.2 Getypeerde moves | Fase 2, baat bij 3.1 | Small–Medium |
| 3 | 3.3 Singletons → DI | Fase 2 | Large |
| 3 | 3.4 Frontend API-base consolideren | geen hard, baat bij Fase 2 | Small (Large voor volledige consolidatie) |
| 3 | 3.5 Functieomvang (doorlopend) | Fase 2 | n.v.t. (proces) |
| 4 | 4.1 Deploymentdoel + build | Fase 2 compleet | — (beslissing) |
| 4 | 4.2 SQLite vs. robuustere DB | 4.1 | — (beslissing) |
| 4 | 4.3 Alembic-migraties | 4.2, Fase 2 | Large |
| 4 | 4.4 Backups + geteste restore | 4.1 | Medium |
| 4 | 4.5 Observability | geen hard, baat bij 4.1 | Small–Medium |
| 4 | 4.6 Runbook | 4.1–4.5 | — (documentatie) |
| 4 | 4.7 Playwright-smoke in CI | 4.1, Fase 2 | Medium |

**Leeswijzer**: fasen zijn sequentieel bedoeld (0 → 1 → 2 → 3 → 4) omdat
elke fase een vangnet vormt voor de volgende (Fase 0 maakt tests
betrouwbaar vóór Fase 1 daarop leunt; Fase 2 maakt CI betrouwbaar vóór
Fase 3 daarop leunt bij een refactor). Binnen een fase kunnen stappen
zonder onderlinge afhankelijkheid parallel worden opgepakt, mits elke stap
afzonderlijk gecommit en getest wordt conform de acceptatiecriteria
hierboven.

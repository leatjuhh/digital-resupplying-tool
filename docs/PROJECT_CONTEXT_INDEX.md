---
title: Project Context Index
category: technical
tags: [documentation, context, navigation]
last_updated: 2026-03-14
related:
  - DOCUMENTATION_GUIDELINES.md
  - REORGANIZATION_SUMMARY.md
  - ../README.md
---

# Project Context Index

Deze index maakt snel duidelijk welke Markdown-bestanden relevant zijn voor toekomstige prompts en waar specifieke informatie staat.

## Leesvolgorde

1. `README.md`
   Startpunt voor projectdoel, stack, opstarten en hoofdlinks.
2. `docs/PROJECT_CONTEXT_INDEX.md`
   Kaart van de documentatie en prioriteit per map.
3. `docs/DOCUMENTATION_GUIDELINES.md`
   Bepaalt waar nieuwe of bijgewerkte documentatie hoort.

## Welke bron is leidend

### Primair actueel

- `README.md`
  Hoog-niveau projectstatus, links en startcommando's.
- `docs/getting-started/*.md`
  Installatie, quick start, browser debugging, mobile access en troubleshooting.
- `docs/guides/*.md`
  Functionele en procesmatige uitleg per onderwerp.
- `docs/technical/*.md`
  Architectuur, analyse en technische achtergrond.

### Aanvullend, maar taakafhankelijk

- `frontend/PROJECT-OVERVIEW.md`
  Beschrijft de beoogde productscope, rollen, schermen en workflows. Goed voor functionele intentie, minder geschikt als bron voor actuele implementatiestatus.
- `backend/README.md`
  Nuttig voor backend-opstart en basis-API-info, maar sommige roadmapteksten zijn ouder dan de huidige codebasis.
- `todo/*.md`
  Open werk, analyses, issue-notities en handoff-documenten. Handig voor vervolgwerk, maar niet automatisch de bron van waarheid.

### Historisch of referentie

- `archive/*.md`
  Oude status- en quickstartdocumenten. Alleen raadplegen als historische context nodig is.
- `docs/sessions/*.md`
  Tijdgebonden sessielogs; bruikbaar voor besluitgeschiedenis.
- `CHANGELOG.md`
  Versiehistorie en wijzigingslog, niet bedoeld als complete operationele handleiding.

## Waar staat wat

### Project en structuur

- `README.md`
  Projectdoel, stack, quick start, hoofdstructuur en centrale documentatielinks.
- `docs/REORGANIZATION_SUMMARY.md`
  Uitleg van de documentatiestructuur en waarom die zo is opgezet.
- `docs/DOCUMENTATION_GUIDELINES.md`
  Regels voor naamgeving, plaatsing en onderhoud van documentatie.

### Opstarten en omgeving

- `docs/getting-started/quick-start.md`
  Snelste route om het project lokaal te starten.
- `docs/getting-started/installation.md`
  Volledige installatie-instructies.
- `docs/getting-started/troubleshooting.md`
  Veelvoorkomende problemen en oplossingen.
- `docs/getting-started/browser-debugging.md`
  Browser-debugworkflow.
- `docs/getting-started/mobile-network-access.md`
  Testen op mobiel netwerk of device.

### Functionele gidsen

- `docs/guides/cursor-workflow.md`
  Bestaande AI/ontwikkelworkflow.
- `docs/guides/authentication-testing.md`
  Auth-scenario's en testaanpak.
- `docs/guides/batch-system.md`
  PDF-upload, parsing en batchverwerking.
- `docs/guides/database.md`
  Databasemodellen en beheer.
- `docs/guides/integration.md`
  Frontend-backend koppeling.
- `docs/guides/redistribution-algorithm.md`
  Herverdelingslogica.

### Technische achtergrond

- `docs/technical/gui-overview.md`
  Gedetailleerde GUI- en paginabeschrijving.
- `docs/technical/pdf-extraction-system.md`
  Technische details van PDF-extractie.
- `docs/technical/frontend-consolidation.md`
  Frontend-architectuur en refactorcontext.
- `docs/technical/baseline-implementation-plan.md`
  Baseline-implementatieplan.
- `docs/technical/backup-recovered-context.md`
  Vastgelegde context uit een lokale backup, waaronder teruggevonden upload-flow intentie en ontbrekende testfixtures.
- `docs/technical/dummy-data-audit.md`
  Analyse van dummydata.
- `docs/technical/next-steps-analysis.md`
  Technische vervolgstappen.

### Specifieke context buiten `docs/`

- `frontend/PROJECT-OVERVIEW.md`
  Productvisie, rollen, routes en UI-flow.
- `backend/AUTH_FIX_SUMMARY.md`
  Samenvatting van auth-fixwerk.
- `todo/NEW_CHAT_PROMPT.md`
  Tijdelijke handoff voor auth-probleem; alleen gebruiken als die context nog relevant is.
- `todo/next_session_checklist.md`
  Werkafspraken voor de eerstvolgende sessie.

## Praktische interpretatie voor agents

- Gebruik `docs/` als eerste bron voor beantwoording en planning.
- Gebruik `todo/` voor open vragen, nog uit te voeren werk en eerdere denkrichtingen.
- Gebruik `archive/` alleen als iets nergens anders meer uitgelegd staat.
- Als documenten elkaar tegenspreken, geef prioriteit aan actuele code, daarna `docs/`, daarna `README.md`, daarna `todo/`, en pas als laatste `archive/`.

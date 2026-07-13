---
title: Project Context Index
category: technical
tags: [documentation, context, navigation]
last_updated: 2026-07-13
related:
  - DOCUMENTATION_GUIDELINES.md
  - technical/current-state.md
  - engineering/PRODUCTION_ENGINEERING_STANDARD.md
  - ../README.md
---

# Project Context Index

Deze index onderscheidt expliciet tussen leidende, aanvullende en historische bronnen.

## Leidend

- `README.md`
  Startpunt voor projectdoel, kernflow, startcommando's en de huidige documenthiërarchie.
- `docs/technical/current-state.md`
  De enige actuele status- en roadmapbron tijdens de consolidatiefase.
- `todo/master-backlog.md`
  De enige actieve backlog met prioriteiten, afhankelijkheden en acceptatiecriteria.

### Leidend voor engineering-/kwaliteitsvragen

- `docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md`
  Canonieke engineeringstandaard (P10-vertaling); leidend bij elke hoe-vraag over codekwaliteit, architectuur, security, testen of quality gates.
- `docs/engineering/PRODUCTION_READINESS_AUDIT.md`
  Production-readiness bevindingen met bewijs, gekoppeld aan de standaard.
- `docs/engineering/PRODUCTION_READINESS_PLAN.md`
  Gefaseerd verbeterplan dat op de audit voortbouwt.
- `docs/engineering/AI_SESSION_HANDOFF.md`
  Leidend rapportagesjabloon bij sessie-einde of AI-overdracht.

## Aanvullend

### Opstarten en omgeving

- `docs/getting-started/quick-start.md`
- `docs/getting-started/installation.md`
- `docs/getting-started/troubleshooting.md`
- `docs/getting-started/gui-testing-and-debugging.md`
- `docs/getting-started/browser-debugging.md`
- `docs/getting-started/mobile-network-access.md`

### Functionele en technische uitleg

- `docs/guides/batch-system.md`
- `docs/guides/integration.md`
- `docs/guides/redistribution-algorithm.md`
- `docs/technical/baseline-algorithm-phase-1.md`
- `docs/guides/database.md`
- `docs/guides/authentication-testing.md`
- `docs/guides/cursor-workflow.md`
- `docs/technical/pdf-extraction-system.md`
- `backend/README.md`
- `frontend/PROJECT-OVERVIEW.md`

### AI-instructielaag (adapters)

- `CLAUDE.md`
  Claude Code-adapter; importeert de canonieke standaard, definieert geen eigen regels.
- `CHATGPT_PROJECT_INSTRUCTIONS.md`
  Zelfstandige, kopieerbare ChatGPT-projectinstructies; verwijst naar dezelfde canonieke standaard.

Gebruik deze bronnen alleen als aanvulling op de leidende documenten.

Specifiek voor de huidige baseline-slice geldt:

- `docs/technical/baseline-algorithm-phase-1.md` beschrijft de actieve shadow-mode classificatie
- externe algoritme-import is aanvullende technische context, geen leidende planning- of roadmapbron

## Bronnen

- `docs/references/P10.pdf`
  Oorspronkelijke bron van de engineeringstandaard ("The Power of Ten", Holzmann/NASA-JPL). Alleen-lezen; nooit inhoudelijk wijzigen.

## Historisch

- `archive/`
  Historische documentatie, ingehaalde analyses en geconsolideerde todo's.
- `archive/2026-03-consolidation/`
  De archiefset van de consolidatieslag van maart 2026.
- `docs/sessions/`
  Tijdgebonden sessielogs en besluitgeschiedenis.
- Oudere handoffs, promptnotities en ingehaalde roadmapbestanden
  Niet meer leidend voor actuele planning of status.

## Praktische Leesvolgorde

1. `README.md`
2. `docs/technical/current-state.md`
3. `todo/master-backlog.md`
4. Pas daarna aanvullende documentatie per onderwerp

## Interpretatieregel

Als documenten elkaar tegenspreken, geldt deze volgorde:

1. actuele code
2. `docs/technical/current-state.md`
3. `docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md` (voor hoe-/kwaliteitsvragen: architectuur, security, testen, quality gates)
4. `todo/master-backlog.md`
5. overige actieve docs
6. `archive/` en sessielogs

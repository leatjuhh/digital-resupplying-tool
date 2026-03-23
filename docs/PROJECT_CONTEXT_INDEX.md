---
title: Project Context Index
category: technical
tags: [documentation, context, navigation]
last_updated: 2026-03-23
related:
  - DOCUMENTATION_GUIDELINES.md
  - technical/current-state.md
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
- `docs/guides/database.md`
- `docs/guides/authentication-testing.md`
- `docs/guides/cursor-workflow.md`
- `docs/technical/pdf-extraction-system.md`
- `backend/README.md`
- `frontend/PROJECT-OVERVIEW.md`

Gebruik deze bronnen alleen als aanvulling op de leidende documenten.

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
3. `todo/master-backlog.md`
4. overige actieve docs
5. `archive/` en sessielogs

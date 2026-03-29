---
title: Current State
category: technical
tags: [status, roadmap, consolidation]
last_updated: 2026-03-30
related:
  - ../../README.md
  - ../PROJECT_CONTEXT_INDEX.md
  - ../../todo/master-backlog.md
---

# Current State

Dit document is de enige actuele status- en roadmapbron tijdens de consolidatiefase.

## Huidige Kernflow

De leidende productkern is:

`PDF ingest -> proposal generatie/opslag -> proposal detail/edit/review`

Deze flow moet intact blijven tijdens opschoning van documentatie, backlog en niet-kernschermen.

## Wat Aantoonbaar Werkt

- Backend start lokaal en exposeert PDF- en proposal-endpoints.
- PDF batches kunnen worden ingelezen en opgeslagen.
- Proposals worden voor een batch gegenereerd en persistent opgeslagen.
- Proposal detail en editflow zijn op echte backenddata aangesloten.
- Proposal reject, update en approve bestaan als actieve API-flow.
- Goedgekeurde proposals worden omgezet naar echte assignments per bronfiliaal.
- Assignments list, reeksdetail en itemdetail draaien op echte backenddata met statusupdates voor winkelgebruikers.
- Dashboard draait nu data-gedreven op een auth-beschermde summary endpoint met echte KPI's, pending batches, systeemevents en aandachtspunten.
- Settings draait nu permission-driven op echte backenddata voor algemeen, regels, users, rollen en write-only API-key beheer.
- Het herverdelingsalgoritme is vereenvoudigd (2026-03-30): multi-factor scoring (series/efficiency) en de move-consolidatie-optimizer zijn verwijderd. Scoring is nu puur demand-gebaseerd. De kernflow (greedy matching, BV-constraint, BV-consolidatie) en de volledige API-compatibiliteit zijn behouden.
- Het algoritme annoteert proposals in shadow mode met een stabiele situatie-marker via `applied_rules` (`LOW_STOCK`, `MEDIUM_STOCK`, `HIGH_STOCK`, `PARTIJ`).
- Er is een lokale offline evaluatiehaak voor situatieclassificatie tegen geïmporteerde weekbestanden en handmatige redistributies.
- DRT heeft nu een aparte read-only importerlaag voor externe algoritme-artefacten uit `Herverdelingsalgoritme`, inclusief aggregate datasetstatus, weekevaluaties en lineage per artefact.
- De proposals-overview toont nu externe leersignalen zoals verwerkte weken, trainingssamenvatting en modelmetrics.
- Proposal detail toont nu explainability-context voor hetzelfde artikel: huidig DRT-voorstel tegenover handmatige moves, externe baseline en externe modelhints.
- `.\dev.ps1 -Restart` is nu de officiële lokale restartflow wanneer poort `3000` of `8000` nog bezet is door een vorige sessie.
- De frontend production build slaagt weer.
- Er is een browser smoke voor login, backend health, admin settings-tabs, user settingsrechten en store redirect naar assignments.
- De leidende kernflow-checklist staat vast in `docs/getting-started/gui-testing-and-debugging.md`.

## Wat Bewust Geparkeerd Is

- Verdere baseline-uitbouw van het herverdelingsalgoritme voorbij fase 1 situatieclassificatie (het vereenvoudigde algoritme is nu het vertrekpunt voor toekomstige iteraties)
- SQL-first of andere brontransitie

Deze onderdelen mogen zichtbaar blijven, maar zijn niet leidend voor planning of productclaim.

## Bekende Huidige Randen

- Assignments blijven buiten de leidende kernflow, ook nu de store-uitvoering op echte data draait.
- Settings blijft buiten de leidende kernflow; API-key beheer is bewust write-only en toont alleen masked metadata terug aan de UI.
- De situatieclassificatie draait bewust in shadow mode; thresholds zijn heuristisch en gebaseerd op de huidige lokale dataset van 2 weken / 2 manuele herverdelingen.
- De externe algoritmekoppeling is bewust read-only; `algorithm_assist_mode` staat standaard op `off` en stuurt de DRT-proposalgeneratie nog niet aan.
- Browser smoke is stabiel gevalideerd op een schone frontendstart; een vervuilde Next dev-cache kan lokaal nog steeds rare `.next` chunkfouten geven totdat de frontend opnieuw schoon is gestart.
- Historische roadmap- en analysebestanden zijn verplaatst naar `archive/2026-03-consolidation/`.

## Eerstvolgende Fasen

### Fase A

Consolidatie van documentatie, backlog en actieve waarheid.

### Fase B

Build- en runbaarheid van de leidende kernflow valideren en herstellen waar nodig.

### Fase C

De kernflow `PDF -> voorstel -> review` verder stabiliseren en regressies expliciet afdekken.

### Fase D

Geparkeerde domeinen heropenen vanuit `todo/master-backlog.md`, niet vanuit losse historische notities.

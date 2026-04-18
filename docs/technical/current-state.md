---
title: Current State
category: technical
tags: [status, roadmap, consolidation]
last_updated: 2026-04-18 (sessie 2)
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
- De beoogde AI-richting is aangescherpt als feedbackgedreven regelverfijning: periodieke analyse van gebruikersfeedback moet het bestaande algoritme adviserend verbeteren zonder de runtime proposalflow over te nemen.
- `.\dev.ps1 -Restart` is nu de officiële lokale restartflow wanneer poort `3000` of `8000` nog bezet is door een vorige sessie.
- De frontend production build slaagt weer.
- Er is een browser smoke voor login, backend health, admin settings-tabs, user settingsrechten en store redirect naar assignments.
- De leidende kernflow-checklist staat vast in `docs/getting-started/gui-testing-and-debugging.md`.

- Het herverdelingsalgoritme is fundamenteel herschreven (2026-04-17): de gemiddelde-drempel logica (`1.5x/0.5x`) is vervangen door demand-gedreven donor/ontvanger scoring op basis van de baseline uit `Herverdelingsalgoritme`. Donors worden bepaald op verkoop + voorraad per maat; ontvangers zijn winkels met `qty=0` voor die maat. Werkende voorraad wordt per artikel over alle maten bijgehouden. Gevalideerd op 4 weken manuele herverdelingsdata (weken 12, 13, 14, 16).
- De BV-configuratie is ingesteld op de werkelijke filiaalindeling: 6, 8, 9, 11, 12, 13, 31 en 38 vallen onder Lumitex B.V.; filiaal 5 (Panningen) valt onder een aparte BV en is daarmee automatisch uitgesloten van DRT-herverdelingen. Configuratie staat in `backend/bv_mapping.json`.
- `backend/redistribution/domain.py` bug gefixed: `calculate_aggregates` telde stores met `qty=0` onterecht mee in het maatgemiddelde.
- `backend/redistribution/algorithm.py` bug gefixed: `int()` truncation vervangen door `round()` voor overschot/tekort berekening (nu niet meer relevant na het herontwerp).
- Store-niveau capaciteitsprofielen toegevoegd (`backend/redistribution/store_profiles.py`): vaste vloeroppervlak en max-capaciteitsschatting per filiaal (6, 8, 9, 11, 12, 13, 31, 38). Algoritme gebruikt deze als tiebreaker bij gelijke demand-score via `calculate_batch_store_totals`.
- Maatreekslogica toegevoegd aan het algoritme: `_series_width`, `_would_break_sequence` en `_would_improve_sequence` voorkomen dat moves een aaneengesloten maatreeks bij een donor breken of die bij een ontvanger verbeteren.
- Feedback-router toegevoegd (`backend/routers/feedback.py`): legt gebruikersacties (approved/edited/rejected/removed/added) met reden-code, feature-snapshot en model-score vast per proposal of individuele move (move_index). Vereiste basis voor de ML-feedbackloop.
- `ProposalFeedback` DB-model uitgebreid met `action_taken`, `reason_code`, `move_index`, `feature_snapshot` en `model_score_at_time` voor retroactieve ML-analyse.
- Architectuurdocument ML-feedbackloop toegevoegd (`docs/technical/fase1-ml-feedback-loop.md`): beschrijft de beoogde batchmatige AI-laag als adviserende aanvulling op het deterministische algoritme, zonder realtime LLM-calls in de proposalflow.
- De externe algoritmedata (4 weken JSON + aggregate, ~37MB) staat nu binnen de repo in `backend/algorithm_data/`. De sibling-map `Herverdelingsalgoritme/` is geen vereiste meer voor een werkende DRT-setup — `git pull` + setup-scripts is voldoende.
- De historische baseline-pipeline (week-verwerking, training-scripts, oud redistribution-pakket) staat bevroren in `tools/baseline-pipeline/` inclusief README. Deze tooling is niet actief in de DRT-runtime maar blijft bruikbaar voor handmatige verwerking van nieuwe weken zolang DRT de manuele flow nog niet volledig vervangt.

## Wat Bewust Geparkeerd Is

- Verdere baseline-uitbouw van het herverdelingsalgoritme voorbij fase 1 situatieclassificatie (het vereenvoudigde algoritme is nu het vertrekpunt voor toekomstige iteraties)
- SQL-first of andere brontransitie

Deze onderdelen mogen zichtbaar blijven, maar zijn niet leidend voor planning of productclaim.

## Bekende Huidige Randen

- Assignments blijven buiten de leidende kernflow, ook nu de store-uitvoering op echte data draait.
- Settings blijft buiten de leidende kernflow; API-key beheer is bewust write-only en toont alleen masked metadata terug aan de UI.
- De situatieclassificatie draait bewust in shadow mode; thresholds zijn heuristisch en gebaseerd op de huidige lokale dataset van 2 weken / 2 manuele herverdelingen.
- De externe algoritmekoppeling is bewust read-only; `algorithm_assist_mode` staat standaard op `off` en stuurt de DRT-proposalgeneratie nog niet aan.
- De AI-architectuur is bewust adviserend en batchmatig: feedbackanalyse en regelverfijning zijn de beoogde vervolgrichting, maar actieve runtime-sturing door AI hoort nog niet bij de huidige productclaim.
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

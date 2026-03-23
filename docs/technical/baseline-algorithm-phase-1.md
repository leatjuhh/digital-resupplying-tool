---
title: Baseline Algorithm Phase 1
category: technical
tags: [baseline, redistribution, evaluation, shadow-mode]
last_updated: 2026-03-23
related:
  - ../../todo/master-backlog.md
  - ./current-state.md
---

# Baseline Algorithm Phase 1

Fase 1 voegt situatieclassificatie toe aan de bestaande redistributielaag in **shadow mode**.

Dat betekent:

- proposals krijgen een stabiele marker in `applied_rules` als `Situation: LOW_STOCK|MEDIUM_STOCK|HIGH_STOCK|PARTIJ`
- de bestaande move-generatie, scoring en optimalisatie blijven ongewijzigd
- de classificatie wordt alleen zichtbaar gemaakt en offline geëvalueerd

## Huidige thresholds

De classifier gebruikt voorlopig eenvoudige, configureerbare heuristieken uit `backend/redistribution/constraints.py`.

- `LOW_STOCK`
  - `total_inventory <= 6` of `avg_units_per_active_store <= 1.5`
- `HIGH_STOCK`
  - `total_inventory >= 18` of `avg_units_per_active_store >= 3.0` of `stock_to_sales_ratio >= 2.5`
- `PARTIJ`
  - `total_inventory >= 24`
  - `avg_units_per_active_store >= 4.0`
  - en `total_sales == 0` of `stock_to_sales_ratio >= 4.0`
- `MEDIUM_STOCK`
  - alle overige gevallen

Deze thresholds zijn bewust fase-1 heuristieken. Ze zijn afgeleid voor snelle annotatie en evaluatie, niet voor directe sturing van het voorstelgedrag.

## Offline evaluatiehaak

De evaluator leest read-only geïmporteerde weekbestanden via `combined.json` en vergelijkt de situatieclassificatie met de handmatige weekmoves uit dezelfde dataset.

Entrypoint:

```powershell
cd C:\Codex\DRT\backend
.\venv\Scripts\python.exe -m redistribution.offline_evaluation --data-root "C:\Users\Alain\OneDrive\Werk\.codex projecten\Herverdelingsalgoritme\data" --year 2026 --weeks 12 13
```

De output groepeert per week:

- aantal artikelen per situatie
- aantal handmatig herverdeelde artikelen per situatie
- aantal handmatige moves per situatie
- per artikel de basismetrics waarop de classifier draait

## Datasetstatus bij implementatie

De huidige lokale evaluatieset bestaat uit:

- `2026/week_12`
- `2026/week_13`

Samen is dat momenteel:

- `2` weken
- `2` manuele herverdelingen
- `109` geclassificeerde artikelen in de lokale evaluatierun van 2026-03-23
- `867` handmatige moves in diezelfde run

Verdieping in strategie, categoriebeleid, prioritering, compensatie en feedbackloop valt buiten fase 1 en blijft open in de master backlog.

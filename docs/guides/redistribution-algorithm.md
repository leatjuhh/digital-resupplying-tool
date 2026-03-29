# Herverdelingsalgoritme - Technische Documentatie

Statusnoot: dit document beschrijft de kernlogica van het redistributie-algoritme na de vereenvoudiging van 2026-03-30. De actuele status wordt leidend vastgelegd in `docs/technical/current-state.md` en `todo/master-backlog.md`.

## Huidige aanvullende laag

Naast de hieronder beschreven kernlogica draait momenteel ook:

- situatieclassificatie fase 1 in shadow mode via `LOW_STOCK`, `MEDIUM_STOCK`, `HIGH_STOCK` en `PARTIJ`
- read-only externe artefactimport vanuit het aparte project `Herverdelingsalgoritme`
- proposal explainability in DRT via vergelijking tussen huidig voorstel, handmatige moves, baseline-output en modelhints

**Versie**: 2.0
**Datum**: 30 maart 2026
**Status**: Vereenvoudigd naar demand-gebaseerd algoritme

---

## Overzicht

Het herverdelingsalgoritme genereert herverdelingsvoorstellen voor artikelen tussen winkels op basis van:
- Actuele voorraad per winkel per maat
- Verkoopcijfers (demand)
- BV-constraints (Lumitex B.V. vs MC Company Partners B.V.)

## Architectuur

### Componentenoverzicht

```
backend/redistribution/
├── __init__.py           # Module exports
├── domain.py             # Dataclasses (ArticleStock, Move, Proposal)
├── constraints.py        # Parameters en drempelwaarden
├── bv_config.py          # BV-winkel mapping (configureerbaar)
├── scoring.py            # Demand-gebaseerde scoring
├── algorithm.py          # Hoofdlogica (greedy per maat)
├── situation.py          # Shadow-mode situatieclassificatie
├── adapter.py            # Weekbestand → domainmodel conversie
└── offline_evaluation.py # Offline evaluatie tegen weekdata
```

### Data Flow

```
┌─────────────────────┐
│  Database           │
│  (artikel_voorraad) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Load Article Data  │  ← Haal voorraad + verkoop op
│  Calculate Metrics  │  ← Bereken demand scores
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  BV Consolidatie    │  ← Gefragmenteerde BV's consolideren
│  (Prioriteit)       │  ← ≤6 items → best verkopende winkel
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Generate Moves     │  ← Greedy matching per maat
│  (Per Size)         │  ← Overschotten → Tekorten
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Score & Filter     │  ← Demand-gebaseerde score
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Create Proposal    │  ← Output naar database/API
└─────────────────────┘
```

---

## Kernfunctionaliteit

### 1. BV Constraint (Cross-BV Blokkering)

**Doel**: Voorkom herverdeling tussen verschillende bedrijfsvennootschappen.

```python
# Check in algorithm.py
if params.enforce_bv_separation:
    is_valid, reason = validate_bv_move(from_store, to_store)
    if not is_valid:
        continue  # Skip deze move
```

**Configuratie**:
- JSON bestand: `bv_mapping.json`
- Via API instelbaar per winkel
- Regel kan aan/uit gezet worden in settings

### 2. BV Consolidatie

**Doel**: Voorkom fragmentatie binnen een BV.

Als een BV in totaal ≤6 stuks heeft van een artikel, worden alle stuks geconsolideerd naar de best verkopende winkel binnen die BV. Dit voorkomt dat kleine hoeveelheden over meerdere winkels verspreid liggen.

### 3. Vraaggestuurde Herverdeling

**Doel**: Verplaats voorraad van lage demand naar hoge demand winkels.

**Demand Score Berekening**:
```python
demand_score = verkocht / voorraad

# Voorbeeld:
# Winkel A: 10 verkocht / 20 voorraad = 0.5 (50% demand)
# Winkel B: 16 verkocht / 20 voorraad = 0.8 (80% demand)
# → Voorraad van A naar B is een goede move
```

**Prioritering**:
1. **Overschotten**: Lage demand winkels leveren eerst
2. **Tekorten**: Hoge demand winkels krijgen eerst

### 4. Scoring

Elke move krijgt een score tussen 0.0 en 1.0, puur gebaseerd op het demand-verschil tussen bron- en doelwinkel:

```python
demand_diff = to_demand - from_demand
score = 0.5 + (demand_diff / 2.0)  # Range: 0.0 - 1.0
```

Moves met score < 0.2 worden gefilterd.

---

## Parameters

### Overschot/Tekort Drempelwaarden

```python
oversupply_threshold = 1.5    # 150% van gemiddelde
undersupply_threshold = 0.5   # 50% van gemiddelde
```

**Voorbeeld**:
- Gemiddelde voorraad maat 38: 10 stuks
- Winkel met >15 stuks = overschot (levert)
- Winkel met <5 stuks = tekort (ontvangt)

### BV Parameters

```python
enforce_bv_separation = True   # Cross-BV moves blokkeren
enable_bv_consolidation = True # Gefragmenteerde BV's consolideren
min_items_per_store = 6        # Drempel voor BV consolidatie
```

### Move Limieten

```python
min_move_quantity = 1          # Minimaal 1 stuk per move
max_move_quantity = 100        # Maximaal 100 stuks per move
min_move_score = 0.2           # Minimale score om te behouden
```

---

## Gebruik

### Basis Gebruik

```python
from redistribution import generate_redistribution_proposals_for_article
from database import get_db

db = get_db()
proposal = generate_redistribution_proposals_for_article(
    db=db,
    volgnummer="423264",
    batch_id=1
)

if proposal:
    print(f"Gegenereerd: {proposal.total_moves} moves")
    for move in proposal.moves:
        print(f"{move.from_store} → {move.to_store}: {move.qty}× {move.size}")
        print(f"  Score: {move.score:.2f} - {move.reason}")
```

### Custom Parameters

```python
from redistribution import RedistributionParams

params = RedistributionParams(
    oversupply_threshold=2.0,        # Strengere drempelwaarde
    enforce_bv_separation=False,     # BV constraint uit
)

proposal = generate_redistribution_proposals_for_article(
    db=db,
    volgnummer="423264",
    batch_id=1,
    params=params
)
```

### Batch Processing

```python
from redistribution.algorithm import generate_redistribution_proposals_for_batch

proposals = generate_redistribution_proposals_for_batch(db=db, batch_id=1)
print(f"Gegenereerd: {len(proposals)} voorstellen")
```

---

## Configuratie

### BV Mapping

Bewerk `bv_mapping.json`:

```json
{
  "store_to_bv": {
    "AMS": "Lumitex B.V.",
    "ROT": "Lumitex B.V.",
    "EIN": "MC Company Partners B.V.",
    "GRO": "MC Company Partners B.V."
  }
}
```

### Custom Maat Reeksen

```python
from redistribution.constraints import register_custom_size_order

register_custom_size_order(
    "shoe_sizes",
    ["35", "35.5", "36", "36.5", "37", "37.5", "38"]
)
```

---

## Output

### Proposal Object

```python
{
    "volgnummer": "423264",
    "article_name": "Winter Jas Blauw",
    "batch_id": 1,
    "moves": [
        {
            "from_store": "AMS",
            "to_store": "ROT",
            "size": "38",
            "qty": 5,
            "score": 0.82,
            "reason": "Hoge demand in doel winkel (80% verkocht)"
        }
    ],
    "status": "pending",
    "applied_rules": ["Situation: HIGH_STOCK", "BV Separation", "Demand-based Allocation"],
    "total_moves": 12,
    "total_quantity": 48
}
```

---

## Vereenvoudiging 2026-03-30

Het algoritme is vereenvoudigd van ~2.800 naar ~1.400 LOC. Verwijderd:

- **Move consolidation optimizer** (339 LOC) — swap-iteraties om bestemmingen te reduceren, overkill bij 8 filialen
- **Size sequence detectie** — detectie van opeenvolgende maten met penalties/bonussen (onbewezen waarde)
- **Series-score** (was 20% van totale score) — vervangen door puur demand-gebaseerde scoring
- **Efficiency-score** (was 10% van totale score) — lineaire schaling op qty, weinig toevoegend
- **20+ configuratieparameters** — teruggebracht naar essentiële set

Behouden:
- Greedy matching per maat (surplus → shortage)
- Demand-gebaseerde prioritering en scoring
- BV-constraint en BV-consolidatie
- Situatieclassificatie (shadow mode)
- Volledige API-compatibiliteit

**Versie**: 2.0
**Laatste update**: 30 maart 2026

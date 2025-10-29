# Herverdelingsalgoritme - Technische Documentatie

**Versie**: 1.0  
**Datum**: 28 oktober 2025  
**Status**: Eerste implementatie compleet

---

## 📋 Overzicht

Het herverdelingsalgoritme genereert slimme herverdelingsvoorstellen voor artikelen tussen winkels op basis van:
- Actuele voorraad per winkel per maat
- Verkoopcijfers (demand)
- BV-constraints (Lumitex B.V. vs MC Company Partners B.V.)
- Maatserie integriteit (minimaal 3 opeenvolgende maten)

## 🏗️ Architectuur

### Componentenoverzicht

```
backend/redistribution/
├── __init__.py           # Module exports
├── domain.py             # Dataclasses (ArticleStock, Move, Proposal)
├── constraints.py        # Parameters en drempelwaarden
├── bv_config.py          # BV-winkel mapping (configureerbaar)
├── scoring.py            # Demand/series/efficiency scoring
├── algorithm.py          # Hoofdlogica (greedy per maat)
└── optimizer.py          # Move consolidation optimalisatie
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
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Detect Sequences   │  ← Analyseer maatreeksen
│  Calculate Metrics  │  ← Bereken demand scores
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
│  Score & Filter     │  ← Weeg demand, series, efficiency
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Optimize           │  ← Move consolidation (optioneel)
│  (Consolidation)    │  ← Minimaliseer verzendbestemmingen
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Create Proposal    │  ← Output naar database/API
└─────────────────────┘
```

---

## 🎯 Kernfunctionaliteit

### 1. BV Constraint (Cross-BV Blokkering)

**Doel**: Voorkom herverdeling tussen verschillende bedrijfsvennootschappen.

**Implementatie**:
```python
# bv_config.py
bv_config = {
    'AMS': 'Lumitex B.V.',
    'ROT': 'Lumitex B.V.',
    'EIN': 'MC Company Partners B.V.',
    'GRO': 'MC Company Partners B.V.',
}

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

### 2. Vraaggestuurde Herverdeling

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

**Scoring**:
- Demand score weegt 70% mee in totale score
- Negatieve moves (hoge → lage demand) worden afgestraft

### 3. Maatseriebehoud

**Doel**: Behoud minimaal 3 opeenvolgende maten per winkel.

**Detectie**:
```python
# Voorbeeld: Winkel heeft maten 36, 38, 40, 42
# Dit is een serie van 4 opeenvolgende maten
# Verwijderen van 38 of 40 zou serie breken (penalty)
# Verwijderen van 36 of 42 is OK (eindpunt)
```

**Rules**:
- Minimaal 3 opeenvolgende maten = 1 serie
- Penalty voor moves die serie breken (score -50%)
- Bonus voor moves die serie creëren (+30%)
- Detecteert automatisch numerieke (32-48) en letter (XS-XXL) maten

### 4. Volledige Maatserieverdeling

**Doel**: Verdeel voorraad over zoveel mogelijk winkels zonder gaten.

**Implementatie**:
- Greedy matching: overschotten → tekorten
- Prioriteer moves die series compleet maken
- Vermijd dubbele maten per winkel waar mogelijk

---

## 🔢 Scoring Systeem

### Move Score Berekening

Elke move krijgt een score tussen 0.0 en 1.0:

```
Total Score = 
    (Demand Score × 0.7) + 
    (Series Score × 0.2) + 
    (Efficiency Score × 0.1)
```

#### Demand Score (0.7 weight)
```python
demand_diff = to_demand - from_demand

if demand_diff > 0:
    score = 0.5 + (demand_diff / 2.0)  # 0.5 - 1.0
else:
    score = 0.5 + (demand_diff / 2.0)  # 0.0 - 0.5
```

#### Series Score (0.2 weight)
```python
score = 0.5  # Neutral

if breaks_source_sequence:
    score -= 0.5  # Penalty

if creates_or_extends_sequence:
    score += 0.3  # Bonus
```

#### Efficiency Score (0.1 weight)
```python
# Lineair schalen tussen min en max quantity
score = (qty - min_qty) / (max_qty - min_qty)
```

---

## 🔄 Move Consolidation Optimalisatie

### Probleem

Bij greedy per-maat aanpak kan je eindigen met inefficiënte verzendstructuur:

**Voor optimalisatie:**
```
Winkel A → Winkel C: 5× maat 38
Winkel A → Winkel D: 3× maat 38
Winkel B → Winkel C: 2× maat 40
```
- Winkel A verstuurt naar 2 bestemmingen
- **Totaal: 3 verzendingen**

**Na optimalisatie (swap):**
```
Winkel A → Winkel C: 5× maat 38
Winkel B → Winkel D: 3× maat 38  ← Swapped
Winkel B → Winkel C: 2× maat 40
```
- Winkel A verstuurt naar 1 bestemming
- Winkel B verstuurt naar 2 bestemmingen (maar had al verzending naar C)
- **Efficiënter: minder complexiteit**

### Algoritme

1. **Identificeer** bronnen met meerdere bestemmingen
2. **Zoek** swap kandidaten (zelfde maat, vergelijkbare hoeveelheid)
3. **Evalueer** of swap verbetering oplevert
4. **Voer uit** indien voordeel ≥ drempelwaarde
5. **Herhaal** tot geen verbeteringen meer mogelijk

### Swap Criteria

Een goede swap voldoet aan:
- ✅ Zelfde maat
- ✅ Quantity verschil ≤ 20%
- ✅ Reduceert aantal bestemmingen
- ✅ Behoud BV constraints
- ✅ Breekt geen series

### Consolidation Score

```python
score = 
    (destinations_reduced × 0.7) +
    (quantity_match × 0.1) +
    (series_preserved × 0.2)
```

---

## 📊 Parameters

### Overschot/Tekort Drempelwaarden

```python
oversupply_threshold = 1.5    # 150% van gemiddelde
undersupply_threshold = 0.5   # 50% van gemiddelde
```

**Voorbeeld**:
- Gemiddelde voorraad maat 38: 10 stuks
- Winkel met >15 stuks = overschot (levert)
- Winkel met <5 stuks = tekort (ontvangt)

### Maatserie Parameters

```python
min_sequence_width = 3          # Minimaal 3 maten
sequence_break_penalty = 0.5    # 50% penalty
sequence_creation_bonus = 0.3   # 30% bonus
```

### Scoring Wegingen

```python
demand_weight = 0.7      # 70% demand-driven
series_weight = 0.2      # 20% series preservation
efficiency_weight = 0.1  # 10% quantity efficiency
```

### Optimalisatie Parameters

```python
enable_consolidation = True
max_swap_quantity_diff = 0.2      # 20% verschil toegestaan
min_consolidation_benefit = 1      # Min 1 verzending bespaard
max_swap_iterations = 10           # Max 10 iteraties
max_swaps_per_article = 50         # Max 50 swaps
```

---

## 💻 Gebruik

### Basis Gebruik

```python
from redistribution import generate_redistribution_proposals_for_article
from database import get_db

# Voor één artikel
db = get_db()
proposal = generate_redistribution_proposals_for_article(
    db=db,
    volgnummer="423264",
    batch_id=1
)

if proposal:
    print(f"Gegenereerd: {proposal.total_moves} moves")
    print(f"Toegepaste regels: {proposal.applied_rules}")
    
    for move in proposal.moves:
        print(f"{move.from_store} → {move.to_store}: {move.qty}× {move.size}")
        print(f"  Score: {move.score:.2f} - {move.reason}")
```

### Custom Parameters

```python
from redistribution import RedistributionParams

# Custom parameters
params = RedistributionParams(
    oversupply_threshold=2.0,  # Strengere drempelwaarde
    enforce_bv_separation=False,  # BV constraint uit
    enable_optimization=True
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
from redistribution import generate_redistribution_proposals_for_batch

# Alle artikelen in een batch
proposals = generate_redistribution_proposals_for_batch(
    db=db,
    batch_id=1
)

print(f"Gegenereerd: {len(proposals)} voorstellen")
```

---

## 🔧 Configuratie

### BV Mapping

Bewerk `bv_mapping.json`:

```json
{
  "store_to_bv": {
    "AMS": "Lumitex B.V.",
    "ROT": "Lumitex B.V.",
    "UTR": "Lumitex B.V.",
    "EIN": "MC Company Partners B.V.",
    "GRO": "MC Company Partners B.V."
  }
}
```

Of via code:

```python
from redistribution.bv_config import get_bv_config

config = get_bv_config()
config.set_bv_for_store("MAA", "MC Company Partners B.V.")
```

### Custom Maat Reeksen

```python
from redistribution.constraints import register_custom_size_order

# Voor custom maat reeks
register_custom_size_order(
    "shoe_sizes",
    ["35", "35.5", "36", "36.5", "37", "37.5", "38"]
)
```

---

## 📈 Output

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
    "applied_rules": ["BV Separation", "Demand-based Allocation"],
    "optimization_applied": true,
    "total_moves": 12,
    "total_quantity": 48
}
```

### Optimization Explanation

Als optimalisatie is toegepast:

```python
{
    "optimization_type": "move_consolidation",
    "metrics": {
        "shipments_saved": 3,
        "consolidation_improvement_pct": 25.0,
        "swaps_performed": 5
    },
    "summary": "Optimalisatie toegepast: 3 verzendingen bespaard (25.0% verbetering). 5 swaps uitgevoerd.",
    "swaps": [
        {
            "move_a_before": "AMS → ROT: 5× 38",
            "move_a_after": "AMS → UTR: 5× 38",
            "reason": "Reduced AMS's destinations from 3 to 2"
        }
    ]
}
```

---

## 🧪 Testing

### Unit Tests

```python
# Test surplus/shortage identification
def test_identify_surplus():
    article = load_article_data(db, "423264", 1)
    surplus, shortage = identify_surplus_and_shortage(
        article, "38", DEFAULT_PARAMS
    )
    assert len(surplus) > 0
    assert len(shortage) > 0

# Test BV constraint
def test_bv_blocking():
    moves = generate_moves_for_size(article, "38", params)
    # Check geen cross-BV moves
    for move in moves:
        assert move.from_bv == move.to_bv
```

### Integration Test

```python
# Test volledige flow
def test_full_algorithm():
    proposal = generate_redistribution_proposals_for_article(
        db, "423264", 1
    )
    
    assert proposal is not None
    assert proposal.total_moves > 0
    assert all(m.score > 0 for m in proposal.moves)
    
    if proposal.optimization_applied:
        assert proposal.optimization_explanation is not None
```

---

## 🚀 Volgende Stappen

### Implementatie Status

- [x] Domain models (domain.py)
- [x] Constraints en parameters (constraints.py)
- [x] BV configuratie (bv_config.py)
- [x] Scoring systeem (scoring.py)
- [x] Kern algoritme (algorithm.py)
- [x] Move consolidation optimalisatie (optimizer.py)
- [ ] API endpoints (redistribution.py router)
- [ ] Database integratie (proposals opslaan)
- [ ] Export functionaliteit (CSV/XLSX)
- [ ] Frontend UI voor settings
- [ ] Testing suite

### Geplande Verbeteringen

1. **Min-cost flow optimalisatie** (v2.0)
   - Vervang greedy door network flow
   - Globaal optimale oplossing

2. **Geographic awareness** (v2.0)
   - Voorkeurt nabije winkels
   - Transport kosten meewegen

3. **Historical learning** (v3.0)
   - Leer van eerdere voorstellen
   - Voorspel seizoenspatronen

4. **Multi-objective optimization** (v3.0)
   - Balanceer meerdere doelen
   - Pareto-optimale oplossingen

---

## 📚 Referenties

- **Greedy Algorithm**: Basis matching strategie
- **Network Flow**: Toekomstige optimalisatie
- **Multi-objective Optimization**: Voor complexere trade-offs

---

## 📞 Support

Voor vragen of problemen:
1. Check TROUBLESHOOTING.md
2. Review code comments in algorithm.py
3. Run tests om gedrag te verifiëren

**Versie**: 1.0  
**Laatste update**: 28 oktober 2025

# Baseline Fase 4: Intelligente Prioritering

**Status:** ⏸️ Waiting (Blocked by Fase 3)  
**Priority:** 🟡 Medium Priority  
**Tijdsinschatting:** 2-3 dagen  
**Start Datum:** TBD (na Fase 3)  
**Target Datum:** TBD

---

## 🎯 Doel

Implementeer multi-factor priority scoring voor betere winkel ranking op basis van verkoop, voorraad, series, en categorie.

---

## 📋 Checklist

### Design & Planning
- [ ] Analyseer huidige demand score (verkocht/voorraad ratio)
- [ ] Design multi-factor scoring formule
- [ ] Bepaal wegingen per factor
- [ ] Plan BV-level ranking integratie

### Implementation
- [ ] Update `backend/redistribution/scoring.py`
  - [ ] Implementeer `calculate_multi_factor_priority()`
  - [ ] Implementeer factor berekeningen:
    - [ ] Verkoop ratio factor (40%)
    - [ ] Absolute verkoop factor (25%)
    - [ ] Serie compleetheid factor (20%)
    - [ ] Categorie modifier factor (10%)
    - [ ] BV relatief factor (5%)
  - [ ] Implementeer `calculate_bv_priority_ranking()`
  - [ ] Type hints en docstrings
  - [ ] Logging van scoring details

- [ ] Update strategies om nieuwe priority te gebruiken
  - [ ] Update `strategies/base.py` met enhanced ranking
  - [ ] Update `strategies/high_stock.py` priority selection
  - [ ] Update `strategies/low_stock.py` priority selection
  - [ ] Replace oude demand_score met nieuwe priority_score

- [ ] Update `backend/redistribution/domain.py`
  - [ ] Voeg `priority_score` toe aan `StoreInventory`
  - [ ] Voeg `priority_factors` toe voor debugging

### Testing
- [ ] Maak test bestand `backend/test_priority_scoring.py`
  - [ ] Test verkoop ratio calculation
  - [ ] Test absolute verkoop factor
  - [ ] Test serie compleetheid factor
  - [ ] Test categorie modifier
  - [ ] Test BV relatief ranking
  - [ ] Test multi-factor combinatie
  - [ ] Test edge cases (0 verkoop, 0 voorraad)

- [ ] Integration tests
  - [ ] Test priority ranking met reële data
  - [ ] Compare priority vs oude demand score
  - [ ] Verify top sellers krijgen hogere scores
  - [ ] Verify serie bonus werkt
  - [ ] Test BV-level ranking

### Documentation
- [ ] Voeg docstrings toe aan alle functies
- [ ] Update `docs/technical/baseline-implementation-plan.md`
- [ ] Maak `docs/technical/priority-scoring.md`
  - [ ] Formule uitleg
  - [ ] Factor wegingen
  - [ ] Voorbeelden
- [ ] Update `docs/guides/redistribution-algorithm.md`

### Review & Refinement
- [ ] Code review (formules, wegingen)
- [ ] Test met user op reële data
- [ ] Verzamel feedback op priority rankings
- [ ] Tune wegingen indien nodig
- [ ] Validate ranking verbeteringen
- [ ] Final testing

### Git & Documentation
- [ ] Git commit met message: "feat: implement multi-factor priority scoring (Baseline Phase 4)"
- [ ] Update `CHANGELOG.md` met Fase 4 changes
- [ ] Update session log
- [ ] Mark todo as complete

---

## 📐 Technical Design

### Multi-Factor Priority Formula
```python
priority_score = (
    verkoop_ratio_factor * 0.40 +      # Demand (klassiek)
    absolute_verkoop_factor * 0.25 +   # Top sellers voorkeur
    serie_compleetheid_factor * 0.20 + # Bijna-complete serie bonus
    categorie_modifier * 0.10 +        # Jassen vs shirts
    bv_relatief_factor * 0.05          # Relatief binnen BV
)
```

### Factor Calculations

#### 1. Verkoop Ratio Factor (40%)
```python
def calculate_verkoop_ratio_factor(
    verkocht: int,
    voorraad: int
) -> float:
    """
    Klassieke demand score (verkocht / voorraad).
    Genormaliseerd naar 0.0 - 1.0
    """
    if voorraad == 0:
        # Alles verkocht = hoge demand
        return 1.0 if verkocht > 0 else 0.0
    
    ratio = verkocht / voorraad
    
    # Clamp en normalize (max ratio = 2.0 = 1.0 score)
    return min(ratio / 2.0, 1.0)
```

#### 2. Absolute Verkoop Factor (25%)
```python
def calculate_absolute_verkoop_factor(
    verkocht: int,
    max_verkocht: int,
    article: ArticleStock
) -> float:
    """
    Prioriteit aan absolute top sellers.
    
    Args:
        verkocht: Verkocht in deze winkel
        max_verkocht: Max verkocht over alle winkels
        article: Voor context
        
    Returns:
        Score 0.0 - 1.0 (hoogste seller krijgt 1.0)
    """
    if max_verkocht == 0:
        return 0.0
    
    return verkocht / max_verkocht
```

#### 3. Serie Compleetheid Factor (20%)
```python
def calculate_serie_compleetheid_factor(
    store: StoreInventory,
    article: ArticleStock,
    min_series_width: int = 3
) -> float:
    """
    Bonus voor winkels met bijna-complete series.
    Stimuleert het compleet maken van series.
    
    Returns:
        0.0 - 1.0 (1.0 = complete serie aanwezig)
    """
    # Check huidige series
    sequences = article.size_sequences.get(store.store_code, [])
    
    if not sequences:
        # Geen serie: check potentieel
        # Als winkel 2/3 maten heeft van potentiële serie, geef bonus
        return calculate_potential_series_bonus(store, article)
    
    # Heeft serie: geef score op basis van breedte
    max_width = max(seq.width for seq in sequences)
    ideal_width = len(article.all_sizes)
    
    return min(max_width / ideal_width, 1.0)
```

#### 4. Categorie Modifier (10%)
```python
def calculate_categorie_modifier(
    category_policy: CategoryPolicy,
    store: StoreInventory
) -> float:
    """
    Modifier op basis van categorie beleid.
    Jassen krijgen hogere scores in meer winkels.
    
    Returns:
        Multiplier (bijv. 1.2 voor jassen, 1.0 default)
    """
    multiplier = category_policy.priority_weight_multiplier
    
    # Normalize to 0.0 - 1.0 range
    # Assume multiplier range: 0.8 - 1.5
    normalized = (multiplier - 0.8) / 0.7
    
    return max(0.0, min(1.0, normalized))
```

#### 5. BV Relatief Factor (5%)
```python
def calculate_bv_relatief_factor(
    store: StoreInventory,
    article: ArticleStock
) -> float:
    """
    Relatieve prestatie binnen BV.
    Top performer in BV krijgt hogere score.
    
    Returns:
        0.0 - 1.0 (1.0 = beste in BV)
    """
    bv_name = store.bv_name
    if not bv_name:
        return 0.5  # Neutral
    
    # Vind alle winkels in deze BV
    bv_stores = [
        s for s in article.stores.values()
        if s.bv_name == bv_name
    ]
    
    if len(bv_stores) <= 1:
        return 1.0  # Enige winkel in BV
    
    # Rank op verkoop
    sorted_stores = sorted(
        bv_stores,
        key=lambda s: s.total_sales,
        reverse=True
    )
    
    # Position in ranking
    position = next(
        i for i, s in enumerate(sorted_stores)
        if s.store_code == store.store_code
    )
    
    # Normalize (1e plaats = 1.0, laatste = 0.0)
    return 1.0 - (position / (len(sorted_stores) - 1))
```

### BV-Level Priority Ranking
```python
def calculate_bv_priority_ranking(
    article: ArticleStock,
    category_policy: CategoryPolicy
) -> Dict[str, List[Tuple[str, float]]]:
    """
    Rank winkels per BV op priority score.
    
    Returns:
        {bv_name: [(store_code, priority_score), ...]}
        Sorted descending by priority_score
    """
    bv_rankings = {}
    
    # Groepeer per BV
    bv_stores = defaultdict(list)
    for store in article.stores.values():
        bv_stores[store.bv_name].append(store)
    
    # Calculate priority per BV
    for bv_name, stores in bv_stores.items():
        # Bereken scores
        store_scores = []
        for store in stores:
            priority = calculate_multi_factor_priority(
                store, article, category_policy
            )
            store_scores.append((store.store_code, priority))
        
        # Sort descending
        store_scores.sort(key=lambda x: x[1], reverse=True)
        bv_rankings[bv_name] = store_scores
    
    return bv_rankings
```

---

## 🧪 Test Cases

### Test 1: Verkoop Ratio Factor
**Input:** verkocht=8, voorraad=10
**Expected:** ~0.4 (8/10 = 0.8, normalized to 0.4 met max=2.0)

### Test 2: Absolute Verkoop Factor
**Input:** 
- Winkel A: verkocht=15
- Winkel B: verkocht=10  
- Max=15
**Expected:** 
- Winkel A: 1.0
- Winkel B: 0.67

### Test 3: Serie Compleetheid
**Input:** Winkel heeft M-L-XL (3 breed) van totaal 5 maten
**Expected:** 3/5 = 0.6

### Test 4: Multi-Factor Combination
**Input:**
- Verkoop ratio: 0.8 → 0.4 (normalized)
- Absolute: 1.0 (top seller)
- Serie: 0.6
- Categorie: 1.0 (default)
- BV: 1.0 (top in BV)

**Expected:**
```
priority = (0.4 * 0.40) + (1.0 * 0.25) + (0.6 * 0.20) + (1.0 * 0.10) + (1.0 * 0.05)
         = 0.16 + 0.25 + 0.12 + 0.10 + 0.05
         = 0.68
```

### Test 5: BV Ranking
**Input:** BV met 4 winkels, verschillende verkopen
**Expected:** Correct gesorteerde lijst per BV

---

## 📊 Success Criteria

### Functional
✅ Priority scores reflecteren multi-factor analyse  
✅ Top sellers krijgen hogere scores  
✅ Serie bonus werkt correct  
✅ BV-level ranking functional  
✅ Categorie modifiers toegepast  

### Technical
✅ Type hints en docstrings  
✅ Unit tests >85% coverage  
✅ Performance geen regression  
✅ Logging van factor breakdown  

### Quality
✅ Ranking vergelijkbaar met manuele prioritering  
✅ Better than oude demand score  
✅ Strategies gebruiken nieuwe priority  
✅ Code review passed  

---

## 🔗 Dependencies

### Blocked By:
- Fase 3: Categorieën (gebruikt category_policy voor modifier)

### Blocks:
- Fase 5: Compensatie (gebruikt priority ranking)

---

## 📝 Notes

### Weging Tuning
De wegingen (40%, 25%, 20%, 10%, 5%) zijn initiële waarden en kunnen aangepast worden op basis van:
- User feedback
- A/B testing
- Historical performance

### Factor Balancing
Belangrijk dat alle factoren genormaliseerd zijn naar 0.0-1.0 range voor eerlijke weging.

### Future Enhancements
- Dynamic weging op basis van situatie
- Seizoen-specifieke factoren
- Verkoop trend (stijgend vs dalend)
- Store capacity constraints

---

**Last Updated:** 2025-11-05  
**Assigned To:** Cline AI  
**Reviewer:** User

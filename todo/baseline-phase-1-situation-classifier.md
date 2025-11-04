# Baseline Fase 1: Situatie Classificatie

**Status:** 🔄 Ready to Start  
**Priority:** 🔴 Critical Path  
**Tijdsinschatting:** 2-3 dagen  
**Start Datum:** 2025-11-05  
**Target Datum:** 2025-11-07

---

## 🎯 Doel

Implementeer een situatie classifier die automatisch detecteert of een artikel in een "veel voorraad" of "weinig voorraad" situatie zit.

---

## 📋 Checklist

### Design & Planning
- [ ] Review manuele werkwijze uit `docs/guides/beestprompt.md`
- [ ] Analyseer test data in `/dummyinfo/*.pdf`
- [ ] Bepaal exacte thresholds op basis van test data
- [ ] Design `StockSituation` enum structuur
- [ ] Design `SituationThresholds` dataclass

### Implementation
- [ ] Maak nieuw bestand `backend/redistribution/situation_classifier.py`
  - [ ] Implementeer `StockSituation` enum
  - [ ] Implementeer `classify_article_situation()` functie
  - [ ] Implementeer `_analyze_store_series_width()` helper
  - [ ] Implementeer `_analyze_total_inventory()` helper
  - [ ] Voeg logging toe voor beslissingen
  - [ ] Voeg type hints toe
  - [ ] Voeg docstrings toe

- [ ] Update `backend/redistribution/constraints.py`
  - [ ] Voeg `SituationThresholds` dataclass toe
  - [ ] Voeg default thresholds toe
  - [ ] Update `DEFAULT_PARAMS` met thresholds

- [ ] Update `backend/redistribution/algorithm.py`
  - [ ] Import `situation_classifier`
  - [ ] Voeg situatie classificatie stap toe in hoofdfunctie
  - [ ] Log geselecteerde situatie
  - [ ] Prepareer voor strategy selection (Fase 2)

### Testing
- [ ] Maak test bestand `backend/test_situation_classifier.py`
  - [ ] Test HIGH_STOCK detectie (40-56 stuks)
  - [ ] Test LOW_STOCK detectie (<25 stuks)
  - [ ] Test MEDIUM_STOCK detectie (25-40 stuks)
  - [ ] Test PARTIJ detectie (>56 stuks)
  - [ ] Test edge cases (exact op thresholds)
  - [ ] Test met verschillende maatserie breedtes

- [ ] Integration test met reële data
  - [ ] Test met artikelen uit `/dummyinfo/*.pdf`
  - [ ] Verify correcte classificatie per artikel
  - [ ] Log output voor manual review

### Documentation
- [ ] Voeg docstrings toe aan alle functies
- [ ] Update `docs/technical/baseline-implementation-plan.md`
- [ ] Maak `docs/technical/situation-classifier-design.md`
- [ ] Update `docs/guides/redistribution-algorithm.md`

### Review & Refinement
- [ ] Code review (type hints, naming, structure)
- [ ] Test met user op reële data
- [ ] Verzamel feedback op threshold waarden
- [ ] Pas thresholds aan indien nodig
- [ ] Final testing

### Git & Documentation
- [ ] Git commit met message: "feat: add situation classifier (Baseline Phase 1)"
- [ ] Update `CHANGELOG.md` met Fase 1 changes
- [ ] Update session log
- [ ] Mark todo as complete

---

## 📐 Technical Design

### StockSituation Enum
```python
class StockSituation(Enum):
    """
    Classificatie van voorraad situatie voor een artikel.
    Bepaalt welke herverdeling strategie gebruikt wordt.
    """
    HIGH_STOCK = "high_stock"      # 40-56 stuks: behoud series overal
    LOW_STOCK = "low_stock"        # <25 stuks: concentreer op top winkels
    MEDIUM_STOCK = "medium_stock"  # 25-40 stuks: balans tussen beide
    PARTIJ = "partij"              # >56 stuks: partijgoederen
```

### SituationThresholds Dataclass
```python
@dataclass
class SituationThresholds:
    """Drempelwaarden voor situatie classificatie"""
    
    # Totale voorraad thresholds
    high_stock_min: int = 40       # Minimum voor "veel voorraad"
    high_stock_max: int = 56       # Maximum normale levering
    low_stock_max: int = 25        # Maximum voor "weinig voorraad"
    partij_threshold: int = 70     # Partijgoederen drempel
    
    # Voor detectie "complete serie" situatie
    min_stores_with_series: int = 4      # Aantal winkels met ≥3 maten
    min_series_width: int = 3            # Minimum breedte van serie
    
    # Voor serie breedte analyse
    complete_series_threshold: float = 0.7  # 70% van winkels moet serie hebben
```

### Classificatie Algoritme
```python
def classify_article_situation(
    article: ArticleStock,
    thresholds: SituationThresholds
) -> StockSituation:
    """
    Classificeer artikel op basis van:
    1. Totale voorraad
    2. Distributie over winkels
    3. Maatserie breedtes
    
    Args:
        article: ArticleStock object met voorraad data
        thresholds: Configureerbare drempelwaarden
        
    Returns:
        StockSituation classificatie
    """
    
    total_inventory = article.total_inventory
    
    # Check PARTIJ eerst (hoogste priority)
    if total_inventory > thresholds.partij_threshold:
        return StockSituation.PARTIJ
    
    # Check LOW_STOCK
    if total_inventory <= thresholds.low_stock_max:
        return StockSituation.LOW_STOCK
    
    # Check HIGH_STOCK
    if thresholds.high_stock_min <= total_inventory <= thresholds.high_stock_max:
        # Extra validatie: zijn er inderdaad complete series in veel winkels?
        stores_with_series = _count_stores_with_complete_series(
            article, 
            thresholds.min_series_width
        )
        
        serie_ratio = stores_with_series / len(article.stores)
        
        if serie_ratio >= thresholds.complete_series_threshold:
            return StockSituation.HIGH_STOCK
    
    # Default: MEDIUM_STOCK
    return StockSituation.MEDIUM_STOCK
```

---

## 🧪 Test Cases

### Test 1: HIGH_STOCK Detection
**Input:**
- Totale voorraad: 48 stuks
- 6 winkels
- 5 winkels hebben series van 3-4 breed
- Distributie: relatief gelijk

**Expected:** `StockSituation.HIGH_STOCK`

### Test 2: LOW_STOCK Detection
**Input:**
- Totale voorraad: 18 stuks
- 6 winkels
- Fragmentatie: elk 1-3 stuks per winkel

**Expected:** `StockSituation.LOW_STOCK`

### Test 3: PARTIJ Detection
**Input:**
- Totale voorraad: 85 stuks
- 8 winkels

**Expected:** `StockSituation.PARTIJ`

### Test 4: MEDIUM_STOCK Detection
**Input:**
- Totale voorraad: 32 stuks
- 5 winkels
- Gemengde distributie

**Expected:** `StockSituation.MEDIUM_STOCK`

### Test 5: Edge Case - Exact Threshold
**Input:**
- Totale voorraad: 25 stuks (exact op threshold)

**Expected:** `StockSituation.LOW_STOCK` (inclusief threshold)

---

## 📊 Success Criteria

### Functional
✅ Algoritme classificeert correct op basis van voorraad  
✅ Serie-analyse werkt voor HIGH_STOCK detectie  
✅ Thresholds zijn configureerbaar  
✅ Edge cases worden correct afgehandeld  

### Technical
✅ Type hints voor alle functies  
✅ Docstrings volgen numpy/google style  
✅ Unit tests met >90% coverage  
✅ Logging van beslissingen  

### Integration
✅ Integreert met bestaand algoritme  
✅ Backwards compatible (geen breaking changes)  
✅ Test met reële PDF data succesvol  

---

## 🔗 Dependencies

### Blocked By:
- Niets (kan direct starten)

### Blocks:
- Fase 2: Strategieën Implementatie (heeft situatie classificatie nodig)

---

## 📝 Notes

### Threshold Tuning
De threshold waarden kunnen na user testing aangepast worden. Belangrijke factoren:
- **High Stock Min (40):** Typische levering vanuit magazijn
- **Low Stock Max (25):** Punt waar concentratie nodig is
- **Partij Threshold (70):** Duidelijk partijgoederen of hergebruikte codes

### Serie Analyse Complexity
De serie-analyse voor HIGH_STOCK is optioneel maar verbetert accuracy. Als een artikel technisch 45 stuks heeft maar deze zijn over 10 winkels verdeeld met elk 1-2 stuks, is het eigenlijk LOW_STOCK gedrag.

### Future Enhancements
- Seizoenskenmerken (winter vs zomer)
- Artikel leeftijd (hoe lang al in voorraad)
- Verkoop trend (stijgend vs dalend)

---

**Last Updated:** 2025-11-05  
**Assigned To:** Cline AI  
**Reviewer:** User

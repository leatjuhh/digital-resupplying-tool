# Baseline Fase 5: Maat Compensatie Mechanisme

**Status:** ⏸️ Waiting (Blocked by Fase 4)  
**Priority:** 🟢 Nice-to-Have  
**Tijdsinschatting:** 1-2 dagen  
**Start Datum:** TBD (na Fase 4)  
**Target Datum:** TBD

---

## 🎯 Doel

Implementeer compensatie mechanisme voor ontbrekende maten met alternatieve maten (dubbele toewijzing, buitenliggende maten).

---

## 📋 Checklist

### Design & Planning
- [ ] Review manuele compensatie werkwijze uit `docs/guides/beestprompt.md`
- [ ] Design compensatie voorkeur volgorde
- [ ] Plan integratie met Low Stock Strategy
- [ ] Bepaal wanneer compensatie toegepast wordt

### Implementation
- [ ] Implementeer `backend/redistribution/size_compensation.py`
  - [ ] `CompensationOption` dataclass
  - [ ] `find_compensation_sizes()` functie
  - [ ] Implementeer voorkeur logica:
    - [ ] Dubbele toewijzing naburige maat
    - [ ] Buitenliggende maat (S/XXL)
    - [ ] Één maat verder
  - [ ] `calculate_compensation_score()` functie
  - [ ] Type hints en docstrings
  - [ ] Logging van compensatie beslissingen

- [ ] Update `backend/redistribution/strategies/low_stock.py`
  - [ ] Import size_compensation module
  - [ ] Integreer compensatie in move generation
  - [ ] Apply compensatie voor top-X winkels met gaten
  - [ ] Validate compensatie verbetert compleetheid
  - [ ] Log compensatie decisions

### Testing
- [ ] Maak test bestand `backend/test_compensation.py`
  - [ ] Test dubbele toewijzing scenario
  - [ ] Test buitenliggende maat scenario
  - [ ] Test één maat verder scenario
  - [ ] Test geen compensatie mogelijk
  - [ ] Test compensation scoring
  - [ ] Test edge cases

- [ ] Integration tests
  - [ ] Test LOW_STOCK artikel met compensatie
  - [ ] Verify top winkels krijgen complete-ish series
  - [ ] Compare output met/zonder compensatie
  - [ ] Validate logging van beslissingen

### Documentation
- [ ] Voeg docstrings toe aan alle functies
- [ ] Update `docs/technical/baseline-implementation-plan.md`
- [ ] Maak `docs/technical/size-compensation.md`
  - [ ] Voorkeur volgorde uitleg
  - [ ] Scoring logica
  - [ ] Voorbeelden
- [ ] Update `docs/guides/redistribution-algorithm.md`

### Review & Refinement
- [ ] Code review (compensatie logica)
- [ ] Test met user op reële low stock scenarios
- [ ] Verzamel feedback op compensatie keuzes
- [ ] Tune voorkeur volgorde indien nodig
- [ ] Final testing

### Git & Documentation
- [ ] Git commit met message: "feat: implement size compensation mechanism (Baseline Phase 5)"
- [ ] Update `CHANGELOG.md` met Fase 5 changes
- [ ] Update session log
- [ ] Mark todo as complete

---

## 📐 Technical Design

### CompensationOption Dataclass
```python
@dataclass
class CompensationOption:
    """Optie voor maat compensatie"""
    size: str                   # Compensatie maat (bijv. "S")
    quantity: int               # Beschikbare quantity
    missing_size: str           # Maat die gemist wordt (bijv. "L")
    compensation_type: str      # "double", "outer", "adjacent"
    score: float                # Geschiktheid score (0.0 - 1.0)
    reason: str                 # Uitleg van keuze
    
    def __repr__(self) -> str:
        return f"Compensate {self.missing_size} with {self.size} ({self.compensation_type})"
```

### Compensation Voorkeur Volgorde
```python
def find_compensation_sizes(
    missing_size: str,
    available_sizes: Dict[str, int],
    size_sequence: List[str],
    target_store_inventory: Dict[str, int]
) -> List[CompensationOption]:
    """
    Vind compensatie opties voor ontbrekende maat.
    
    Voorkeur volgorde:
    1. Dubbele toewijzing naburige maat (als qty >= 2)
    2. Buitenliggende maat (S of XXL)
    3. Één maat verder
    
    Args:
        missing_size: Maat die gemist wordt
        available_sizes: Beschikbare maten {maat: qty}
        size_sequence: Volledige maat volgorde
        target_store_inventory: Current inventory in target store
        
    Returns:
        Lijst van CompensationOption, gesorteerd op score
    """
    options = []
    
    if missing_size not in size_sequence:
        return options  # Kan niet compenseren
    
    missing_idx = size_sequence.index(missing_size)
    
    # === VOORKEUR 1: Dubbele Toewijzing Naburige Maat ===
    # Check naburige maten (direct +1 of -1)
    for offset in [-1, 1]:
        adjacent_idx = missing_idx + offset
        if 0 <= adjacent_idx < len(size_sequence):
            adjacent_size = size_sequence[adjacent_idx]
            available_qty = available_sizes.get(adjacent_size, 0)
            current_qty = target_store_inventory.get(adjacent_size, 0)
            
            # Als er >= 2 beschikbaar EN winkel heeft er al 1+
            if available_qty >= 2 and current_qty >= 1:
                option = CompensationOption(
                    size=adjacent_size,
                    quantity=1,  # Geef extra 1
                    missing_size=missing_size,
                    compensation_type="double",
                    score=0.9,  # Hoogste score
                    reason=f"Dubbele {adjacent_size} (naast {missing_size})"
                )
                options.append(option)
    
    # === VOORKEUR 2: Buitenliggende Maat ===
    # S (eerste) of XXL (laatste)
    outer_sizes = []
    if missing_idx > len(size_sequence) // 2:
        # Mist maat in 2e helft -> gebruik laatste (XXL)
        outer_sizes = [size_sequence[-1], size_sequence[-2]]
    else:
        # Mist maat in 1e helft -> gebruik eerste (S)
        outer_sizes = [size_sequence[0], size_sequence[1]]
    
    for outer_size in outer_sizes:
        if outer_size in available_sizes and available_sizes[outer_size] > 0:
            option = CompensationOption(
                size=outer_size,
                quantity=1,
                missing_size=missing_size,
                compensation_type="outer",
                score=0.7,  # Medium score
                reason=f"Buitenliggende maat {outer_size} voor {missing_size}"
            )
            options.append(option)
            break  # Eén outer maat is genoeg
    
    # === VOORKEUR 3: Één Maat Verder ===
    for offset in [-2, 2]:
        further_idx = missing_idx + offset
        if 0 <= further_idx < len(size_sequence):
            further_size = size_sequence[further_idx]
            if further_size in available_sizes and available_sizes[further_size] > 0:
                option = CompensationOption(
                    size=further_size,
                    quantity=1,
                    missing_size=missing_size,
                    compensation_type="adjacent",
                    score=0.5,  # Lage score (last resort)
                    reason=f"Één maat verder: {further_size} voor {missing_size}"
                )
                options.append(option)
    
    # Sort op score (hoogste eerst)
    options.sort(key=lambda x: x.score, reverse=True)
    
    return options
```

### Integration in Low Stock Strategy
```python
class LowStockStrategy(RedistributionStrategy):
    """Updates voor compensatie support"""
    
    def generate_moves(self, article: ArticleStock) -> List[Move]:
        # ... bestaande logica voor core series ...
        
        # === COMPENSATIE FASE ===
        # Voor elke top winkel: check gaten in serie
        for target_store, _ in target_stores:
            target_inv = article.stores[target_store]
            
            # Vind ontbrekende core maten
            missing_sizes = [
                size for size in core_sizes
                if size not in target_inv.inventory or target_inv.inventory[size] == 0
            ]
            
            for missing_size in missing_sizes:
                # Zoek compensatie
                compensation_options = find_compensation_sizes(
                    missing_size=missing_size,
                    available_sizes=remaining_availability,
                    size_sequence=article.all_sizes,
                    target_store_inventory=target_inv.inventory
                )
                
                if compensation_options:
                    # Gebruik beste optie
                    best_option = compensation_options[0]
                    
                    # Vind bron voor deze maat
                    for source_store, _ in source_stores:
                        source_inv = article.stores[source_store]
                        if (best_option.size in source_inv.inventory and 
                            source_inv.inventory[best_option.size] > 0):
                            
                            move = Move(
                                volgnummer=article.volgnummer,
                                size=best_option.size,
                                from_store=source_store,
                                from_store_name=source_inv.store_name,
                                to_store=target_store,
                                to_store_name=target_inv.store_name,
                                qty=best_option.quantity,
                                reason=best_option.reason,
                                from_bv=source_inv.bv_name,
                                to_bv=target_inv.bv_name
                            )
                            
                            moves.append(move)
                            
                            # Update availability
                            remaining_availability[best_option.size] -= best_option.quantity
                            
                            break  # Found source
        
        return moves
```

---

## 🧪 Test Cases

### Test 1: Dubbele Toewijzing
**Input:**
- Target winkel mist L
- Beschikbaar: M=3 (winkel heeft al M=1)
- M is naburig aan L

**Expected:** Compensate met extra M (dubbele toewijzing)

### Test 2: Buitenliggende Maat
**Input:**
- Target winkel mist XL (2e helft)
- Beschikbaar: XXL=1
- Geen dubbele toewijzing mogelijk

**Expected:** Compensate met XXL (buitenliggende)

### Test 3: Één Maat Verder
**Input:**
- Target winkel mist M
- Beschikbaar: alleen XL=1
- Geen andere opties

**Expected:** Compensate met XL (één maat verder)

### Test 4: Geen Compensatie Mogelijk
**Input:**
- Target winkel mist L
- Geen geschikte maten beschikbaar

**Expected:** Lege compensatie lijst, geen move

### Test 5: Scoring
**Input:** Alle compensatie types beschikbaar

**Expected:** 
- Dubbele: score 0.9
- Outer: score 0.7
- Adjacent: score 0.5

---

## 📊 Success Criteria

### Functional
✅ Compensatie verbetert serie compleetheid  
✅ Voorkeur volgorde correct toegepast  
✅ Low Stock Strategy gebruikt compensatie  
✅ Logging van compensatie beslissingen  

### Technical
✅ Type hints en docstrings  
✅ Unit tests >80% coverage  
✅ Geen breaking changes  
✅ Performant (geen delays)  

### Quality
✅ Compensatie vergelijkbaar met manuele keuze  
✅ Output betert dan zonder compensatie  
✅ Code review passed  

---

## 🔗 Dependencies

### Blocked By:
- Fase 4: Prioritering (compensatie gebruikt priority ranking voor target selection)

### Blocks:
- Niets (optionele feature)

---

## 📝 Notes

### Wanneer Compenseren?
Compensatie is ALLEEN relevant in LOW_STOCK situaties waar:
- Top-X winkels geselecteerd zijn
- Deze winkels bijna-complete series hebben
- Er gaten zijn die niet met exacte maten gevuld kunnen worden

In HIGH_STOCK situaties is compensatie niet nodig (genoeg voorraad).

### Future Enhancements
- Smart compensatie op basis van verkoop data per maat
- Customer preference data (welke maten worden samen gekocht)
- Seasonal preferences (winter: grotere maten)

---

**Last Updated:** 2025-11-05  
**Assigned To:** Cline AI  
**Reviewer:** User

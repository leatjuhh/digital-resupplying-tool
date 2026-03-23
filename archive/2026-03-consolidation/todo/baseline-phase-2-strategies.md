# Baseline Fase 2: Strategieën Implementatie

**Status:** ⏸️ Waiting (Blocked by Fase 1)  
**Priority:** 🔴 Critical Path  
**Tijdsinschatting:** 4-5 dagen  
**Start Datum:** TBD (na Fase 1)  
**Target Datum:** TBD

---

## 🎯 Doel

Implementeer situatie-specifieke herverdelingsstrategieën die de manuele werkwijze navolgen voor verschillende voorraad situaties.

---

## 📋 Checklist

### Design & Planning
- [ ] Review manuele strategieën per situatie uit `docs/guides/beestprompt.md`
- [ ] Design Strategy Pattern architectuur
- [ ] Bepaal interface voor base strategy class
- [ ] Plan integratie met bestaand algoritme

### Base Strategy Implementation
- [ ] Maak folder `backend/redistribution/strategies/`
- [ ] Maak `backend/redistribution/strategies/__init__.py`
- [ ] Implementeer `backend/redistribution/strategies/base.py`
  - [ ] Abstract `RedistributionStrategy` base class
  - [ ] `generate_moves()` abstract method
  - [ ] Shared helper methods
  - [ ] Type hints en docstrings

### High Stock Strategy (Situatie 1)
- [ ] Implementeer `backend/redistribution/strategies/high_stock.py`
  - [ ] `HighStockStrategy` class
  - [ ] Inventariseer winkels met complete series
  - [ ] Bepaal top 60% priority winkels
  - [ ] Vul gaten in priority winkels aan
  - [ ] Alleen afname van bottom 20% winkels
  - [ ] Valideer serie behoud
  - [ ] Type hints en docstrings
  - [ ] Logging van beslissingen

### Low Stock Strategy (Situatie 2)
- [ ] Implementeer `backend/redistribution/strategies/low_stock.py`
  - [ ] `LowStockStrategy` class
  - [ ] **Identificeer core sizes** (middelste maten M-L-XL)
    - [ ] Voor letter maten: skip eerste/laatste, neem middelste 3
    - [ ] Voor numerieke maten: analyseer distributie
  - [ ] Tel beschikbare core maten per maat
  - [ ] Bereken hoeveel complete core series mogelijk (min van core maten)
  - [ ] Selecteer top X winkels (demand-based priority score)
  - [ ] Trek niet-top winkels **volledig leeg**
  - [ ] Distribueer naar top winkels met optimale maat matching
  - [ ] Type hints en docstrings
  - [ ] Logging van beslissingen (inclusief core size detectie)

### Partij Strategy
- [ ] Implementeer `backend/redistribution/strategies/partij.py`
  - [ ] `PartijStrategy` class
  - [ ] Agressievere herverdeling logica
  - [ ] Minder focus op serie behoud
  - [ ] Meer focus op demand matching
  - [ ] Grotere moves toegestaan
  - [ ] Type hints en docstrings
  - [ ] Logging van beslissingen

### Default Strategy (Fallback)
- [ ] Implementeer `backend/redistribution/strategies/default.py`
  - [ ] `DefaultStrategy` class
  - [ ] Wrap huidige greedy algoritme
  - [ ] Backwards compatible behavior
  - [ ] Type hints en docstrings

### Algorithm Integration
- [ ] Update `backend/redistribution/algorithm.py`
  - [ ] Import strategies module
  - [ ] Implementeer `select_strategy()` functie
  - [ ] Integreer situatie classificatie met strategy selection
  - [ ] Update `generate_redistribution_proposals_for_article()`
  - [ ] Roep juiste strategy aan op basis van situatie
  - [ ] Log geselecteerde strategy

### Testing
- [ ] Maak test bestand `backend/test_strategies.py`
  - [ ] Test HighStockStrategy met mock data
  - [ ] Test LowStockStrategy met mock data
  - [ ] Test PartijStrategy met mock data
  - [ ] Test DefaultStrategy (fallback)
  - [ ] Test strategy selection logic
  - [ ] Test edge cases per strategy

- [ ] Integration tests met reële data
  - [ ] Test HIGH_STOCK artikel uit `/dummyinfo/*.pdf`
  - [ ] Test LOW_STOCK artikel uit `/dummyinfo/*.pdf`
  - [ ] Test PARTIJ artikel (create test data indien nodig)
  - [ ] Verify output vs manuele verwachting
  - [ ] Compare vs huidige algoritme output

### Documentation
- [ ] Voeg docstrings toe aan alle classes/methods
- [ ] Update `docs/technical/baseline-implementation-plan.md`
- [ ] Maak `docs/technical/strategies-design.md`
- [ ] Update `docs/guides/redistribution-algorithm.md`
- [ ] Maak strategy decision flowchart (mermaid diagram)

### Review & Refinement
- [ ] Code review (architecture, patterns, naming)
- [ ] Test met user op reële data
- [ ] Verzamel feedback op strategy output
- [ ] Pas strategy logica aan indien nodig
- [ ] Performance testing (geen regressions)
- [ ] Final testing

### Git & Documentation
- [ ] Git commit met message: "feat: implement situation-based strategies (Baseline Phase 2)"
- [ ] Update `CHANGELOG.md` met Fase 2 changes
- [ ] Update session log
- [ ] Mark todo as complete

---

## 📐 Technical Design

### Base Strategy Interface
```python
from abc import ABC, abstractmethod
from typing import List
from ..domain import ArticleStock, Move
from ..constraints import RedistributionParams

class RedistributionStrategy(ABC):
    """
    Abstract base class voor herverdeling strategieën.
    Elke strategie implementeert een specifieke aanpak
    gebaseerd op voorraad situatie.
    """
    
    def __init__(self, params: RedistributionParams):
        self.params = params
    
    @abstractmethod
    def generate_moves(
        self,
        article: ArticleStock
    ) -> List[Move]:
        """
        Genereer moves voor dit artikel volgens strategie.
        
        Args:
            article: Article met voorraad data
            
        Returns:
            Lijst van Move objecten
        """
        pass
    
    def _rank_stores_by_priority(
        self,
        article: ArticleStock
    ) -> List[Tuple[str, float]]:
        """Helper: rank winkels op priority score"""
        pass
    
    def _get_stores_in_bv(
        self,
        article: ArticleStock,
        bv_name: str
    ) -> List[str]:
        """Helper: get alle winkels in specifieke BV"""
        pass
```

### High Stock Strategy Logic
```python
class HighStockStrategy(RedistributionStrategy):
    """
    Strategie voor HIGH_STOCK situatie (40-56 stuks).
    
    Doel: Behoud zoveel mogelijk complete maatseries in veel winkels.
    
    Aanpak:
    1. Identificeer winkels met complete series (3-4 breed)
    2. Bepaal top 60% priority winkels (op verkoop)
    3. Voor priority winkels: vul ontbrekende maten aan
    4. Bronnen: alleen bottom 20% winkels
    5. Valideer: breekt dit niet teveel series elders?
    """
    
    def generate_moves(self, article: ArticleStock) -> List[Move]:
        moves = []
        
        # Stap 1: Inventariseer series
        stores_with_series = self._find_stores_with_complete_series(article)
        
        # Stap 2: Rank winkels op priority
        priority_ranking = self._rank_stores_by_priority(article)
        top_60_percent = priority_ranking[:int(len(priority_ranking) * 0.6)]
        bottom_20_percent = priority_ranking[-int(len(priority_ranking) * 0.2):]
        
        # Stap 3: Voor elke top winkel, vul gaten
        for store_code, _ in top_60_percent:
            missing_sizes = self._find_missing_sizes_in_series(
                article, store_code
            )
            
            for size in missing_sizes:
                # Zoek beschikbaarheid in bottom winkels
                for source_store, _ in bottom_20_percent:
                    if self._can_provide_without_breaking_series(
                        article, source_store, size
                    ):
                        move = self._create_move(
                            article, size, source_store, store_code
                        )
                        moves.append(move)
                        break
        
        return moves
```

### Low Stock Strategy Logic
```python
class LowStockStrategy(RedistributionStrategy):
    """
    Strategie voor LOW_STOCK situatie (<25 stuks).
    
    Doel: Concentreer voorraad in top X winkels met complete serie.
    
    Aanpak:
    1. Tel beschikbare maten per maat
    2. Bereken hoeveel complete M-L-XL series mogelijk
    3. Selecteer top X winkels (demand-based)
    4. Geef deze winkels complete series
    5. Trek andere winkels (bijna) leeg
    
    Voorbeeld:
    S=3, M=5, L=4, XL=6, XXL=1
    → 4 complete M-L-XL series mogelijk
    → Selecteer top 4 winkels
    → Concentreer voorraad daar
    """
    
    def generate_moves(self, article: ArticleStock) -> List[Move]:
        moves = []
        
        # Stap 1: Analyseer beschikbare maten
        size_availability = self._count_sizes_per_size(article)
        
        # Stap 2: Bepaal hoeveel complete series mogelijk
        # Focus op middelste maten (M, L, XL typisch)
        core_sizes = self._identify_core_sizes(article.all_sizes)
        max_complete_series = min(
            size_availability.get(size, 0) 
            for size in core_sizes
        )
        
        # Stap 3: Selecteer top X winkels
        priority_ranking = self._rank_stores_by_priority(article)
        target_stores = priority_ranking[:max_complete_series]
        source_stores = priority_ranking[max_complete_series:]
        
        # Stap 4: Trek source winkels leeg naar target winkels
        for target_store, _ in target_stores:
            for size in core_sizes:
                # Vind source voor deze maat
                for source_store, _ in source_stores:
                    source_inv = article.stores[source_store]
                    if size in source_inv.inventory and source_inv.inventory[size] > 0:
                        move = self._create_move(
                            article, size, source_store, target_store, 
                            qty=source_inv.inventory[size]  # Trek leeg!
                        )
                        moves.append(move)
                        break
        
        return moves
```

---

## 🧪 Test Cases

### Test 1: High Stock Strategy
**Input:**
- Artikel met 48 stuks, 6 winkels
- 4 winkels hebben M-L-XL serie
- 2 winkels missen 1-2 maten
- Verkoop: winkel 1-2 top, winkel 5-6 bottom

**Expected:**
- Moves vullen gaten in winkel 1-2
- Bron: alleen winkel 5-6
- Winkel 3-4 blijven intact
- Serie behoud gevalideerd

### Test 2: Low Stock Strategy
**Input:**
- Artikel met 18 stuks, 6 winkels
- Maten: S=2, M=4, L=3, XL=5, XXL=4
- Verkoop: duidelijke top 3 winkels

**Expected:**
- 3 winkels krijgen complete M-L-XL
- Andere 3 winkels bijna leeg getrokken
- Concentratie in top performers

### Test 3: Partij Strategy
**Input:**
- Artikel met 85 stuks, 8 winkels
- Gemengde distributie

**Expected:**
- Agressievere herverdeling
- Grotere move quantities
- Minder serie behoud concern

### Test 4: Strategy Selection
**Input:**
- HIGH_STOCK artikel (48 stuks)

**Expected:**
- `HighStockStrategy` geselecteerd
- Strategy logic toegepast
- Correcte output

---

## 📊 Success Criteria

### Functional
✅ Elke strategy genereert situatie-specifieke moves  
✅ HighStockStrategy behoudt series in veel winkels  
✅ LowStockStrategy concentreert op top-X  
✅ PartijStrategy is agressiever  
✅ Strategy selection werkt correct  

### Technical
✅ Strategy pattern correct geïmplementeerd  
✅ Type hints en docstrings overal  
✅ Unit tests >85% coverage  
✅ Integration tests passeren  
✅ Logging van strategy beslissingen  

### Quality
✅ Output vergelijkbaar met manuele beslissingen  
✅ No performance regression vs huidig  
✅ Backwards compatible (DEFAULT strategy)  
✅ Code review passed  

---

## 🔗 Dependencies

### Blocked By:
- Fase 1: Situatie Classificatie (nodig voor strategy selection)

### Blocks:
- Fase 3: Artikel Categorieën (strategies gebruiken categorie policies)

---

## 📝 Notes

### Strategy Selection Logic
```python
def select_strategy(
    situation: StockSituation,
    params: RedistributionParams
) -> RedistributionStrategy:
    """Select strategie op basis van situatie"""
    
    if situation == StockSituation.HIGH_STOCK:
        return HighStockStrategy(params)
    elif situation == StockSituation.LOW_STOCK:
        return LowStockStrategy(params)
    elif situation == StockSituation.PARTIJ:
        return PartijStrategy(params)
    else:
        return DefaultStrategy(params)  # Fallback
```

### Backwards Compatibility
DefaultStrategy wraps het huidige greedy algoritme zodat bestaande functionaliteit blijft werken voor MEDIUM_STOCK situaties of als fallback.

### Future Enhancements
- Hybrid strategies (combinatie van HIGH + LOW)
- Seizoen-specifieke strategies
- Store capacity constraints
- Transport cost optimization per strategy

---

**Last Updated:** 2025-11-05  
**Assigned To:** Cline AI  
**Reviewer:** User

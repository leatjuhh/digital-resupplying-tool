# Baseline Fase 3: Artikel Categorie System

**Status:** ⏸️ Waiting (Blocked by Fase 2)  
**Priority:** 🟡 Medium Priority  
**Tijdsinschatting:** 2-3 dagen  
**Start Datum:** TBD (na Fase 2)  
**Target Datum:** TBD

---

## 🎯 Doel

Implementeer artikel categorie detectie en pas categorie-specifiek beleid toe (bijv. jassen worden anders herverdeeld dan shirts).

---

## 📋 Checklist

### Design & Planning
- [ ] Analyseer artikel omschrijvingen in test data
- [ ] Identify common categorie keywords
- [ ] Design categorie policies per type
- [ ] Plan detectie algoritme (keyword matching)

### Implementation
- [ ] Implementeer `backend/redistribution/article_categories.py`
  - [ ] `ArticleCategory` enum (definities)
  - [ ] `CategoryPolicy` dataclass
  - [ ] `CATEGORY_POLICIES` dict (default policies)
  - [ ] `detect_article_category()` functie
  - [ ] Keyword matching logica
  - [ ] Type hints en docstrings

- [ ] Update strategies voor categorie awareness
  - [ ] Update `strategies/base.py` met category support
  - [ ] Update `strategies/high_stock.py` voor jassen beleid
  - [ ] Update `strategies/low_stock.py` voor categorie modifiers
  - [ ] Pass category policy to strategies

- [ ] Update `backend/redistribution/algorithm.py`
  - [ ] Import article_categories
  - [ ] Detect categorie voor elk artikel
  - [ ] Pass category policy to strategy
  - [ ] Log detected category

### Testing
- [ ] Maak test bestand `backend/test_categories.py`
  - [ ] Test jas detectie (verschillende keywords)
  - [ ] Test broek detectie
  - [ ] Test jurk detectie
  - [ ] Test shirt detectie
  - [ ] Test UNKNOWN fallback
  - [ ] Test case-insensitive matching
  - [ ] Test policy application

- [ ] Integration tests met reële data
  - [ ] Test categorie detectie met `/dummyinfo/*.pdf`
  - [ ] Verify correcte policies toegepast
  - [ ] Compare output: jassen vs shirts
  - [ ] Validate >90% detection accuracy

### Documentation
- [ ] Voeg docstrings toe aan alle functies
- [ ] Update `docs/technical/baseline-implementation-plan.md`
- [ ] Maak `docs/technical/category-detection.md`
  - [ ] Lijst van keywords per categorie
  - [ ] Policy definities
  - [ ] Detection algorithm
- [ ] Update `docs/guides/redistribution-algorithm.md`

### Review & Refinement
- [ ] Review keyword lijst (completeness)
- [ ] Test met user op reële artikelen
- [ ] Verzamel feedback op wrong classifications
- [ ] Expand keyword lijst
- [ ] Tune policies per categorie
- [ ] Final testing

### Git & Documentation
- [ ] Git commit met message: "feat: add article category system (Baseline Phase 3)"
- [ ] Update `CHANGELOG.md` met Fase 3 changes
- [ ] Update session log
- [ ] Mark todo as complete

---

## 📐 Technical Design

### ArticleCategory Enum
```python
class ArticleCategory(Enum):
    """Artikel categorieën voor specifiek herverdeling beleid"""
    WINTER_JAS = "winter_jas"
    ZOMER_JAS = "zomer_jas"
    BROEK = "broek"
    JURK = "jurk"
    SHIRT = "shirt"
    TRUI = "trui"
    ROK = "rok"
    ACCESSOIRE = "accessoire"
    UNKNOWN = "unknown"
```

### CategoryPolicy Dataclass
```python
@dataclass
class CategoryPolicy:
    """Beleid voor een specifieke artikel categorie"""
    
    # Serie behoud
    preserve_in_more_stores: bool = False  # Jassen: True, shirts: False
    allow_low_quantities: bool = False     # Jassen: True (1-2 per winkel ok)
    min_items_per_store: int = 3           # Minimum voor niet-jassen
    
    # Prioritering
    priority_weight_multiplier: float = 1.0  # Jassen: 1.2, shirts: 1.0
    
    # Strategy modifiers
    high_stock_top_pct: float = 0.6      # Top % winkels in HIGH_STOCK
    low_stock_concentration: int = 3     # Aantal winkels voor LOW_STOCK
    
    # Thresholds
    min_move_quantity: int = 1           # Jassen: 1, andere: 2+
    
    def __str__(self) -> str:
        return f"CategoryPolicy(preserve={self.preserve_in_more_stores})"
```

### Detection Algorithm
```python
# Keyword dictionaries per categorie
CATEGORY_KEYWORDS = {
    ArticleCategory.WINTER_JAS: [
        "winterjas", "jas", "jacket", "coat", "parka", 
        "wintercoat", "gewatteerd", "donsjas"
    ],
    ArticleCategory.ZOMER_JAS: [
        "zomerjas", "blazer", "vest", "suede", "leren jas"
    ],
    ArticleCategory.BROEK: [
        "broek", "jeans", "pantalon", "legging", "chino",
        "cargo", "palazzo", "culotte"
    ],
    ArticleCategory.JURK: [
        "jurk", "dress", "maxi", "midi", "mini",
        "avondjurk", "cocktailjurk"
    ],
    ArticleCategory.SHIRT: [
        "shirt", "top", "blouse", "t-shirt", "tshirt",
        "polo", "longsleeve"
    ],
    # ... meer categorieën
}

def detect_article_category(
    volgnummer: str,
    omschrijving: str
) -> ArticleCategory:
    """
    Detecteer categorie op basis van omschrijving.
    
    Args:
        volgnummer: Artikelnummer (voor toekomstige pattern matching)
        omschrijving: Artikel beschrijving uit PDF
        
    Returns:
        ArticleCategory classificatie
    """
    omschrijving_lower = omschrijving.lower()
    
    # Check elke categorie
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in omschrijving_lower:
                return category
    
    # Fallback
    return ArticleCategory.UNKNOWN
```

### Policy Definitions
```python
CATEGORY_POLICIES = {
    ArticleCategory.WINTER_JAS: CategoryPolicy(
        preserve_in_more_stores=True,  # Jassen in meer winkels
        allow_low_quantities=True,     # 1-2 stuks per winkel ok
        min_items_per_store=1,
        priority_weight_multiplier=1.2,  # Extra prioriteit
        high_stock_top_pct=0.8,        # 80% winkels behouden voorraad
        low_stock_concentration=5,      # Concentreer in 5 winkels
        min_move_quantity=1
    ),
    
    ArticleCategory.SHIRT: CategoryPolicy(
        preserve_in_more_stores=False,  # Concentreer shirts
        allow_low_quantities=False,
        min_items_per_store=3,
        priority_weight_multiplier=1.0,
        high_stock_top_pct=0.6,        # 60% winkels
        low_stock_concentration=3,      # Concentreer in 3 winkels
        min_move_quantity=2
    ),
    
    ArticleCategory.UNKNOWN: CategoryPolicy(
        # Default policy (balanced)
        preserve_in_more_stores=False,
        allow_low_quantities=False,
        min_items_per_store=2,
        priority_weight_multiplier=1.0,
        high_stock_top_pct=0.6,
        low_stock_concentration=3,
        min_move_quantity=1
    ),
    
    # ... meer policies
}
```

---

## 🧪 Test Cases

### Test 1: Jas Detection
**Input:** "Winterjas gewatteerd zwart"
**Expected:** `ArticleCategory.WINTER_JAS`

### Test 2: Shirt Detection  
**Input:** "Basic T-shirt wit"
**Expected:** `ArticleCategory.SHIRT`

### Test 3: Unknown Fallback
**Input:** "Artikel zonder duidelijke keywords"
**Expected:** `ArticleCategory.UNKNOWN`

### Test 4: Policy Application
**Input:** WINTER_JAS artikel
**Expected:** 
- `preserve_in_more_stores = True`
- `allow_low_quantities = True`
- Strategy gebruikt deze policies

### Test 5: Case Insensitive
**Input:** "WINTERJAS" (uppercase)
**Expected:** Correct WINTER_JAS detectie

---

## 📊 Success Criteria

### Functional
✅ >90% correcte categorie detectie  
✅ Policies worden correct toegepast  
✅ Jassen blijven in meer winkels dan shirts  
✅ Unknown fallback werkt  

### Technical
✅ Type hints en docstrings  
✅ Unit tests >85% coverage  
✅ Configureerbare keyword lists  
✅ Logging van detecties  

### Integration
✅ Strategies gebruiken category policies  
✅ Output verschilt tussen categorieën  
✅ No breaking changes  

---

## 🔗 Dependencies

### Blocked By:
- Fase 2: Strategieën (strategies moeten categorie-aware zijn)

### Blocks:
- Fase 4: Prioritering (gebruikt category modifiers)

---

## 📝 Notes

### Keyword Expansion
De keyword lijst moet uitgebreid worden op basis van:
- User feedback (wrong classifications)
- Analyse van reële artikel omschrijvingen
- Seizoen-specifieke termen

### Future: ML-Based Detection
In plaats van keyword matching kun je later overstappen naar:
- Simple classifier (sklearn)
- Word embeddings
- LLM-based classification

Maar start met keywords - simpel en effectief!

---

**Last Updated:** 2025-11-05  
**Assigned To:** Cline AI  
**Reviewer:** User

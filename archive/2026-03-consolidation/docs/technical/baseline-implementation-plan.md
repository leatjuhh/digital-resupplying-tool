---
title: Baseline Herverdelingsalgoritme - Implementatie Plan
category: technical
tags: [algorithm, baseline, implementation, roadmap]
last_updated: 2025-11-05
version: 1.0
status: in-progress
---

# Baseline Herverdelingsalgoritme - Implementatie Plan

## 🎯 Doel

Transformeer het huidige technisch werkende herverdelingsalgoritme naar een **baseline** die de manuele werkwijze navolgt. Het algoritme moet:

1. Artikelcategorie-specifiek beleid toepassen (bijv. jassen vs shirts)
2. Situatie-gebaseerde strategieën hanteren (veel vs weinig voorraad)
3. Intelligente prioritering op basis van meerdere factoren
4. Iteratief verbeteren via human-in-the-loop feedback

---

## 📊 Gap Analyse: Huidig vs Baseline

### ✅ Wat Het Huidige Algoritme WEL Doet

**Technische Functionaliteit:**
- ✅ Analyseert voorraad en verkoop per winkel/maat
- ✅ Berekent gemiddelden en detecteert overschotten/tekorten
- ✅ Scoort moves op demand, series, en efficiency
- ✅ BV constraint enforcement (geen cross-BV herverdelingen)
- ✅ Maatserie behoud (penalty/bonus systeem)
- ✅ Move consolidation optimalisatie

**Locatie:** `backend/redistribution/`
- `algorithm.py` - Hoofdlogica (greedy per maat)
- `scoring.py` - Demand/series/efficiency scoring
- `optimizer.py` - Move consolidation
- `constraints.py` - Parameters en drempelwaarden
- `domain.py` - Data models
- `bv_config.py` - BV configuratie

### ❌ Wat Er ONTBREEKT voor een Echte Baseline

#### 1. 🔴 Artikelcategorie-Specifiek Beleid (HIGH PRIORITY)
**Manueel:** Jassen worden anders herverdeeld dan T-shirts
- Jassen: meer winkels, lage aantallen (vallen op, duur, manueel bestelbaar)
- Shirts: concentratie in top winkels

**Huidig:** Alle artikelen krijgen dezelfde behandeling

**Impact:** Fundamenteel voor realistische herverdelingen

#### 2. 🔴 Situatie-Gebaseerde Strategieën (HIGH PRIORITY)
**Manueel:**
- **Situatie 1** (40-56+ stuks): Behoud series in zo veel mogelijk winkels
- **Situatie 2** (<20-25 stuks): Concentreer op top X winkels, trek andere leeg

**Huidig:** Gebruikt vaste drempelwaarden zonder situatie-context

**Impact:** Mist de kern van de manuele besluitvorming

#### 3. 🟡 Intelligente Prioritering (MEDIUM PRIORITY)
**Manueel:** Eerst stamgegevens → verkoop → demand per BV → serie-inschatting

**Huidig:** Alleen demand score (verkocht/voorraad ratio)

**Impact:** Basis aanwezig, verbetering mogelijk

#### 4. 🟡 Maat Compensatie Strategie (MEDIUM PRIORITY)
**Manueel:** Bij tekorten compenseer met S/XXL of dubbele toewijzingen

**Huidig:** Geen compensatie mechanisme

**Impact:** Nice-to-have voor optimale verdeling

#### 5. 🟢 Cooldown Periode (LOW PRIORITY - DATA LIMITATIE)
**Manueel:** Wacht 2 weken na initiële levering uit magazijn

**Huidig:** Geen cooldown check (data komt uit PDF, geen timestamp)

**Impact:** Data limitatie, kan later toegevoegd

#### 6. 🔴 Feedback Loop & Iteratie (HIGH PRIORITY)
**Manueel:** Gebruiker leert en past aan

**Huidig:** Geen feedback mechanisme

**Impact:** Essentieel voor "lerende" baseline

---

## 🏗️ Implementatie Roadmap (6 Fases)

### Fase 1: Situatie Classificatie ⭐ CRITICAL PATH
**Doel:** Algoritme detecteert automatisch in welke situatie een artikel zich bevindt

**Tijdsinschatting:** 2-3 dagen

**Bestanden:**
- `backend/redistribution/situation_classifier.py` (NEW)
- `backend/redistribution/constraints.py` (UPDATE)
- `backend/redistribution/algorithm.py` (UPDATE)

**Deliverables:**
- ✅ `StockSituation` enum (HIGH_STOCK, LOW_STOCK, MEDIUM_STOCK, PARTIJ)
- ✅ `SituationThresholds` dataclass
- ✅ `classify_article_situation()` functie
- ✅ Unit tests voor classificatie
- ✅ Documentatie

**Success Criteria:**
- Algoritme kan artikelen correct classificeren
- Thresholds zijn configureerbaar
- Tests passeren met dummy data

**Test Data:** `/dummyinfo/*.pdf` voor verschillende situaties

**Todo:** `todo/baseline-phase-1-situation-classifier.md`

---

### Fase 2: Strategieën Implementatie ⭐ CRITICAL PATH
**Doel:** Implementeer situatie-specifieke herverdelingsstrategieën

**Tijdsinschatting:** 4-5 dagen

**Bestanden:**
- `backend/redistribution/strategies/` (NEW FOLDER)
  - `base.py` - Abstract base class
  - `high_stock.py` - Situatie 1 (veel voorraad)
  - `low_stock.py` - Situatie 2 (weinig voorraad)
  - `partij.py` - Partijgoederen
  - `default.py` - Fallback (huidig greedy)
- `backend/redistribution/algorithm.py` (UPDATE)

**Deliverables:**

#### 2.1 High Stock Strategy
**Focus:** Behoud zoveel mogelijk complete maatseries in veel winkels

**Filosofie:** "Het is de kunst om niet onnodig winkels compleet leeg te halen"
- Goed verkopende winkels worden "beloond" met aanvulling van ontbrekende maten
- Middelmatige winkels behouden hun series waar mogelijk
- Alleen slechtst verkopende winkels (bottom 20%) dienen als bron

**Algoritme:**
1. Inventariseer welke winkels complete series hebben (3-4 breed)
2. Bepaal top 60% priority winkels (op verkoop) - deze krijgen prioriteit
3. Voor priority winkels: vul ontbrekende maten aan uit bottom 20%
4. **Constraint:** Haal bronwinkels NIET volledig leeg (behoud minimaal 1-2 stuks waar mogelijk)
5. Valideer: breekt dit niet teveel series elders?
6. Maximaliseer: aantal winkels met ononderbroken maatseries

#### 2.2 Low Stock Strategy
**Focus:** Concentreer voorraad in top X winkels met complete serie

**Filosofie:** Bij schaarste prioriteit aan best performers
- Focus op "middelste maten" (typisch M, L, XL) voor core serie
- Top X winkels krijgen volledige concentratie
- Andere winkels worden volledig leeggetrokken

**Algoritme:**
1. **Identificeer core sizes:** Detecteer middelste maten (meestal M-L-XL)
   - Voor letter maten: skip eerste/laatste, neem middelste 3
   - Voor numerieke maten: analyseer distributie, neem meest voorkomende midden
2. Tel beschikbare maten: S=3, M=5, L=4, XL=6, XXL=1
3. Bereken: hoeveel complete core series mogelijk? 
   - Min(M=5, L=4, XL=6) = 4 complete M-L-XL series
4. Bepaal top X winkels (op priority score):
   - Als 4 complete series mogelijk → selecteer top 4
   - Check of 5e winkel nog serie kan krijgen met compensatie
5. Trek niet-top winkels **volledig leeg**
6. Distribueer naar top winkels met optimale maat matching

#### 2.3 Partij Strategy
**Focus:** Agressievere herverdeling voor partijgoederen (>56 stuks)

**Context:** Partij aantallen of artikelen met hergebruikte codes uit eerdere jaren
- Vaak grotere hoeveelheden dan normale levering (>70 stuks)
- Minder kritisch om in veel winkels te behouden
- Snellere doorstroming gewenst

**Algoritme:**
- Minder focus op serie behoud (series mogen gebroken worden)
- Meer focus op demand matching (concentreer bij beste verkopers)
- Grotere moves toegestaan (min_move_quantity = 1, max verhoogd)
- Agressievere threshold voor oversupply/undersupply
- Prioriteit: verkoop maximaliseren, niet spreiding

**Success Criteria:**
- Elke strategie genereert verschillende moves
- Output vergelijkbaar met manuele beslissingen
- Tests met reële data succesvol

**Test Data:** `/dummyinfo/*.pdf` voor elke situatie

**Todo:** `todo/baseline-phase-2-strategies.md`

---

### Fase 3: Artikel Categorie System
**Doel:** Detecteer artikelcategorie en pas beleid toe

**Tijdsinschatting:** 2-3 dagen

**Bestanden:**
- `backend/redistribution/article_categories.py` (NEW)
- `backend/redistribution/strategies/*.py` (UPDATE)

**Deliverables:**

#### 3.1 Categorie Definitie
```python
class ArticleCategory(Enum):
    WINTER_JAS = "winter_jas"
    ZOMER_JAS = "zomer_jas"
    BROEK = "broek"
    JURK = "jurk"
    SHIRT = "shirt"
    UNKNOWN = "unknown"

class CategoryPolicy:
    preserve_in_more_stores: bool
    allow_low_quantities: bool
    priority_weight_multiplier: float
    min_items_per_store: int
```

#### 3.2 Categorie Detectie
**Methode:** Tekst analyse van artikel omschrijving (uit PDF)

**Keywords:**
- Jassen: "jas", "jacket", "coat", "winterjas"
- Broeken: "broek", "jeans", "pantalon", "legging"
- Jurken: "jurk", "dress", "maxi", "midi"
- Shirts: "shirt", "top", "blouse", "t-shirt"

**Fallback:** UNKNOWN categorie → gebruik default policy

#### 3.3 Policy Application
- Jassen: `preserve_in_more_stores=True`, `allow_low_quantities=True`
- Shirts: `preserve_in_more_stores=False`, concentratie in top winkels

**Success Criteria:**
- Correcte categorie detectie (>90% accuracy)
- Policies beïnvloeden strategie keuzes
- Configureerbaar via settings
- Logging van detectie beslissingen

**Test Data:** Diverse artikelen in `/dummyinfo/*.pdf`

**Todo:** `todo/baseline-phase-3-categories.md`

---

### Fase 4: Intelligente Prioritering
**Doel:** Multi-factor priority scoring voor betere winkel ranking

**Tijdsinschatting:** 2-3 dagen

**Bestanden:**
- `backend/redistribution/scoring.py` (UPDATE)

**Deliverables:**

#### 4.1 Enhanced Priority Scoring
**Multi-factor formule:**

```python
priority_score = (
    verkoop_ratio * 0.40 +           # Demand score
    absolute_verkoop * 0.25 +        # Top sellers voorkeur
    serie_compleetheid * 0.20 +      # Bijna-complete serie bonus
    categorie_modifier * 0.10 +      # Jassen vs shirts
    bv_relatief * 0.05               # Relatief binnen BV
)
```

**Factoren:**
1. **Verkoop Ratio** - Klassieke demand (verkocht/voorraad)
2. **Absolute Verkoop** - Prioriteit aan best sellers
3. **Serie Compleetheid** - Bonus voor winkels met bijna-complete serie
4. **Categorie Modifier** - Jassen krijgen andere weging
5. **BV Performance** - Relatieve prestatie binnen BV

#### 4.2 BV-Level Ranking
**Per BV:** Rank alle winkels op priority score

**Output:** `{bv_name: [(store_code, priority_score), ...]}`

**Gebruik:** In strategieën voor top-X selectie

**Success Criteria:**
- Priority scores reflecteren manuele prioritering
- BV-level ranking werkend
- Categorie-aware weging
- Tests met edge cases

**Todo:** `todo/baseline-phase-4-priority.md`

---

### Fase 5: Maat Compensatie Mechanisme
**Doel:** Compenseer ontbrekende maten met alternatieven

**Tijdsinschatting:** 1-2 dagen

**Bestanden:**
- `backend/redistribution/size_compensation.py` (NEW)
- `backend/redistribution/strategies/low_stock.py` (UPDATE)

**Deliverables:**

#### 5.1 Compensatie Logica
**Voorkeur volgorde:**
1. Dubbele toewijzing van naburige maat (als qty >1)
2. Buitenliggende maat (S of XXL)
3. Één maat verder

**Voorbeeld:**
- Winkel 5 mist L (al vergeven aan top 4)
- Beschikbaar: S=1, XXL=1, extra M=1
- Compensatie: Geef XXL (buitenliggende maat)

#### 5.2 Gebruik Cases
**Alleen in Low Stock Strategy:**
- Wanneer top-X winkels anders incomplete serie krijgen
- Als alternatieve maten beschikbaar zijn
- Met logging van compensatie beslissing

**Success Criteria:**
- Compensatie verbetert serie compleetheid
- Logging van compensatie beslissingen
- Tests met verschillende scenarios

**Todo:** `todo/baseline-phase-5-compensation.md`

---

### Fase 6: Feedback & Iteratie System
**Doel:** Human-in-the-loop feedback voor iteratieve verbetering

**Tijdsinschatting:** 3-4 dagen

**Bestanden:**
- `backend/db_models.py` (UPDATE - nieuwe tabel)
- `backend/routers/proposals.py` (UPDATE - feedback endpoint)
- `backend/redistribution/feedback_analyzer.py` (NEW)
- `frontend/components/proposals/feedback-form.tsx` (NEW)

**Deliverables:**

#### 6.1 Database Schema
```python
class ProposalFeedback(Base):
    __tablename__ = "proposal_feedback"
    
    id: int
    proposal_id: int (FK)
    user_id: int (FK)
    feedback_type: str  # 'approve', 'reject', 'edit', 'comment'
    feedback_text: str  # Vrije tekst uitleg
    changes_made: JSON  # Bij 'edit': welke wijzigingen
    algorithm_version: str  # Voor tracking
    created_at: DateTime
```

#### 6.2 Feedback API
```python
@router.post("/api/proposals/{id}/feedback")
def submit_feedback(
    proposal_id: int,
    feedback: ProposalFeedbackCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Capture gebruikersfeedback op proposal
    """
```

#### 6.3 Feedback Analysis (Manueel)
**Proces:**
1. Admin bekijkt feedback in dashboard
2. Identificeert patronen (bijv. "jassen altijd te geconcentreerd")
3. Past parameters handmatig aan in configuratie
4. Test nieuwe configuratie met rerun
5. Publiceert als nieuwe versie

**Minimale OpenAI Use:**
- GEEN automatische parameter tuning
- ALLEEN feedback samenvatting (optioneel)
- Focus op human expertise

#### 6.4 Configuratie Versioning
```python
class AlgorithmConfig(Base):
    __tablename__ = "algorithm_configs"
    
    id: int
    version: str  # "1.0", "1.1", etc.
    params: JSON  # Complete RedistributionParams
    category_policies: JSON
    situation_thresholds: JSON
    notes: str
    active: bool
    created_at: DateTime
    created_by: int (FK)
```

**Success Criteria:**
- Feedback wordt opgeslagen in database
- Admin kan feedback reviewen
- Parameter wijzigingen zijn traceerbaar
- Versioning systeem werkend

**Todo:** `todo/baseline-phase-6-feedback.md`

---

## 📁 Nieuwe Bestanden Structuur

```
backend/redistribution/
├── __init__.py                      # BESTAAND
├── algorithm.py                     # UPDATE (strategy pattern)
├── constraints.py                   # UPDATE (nieuwe thresholds)
├── domain.py                        # BESTAAND
├── scoring.py                       # UPDATE (enhanced scoring)
├── optimizer.py                     # BESTAAND
├── bv_config.py                     # BESTAAND
│
├── situation_classifier.py          # NIEUW - Fase 1
├── article_categories.py            # NIEUW - Fase 3
├── size_compensation.py             # NIEUW - Fase 5
├── feedback_analyzer.py             # NIEUW - Fase 6
│
└── strategies/                      # NIEUW - Fase 2
    ├── __init__.py
    ├── base.py                      # Abstract base class
    ├── high_stock.py                # Situatie 1
    ├── low_stock.py                 # Situatie 2
    ├── partij.py                    # Partijgoederen
    └── default.py                   # Fallback (huidig greedy)
```

---

## 🎯 Success Criteria Per Versie

### Baseline V1.0 (Na Fase 1-2) ⭐ MVP
**Target:** 2 weken

✅ Algoritme detecteert situaties correct  
✅ High Stock: behoudt series in veel winkels  
✅ Low Stock: concentreert op top-X  
✅ Output vergelijkbaar met manuele beslissingen  
✅ Tests met reële data succesvol  

### Baseline V2.0 (Na Fase 3-4)
**Target:** +1 week

✅ Jassen worden anders behandeld dan shirts  
✅ Priority scoring multi-factor  
✅ Categorie beleid configureerbaar  
✅ Documentatie compleet  

### Baseline V3.0 (Na Fase 5-6)
**Target:** +1 week

✅ Maat compensatie werkend  
✅ Feedback capture operationeel  
✅ Configuratie versioning  
✅ Iteratieve verbetering framework  

**Totaal:** ~4 weken voor volledige baseline

---

## 🧪 Test Strategie

### Fase 1-2: Situatie & Strategieën
**Test Data:** `/dummyinfo/*.pdf`

**Test Cases:**
1. **High Stock Scenario** - Artikel met 40-56 stuks
   - Verify: Series behouden in meerdere winkels
   - Verify: Alleen bottom winkels leveren aan top winkels

2. **Low Stock Scenario** - Artikel met <25 stuks
   - Verify: Concentratie in top X winkels
   - Verify: Andere winkels worden leeggetrokken
   - Verify: Complete middelste serie in top winkels

3. **Partij Scenario** - Artikel met >56 stuks
   - Verify: Agressievere herverdeling
   - Verify: Grotere moves

### Fase 3: Categorieën
**Test Cases:**
1. Jas artikel - Verify: meer winkels, lage aantallen
2. Shirt artikel - Verify: concentratie in top winkels
3. Unknown categorie - Verify: default policy

### Fase 4: Prioritering
**Test Cases:**
1. Verify: Top sellers krijgen hogere priority
2. Verify: BV-level ranking correct
3. Verify: Categorie modifier werkt

### Fase 5: Compensatie
**Test Cases:**
1. Verify: Dubbele toewijzing bij voldoende qty
2. Verify: Buitenliggende maat als fallback
3. Verify: Logging van compensatie

### Fase 6: Feedback
**Test Cases:**
1. Verify: Feedback wordt opgeslagen
2. Verify: Admin kan reviewen
3. Verify: Parameter wijzigingen traceerbaar

---

## 📝 Documentatie Updates

### Tijdens Implementatie
- ✅ Update `docs/technical/baseline-implementation-plan.md` (dit bestand)
- ✅ Update `docs/guides/redistribution-algorithm.md` met baseline details
- ✅ Update `CHANGELOG.md` per fase
- ✅ Session logs in `docs/sessions/YYYY-MM-DD.md`

### Na Voltooiing
- ✅ Complete technical reference in `docs/technical/`
- ✅ User guide update in `docs/guides/`
- ✅ README.md update met baseline features

---

## 🔄 Iteratie Proces

### Per Fase:
1. **Plan** - Todo item maken, design documenten
2. **Implement** - Code schrijven, tests maken
3. **Test** - Met dummy data uit `/dummyinfo/`
4. **Review** - User test met reële data
5. **Refine** - Aanpassingen op basis van feedback
6. **Document** - Update docs, session logs
7. **Next** - Volgende fase

### Tussen Fases:
- Git commit met duidelijke message
- CHANGELOG.md update
- Demo aan user (optioneel)
- Go/no-go beslissing voor volgende fase

---

## 🚀 Volgende Stappen

### Immediate (Vandaag/Morgen)
1. ✅ Maak todo items voor alle 6 fases
2. 🔄 Start Fase 1: Situatie Classificatie
   - Implementeer `situation_classifier.py`
   - Update `constraints.py`
   - Schrijf unit tests
   - Test met dummy data

### Short Term (Deze Week)
3. Fase 2: Strategieën Implementation
4. Test beide fases samen
5. Demo aan user

### Medium Term (Volgende 2 Weken)
6. Fase 3: Categorieën
7. Fase 4: Prioritering
8. Test V2.0 met user

### Long Term (Week 4)
9. Fase 5: Compensatie
10. Fase 6: Feedback
11. Test complete V3.0
12. Production release

---

## 📊 Progress Tracking

Gebruik todo items in `/todo/` voor gedetailleerde tracking:
- `baseline-phase-1-situation-classifier.md`
- `baseline-phase-2-strategies.md`
- `baseline-phase-3-categories.md`
- `baseline-phase-4-priority.md`
- `baseline-phase-5-compensation.md`
- `baseline-phase-6-feedback.md`

Update dit plan document regelmatig met:
- ✅ Completed milestones
- 🔄 In progress items
- ⏸️ Blocked items
- 📝 Lessons learned

---

## 💡 Design Principles

### Code Quality
- Type hints verplicht
- Docstrings voor alle functies
- Unit tests met >80% coverage
- Clear variable naming

### Architecture
- Modulair design (strategies pattern)
- Configureerbaar via parameters
- Backwards compatible waar mogelijk
- Clear separation of concerns

### Documentation
- Inline comments voor complexe logica
- README per module folder
- API documentation
- User-facing guides

### Testing
- Test met reële data (`/dummyinfo/`)
- Edge case coverage
- Integration tests tussen modules
- Performance benchmarks

### Manuele Werkwijze als Leidraad
"Er is niet één goede oplossing, er zijn er veel. Maar er is altijd maar één de beste!"
- Algoritme moet iteratief verbeteren via feedback
- Manuele expertise is leidend, niet technische optimalisatie
- Focus op praktische bruikbaarheid, niet theoretische perfectie
- Continuous learning via human-in-the-loop

---

## 📊 KPI's & Evaluatiecriteria

### Per Situatie Type

**High Stock (40-56 stuks):**
1. **Serie Behoud** - % winkels met ononderbroken maatserie (target: >70%)
2. **Spreiding** - Aantal winkels met voorraad (target: maximaal behoud)
3. **Top Winkel Compleetheid** - % top 60% winkels met complete serie
4. **Minimale Leegtrekking** - Aantal volledig leeggetrokken winkels (target: minimaal)

**Low Stock (<25 stuks):**
1. **Concentratie Effectiviteit** - % top-X winkels met complete core serie (target: 100%)
2. **Middelste Maten Focus** - % core maten (M-L-XL) correct gealloceerd
3. **Compensatie Success** - % gevallen waar compensatie succesvol toegepast
4. **Leegtrekking Efficiency** - % niet-top winkels volledig leeggetrokken

**Partij (>56 stuks):**
1. **Demand Match** - Correlatie tussen voorraad en verkoopcijfers
2. **Doorstroming** - Snelheid waarmee voorraad naar top performers gaat
3. **Volume Efficiency** - Gemiddelde move size (grotere moves = beter)

**Algemeen (alle situaties):**
1. **BV Compliance** - % moves binnen BV grenzen (target: 100%)
2. **Move Quality** - Gemiddelde move score (target: >0.6)
3. **User Approval Rate** - % proposals goedgekeurd door gebruiker
4. **Manual Similarity** - Gelijkenis met manuele herverdelingen (expert beoordeling)

### Operationele Constraints (Te Determineren)

**Tijdens iteratie te verfijnen:**
- Maximaal aantal moves per winkel per batch
- Minimale restvoorraad per winkel
- Maximale afstand voor herverdeling (logistiek)
- Minimale move grootte (efficiency)
- Cooldown periode implementatie (als data beschikbaar)

---

## 🎓 Lessons Learned (Update Tijdens Project)

### Fase 1:
- TBD

### Fase 2:
- TBD

### Fase 3:
- TBD

### Fase 4:
- TBD

### Fase 5:
- TBD

### Fase 6:
- TBD

---

**Last Updated:** 2025-11-05  
**Version:** 1.0  
**Status:** Planning Complete, Ready for Implementation

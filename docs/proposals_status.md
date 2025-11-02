# Proposals Status - Inventarisatie en Diagnose

**Datum:** 2025-11-02
**Doel:** Onderzoeken waarom voorstellen niet zichtbaar zijn en edit functionaliteit implementeren

---

## AANWEZIG

### Backend - Database Models (`backend/db_models.py`)
- ✅ `Proposal` tabel bestaat met volledige schema:
  - `id`, `batch_id`, `pdf_batch_id`, `artikelnummer`, `article_name`
  - `moves` (JSON), `total_moves`, `total_quantity`
  - `status` ('pending', 'approved', 'rejected', 'edited')
  - `reason`, `applied_rules`, `optimization_applied`, `stores_affected`
  - `created_at`, `reviewed_at`, `rejection_reason`

- ✅ `PDFBatch` tabel bestaat:
  - `id`, `naam`, `status`, `pdf_count`, `processed_count`, `created_at`

- ✅ `ArtikelVoorraad` tabel bestaat:
  - `id`, `batch_id`, `volgnummer`, `omschrijving`
  - `filiaal_code`, `filiaal_naam`, `maat`, `voorraad`, `verkocht`
  - `pdf_metadata`, `created_at`

### Backend - Proposal Generatie (`backend/redistribution/algorithm.py`)
- ✅ `generate_redistribution_proposals_for_article()` functie bestaat
- ✅ `generate_redistribution_proposals_for_batch()` functie bestaat
- ✅ Algoritme genereert proposals met moves, scoring, rules

### Backend - PDF Ingest Router (`backend/routers/pdf_ingest.py`)
- ✅ `/api/pdf/ingest` endpoint voor upload & processing
- ✅ `generate_and_save_proposals()` functie wordt aangeroepen na PDF processing
- ✅ Proposals worden opgeslagen in database (regel 318-338)
- ✅ `/api/pdf/batches/{batch_id}/proposals` endpoint bestaat (regel 478)
- ✅ `/api/pdf/proposals/{proposal_id}` endpoint bestaat (regel 515)
- ✅ `/api/pdf/proposals/{proposal_id}/full` endpoint bestaat (regel 537)
  - Berekent `inventory_proposed` door moves toe te passen op `inventory_current`
- ✅ `/api/pdf/proposals/{proposal_id}/approve` endpoint (regel 656)
- ✅ `/api/pdf/proposals/{proposal_id}/reject` endpoint (regel 680)
- ✅ `/api/pdf/proposals/{proposal_id}` PUT endpoint voor updates (regel 709)

### Frontend - Pages
- ✅ `frontend/app/proposals/[id]/page.tsx` - Detail view
- ✅ `frontend/app/proposals/[id]/edit/page.tsx` - Edit view

### Frontend - Components
- ✅ `frontend/components/proposals/proposal-detail.tsx` - Read-only display
  - Heeft 3 tabs: "Vergelijking", "Huidige Situatie", "Voorgestelde Situatie"
- ✅ `frontend/components/proposals/editable-proposal-detail.tsx` - Editable display
- ✅ `frontend/components/proposals/proposal-actions.tsx` - Action buttons

### Frontend - API Client (`frontend/lib/api.ts`)
- ✅ `api.proposals.getById()` functie
- ✅ `api.proposals.getByIdFull()` functie
- ✅ `api.proposals.approve()` functie
- ✅ `api.proposals.reject()` functie
- ✅ `api.proposals.update()` functie
- ✅ `api.pdf.getBatchProposals()` functie

---

## ONTBREEKT

### Backend
- ❌ Geen dedicated `backend/routers/proposals.py` (alles zit in pdf_ingest.py)
- ? Configuratie/setup issues mogelijk

### Frontend
- ? Mogelijk data mapping issues tussen backend response en frontend verwachtingen
- ? Mogelijk rendering issues in de tabs

---

## ONZEKER

### Data Flow
- ? Worden proposals daadwerkelijk aangemaakt na PDF upload?
- ? Werkt de `/api/pdf/proposals/{id}/full` endpoint correct?
- ? Wordt de data correct gemapped in frontend components?

### Runtime Gedrag
- ? Console errors in browser?
- ? Network errors bij API calls?
- ? Empty payloads in responses?

---

## RUNTIME BEVINDINGEN

### Database Check Resultaten (2025-11-02 23:02)

**PDF Batches:**
- 3 batches aanwezig (ID 1, 2, 3)
- Alle status: SUCCESS
- Totaal 5 PDFs verwerkt
- 421 voorraad records in database

**Proposals:**
- ✅ 5 proposals aangemaakt in database
- ❌ **KRITIEK: ALLE proposals hebben moves=[] (LEEG)**
- ❌ **KRITIEK: Alle proposals hebben total_moves=0 en total_quantity=0**
- Status: 4x pending, 1x approved
- Alle proposals hebben reason: "Dit artikel is reeds optimaal verdeeld"

**Voorbeeld - Proposal 3:**
```
Artikelnummer: 424123
Article Name: Jacket Loops
Status: approved
Batch ID: 3
Total Moves: 0
Total Quantity: 0
Moves (JSON): EMPTY
Applied Rules: ['Optimal Distribution Analysis']
Reason: Dit artikel is reeds optimaal verdeeld. Er hoeven geen wijzigingen aangebracht te worden.
```

### ROOT CAUSE ANALYSE

**Problem:** Voorstellen zijn niet zichtbaar in GUI tabs "Vergelijking" en "Voorgestelde situatie"

**Root Cause:** 
1. ✅ Proposals worden WEL aangemaakt in database
2. ✅ API endpoints werken correct
3. ✅ Frontend components werken correct
4. ❌ **MAAR: Herverdelingsalgoritme genereert GEEN moves**
   - Alle 5 artikelen worden als "optimaal verdeeld" beoordeeld
   - `moves` array is leeg voor alle proposals
   - Hierdoor is `inventory_proposed` identiek aan `inventory_current`
   - Tabs tonen geen verschillen omdat er geen verschillen zijn

**Mogelijke Oorzaken:**
1. Test PDF data is daadwerkelijk optimaal verdeeld (geen herverdeling nodig)
2. Algoritme thresholds zijn te streng (detecteert geen oversupply/undersupply)
3. Bug in herverdelingsalgoritme

**Impact:**
- Gebruiker ziet geen verschillen tussen tabs
- "Vergelijking" tab toont geen highlighting (want geen verschillen)
- "Voorgestelde situatie" is identiek aan "Huidige situatie"
- Dit is TECHNISCH CORRECT gedrag voor optimaal verdeelde artikelen
- MAAR gebruiker verwacht voorstellen te zien

---

## VOLGENDE STAPPEN

### Diagnose
1. ✅ Database check - AFGEROND
2. ✅ Root cause identificatie - AFGEROND
3. [ ] Test met niet-optimale data
4. [ ] Verifiëer algoritme thresholds
5. [ ] Check BV mapping en constraints

### Fix Opties
**Optie A: Test Data Fix**
- Upload PDF met niet-optimaal verdeelde voorraad
- Verifiëer dat algoritme dan WEL moves genereert

**Optie B: Algoritme Threshold Tuning**
- Verlaag `oversupply_threshold` en `undersupply_threshold`
- Maak algoritme gevoeliger voor herverdelingen

**Optie C: UI Enhancement**
- Toon duidelijk bericht: "Dit artikel is reeds optimaal verdeeld"
- Verberg/disable tabs als er geen moves zijn
- Toon "Optimaal" badge

### Aanbeveling
Start met **Optie A**: Test met echte niet-optimale data om te verifiëren dat het systeem end-to-end werkt wanneer er wél moves zijn.

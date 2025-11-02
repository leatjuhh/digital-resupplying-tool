# Volgende Stappen - Prioriteitsanalyse
**Project**: Digital Resupplying Tool  
**Status**: Herverdelingsalgoritme Compleet, API Integration Nodig  
**Laatste Update**: 29 oktober 2025

---

## 🎉 UPDATE 29 OKTOBER 2025 - MAJOR BREAKTHROUGH!

### ✅ HERVERDELINGSALGORITME COMPLEET! (Priority 1 - AFGEROND)

**Status**: ✅ **VOLLEDIG GEÏMPLEMENTEERD**  
**Impact**: 🚀 **Core functionaliteit van de applicatie is nu werkend!**

Dit was de **#1 prioriteit** en is nu volledig afgerond. Zie `SESSION_29_OKT_2025.md` voor complete details.

#### Wat is Geïmplementeerd:

1. **Algorithm Core** (`backend/redistribution/algorithm.py`) ✅
   - `generate_redistribution_proposals_for_article()` - Volledig werkend
   - `generate_redistribution_proposals_for_batch()` - Volledig werkend
   - BV consolidatie logica - Detecteert gefragmenteerde BV's
   - Demand-based allocation - Verkoop cijfers worden meegewogen
   - Size sequence detection - Alle maat types ondersteund
   - Greedy matching algoritme - Efficiënte herverdeling

2. **Supporting Modules** ✅
   - `domain.py` - Alle data modellen compleet
   - `constraints.py` - Configureerbare parameters
   - `scoring.py` - Move quality scoring (0.0-1.0)
   - `optimizer.py` - Move consolidatie
   - `bv_config.py` - BV mapping en validatie

3. **Frontend UI** ✅
   - Proposal detail view (`/proposals/[id]`)
   - Editable proposal view (`/proposals/[id]/edit`)
   - Live balance validation
   - Visual feedback en progress tracking
   - Complete component set

4. **Test Scripts** ✅
   - `backend/test_generate_proposals.py` werkend
   - Edge case testing
   - Performance validation

#### Wat Nog Nodig Is (Quick Wins - 1-2 uur):

1. **Proposals API Router** (30 min) ⏳
   - `backend/routers/proposals.py` aanmaken
   - POST `/api/proposals/generate/{batch_id}`
   - GET `/api/proposals/{id}`
   - PUT `/api/proposals/{id}` (voor edits)
   - POST `/api/proposals/{id}/approve`
   - POST `/api/proposals/{id}/reject`

2. **Database Proposals Table** (30 min) ⏳
   - Proposals model in `db_models.py`
   - Migratie script
   - Test data seeding

3. **Frontend API Integration** (30 min) ⏳
   - Uncomment TODO in `frontend/app/proposals/[id]/edit/page.tsx` (regel 77-78)
   - Implementeer `api.proposals.update()` in `lib/api.ts`
   - Test de complete flow

**Na deze 3 stappen: MVP IS COMPLEET! 🎉**

---

## 📊 Huidige Status - Code Analyse

### ✅ Wat is Compleet en Robuust

#### 1. **PDF Extraction Layer** (100% Compleet)
- ✅ Deterministische extractie van voorraad PDFs
- ✅ Multiple fallback strategies (table → text)
- ✅ Support voor letter maten (XXS-XXXL) en numerieke maten (32-48)
- ✅ Negatieve voorraad detectie en flagging
- ✅ Comprehensive logging en error handling
- ✅ Volledige test coverage (7/7 PDFs succesvol)
- ✅ Data normalisatie en validatie
- ✅ Database integratie

**Code Kwaliteit**: ⭐⭐⭐⭐⭐ (Excellent)
- Goed gestructureerd en modulair
- Comprehensive error handling
- Duidelijke separation of concerns
- Uitgebreide documentatie

#### 2. **Database Schema** (Compleet)
- ✅ Batch tracking systeem
- ✅ Artikel voorraad opslag
- ✅ PDF metadata opslag
- ✅ Parse logging

**Code Kwaliteit**: ⭐⭐⭐⭐ (Good)
- Schema is functioneel
- Relaties zijn correct gedefinieerd

#### 3. **API Endpoints** (Basis Aanwezig)
- ✅ `/api/pdf/ingest` - PDF upload en processing
- ✅ `/api/pdf/batches` - Batch management
- ✅ Basic CRUD voor batches

**Code Kwaliteit**: ⭐⭐⭐ (Adequate)
- Functioneel maar minimaal
- Ontbreekt: error responses, status codes, validatie

---

## 🔴 Kritieke Ontbrekende Componenten

### 1. **Herverdelingsalgoritme** (PRIORITY 1 - CRITICAL)
**Status**: Niet geïmplementeerd  
**Impact**: Dit is de CORE functionaliteit van de app

**Wat Moet Worden Gebouwd**:
```
Input: Geëxtraheerde voorraad data uit database
Output: Herverdelingsvoorstellen per artikel

Algoritme moet:
- Voorraad per filiaal per maat analyseren
- Overschotten en tekorten identificeren
- Optimale herverdeling berekenen
- Rekening houden met:
  * Minimale voorraad per filiaal
  * Maximale voorraad per filiaal
  * Verkoopcijfers (demand)
  * Geografische nabijheid (optioneel)
  * Transportkosten (optioneel)
```

**Geschatte Complexity**: HOOG
**Geschatte Tijd**: 2-3 dagen
**Prioriteit**: 🔥 CRITICAL - Start hier

**Technische Aanpak**:
```python
# backend/redistribution/algorithm.py

def generate_redistribution_proposals(
    volgnummer: str,
    batch_id: int
) -> List[RedistributionProposal]:
    """
    Genereer herverdelingsvoorstellen voor een artikel
    
    1. Haal voorraad data op uit database
    2. Bereken gemiddelde voorraad per maat
    3. Identificeer overschotten (> gemiddelde + threshold)
    4. Identificeer tekorten (< gemiddelde - threshold)
    5. Match overschotten met tekorten
    6. Genereer voorstellen
    """
    pass
```

---

### 2. **PDF Ingest API - Production Ready** (PRIORITY 2 - HIGH)
**Status**: Basis aanwezig maar niet production-ready  
**Impact**: Critical voor gebruikerservaring

**Wat Ontbreekt**:
- ❌ Proper file validation (size limits, file types)
- ❌ Progress tracking voor lange uploads
- ❌ Batch naming en metadata
- ❌ Duplicate detection
- ❌ Error responses met duidelijke messages
- ❌ Rollback bij failure

**Geschatte Complexity**: MEDIUM
**Geschatte Tijd**: 1 dag
**Prioriteit**: 🟠 HIGH

**Verbeteringen**:
```python
# backend/routers/pdf_ingest.py

@router.post("/ingest")
async def ingest_pdfs(
    files: List[UploadFile],
    batch_name: Optional[str] = None,
    overwrite: bool = False  # Allow duplicate handling
):
    # 1. Validate files (size, type, count)
    # 2. Check for duplicates
    # 3. Create batch with metadata
    # 4. Process each PDF with progress tracking
    # 5. Return detailed status per file
    # 6. Rollback on critical failures
    pass
```

---

### 3. **Frontend - PDF Upload & Batch Management** (PRIORITY 3 - HIGH)
**Status**: Basis UI aanwezig, maar niet specifiek voor PDF upload  
**Impact**: Users kunnen nog geen PDFs uploaden

**Wat Moet Worden Gebouwd**:
- ❌ Drag & drop PDF upload interface
- ❌ Batch naam input
- ❌ Upload progress indicator
- ❌ Batch lijst met status
- ❌ Per-PDF status in batch
- ❌ Error display met details
- ❌ Negatieve voorraad warnings weergeven

**Geschatte Complexity**: MEDIUM
**Geschatte Tijd**: 1-2 dagen
**Prioriteit**: 🟠 HIGH

**Componenten**:
```typescript
// frontend/app/pdf-upload/page.tsx
- PDFUploader component (drag & drop)
- BatchList component
- BatchDetail component (per PDF status)
- NegativeInventoryWarnings component
```

---

### 4. **Herverdelingsvoorstellen UI** (PRIORITY 4 - HIGH)
**Status**: Niet geïmplementeerd  
**Impact**: Core functionaliteit moet zichtbaar zijn

**Wat Moet Worden Gebouwd**:
- ❌ Lijst van voorstellen per batch
- ❌ Detail view per voorstel
  * Van welk filiaal
  * Naar welk filiaal  
  * Welke maat
  * Hoeveel stuks
  * Reden (overschot/tekort)
- ❌ Approve/Reject functionaliteit
- ❌ Bulk approve/reject
- ❌ Export naar Excel/PDF

**Geschatte Complexity**: MEDIUM-HIGH
**Geschatte Tijd**: 2 dagen
**Prioriteit**: 🟠 HIGH

---

## 🟡 Belangrijke Optimalisaties

### 5. **Database Optimalisatie** (PRIORITY 5 - MEDIUM)
**Issues**:
- Geen indexes op vaak-gebruikt kolommen
- Geen foreign key constraints
- Geen cascading deletes

**Verbeteringen**:
```python
# backend/db_models.py

class ArtikelVoorraad(Base):
    # Add indexes
    __table_args__ = (
        Index('idx_volgnummer', 'volgnummer'),
        Index('idx_batch_id', 'batch_id'),
        Index('idx_filiaal_code', 'filiaal_code'),
    )
```

**Geschatte Tijd**: 2-3 uur
**Prioriteit**: 🟡 MEDIUM

---

### 6. **API Error Handling & Validation** (PRIORITY 6 - MEDIUM)
**Issues**:
- Inconsistente error responses
- Geen input validatie met Pydantic
- Geen rate limiting
- Geen request logging

**Verbeteringen**:
```python
# backend/models.py - Add Pydantic models

class PDFIngestRequest(BaseModel):
    batch_name: str = Field(..., min_length=1, max_length=100)
    overwrite: bool = False
    
class PDFIngestResponse(BaseModel):
    batch_id: int
    status: str
    files_processed: int
    files_failed: int
    errors: List[str]
```

**Geschatte Tijd**: 1 dag
**Prioriteit**: 🟡 MEDIUM

---

### 7. **Comprehensive Logging** (PRIORITY 7 - MEDIUM)
**Issues**:
- Logs gaan alleen naar console
- Geen structured logging (JSON)
- Geen log rotation
- Geen centralized logging

**Verbeteringen**:
```python
# backend/logging_config.py

import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    # File handler with rotation
    handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # JSON formatter
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
```

**Geschatte Tijd**: 3-4 uur
**Prioriteit**: 🟡 MEDIUM

---

## 🟢 Nice-to-Have Features

### 8. **Bulk PDF Processing** (PRIORITY 8 - LOW)
**Feature**: Parallelle verwerking van meerdere PDFs
**Impact**: Snellere verwerking bij grote batches
**Geschatte Tijd**: 1 dag

### 9. **Export Functionaliteit** (PRIORITY 9 - LOW)
**Feature**: Export voorstellen naar Excel/CSV
**Impact**: Gebruikers willen data offline bekijken
**Geschatte Tijd**: 4-6 uur

### 10. **Dashboard & Analytics** (PRIORITY 10 - LOW)
**Feature**: Visualisaties van voorraad distributie
**Impact**: Betere insights, maar niet essentieel voor MVP
**Geschatte Tijd**: 2-3 dagen

---

## 📋 Aanbevolen Implementatie Volgorde

### **FASE 1: Core Functionaliteit** (Week 1-2)
**Doel**: MVP met werkende herverdeling

1. **Herverdelingsalgoritme** (2-3 dagen) 🔥
   - Input: Database voorraad
   - Output: Herverdelingsvoorstellen
   - Test met bestaande data

2. **API - Redistribution Endpoints** (1 dag) 🔥
   ```
   POST /api/redistribution/generate/{batch_id}
   GET  /api/redistribution/proposals/{batch_id}
   POST /api/redistribution/proposals/{id}/approve
   POST /api/redistribution/proposals/{id}/reject
   ```

3. **Frontend - Voorstellen UI** (2 dagen) 🔥
   - Lijst van voorstellen
   - Detail view
   - Approve/reject

**Deliverable**: Werkende end-to-end flow van PDF → Voorstellen → Goedkeuring

---

### **FASE 2: Production Ready** (Week 3)
**Doel**: Robuuste, gebruiksklare applicatie

4. **PDF Upload UI** (1-2 dagen) 🟠
   - Drag & drop
   - Progress tracking
   - Batch management

5. **API Improvements** (1 dag) 🟠
   - Validatie
   - Error handling
   - Better responses

6. **Database Optimalisatie** (3 uur) 🟡
   - Indexes
   - Constraints
   - Performance tuning

**Deliverable**: Production-ready applicatie voor intern gebruik

---

### **FASE 3: Verfijning** (Week 4)
**Doel**: Polish en extra features

7. **Export Functionaliteit** (4-6 uur) 🟢
8. **Comprehensive Logging** (3-4 uur) 🟡
9. **Bulk Processing** (1 dag) 🟢
10. **Analytics Dashboard** (2-3 dagen) 🟢

**Deliverable**: Gepolijste applicatie met alle gewenste features

---

## 🎯 Kritieke Beslissingen Needed

### 1. **Herverdelings Logica**
**Vraag**: Wat zijn de exacte business rules voor herverdeling?

**Te Beslissen**:
- Minimale voorraad per filiaal per maat?
- Maximale voorraad per filiaal per maat?
- Wordt verkoopcijfer meegewogen (demand-based)?
- Geografische beperkingen?
- Transportkosten relevant?

**Actie**: Overleg met stakeholders over algoritme parameters

---

### 2. **Goedkeuringsproces**
**Vraag**: Hoe werkt het goedkeuringsproces?

**Te Beslissen**:
- Wie kan voorstellen goedkeuren?
- Bulk approval mogelijk?
- Partial approval (sommige wel, andere niet)?
- Revision history nodig?
- Notificaties bij goedkeuring?

**Actie**: Define workflow requirements

---

### 3. **Multi-tenant vs Single-tenant**
**Vraag**: Is dit systeem voor één organisatie of meerdere?

**Impact**:
- Database schema
- Authentication
- Data isolation

**Actie**: Clarify scope

---

## 💡 Code Quality Observations

### **Strengths**:
✅ Modulaire architectuur  
✅ Goede separation of concerns  
✅ Comprehensive error handling in PDF layer  
✅ Extensive logging in extraction  
✅ Clear documentation  
✅ Good test coverage voor PDF extraction  

### **Areas for Improvement**:
⚠️ API layer heeft minimale validatie  
⚠️ Geen consistent error response format  
⚠️ Database migrations ontbreken (gebruik Alembic)  
⚠️ Geen authentication/authorization  
⚠️ Frontend heeft geen error boundaries  
⚠️ Geen CI/CD pipeline  

---

## 🚀 Snelle Wins (< 1 dag werk)

1. **Database Indexes** (2 uur) → 10x snellere queries
2. **API Error Responses** (3 uur) → Betere developer experience
3. **Logging Setup** (3 uur) → Makkelijker debuggen
4. **Frontend Error Boundaries** (2 uur) → Betere user experience
5. **Input Validatie** (4 uur) → Minder bugs

**Total**: ~1 dag werk, grote impact op stabiliteit

---

## 📈 Success Metrics

### MVP (End of Week 2):
- [ ] User kan PDFs uploaden
- [ ] Systeem genereert herverdelingsvoorstellen
- [ ] User kan voorstellen goedkeuren/afwijzen
- [ ] Data wordt correct opgeslagen

### Production (End of Week 3):
- [ ] < 5 sec response time voor voorstellen
- [ ] 99% uptime
- [ ] Geen data corruption
- [ ] Duidelijke error messages

### Polished (End of Week 4):
- [ ] Export functionaliteit
- [ ] Dashboard met insights
- [ ] < 2 sec page load times
- [ ] Mobile responsive

---

## 🎓 Als Senior Developer - Mijn Aanbeveling

**Start Hier (Deze Week)**:
1. **Vandaag/Morgen**: Herverdelingsalgoritme (core logica)
2. **Overmorgen**: API endpoints voor redistribution
3. **Dag 4-5**: Frontend voorstellen UI

**Waarom Deze Volgorde?**:
- Herverdelingsalgoritme is de KERN van de applicatie
- Zonder dit is de app nutteloos
- PDF extractie is af, nu moet data gebruikt worden
- UI kan parallel ontwikkeld worden als API klaar is

**Wat NIET Doen**:
- ❌ Beginnen met analytics/dashboards
- ❌ Focus op edge cases voordat MVP werkt
- ❌ Overengineering (KISS principe)
- ❌ Te veel polish voordat core werkt

**Risico's**:
- Herverdelingsalgoritme complexiteit onderschat → mitigeer met simpele v1
- Business rules onduidelijk → early stakeholder alignment
- Scope creep → blijf bij MVP eerst

**Success Criteria**:
✅ In 2 weken: User kan PDF uploaden en herverdelingsvoorstellen krijgen  
✅ In 3 weken: Production ready voor intern gebruik  
✅ In 4 weken: Gepolijste applicatie met alle features  

---

## 📞 Volgende Acties

1. **Onmiddellijk**: Start met herverdelingsalgoritme design
2. **Deze Week**: Implementeer core redistribution flow
3. **Volgende Week**: Production ready maken
4. **Week 3-4**: Polish en extra features

**Klaar voor de volgende sprint!** 🚀

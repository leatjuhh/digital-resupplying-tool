# Dummy Data Audit - Digital Resupplying Tool

**Laatst geupdate:** 29 oktober 2025  
**Status:** In behandeling - Vervanging naar echte data in uitvoering

Dit document bevat een complete inventarisatie van alle locaties in de frontend waar dummy/placeholder data wordt gebruikt in plaats van echte database-gekoppelde data.

---

## 📊 DASHBOARD COMPONENTEN

### 1. `frontend/components/dashboard/dashboard-stats.tsx`
**Status:** 🔴 HARDCODED DUMMY DATA

**Huidige situatie:**
```typescript
const stats = {
  totaalVoorstellen: { waarde: 142, verandering: 12, positief: true },
  inBehandeling: { waarde: 24, verandering: 7, positief: true },
  afgekeurd: { waarde: 18, percentage: 5, verandering: -2, positief: false },
  actieveWinkels: { waarde: 32, verandering: 2, positief: true }
}
```

**Vereiste wijzigingen:**
- [ ] Nieuwe backend endpoint maken: `GET /api/dashboard/stats`
- [ ] Component updaten met `useEffect` + API call
- [ ] Loading state toevoegen
- [ ] Error handling toevoegen
- [ ] Periode filter integreren

**Backend data source:**
- Database: `PDFBatch`, `Proposal`, `ArtikelVoorraad` tabellen
- Berekeningen: Count aggregaties op basis van status en datum filters

---

### 2. `frontend/components/dashboard/pending-proposals.tsx`
**Status:** 🔴 HARDCODED DUMMY DATA

**Huidige situatie:**
```typescript
const proposalSeries = [
  { id: "2025032301", title: "Herverdeling voor week 12 2025", date: "24 maart 2025", 
    totalProposals: 42, assessedProposals: 12, nextProposalId: "423264" },
  { id: "2025031501", title: "Herverdeling voor week 11 2025", ... },
  { id: "2025030201", title: "Restpartijen week 9 2025", ... },
  { id: "2025021501", title: "Herverdeling voor week 7 2025", ... }
]
```

**Vereiste wijzigingen:**
- [x] API endpoint bestaat al: `api.pdf.getBatches()`
- [ ] Component updaten om API te gebruiken
- [ ] Voor elke batch: `api.pdf.getBatchProposals(batchId)` om status te krijgen
- [ ] Loading state toevoegen
- [ ] Empty state toevoegen (geen wachtende reeksen)

**Backend data source:**
- API: `/api/pdf/batches` (bestaat al)
- API: `/api/pdf/batches/{id}/proposals` (bestaat al)
- Database: `PDFBatch` en `Proposal` tabellen

---

### 3. `frontend/components/dashboard/recent-activity.tsx`
**Status:** 🔴 HARDCODED DUMMY DATA + PLACEHOLDER IMAGES

**Huidige situatie:**
```typescript
const activities = [
  { id: 1, user: { name: "Marieke", initials: "MV", image: "/placeholder-user.jpg" },
    action: "heeft een voorstel goedgekeurd", time: "2 minuten geleden", 
    proposal: "Voorstel #1234" },
  { id: 2, user: { name: "Jan", ... }, ... },
  { id: 3, user: { name: "Sophie", ... }, ... },
  { id: 4, user: { name: "Thomas", ... }, ... }
]
```

**Placeholder images:**
- `/placeholder-user.jpg` - Gebruikt voor alle gebruikers

**Vereiste wijzigingen:**
- [ ] Nieuwe backend endpoint: `GET /api/activity/recent?limit=10`
- [ ] User management systeem toevoegen (of anonymous tracking)
- [ ] Component updaten met API call
- [ ] Loading state toevoegen
- [ ] Empty state voor geen recente activiteit

**Backend data source:**
- Nieuwe tabel nodig: `ActivityLog` of `ProposalHistory`
- Velden: timestamp, action_type, proposal_id, user (optioneel), details

**NOTE:** Dit vereist een audit trail systeem dat nog niet bestaat!

---

## 📋 PROPOSALS COMPONENTEN

### 4. `frontend/components/proposals/proposals-table.tsx`
**Status:** 🔴 HARDCODED DUMMY DATA

**Huidige situatie:**
```typescript
const proposals = [
  { id: "1234", title: "Zomervoorraad Herverdeling", store: "Amsterdam Centrum",
    date: "24 mei 2023", status: "Wachtend", items: 24 },
  { id: "1235", title: "Nieuwe Collectie Verdeling", ... },
  // ... 7 dummy proposals totaal
]
```

**Vereiste wijzigingen:**
- [x] API endpoint bestaat: `api.pdf.getBatches()` voor overzicht
- [ ] Voor detailed view: `api.pdf.getBatchProposals(batchId)`
- [ ] Component restructuren: toon batches met hun proposals
- [ ] Sorteer functionaliteit behouden
- [ ] Filter functionaliteit toevoegen
- [ ] Pagination toevoegen voor grote datasets

**Backend data source:**
- API: `/api/pdf/batches` (bestaat al)
- API: `/api/pdf/batches/{id}/proposals` (bestaat al)
- Database: `PDFBatch`, `Proposal` tabellen

---

## 📤 UPLOADS COMPONENTEN

### 5. `frontend/components/uploads/manual-file-uploader.tsx`
**Status:** 🟡 PARTIAL - Upload werkt, maar existing series is hardcoded

**Huidige situatie:**
```typescript
const existingSeriesList = [
  { id: "2025032301", name: "Herverdeling voor week 12 2025" },
  { id: "2025031501", name: "Herverdeling voor week 11 2025" },
  { id: "2025030201", name: "Restpartijen week 9 2025" }
]
```

**Vereiste wijzigingen:**
- [x] API endpoint bestaat: `api.pdf.getBatches()`
- [ ] Component updaten om batches dynamisch te laden
- [ ] Bij mount: fetch alle beschikbare batches
- [ ] Filter alleen batches met status "SUCCESS" of "PARTIAL_SUCCESS"
- [ ] Loading state voor dropdown

**Backend data source:**
- API: `/api/pdf/batches` (bestaat al)
- Database: `PDFBatch` tabel

---

## 🖼️ PLACEHOLDER IMAGES

### Gebruikte Placeholder Images:
1. `/placeholder-user.jpg` - Gebruikt in `recent-activity.tsx`
2. `/placeholder-logo.png` - Mogelijk gebruikt in layout/header
3. `/placeholder-logo.svg` - Mogelijk gebruikt in layout/header
4. `/placeholder.jpg` - General placeholder
5. `/placeholder.svg` - General placeholder

**Actie vereist:**
- [ ] Audit waar elk placeholder image wordt gebruikt
- [ ] Vervang met echte logo's / user avatars
- [ ] Implementeer default avatar generator (initialen)
- [ ] Verwijder ongebruikte placeholder files

---

## ✅ COMPONENTEN ZONDER DUMMY DATA

### Correct geïmplementeerd:
- ✅ `frontend/components/uploads/generate-proposals.tsx` - Geen dummy data
- ✅ `frontend/lib/api.ts` - Correct API client zonder hardcoded data
- ✅ Backend routers - Alle endpoints gebruiken database

---

## 🎯 IMPLEMENTATIE PRIORITEIT

### Hoge Prioriteit (Core Functionaliteit)
1. **Manual File Uploader** - Existing series dropdown
2. **Pending Proposals** - Dashboard widget  
3. **Proposals Table** - Main proposals overzicht

### Gemiddelde Prioriteit (User Experience)
4. **Dashboard Stats** - Statistieken overzicht
5. **Placeholder Images** - Visual polish

### Lage Prioriteit (Nice to Have)
6. **Recent Activity** - Vereist nieuw audit trail systeem

---

## 🔧 BENODIGDE NIEUWE BACKEND ENDPOINTS

### 1. Dashboard Statistics
```
GET /api/dashboard/stats?period=week|month|year
Response: {
  total_proposals: number,
  pending_proposals: number,
  approved_proposals: number,
  rejected_proposals: number,
  edited_proposals: number,
  active_stores: number,
  changes_vs_previous: {
    total: number,
    pending: number,
    approved: number,
    rejected: number
  }
}
```

### 2. Recent Activity (Toekomstig)
```
GET /api/activity/recent?limit=10
Response: [{
  id: number,
  timestamp: string,
  action_type: 'approved' | 'rejected' | 'edited' | 'uploaded',
  proposal_id: number,
  batch_id: number,
  user: string | null,
  details: object
}]
```

---

## 📝 IMPLEMENTATIE CHECKLIST

### Frontend Updates
- [ ] Update `dashboard-stats.tsx` met API call
- [ ] Update `pending-proposals.tsx` met API call
- [ ] Update `proposals-table.tsx` met API call
- [ ] Update `manual-file-uploader.tsx` existing series
- [ ] Verwijder recent-activity.tsx of mark als "Coming Soon"
- [ ] Audit en vervang placeholder images

### Backend Updates
- [ ] Maak `/api/dashboard/stats` endpoint
- [ ] Implementeer period filtering in stats
- [ ] Test alle bestaande endpoints met echte data
- [ ] (Optioneel) Maak activity tracking systeem

### Documentatie
- [ ] Update README.md met API endpoints lijst
- [ ] Update DEVELOPMENT_GUIDE.md met frontend patterns
- [ ] Mark dit document als "COMPLETED" na implementatie

---

## 🚀 STATUS TRACKING

**Totaal componenten met dummy data:** 6  
**Vervangen:** 3  
**In behandeling:** 3  
**Vooruitgang:** 50%

**Laatste update:** 29 oktober 2025, 00:14

### ✅ Vervangen (3/6):
1. ✅ `frontend/components/uploads/manual-file-uploader.tsx` - Existing series dropdown
2. ✅ `frontend/components/dashboard/pending-proposals.tsx` - Dashboard widget
3. ✅ `frontend/components/uploads/recent-series.tsx` - Recent series list

### ⏳ Nog te doen (3/6):
4. ⏳ `frontend/components/dashboard/dashboard-stats.tsx` - Vereist backend endpoint
5. ⏳ `frontend/components/proposals/proposals-table.tsx` - API connectie
6. ⏳ `frontend/components/dashboard/recent-activity.tsx` - Vereist audit trail systeem

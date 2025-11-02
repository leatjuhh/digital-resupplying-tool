# Proposals Changes - Implementatie Details

**Datum:** 2025-11-02
**Status:** In Progress

---

## STAP 1: Voorstellen Zichtbaar Maken

### Problem Statement
Gebruikers zien geen verschillen in tabs "Vergelijking" en "Voorgestelde situatie" omdat het herverdelingsalgoritme bepaalt dat artikelen optimaal verdeeld zijn (geen moves nodig).

### Root Cause
- Proposals worden aangemaakt met `moves=[]` (leeg)
- `inventory_proposed` blijft identiek aan `inventory_current`
- Frontend toont correct de data, maar er zijn geen verschillen te zien

### Solution Approach
**UI Enhancement** - Maak duidelijk aan gebruiker wanneer een artikel optimaal verdeeld is:

1. **Voeg "No Changes" indicator toe aan proposal-detail component**
   - Detecteer wanneer `hasDifferences === false`
   - Toon prominente melding: "Dit artikel is reeds optimaal verdeeld"
   - Voeg badge/alert toe bovenaan de tabs

2. **Update tab gedrag**
   - Disable tabs indien geen differences
   - Of: Verberg "Voorgestelde Situatie" tab volledig
   - Toon alleen "Huidige Situatie" met explanation

3. **Optioneel: Filter "optimale" proposals**
   - Voeg filter toe aan batches list
   - "Toon alleen voorstellen met wijzigingen"

### Implementation Plan

#### Bestand: `frontend/components/proposals/proposal-detail.tsx`

**Wijziging 1: Detecteer "no changes" situatie**
```typescript
// Na het berekenen van hasDifferences:
const hasNoChanges = !hasDifferences && proposalData.stores.length > 0
```

**Wijziging 2: Toon melding bij no changes**
```typescript
{hasNoChanges && (
  <Alert className="mb-4">
    <AlertCircle className="h-4 w-4" />
    <AlertTitle>Optimaal Verdeeld</AlertTitle>
    <AlertDescription>
      Dit artikel is reeds optimaal verdeeld over de filialen. 
      Er zijn geen herverdelingen nodig.
    </AlertDescription>
  </Alert>
)}
```

**Wijziging 3: Conditionally render tabs**
```typescript
<TabsList className="mb-4">
  <TabsTrigger value="comparison">Vergelijking</TabsTrigger>
  <TabsTrigger value="current">Huidige Situatie</TabsTrigger>
  {hasDifferences && (
    <TabsTrigger value="proposed">Voorgestelde Situatie</TabsTrigger>
  )}
</TabsList>
```

### Testing
1. Open `/proposals/3?batchId=3` (optimaal artikel)
2. Verifieer melding wordt getoond
3. Verifieer "Voorgestelde Situatie" tab ontbreekt
4. Test met article dat WEL moves heeft (wanneer beschikbaar)

---

## STAP 2: "Load Proposal" Functie

### Problem Statement
Op edit pagina `/proposals/4/edit?batchId=3` kan gebruiker alleen vanaf current inventory editen. Er is geen mogelijkheid om een afgekeurd voorstel te laden als startpunt.

### Current State
- Edit component laadt altijd `inventory_current` uit PDF
- `inventory_proposed` wordt niet gebruikt
- User moet vanaf nul editen

### Solution Approach
**Add "Load Proposal" Button**:

1. **Detecteer of er een voorstel beschikbaar is**
   - Check of `initialProposalData.stores[x].inventoryProposed` bestaat
   - Check of het verschilt van `inventory_current`

2. **Voeg "Laad Voorstel" knop toe**
   - Positie: Naast "Reset naar origineel"
   - Actie: Laadt `inventoryProposed` als editable state
   - State tracking: Houdt bij wat de "basis" is

3. **Update reset logic**
   - Reset gaat terug naar huidige basis (current vs proposed)
   - Visuele indicator welke basis actief is

### Implementation Plan

#### Bestand: `frontend/components/proposals/editable-proposal-detail.tsx`

**Wijziging 1: Track editing basis**
```typescript
const [editingBasis, setEditingBasis] = useState<'current' | 'proposed'>('current')
```

**Wijziging 2: Load proposal function**
```typescript
const loadProposalAsBase = () => {
  if (!initialProposalData) return
  
  // Copy proposed inventory as new editable state
  const newProposalData = {
    ...initialProposalData,
    stores: initialProposalData.stores.map(store => ({
      ...store,
      inventoryProposed: [...store.inventoryProposed]
    }))
  }
  
  setProposalData(newProposalData)
  setEditingBasis('proposed')
  setHasChanges(false)
}
```

**Wijziging 3: Update reset logic**
```typescript
const resetProposal = () => {
  if (editing Basis === 'proposed') {
    // Reset to proposed
    loadProposalAsBase()
  } else {
    // Reset to current
    setProposalData(initialProposalData)
  }
  setHasChanges(false)
}
```

**Wijziging 4: UI voor knop**
```typescript
<div className="flex items-center gap-2">
  <Badge variant={editingBasis === 'current' ? 'default' : 'secondary'}>
    Basis: {editingBasis === 'current' ? 'Huidige Voorraad' : 'AI Voorstel'}
  </Badge>
  
  {hasProposedDifferences && editingBasis === 'current' && (
    <Button variant="outline" size="sm" onClick={loadProposalAsBase}>
      Laad AI Voorstel
    </Button>
  )}
  
  <Button variant="outline" size="sm" onClick={resetProposal} disabled={!hasChanges}>
    Resetten naar {editingBasis === 'current' ? 'origineel' : 'voorstel'}
  </Button>
</div>
```

### Testing
1. Open edit pagina
2. Verifieer "Laad AI Voorstel" knop verschijnt (als er verschillen zijn)
3. Klik knop - verifieer editor laadt proposed values
4. Maak wijzigingen
5. Test reset - gaat terug naar proposed (niet current)
6. Test switch tussen bases

---

## IMPLEMENTATION STATUS

### STAP 1: UI Enhancement
- [ ] Detecteer no changes situatie
- [ ] Voeg Alert component toe
- [ ] Conditionally render tabs
- [ ] Test met optimaal artikel

### STAP 2: Load Proposal
- [ ] Add editingBasis state
- [ ] Implement loadProposalAsBase()
- [ ] Update resetProposal()
- [ ] Add UI components
- [ ] Test functionaliteit

---

## FILES TO MODIFY

### Frontend
1. `frontend/components/proposals/proposal-detail.tsx`
   - Add Alert for "optimaal verdeeld"
   - Conditionally render tabs

2. `frontend/components/proposals/editable-proposal-detail.tsx`
   - Add editingBasis state
   - Add loadProposalAsBase function
   - Update resetProposal logic
   - Add UI for basis switching

### No Backend Changes Required
- All data is already available via `/full` endpoint
- No new API endpoints needed

---

## DEFINITION OF DONE

### STAP 1
- ✅ Detailpagina toont duidelijke melding bij optimaal verdeelde artikelen
- ✅ Tabs worden correct getoond/verborgen
- ✅ User begrijpt waarom er geen verschillen zijn
- ✅ Geen console errors

### STAP 2
- ✅ Edit pagina heeft "Laad AI Voorstel" knop
- ✅ Knop verschijnt alleen als er proposed changes zijn
- ✅ Klikken laadt proposed inventory
- ✅ Badge toont huidige basis
- ✅ Reset werkt correct voor beide bases
- ✅ No console errors

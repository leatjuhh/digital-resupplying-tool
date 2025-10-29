# Proposal Edit Route Documentatie

## Route: `/proposals/[id]/edit?batchId=...`

Deze route biedt een bewerkbare interface voor het aanpassen van afgekeurde herverdelingsvoorstellen. Gebruikers kunnen de voorgestelde inventarisposities handmatig aanpassen en het voorstel opnieuw goedkeuren.

---

## 1. Route Structuur

### URL Parameters
- **`[id]`** (required): Het unieke ID van het voorstel dat bewerkt wordt
  - Voorbeeld: `423264`
  
### Query Parameters
- **`batchId`** (optional): Het ID van de batch waartoe dit voorstel behoort
  - Voorbeeld: `2025032301`
  - Gebruikt voor batch-navigatie en voortgangstracking

### Voorbeelden
\`\`\`
/proposals/423264/edit
/proposals/423264/edit?batchId=2025032301
\`\`\`

---

## 2. Bestandsstructuur

### Hoofdbestanden
\`\`\`
app/proposals/[id]/edit/
└── page.tsx                                    # Edit pagina component

components/proposals/
├── editable-proposal-detail.tsx                # Bewerkbare voorstel component
└── proposal-actions.tsx                        # Actie knoppen (indien gebruikt)
\`\`\`

---

## 3. Functionaliteit Overzicht

### 3.1 Hoofdfuncties
1. **Directe Bewerking**: Gebruikers kunnen inventarisaantallen direct in de tabel bewerken
2. **Balans Validatie**: Systeem controleert of de totale voorraad gebalanceerd blijft
3. **Visuele Feedback**: Wijzigingen worden visueel gemarkeerd met kleuren en iconen
4. **Reset Functionaliteit**: Mogelijkheid om alle wijzigingen ongedaan te maken
5. **Opslaan & Goedkeuren**: Gewijzigde voorstellen kunnen worden opgeslagen en goedgekeurd
6. **Batch Navigatie**: Automatische doorverwijzing naar het volgende voorstel in de batch

### 3.2 Validatieregels
- **Gebalanceerde Herverdeling**: De totale voorraad per maat moet gelijk blijven
  - Som van alle voorgestelde aantallen = Som van alle huidige aantallen
  - Ongebalanceerde voorstellen kunnen niet worden opgeslagen
- **Wijzigingen Vereist**: Er moeten wijzigingen zijn gemaakt om op te kunnen slaan
- **Positieve Getallen**: Inventarisaantallen moeten >= 0 zijn

---

## 4. Component Analyse

### 4.1 EditProposalPage (`app/proposals/[id]/edit/page.tsx`)

#### Props
\`\`\`typescript
{
  params: { id: string }           // Voorstel ID uit URL
  searchParams: { batchId?: string } // Optionele batch ID
}
\`\`\`

#### State Management
\`\`\`typescript
const [isBalanced, setIsBalanced] = useState(true)    // Balans status
const [hasChanges, setHasChanges] = useState(false)   // Wijzigingen status
\`\`\`

#### Key Features

**1. Batch Voortgang Weergave**
\`\`\`typescript
const batchInfo = batchId ? {
  totalProposals: 42,           // Totaal aantal voorstellen in batch
  assessedProposals: 11,        // Aantal beoordeelde voorstellen
  name: "Herverdeling voor week 12 2025"
} : undefined
\`\`\`

**2. Save & Approve Handler**
\`\`\`typescript
const handleSaveAndApprove = () => {
  // 1. Toon visuele feedback (groene overlay met checkmark)
  // 2. Animeer voortgangsbalk
  // 3. Navigeer naar volgend voorstel of batch overzicht
}
\`\`\`

**Visuele Feedback Flow:**
1. Groene overlay met checkmark verschijnt (800ms)
2. Voortgangsbalk animeert naar nieuwe waarde (500ms)
3. Fade-out effect (500ms)
4. Navigatie naar volgende pagina

**3. State Synchronisatie**
\`\`\`typescript
useEffect(() => {
  const handleStateChange = (event: CustomEvent) => {
    if (event.detail) {
      setIsBalanced(event.detail.isBalanced)
      setHasChanges(event.detail.hasChanges)
    }
  }
  
  window.addEventListener("proposalStateChange", handleStateChange)
  return () => window.removeEventListener("proposalStateChange", handleStateChange)
}, [])
\`\`\`

**4. Opslaan Knop Logica**
\`\`\`typescript
<Button
  disabled={!isBalanced || !hasChanges}
  onClick={handleSaveAndApprove}
>
  Opslaan & Goedkeuren
</Button>
\`\`\`

**Disabled wanneer:**
- `!isBalanced`: Herverdeling is niet gebalanceerd
- `!hasChanges`: Er zijn geen wijzigingen gemaakt

**5. Tooltip Feedback**
\`\`\`typescript
<TooltipContent hidden={isBalanced && hasChanges}>
  {!isBalanced ? (
    <p>Ongebalanceerde herverdeling - totale voorraad moet gelijk blijven</p>
  ) : !hasChanges ? (
    <p>Geen wijzigingen - maak wijzigingen om op te kunnen slaan</p>
  ) : null}
</TooltipContent>
\`\`\`

---

### 4.2 EditableProposalDetail Component

#### Props
\`\`\`typescript
interface EditableProposalDetailProps {
  id: string                    // Voorstel ID
  batchId?: string             // Optionele batch ID
  batchInfo?: {
    totalProposals: number
    assessedProposals: number
    name: string
  }
}
\`\`\`

#### Data Structure
\`\`\`typescript
const proposalData = {
  id: string
  articleCode: string           // "TC039-04"
  description: string           // "Brisia Peacock Top"
  supplier: { id: string, name: string }
  color: { id: string, name: string }
  category: { id: string, name: string }
  subcategory: { id: string, name: string }
  seasonYear: string
  collection: { id: string, name: string }
  orderCode: string
  lastDeliveryDate: string
  totalSold: number
  sizes: string[]               // ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL"]
  stores: Array<{
    id: string
    name: string
    inventoryCurrent: number[]   // Huidige voorraad per maat
    inventoryProposed: number[]  // Voorgestelde voorraad per maat
    sold: number                 // Aantal verkocht
  }>
}
\`\`\`

#### State Management
\`\`\`typescript
const [proposalData, setProposalData] = useState(initialProposalData)
const [isBalanced, setIsBalanced] = useState(true)
const [hasChanges, setHasChanges] = useState(false)
const [totalDifference, setTotalDifference] = useState(0)
\`\`\`

#### Key Functions

**1. Totalen Berekening**
\`\`\`typescript
// Huidige voorraad totalen per maat
const totalsCurrent = proposalData.sizes.map((_, sizeIndex) => {
  return proposalData.stores.reduce((acc, store) => 
    acc + store.inventoryCurrent[sizeIndex], 0
  )
})

// Voorgestelde voorraad totalen per maat
const totalsProposed = proposalData.sizes.map((_, sizeIndex) => {
  return proposalData.stores.reduce((acc, store) => 
    acc + store.inventoryProposed[sizeIndex], 0
  )
})
\`\`\`

**2. Balans Validatie**
\`\`\`typescript
useEffect(() => {
  // Bereken totaal verschil
  let totalDiff = 0
  for (let i = 0; i < totalsCurrent.length; i++) {
    totalDiff += totalsProposed[i] - totalsCurrent[i]
  }
  
  setTotalDifference(totalDiff)
  setIsBalanced(totalDiff === 0)  // Gebalanceerd als verschil = 0
  
  // Check voor wijzigingen
  const hasAnyChanges = proposalData.stores.some((store, storeIndex) => {
    return store.inventoryProposed.some((proposed, sizeIndex) => {
      return proposed !== initialProposalData.stores[storeIndex].inventoryProposed[sizeIndex]
    })
  })
  setHasChanges(hasAnyChanges)
  
  // Update save button state
  const saveButton = document.getElementById("save-button")
  if (saveButton) {
    saveButton.disabled = !isBalanced || !hasAnyChanges
  }
  
  // Dispatch event naar parent component
  window.dispatchEvent(new CustomEvent("proposalStateChange", {
    detail: { isBalanced: totalDiff === 0, hasChanges: hasAnyChanges }
  }))
}, [proposalData, totalsCurrent, totalsProposed])
\`\`\`

**3. Inventaris Wijziging Handler**
\`\`\`typescript
const handleInventoryChange = (storeIndex: number, sizeIndex: number, value: string) => {
  const numValue = parseInt(value) || 0
  
  const newProposalData = { ...proposalData }
  newProposalData.stores[storeIndex].inventoryProposed[sizeIndex] = numValue
  
  setProposalData(newProposalData)
}
\`\`\`

**4. Reset Functionaliteit**
\`\`\`typescript
const resetProposal = () => {
  setProposalData(initialProposalData)
  setHasChanges(false)
}
\`\`\`

---

## 5. UI Componenten

### 5.1 Batch Voortgang Card
\`\`\`typescript
{showBatchProgress && (
  <Card>
    <CardContent>
      <h3>Reeks: {batchInfo.name}</h3>
      <p>Voorstel {batchInfo.assessedProposals + 1} van {batchInfo.totalProposals}</p>
      <Badge>Voortgang: {progressPercentage}%</Badge>
      <Progress value={progressPercentage} />
    </CardContent>
  </Card>
)}
\`\`\`

### 5.2 Artikel Informatie Card
Toont statische informatie over het artikel:
- Artikel naam, code en bestelcode
- Collectie en seizoen informatie
- Kleur, leverancier en categorie

### 5.3 Bewerkbare Tabel

#### Tabel Structuur
\`\`\`
┌─────────────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬──────────┐
│ Filiaal     │ XXS │ XS  │ S   │ M   │ L   │ XL  │ XXL │XXXL │ Verkocht │
├─────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼──────────┤
│ Totaal      │  0  │  0  │  6  │ 13  │  9  │  9  │  5  │  0  │    14    │
├─────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼──────────┤
│ 5 Panningen │  0  │  0  │ [1] │ [0] │  0  │  0  │  0  │  0  │     6    │
│ 6 Echt      │  0  │  0  │  0  │ [1] │ [1] │ [1] │ [1] │  0  │     1    │
│ ...         │ ... │ ... │ ... │ ... │ ... │ ... │ ... │ ... │    ...   │
└─────────────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴──────────┘

[n] = Bewerkbaar input veld
\`\`\`

#### Visuele Indicatoren

**1. Totaal Rij**
\`\`\`typescript
<TableCell className={hasImbalance ? "bg-red-100 dark:bg-red-900/20" : ""}>
  <span>{proposedTotal}</span>
  {diff !== 0 && (
    <span className={diff > 0 ? "text-green-500" : "text-red-500"}>
      {diff > 0 ? `+${diff}` : diff}
    </span>
  )}
</TableCell>
\`\`\`

**Kleuren:**
- **Rood**: Ongebalanceerde maat (verschil ≠ 0)
- **Groen tekst**: Positief verschil (+n)
- **Rood tekst**: Negatief verschil (-n)

**2. Winkel Cellen**
\`\`\`typescript
<TableCell className={diff !== 0 ? "bg-blue-100 dark:bg-blue-900/20" : ""}>
  <Input
    type="number"
    value={qty}
    onChange={(e) => handleInventoryChange(storeIndex, sizeIndex, e.target.value)}
    className="w-12 h-8 text-center"
    min="0"
  />
  {diff !== 0 && (
    <span className={diff > 0 ? "text-green-500" : "text-red-500"}>
      {diff > 0 ? <ArrowUp /> : <ArrowDown />}
      {Math.abs(diff)}
    </span>
  )}
</TableCell>
\`\`\`

**Kleuren:**
- **Blauw achtergrond**: Gewijzigde cel
- **Groene pijl omhoog**: Toegevoegde voorraad
- **Rode pijl omlaag**: Verwijderde voorraad

### 5.4 Legenda
\`\`\`
┌─────────────────────────────────────────────────────┐
│ Legenda:                                            │
│ ▢ Gewijzigde voorraad (blauw)                      │
│ ↑ Toegevoegd (groen)                               │
│ ↓ Verwijderd (rood)                                │
└─────────────────────────────────────────────────────┘
\`\`\`

---

## 6. Gebruikersflow

### 6.1 Normaal Bewerkingsproces
\`\`\`
1. Gebruiker keurt voorstel af op detail pagina
   ↓
2. Systeem navigeert naar /proposals/[id]/edit
   ↓
3. Gebruiker past inventarisaantallen aan
   ↓
4. Systeem valideert balans real-time
   ↓
5. Gebruiker klikt "Opslaan & Goedkeuren"
   ↓
6. Visuele feedback (checkmark + animatie)
   ↓
7. Navigatie naar volgend voorstel of batch overzicht
\`\`\`

### 6.2 Batch Bewerkingsproces
\`\`\`
1. Gebruiker bewerkt voorstel in batch
   ↓
2. Batch voortgang wordt getoond bovenaan
   ↓
3. Na opslaan: voortgangsbalk animeert
   ↓
4. Automatische navigatie naar volgend voorstel
   ↓
5. Herhaal tot alle voorstellen zijn beoordeeld
   ↓
6. Laatste voorstel: navigeer naar batch overzicht
\`\`\`

### 6.3 Reset Flow
\`\`\`
1. Gebruiker maakt wijzigingen
   ↓
2. Gebruiker klikt "Resetten naar origineel"
   ↓
3. Alle wijzigingen worden ongedaan gemaakt
   ↓
4. State wordt teruggezet naar initiële data
   ↓
5. "Opslaan" knop wordt weer disabled
\`\`\`

---

## 7. Navigatie Logica

### 7.1 Na Opslaan & Goedkeuren
\`\`\`typescript
if (batchId) {
  const nextProposalId = (parseInt(params.id) + 1).toString()
  const hasNextProposal = true  // Zou dynamisch moeten zijn
  
  if (hasNextProposal) {
    router.push(`/proposals/${nextProposalId}?batchId=${batchId}`)
  } else {
    router.push(`/proposals/batch/${batchId}`)
  }
} else {
  router.push("/proposals")
}
\`\`\`

### 7.2 Bij Annuleren
\`\`\`typescript
router.push(`/proposals/${params.id}${batchId ? `?batchId=${batchId}` : ""}`)
\`\`\`

### 7.3 Terug Knop
\`\`\`typescript
<Link href={`/proposals/${params.id}${batchId ? `?batchId=${batchId}` : ""}`}>
  <ArrowLeft /> Terug naar voorstel
</Link>
\`\`\`

---

## 8. State Management & Events

### 8.1 Custom Event: proposalStateChange
\`\`\`typescript
// Dispatched door EditableProposalDetail
window.dispatchEvent(new CustomEvent("proposalStateChange", {
  detail: {
    isBalanced: boolean,
    hasChanges: boolean
  }
}))

// Ontvangen door EditProposalPage
window.addEventListener("proposalStateChange", (event: CustomEvent) => {
  setIsBalanced(event.detail.isBalanced)
  setHasChanges(event.detail.hasChanges)
})
\`\`\`

### 8.2 State Synchronisatie
\`\`\`
EditableProposalDetail (child)
         ↓ (custom event)
EditProposalPage (parent)
         ↓ (props)
Button disabled state
\`\`\`

---

## 9. Validatie & Foutafhandeling

### 9.1 Balans Validatie
\`\`\`typescript
// Voor elke maat: som(voorgesteld) moet gelijk zijn aan som(huidig)
for (let sizeIndex = 0; sizeIndex < sizes.length; sizeIndex++) {
  const currentTotal = stores.reduce((sum, store) => 
    sum + store.inventoryCurrent[sizeIndex], 0
  )
  const proposedTotal = stores.reduce((sum, store) => 
    sum + store.inventoryProposed[sizeIndex], 0
  )
  
  if (currentTotal !== proposedTotal) {
    // Markeer als ongebalanceerd
    isBalanced = false
  }
}
\`\`\`

### 9.2 Visuele Feedback
- **Ongebalanceerd**: Rode achtergrond in totaal rij + badge "Ongebalanceerd"
- **Gebalanceerd**: Normale achtergrond + badge "Gebalanceerd"
- **Wijzigingen**: Badge "Gewijzigd" + blauwe achtergrond in cellen
- **Geen wijzigingen**: Geen extra badges

### 9.3 Button States
\`\`\`typescript
// Opslaan knop disabled wanneer:
disabled={!isBalanced || !hasChanges}

// Tooltip toont reden:
- !isBalanced → "Ongebalanceerde herverdeling"
- !hasChanges → "Geen wijzigingen"
\`\`\`

---

## 10. Animaties & Visuele Effecten

### 10.1 Opslaan Animatie
\`\`\`typescript
// 1. Groene overlay (800ms)
overlay.className = "fixed inset-0 bg-green-500/20 flex items-center justify-center z-50"

// 2. Checkmark icoon
<svg>
  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
  <polyline points="22 4 12 14.01 9 11.01"></polyline>
</svg>

// 3. Fade-out (500ms)
overlay.style.opacity = "0"

// 4. Navigatie
router.push(nextUrl)
\`\`\`

### 10.2 Voortgangsbalk Animatie
\`\`\`typescript
progressBar.style.transition = "width 0.5s ease-in-out"
progressBar.style.width = `${newPercentage}%`
\`\`\`

### 10.3 Cel Hover Effects
\`\`\`css
/* Input velden */
.hover\:border-blue-500:hover {
  border-color: rgb(59 130 246);
}

/* Wijzigingsindicatoren */
.text-green-500 { color: rgb(34 197 94); }
.text-red-500 { color: rgb(239 68 68); }
\`\`\`

---

## 11. Backend Integratie (Toekomstig)

### 11.1 Benodigde API Endpoints

**GET `/api/proposals/:id/edit`**
\`\`\`typescript
// Request
GET /api/proposals/423264/edit

// Response
{
  id: "423264",
  articleCode: "TC039-04",
  description: "Brisia Peacock Top",
  // ... alle artikel data
  stores: [
    {
      id: "5",
      name: "Panningen",
      inventoryCurrent: [0, 0, 1, 1, 0, 0, 0, 0],
      inventoryProposed: [0, 0, 1, 0, 0, 0, 0, 0],
      sold: 6
    },
    // ... meer winkels
  ]
}
\`\`\`

**PUT `/api/proposals/:id/edit`**
\`\`\`typescript
// Request
PUT /api/proposals/423264/edit
{
  stores: [
    {
      id: "5",
      inventoryProposed: [0, 0, 1, 0, 0, 0, 0, 0]
    },
    {
      id: "35",
      inventoryProposed: [0, 0, 1, 2, 1, 1, 0, 0]
    }
  ]
}

// Response
{
  success: true,
  proposalId: "423264",
  status: "approved",
  nextProposalId: "423265"  // Voor batch navigatie
}
\`\`\`

**GET `/api/proposals/batch/:batchId/next`**
\`\`\`typescript
// Request
GET /api/proposals/batch/2025032301/next?currentId=423264

// Response
{
  hasNext: true,
  nextProposalId: "423265",
  progress: {
    current: 12,
    total: 42
  }
}
\`\`\`

### 11.2 Validatie op Backend
\`\`\`typescript
// Server-side validatie
function validateProposal(proposal) {
  // 1. Check balans per maat
  for (let sizeIndex = 0; sizeIndex < proposal.sizes.length; sizeIndex++) {
    const currentTotal = calculateTotal(proposal.stores, sizeIndex, 'current')
    const proposedTotal = calculateTotal(proposal.stores, sizeIndex, 'proposed')
    
    if (currentTotal !== proposedTotal) {
      return {
        valid: false,
        error: `Maat ${proposal.sizes[sizeIndex]} is niet gebalanceerd`
      }
    }
  }
  
  // 2. Check negatieve waarden
  for (const store of proposal.stores) {
    if (store.inventoryProposed.some(qty => qty < 0)) {
      return {
        valid: false,
        error: `Negatieve voorraad niet toegestaan voor ${store.name}`
      }
    }
  }
  
  return { valid: true }
}
\`\`\`

---

## 12. Performance Optimalisaties

### 12.1 Huidige Optimalisaties
- **Memoization**: Totalen worden alleen herberekend bij data wijzigingen
- **Conditional Rendering**: Winkels zonder voorraad worden overgeslagen
- **Event Debouncing**: Input wijzigingen worden direct verwerkt (geen debounce nodig voor kleine datasets)

### 12.2 Toekomstige Optimalisaties
\`\`\`typescript
// 1. Gebruik React.memo voor tabel rijen
const StoreRow = React.memo(({ store, onInventoryChange }) => {
  // ... render logica
})

// 2. Virtualisatie voor grote datasets
import { useVirtualizer } from '@tanstack/react-virtual'

// 3. Debounce voor API calls
const debouncedSave = useMemo(
  () => debounce((data) => saveProposal(data), 500),
  []
)
\`\`\`

---

## 13. Toegankelijkheid

### 13.1 Keyboard Navigatie
- **Tab**: Navigeer tussen input velden
- **Enter**: Bevestig wijziging en ga naar volgend veld
- **Escape**: Annuleer wijziging
- **Ctrl+S**: Opslaan (toekomstig)
- **Ctrl+Z**: Undo laatste wijziging (toekomstig)

### 13.2 Screen Reader Support
\`\`\`typescript
<Input
  type="number"
  aria-label={`Voorraad voor ${store.name}, maat ${size}`}
  aria-describedby={`diff-${storeIndex}-${sizeIndex}`}
/>

<span id={`diff-${storeIndex}-${sizeIndex}`} className="sr-only">
  {diff > 0 ? `${diff} toegevoegd` : `${Math.abs(diff)} verwijderd`}
</span>
\`\`\`

### 13.3 Focus Management
\`\`\`typescript
// Focus op eerste bewerkbaar veld bij laden
useEffect(() => {
  const firstInput = document.querySelector('input[type="number"]')
  if (firstInput) {
    (firstInput as HTMLInputElement).focus()
  }
}, [])
\`\`\`

---

## 14. Testing Scenarios

### 14.1 Unit Tests
\`\`\`typescript
describe('EditableProposalDetail', () => {
  test('validates balanced redistribution', () => {
    // Test dat ongebalanceerde herverdeling wordt gedetecteerd
  })
  
  test('tracks changes correctly', () => {
    // Test dat wijzigingen correct worden bijgehouden
  })
  
  test('resets to original state', () => {
    // Test dat reset functionaliteit werkt
  })
  
  test('disables save button when unbalanced', () => {
    // Test dat save button disabled is bij ongebalanceerde staat
  })
})
\`\`\`

### 14.2 Integration Tests
\`\`\`typescript
describe('Edit Proposal Flow', () => {
  test('complete edit and approve flow', async () => {
    // 1. Navigeer naar edit pagina
    // 2. Maak wijzigingen
    // 3. Klik opslaan
    // 4. Verifieer navigatie naar volgend voorstel
  })
  
  test('batch navigation flow', async () => {
    // Test volledige batch doorloop
  })
})
\`\`\`

### 14.3 E2E Tests
\`\`\`typescript
test('user can edit and approve proposal', async ({ page }) => {
  await page.goto('/proposals/423264/edit?batchId=2025032301')
  
  // Wijzig voorraad
  await page.fill('input[aria-label*="Panningen, maat M"]', '0')
  await page.fill('input[aria-label*="Etten-Leur, maat M"]', '2')
  
  // Verifieer balans
  await expect(page.locator('text=Gebalanceerd')).toBeVisible()
  
  // Opslaan
  await page.click('button:has-text("Opslaan & Goedkeuren")')
  
  // Verifieer navigatie
  await expect(page).toHaveURL('/proposals/423265?batchId=2025032301')
})
\`\`\`

---

## 15. Troubleshooting

### 15.1 Veelvoorkomende Problemen

**Probleem: Save button blijft disabled**
\`\`\`
Oorzaken:
1. Herverdeling is niet gebalanceerd
2. Er zijn geen wijzigingen gemaakt
3. State synchronisatie werkt niet

Oplossing:
- Check console voor "proposalStateChange" events
- Verifieer dat totalen correct worden berekend
- Check of useEffect dependencies correct zijn
\`\`\`

**Probleem: Voortgangsbalk animeert niet**
\`\`\`
Oorzaken:
1. batchInfo is undefined
2. CSS transition werkt niet
3. Element wordt niet gevonden

Oplossing:
- Verifieer dat batchId parameter aanwezig is
- Check of .progress-bar-inner class bestaat
- Verifieer CSS transition property
\`\`\`

**Probleem: Wijzigingen worden niet gedetecteerd**
\`\`\`
Oorzaken:
1. initialProposalData wordt niet correct opgeslagen
2. Vergelijking in useEffect faalt
3. State update werkt niet

Oplossing:
- Log initialProposalData en proposalData
- Verifieer deep equality check
- Check React DevTools voor state updates
\`\`\`

### 15.2 Debug Tips
\`\`\`typescript
// 1. Log state changes
useEffect(() => {
  console.log('[v0] Proposal data changed:', proposalData)
  console.log('[v0] Is balanced:', isBalanced)
  console.log('[v0] Has changes:', hasChanges)
}, [proposalData, isBalanced, hasChanges])

// 2. Log totalen
console.log('[v0] Current totals:', totalsCurrent)
console.log('[v0] Proposed totals:', totalsProposed)
console.log('[v0] Difference:', totalDifference)

// 3. Log events
window.addEventListener('proposalStateChange', (e) => {
  console.log('[v0] State change event:', e.detail)
})
\`\`\`

---

## 16. Toekomstige Uitbreidingen

### 16.1 Geplande Features
1. **Undo/Redo Functionaliteit**
   - History stack voor wijzigingen
   - Ctrl+Z / Ctrl+Y shortcuts

2. **Bulk Edit Mode**
   - Selecteer meerdere cellen
   - Pas dezelfde wijziging toe op selectie

3. **Smart Suggestions**
   - AI-gestuurde herverdelingsvoorstellen
   - Gebaseerd op verkoopcijfers en trends

4. **Drag & Drop**
   - Sleep voorraad tussen winkels
   - Visuele feedback tijdens slepen

5. **Comments & Notes**
   - Voeg notities toe aan wijzigingen
   - Communiceer met andere gebruikers

6. **Version History**
   - Bekijk eerdere versies van voorstel
   - Vergelijk wijzigingen over tijd

### 16.2 Technische Verbeteringen
1. **Real-time Collaboration**
   - WebSocket integratie
   - Zie wijzigingen van andere gebruikers live

2. **Offline Support**
   - Service Worker voor offline editing
   - Sync wijzigingen bij reconnect

3. **Advanced Validatie**
   - Custom validatieregels per categorie
   - Waarschuwingen voor ongebruikelijke wijzigingen

4. **Export Functionaliteit**
   - Export naar Excel/CSV
   - PDF rapport van wijzigingen

---

## 17. Samenvatting

De `/proposals/[id]/edit` route biedt een krachtige interface voor het bewerken van herverdelingsvoorstellen met:

✅ **Real-time validatie** van gebalanceerde herverdeling
✅ **Visuele feedback** voor wijzigingen en fouten
✅ **Batch navigatie** voor efficiënte verwerking
✅ **Reset functionaliteit** voor eenvoudig ongedaan maken
✅ **Smooth animaties** voor betere UX
✅ **Toegankelijkheid** voor alle gebruikers

De component is ontworpen voor uitbreidbaarheid en kan eenvoudig worden aangepast voor toekomstige features zoals drag-and-drop, bulk editing en real-time collaboration.

# Documentatie: app/proposals/[id] Route

## Overzicht

De `app/proposals/[id]` route is een dynamische Next.js route die een gedetailleerde weergave biedt van een individueel herverdelingsvoorstel. Deze route ondersteunt zowel een alleen-lezen weergave als een bewerkbare modus, en kan onderdeel zijn van een batch-verwerking workflow.

## Bestandsstructuur

\`\`\`
app/proposals/[id]/
├── page.tsx                                    # Hoofdpagina component
└── edit/
    └── page.tsx                                # Bewerkbare versie van de pagina

components/proposals/
├── proposal-detail.tsx                         # Alleen-lezen detail component
├── editable-proposal-detail.tsx                # Bewerkbare detail component
└── proposal-actions.tsx                        # Actieknoppen (goedkeuren, afwijzen, etc.)
\`\`\`

## Route Parameters en Query Parameters

### URL Parameters
- `id` (string): Het unieke ID van het voorstel (bijvoorbeeld: "1", "2", "3")

### Query Parameters
- `batchId` (optioneel, string): Het ID van de batch waartoe dit voorstel behoort
  - Voorbeeld: `/proposals/1?batchId=batch-123`
  - Wanneer aanwezig, wordt batch-specifieke functionaliteit geactiveerd

## Hoofdcomponent: page.tsx

### Functionaliteit

De hoofdpagina component (`app/proposals/[id]/page.tsx`) is een **Server Component** die:

1. **Route parameters ontvangt** via Next.js props:
   \`\`\`typescript
   {
     params: { id: string }
     searchParams: { batchId?: string }
   }
   \`\`\`

2. **Batch informatie simuleert** (in productie zou dit van een API komen):
   \`\`\`typescript
   const batchInfo = batchId ? {
     totalProposals: 42,        // Totaal aantal voorstellen in de batch
     assessedProposals: 11,     // Aantal reeds beoordeelde voorstellen
     name: "Herverdeling voor week 12 2025"
   } : undefined
   \`\`\`

3. **Layout structuur biedt** met:
   - Terug-knop (navigeert naar batch-overzicht of algemeen voorstellen-overzicht)
   - Header met voorstel-ID
   - Actieknoppen voor goedkeuren/afwijzen
   - Detail component met voorstelinformatie

### Code Structuur

\`\`\`typescript
export default function ProposalDetailPage({
  params,
  searchParams,
}: {
  params: { id: string }
  searchParams: { batchId?: string }
}) {
  const batchId = searchParams.batchId
  
  // Simuleer batch informatie
  const batchInfo = batchId ? {
    totalProposals: 42,
    assessedProposals: 11,
    name: "Herverdeling voor week 12 2025",
  } : undefined

  return (
    <DashboardShell>
      {/* Terug-knop */}
      <Button variant="ghost" size="sm" asChild>
        <Link href={batchId ? `/proposals/batch/${batchId}` : "/proposals"}>
          <ArrowLeft /> Terug
        </Link>
      </Button>
      
      {/* Header met actieknoppen */}
      <DashboardHeader heading={`Voorstel #${params.id}`}>
        <ProposalActions
          id={params.id}
          batchId={batchId}
          totalInBatch={batchInfo?.totalProposals}
          completedInBatch={batchInfo?.assessedProposals}
        />
      </DashboardHeader>
      
      {/* Detail component */}
      <ProposalDetail 
        id={params.id} 
        batchId={batchId} 
        batchInfo={batchInfo} 
      />
    </DashboardShell>
  )
}
\`\`\`

## ProposalDetail Component

### Doel
Toont een alleen-lezen weergave van een herverdelingsvoorstel met artikel informatie en voorraadverdeling.

### Props Interface

\`\`\`typescript
interface ProposalDetailProps {
  id: string                    // Voorstel ID
  batchId?: string             // Optioneel batch ID
  batchInfo?: {                // Optionele batch informatie
    totalProposals: number
    assessedProposals: number
    name: string
  }
}
\`\`\`

### Datastructuur

Het component werkt met een complexe datastructuur die een herverdelingsvoorstel representeert:

\`\`\`typescript
const proposalData = {
  // Artikel identificatie
  id: string
  articleCode: string          // Bijvoorbeeld: "TC039-04"
  description: string          // Bijvoorbeeld: "Brisia Peacock Top"
  orderCode: string           // Bijvoorbeeld: "TC039-04 Brisia475"
  
  // Leverancier informatie
  supplier: {
    id: string
    name: string
  }
  
  // Kleur informatie
  color: {
    id: string
    name: string
  }
  
  // Categorie informatie
  category: {
    id: string
    name: string
  }
  subcategory: {
    id: string
    name: string
  }
  
  // Collectie informatie
  seasonYear: string
  collection: {
    id: string
    name: string
  }
  
  // Voorraad informatie
  totalSold: number
  sizes: string[]              // Bijvoorbeeld: ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL"]
  
  // Winkel voorraad
  stores: Array<{
    id: string
    name: string
    inventoryCurrent: number[]    // Huidige voorraad per maat
    inventoryProposed: number[]   // Voorgestelde voorraad per maat
    sold: number                  // Aantal verkocht
  }>
}
\`\`\`

### Visuele Componenten

#### 1. Batch Voortgangsindicator (optioneel)
Wordt alleen getoond wanneer `batchInfo` aanwezig is:

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

**Berekening:**
\`\`\`typescript
const progressPercentage = Math.round(
  (batchInfo.assessedProposals / batchInfo.totalProposals) * 100
)
\`\`\`

#### 2. Artikel Informatie Card
Toont alle metadata over het artikel in een 3-koloms grid:

- **Kolom 1: Artikel**
  - Beschrijving
  - Artikelcode
  - Bestelcode

- **Kolom 2: Collectie**
  - Collectienaam
  - Seizoen
  - Collectiecode

- **Kolom 3: Details**
  - Kleur (met visuele kleurindicator)
  - Leverancier
  - Categorie

#### 3. Interfiliaalverdeling Tabel
De kern van het voorstel - toont voorraadverdeling over winkels en maten.

**Tabs:**
1. **Vergelijking** (standaard): Toont huidige en voorgestelde voorraad naast elkaar
2. **Huidige Situatie**: Toont alleen huidige voorraad
3. **Voorgestelde Situatie**: Toont alleen voorgestelde voorraad

**Tabel Structuur:**
\`\`\`
| Filiaal      | XXS | XS | S | M | L | XL | XXL | XXXL | Verkocht |
|--------------|-----|----|----|---|---|----|----|------|----------|
| Totaal       |  0  | 0  | 4  | 13| 9 | 8  | 4  |  0   |    14    |
| 5 Panningen  |  .  | .  | 1  | 1 | . | .  | .  |  .   |     6    |
| 6 Echt       |  .  | .  | .  | 1 | 1 | 1  | 1  |  .   |     1    |
| ...          | ... |... |... |...|...|... |... | ...  |    ...   |
\`\`\`

**Kleurcodering:**
- **Groen** (`bg-green-100`): Huidige voorraad (in vergelijkingsmodus)
- **Blauw** (`bg-blue-100`): Voorgestelde voorraad (wanneer verschillend van huidig)
- **Punt (.)**: Nul voorraad (voor betere leesbaarheid)

### Berekeningen

#### Totalen per Maat (Huidig)
\`\`\`typescript
const totals = proposalData.sizes.map((_, sizeIndex) => {
  return proposalData.stores.reduce(
    (acc, store) => acc + store.inventoryCurrent[sizeIndex], 
    0
  )
})
\`\`\`

#### Totalen per Maat (Voorgesteld)
\`\`\`typescript
const totalsProposed = proposalData.sizes.map((_, sizeIndex) => {
  return proposalData.stores.reduce(
    (acc, store) => acc + store.inventoryProposed[sizeIndex], 
    0
  )
})
\`\`\`

#### Totaal Verkocht
\`\`\`typescript
const totalSold = proposalData.stores.reduce(
  (acc, store) => acc + store.sold, 
  0
)
\`\`\`

#### Detectie van Wijzigingen
\`\`\`typescript
const hasDifferences = proposalData.stores.some((store) => {
  return store.inventoryCurrent.some((current, sizeIndex) => {
    return current !== store.inventoryProposed[sizeIndex]
  })
})
\`\`\`

### Filtering van Lege Rijen
Winkels zonder voorraad en verkoop worden niet getoond (behalve winkel ID "0"):

\`\`\`typescript
const hasInventory = 
  store.inventoryCurrent.some((val) => val > 0) ||
  store.inventoryProposed.some((val) => val > 0) ||
  store.sold > 0

if (!hasInventory && store.id !== "0") return null
\`\`\`

## ProposalActions Component

### Doel
Biedt actieknoppen voor het beoordelen van voorstellen (goedkeuren, afwijzen, bewerken, exporteren).

### Props Interface

\`\`\`typescript
interface ProposalActionsProps {
  id: string                    // Voorstel ID
  batchId?: string             // Optioneel batch ID
  totalInBatch?: number        // Totaal aantal voorstellen in batch
  completedInBatch?: number    // Aantal voltooide voorstellen in batch
}
\`\`\`

### Actieknoppen

#### 1. Exporteren
\`\`\`typescript
<Button variant="outline" size="sm">
  <Download /> Exporteren
</Button>
\`\`\`
- Exporteert het voorstel (functionaliteit nog te implementeren)

#### 2. Notificatie
\`\`\`typescript
<Button variant="outline" size="sm">
  <Mail /> Notificatie
</Button>
\`\`\`
- Stuurt notificatie over het voorstel (functionaliteit nog te implementeren)

#### 3. Goedkeuren
\`\`\`typescript
<Button 
  size="sm" 
  className="bg-green-600 hover:bg-green-700" 
  onClick={handleApprove}
>
  <Check /> Goedkeuren
</Button>
\`\`\`

**Functionaliteit:**
1. Toont visuele feedback (groene overlay met checkmark)
2. Animeert voortgangsbalk (indien in batch-modus)
3. Navigeert automatisch naar volgend voorstel of terug naar batch-overzicht

**Tooltip (bij batch-modus):**
\`\`\`
Voortgang reeks: 26% → 29% (+3%)
Na goedkeuring wordt het volgende voorstel automatisch geopend
\`\`\`

**Implementatie:**
\`\`\`typescript
const handleApprove = () => {
  // 1. Toon visuele feedback
  const overlay = document.createElement("div")
  overlay.className = "fixed inset-0 bg-green-500/20 flex items-center justify-center z-50"
  overlay.innerHTML = `<div class="bg-white rounded-full p-6 shadow-lg">
    <svg><!-- Checkmark icon --></svg>
  </div>`
  document.body.appendChild(overlay)

  // 2. Update voortgangsbalk
  if (totalInBatch > 0) {
    const progressBar = document.querySelector(".progress-bar-inner")
    if (progressBar) {
      progressBar.style.width = `${progressAfterApproval}%`
    }
  }

  // 3. Navigeer na korte delay
  setTimeout(() => {
    overlay.style.opacity = "0"
    setTimeout(() => {
      document.body.removeChild(overlay)
      
      if (batchId) {
        const nextProposalId = (parseInt(id) + 1).toString()
        const hasNextProposal = completedInBatch < totalInBatch - 1

        if (hasNextProposal) {
          router.push(`/proposals/${nextProposalId}?batchId=${batchId}`)
        } else {
          router.push(`/proposals/batch/${batchId}`)
        }
      } else {
        router.back()
      }
    }, 500)
  }, 800)
}
\`\`\`

#### 4. Afwijzen
\`\`\`typescript
<Dialog>
  <DialogTrigger asChild>
    <Button size="sm" variant="destructive">
      <X /> Afwijzen
    </Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Voorstel Afwijzen</DialogTitle>
      <DialogDescription>
        Weet u zeker dat u dit voorstel wilt afwijzen? 
        Geef een reden op voor de afwijzing.
      </DialogDescription>
    </DialogHeader>
    <Textarea placeholder="Reden voor afwijzing..." />
    <DialogFooter>
      <Button variant="outline">Annuleren</Button>
      <Button variant="destructive">Afwijzen</Button>
      <Button className="bg-blue-600">
        <Edit /> Afwijzen & Bewerken
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
\`\`\`

**Opties in dialoog:**
1. **Annuleren**: Sluit dialoog zonder actie
2. **Afwijzen**: Wijst voorstel af met opgegeven reden
3. **Afwijzen & Bewerken**: Wijst af en opent bewerkingsmodus

**Tooltip (bij batch-modus):**
\`\`\`
Voortgang reeks: 26% → 29% (+3%)
\`\`\`

### Voortgangsberekeningen

\`\`\`typescript
const currentProgress = totalInBatch > 0 
  ? Math.round((completedInBatch / totalInBatch) * 100) 
  : 0

const progressAfterApproval = totalInBatch > 0 
  ? Math.round(((completedInBatch + 1) / totalInBatch) * 100) 
  : 0

const progressIncrease = progressAfterApproval - currentProgress
\`\`\`

## EditableProposalDetail Component

### Doel
Biedt een bewerkbare versie van het voorstel waar gebruikers voorraadaantallen kunnen aanpassen.

### Props Interface
Identiek aan `ProposalDetailProps`.

### State Management

\`\`\`typescript
const [proposalData, setProposalData] = useState(initialProposalData)
const [isBalanced, setIsBalanced] = useState(true)
const [hasChanges, setHasChanges] = useState(false)
const [totalDifference, setTotalDifference] = useState(0)
\`\`\`

### Kernfunctionaliteit

#### 1. Voorraad Bewerken
\`\`\`typescript
const handleInventoryChange = (
  storeIndex: number, 
  sizeIndex: number, 
  value: string
) => {
  const numValue = parseInt(value) || 0
  const newProposalData = { ...proposalData }
  newProposalData.stores[storeIndex].inventoryProposed[sizeIndex] = numValue
  setProposalData(newProposalData)
}
\`\`\`

Elke voorraadcel is een bewerkbaar `Input` veld:
\`\`\`typescript
<Input
  type="number"
  value={qty}
  onChange={(e) => handleInventoryChange(storeIndex, sizeIndex, e.target.value)}
  className="w-12 h-8 text-center p-0"
  min="0"
/>
\`\`\`

#### 2. Balans Controle
Het systeem controleert continu of de totale voorraad gebalanceerd is:

\`\`\`typescript
useEffect(() => {
  let totalDiff = 0
  for (let i = 0; i < totalsCurrent.length; i++) {
    totalDiff += totalsProposed[i] - totalsCurrent[i]
  }
  setTotalDifference(totalDiff)
  setIsBalanced(totalDiff === 0)
  
  // Check voor wijzigingen
  const hasAnyChanges = proposalData.stores.some((store, storeIndex) => {
    return store.inventoryProposed.some((proposed, sizeIndex) => {
      return proposed !== initialProposalData.stores[storeIndex].inventoryProposed[sizeIndex]
    })
  })
  setHasChanges(hasAnyChanges)
  
  // Dispatch event naar parent component
  window.dispatchEvent(new CustomEvent("proposalStateChange", {
    detail: { isBalanced: totalDiff === 0, hasChanges: hasAnyChanges }
  }))
}, [proposalData, totalsCurrent, totalsProposed])
\`\`\`

**Balans Regel:**
\`\`\`
Σ(voorgestelde voorraad per maat) = Σ(huidige voorraad per maat)
\`\`\`

Voor elke maat moet gelden:
\`\`\`
totalsProposed[i] === totalsCurrent[i]
\`\`\`

#### 3. Visuele Feedback

**Totalen Rij:**
- **Rood** (`bg-red-100`): Ongebalanceerde maat
- Toont verschil: `+2` (teveel) of `-1` (te weinig)

\`\`\`typescript
<TableCell className={hasImbalance ? "bg-red-100" : ""}>
  <div className="flex flex-col items-center">
    <span>{proposedTotal}</span>
    {diff !== 0 && (
      <span className={diff > 0 ? "text-green-500" : "text-red-500"}>
        {diff > 0 ? `+${diff}` : diff}
      </span>
    )}
  </div>
</TableCell>
\`\`\`

**Voorraad Cellen:**
- **Blauw** (`bg-blue-100`): Gewijzigde voorraad
- Pijl indicator onder cel: ↑ (toegevoegd) of ↓ (verwijderd)

\`\`\`typescript
{diff !== 0 && (
  <span className={diff > 0 ? "text-green-500" : "text-red-500"}>
    {diff > 0 ? <ArrowUp /> : <ArrowDown />}
    {Math.abs(diff)}
  </span>
)}
\`\`\`

#### 4. Reset Functionaliteit
\`\`\`typescript
const resetProposal = () => {
  setProposalData(initialProposalData)
  setHasChanges(false)
}
\`\`\`

Knop is alleen actief wanneer er wijzigingen zijn:
\`\`\`typescript
<Button 
  variant="outline" 
  size="sm" 
  onClick={resetProposal} 
  disabled={!hasChanges}
>
  Resetten naar origineel
</Button>
\`\`\`

#### 5. Opslaan Validatie
De opslaan-knop (in parent component) is alleen actief wanneer:
1. De voorraad gebalanceerd is (`isBalanced === true`)
2. Er wijzigingen zijn aangebracht (`hasChanges === true`)

\`\`\`typescript
const saveButton = document.getElementById("save-button")
if (saveButton) {
  saveButton.disabled = !isBalanced || !hasChanges
}
\`\`\`

### Badges en Status Indicatoren

\`\`\`typescript
<div className="flex items-center gap-2">
  <Button onClick={resetProposal} disabled={!hasChanges}>
    Resetten naar origineel
  </Button>
  <Badge variant={isBalanced ? "outline" : "destructive"}>
    {isBalanced ? "Gebalanceerd" : "Ongebalanceerd"}
  </Badge>
  {hasChanges && <Badge variant="default">Gewijzigd</Badge>}
</div>
\`\`\`

## Bewerkbare Route: app/proposals/[id]/edit/page.tsx

### Structuur
Vergelijkbaar met de hoofdpagina, maar gebruikt `EditableProposalDetail` in plaats van `ProposalDetail`:

\`\`\`typescript
export default function EditProposalPage({
  params,
  searchParams,
}: {
  params: { id: string }
  searchParams: { batchId?: string }
}) {
  // ... batch info setup ...

  return (
    <DashboardShell>
      <Button variant="ghost" size="sm" asChild>
        <Link href={`/proposals/${params.id}${batchId ? `?batchId=${batchId}` : ""}`}>
          <ArrowLeft /> Terug naar voorstel
        </Link>
      </Button>
      
      <DashboardHeader heading={`Voorstel #${params.id} Bewerken`}>
        <EditProposalActions
          id={params.id}
          batchId={batchId}
          totalInBatch={batchInfo?.totalProposals}
          completedInBatch={batchInfo?.assessedProposals}
        />
      </DashboardHeader>
      
      <EditableProposalDetail 
        id={params.id} 
        batchId={batchId} 
        batchInfo={batchInfo} 
      />
    </DashboardShell>
  )
}
\`\`\`

### EditProposalActions Component
Bevat aangepaste actieknoppen voor de bewerkingsmodus:

\`\`\`typescript
<div className="flex items-center gap-2">
  <Button 
    variant="outline" 
    onClick={() => router.back()}
  >
    Annuleren
  </Button>
  
  <Button 
    id="save-button"
    className="bg-blue-600 hover:bg-blue-700"
    onClick={handleSave}
    disabled={!isBalanced || !hasChanges}
  >
    <Save /> Opslaan & Goedkeuren
  </Button>
</div>
\`\`\`

**Opslaan Logica:**
\`\`\`typescript
const handleSave = () => {
  // 1. Valideer balans
  if (!isBalanced) {
    toast({
      title: "Ongebalanceerde herverdeling",
      description: "De totale voorraad moet gelijk blijven.",
      variant: "destructive"
    })
    return
  }

  // 2. Sla wijzigingen op (API call)
  // await saveProposal(id, proposalData)

  // 3. Toon success feedback
  toast({
    title: "Voorstel opgeslagen",
    description: "Het voorstel is succesvol bijgewerkt en goedgekeurd."
  })

  // 4. Navigeer naar volgend voorstel of terug
  if (batchId) {
    const nextProposalId = (parseInt(id) + 1).toString()
    const hasNextProposal = completedInBatch < totalInBatch - 1

    if (hasNextProposal) {
      router.push(`/proposals/${nextProposalId}?batchId=${batchId}`)
    } else {
      router.push(`/proposals/batch/${batchId}`)
    }
  } else {
    router.push(`/proposals/${id}`)
  }
}
\`\`\`

## Navigatie Flows

### 1. Standalone Voorstel (zonder batch)
\`\`\`
/proposals → /proposals/[id] → /proposals
                ↓
         /proposals/[id]/edit
\`\`\`

### 2. Batch Voorstel
\`\`\`
/proposals/batch/[batchId] → /proposals/[id]?batchId=X → /proposals/[id+1]?batchId=X → ... → /proposals/batch/[batchId]
                                      ↓
                              /proposals/[id]/edit?batchId=X
\`\`\`

### 3. Goedkeuren in Batch
\`\`\`
Voorstel #1 (goedkeuren) → Voorstel #2 (goedkeuren) → ... → Voorstel #42 (goedkeuren) → Batch Overzicht
\`\`\`

### 4. Afwijzen & Bewerken
\`\`\`
/proposals/[id] → [Afwijzen & Bewerken] → /proposals/[id]/edit → [Opslaan] → /proposals/[id+1] (of batch overzicht)
\`\`\`

## Data Flow

### 1. Server → Client
\`\`\`
URL Parameters (id, batchId)
    ↓
Server Component (page.tsx)
    ↓
Batch Info Simulatie
    ↓
Props naar Child Components
    ↓
ProposalDetail / EditableProposalDetail
    ↓
Hardcoded Sample Data (in productie: API call)
\`\`\`

### 2. Client State Updates (Bewerkingsmodus)
\`\`\`
User Input (wijzigt voorraad)
    ↓
handleInventoryChange
    ↓
setProposalData (state update)
    ↓
useEffect (balans controle)
    ↓
Update UI (badges, kleuren, button states)
    ↓
Custom Event Dispatch
    ↓
Parent Component (EditProposalActions)
\`\`\`

### 3. Acties → Navigatie
\`\`\`
User Action (goedkeuren/afwijzen/opslaan)
    ↓
Visuele Feedback (overlay, animaties)
    ↓
State Update / API Call
    ↓
Toast Notificatie
    ↓
Router Navigation (volgend voorstel of terug)
\`\`\`

## Styling en UI Patterns

### Kleurenschema

| Element | Kleur | Betekenis |
|---------|-------|-----------|
| Groene achtergrond | `bg-green-100` | Huidige voorraad (in vergelijking) |
| Blauwe achtergrond | `bg-blue-100` | Voorgestelde/gewijzigde voorraad |
| Rode achtergrond | `bg-red-100` | Ongebalanceerde totalen |
| Groene tekst | `text-green-500` | Positief verschil (toegevoegd) |
| Rode tekst | `text-red-500` | Negatief verschil (verwijderd) |
| Groene knop | `bg-green-600` | Goedkeuren actie |
| Rode knop | `bg-red-600` | Afwijzen actie |
| Blauwe knop | `bg-blue-600` | Bewerken/Opslaan actie |

### Responsive Design

De tabel gebruikt `overflow-x-auto` voor horizontaal scrollen op kleine schermen:

\`\`\`typescript
<div className="rounded-md border overflow-x-auto">
  <Table>
    {/* ... */}
  </Table>
</div>
\`\`\`

Artikel informatie gebruikt responsive grid:
\`\`\`typescript
<div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
  {/* 1 kolom op mobiel, 2 op tablet, 3 op desktop */}
</div>
\`\`\`

### Animaties

**Voortgangsbalk:**
\`\`\`css
.progress-bar-inner {
  transition: width 0.5s ease-in-out;
}
\`\`\`

**Goedkeurings Overlay:**
\`\`\`typescript
overlay.style.transition = "opacity 0.5s"
overlay.style.opacity = "0"  // Fade out
\`\`\`

## Toekomstige Uitbreidingen

### Backend Integratie

In productie moet de hardcoded data vervangen worden door API calls:

\`\`\`typescript
// In page.tsx (Server Component)
async function getProposal(id: string) {
  const res = await fetch(`/api/proposals/${id}`)
  return res.json()
}

async function getBatchInfo(batchId: string) {
  const res = await fetch(`/api/batches/${batchId}`)
  return res.json()
}

export default async function ProposalDetailPage({ params, searchParams }) {
  const proposal = await getProposal(params.id)
  const batchInfo = searchParams.batchId 
    ? await getBatchInfo(searchParams.batchId)
    : undefined

  return (
    <DashboardShell>
      <ProposalDetail proposal={proposal} batchInfo={batchInfo} />
    </DashboardShell>
  )
}
\`\`\`

### Drag & Drop Functionaliteit

Voor een meer intuïtieve bewerkingservaring kan drag-and-drop worden toegevoegd:

\`\`\`typescript
// Gebruik react-dnd of @dnd-kit
import { DndContext, useDraggable, useDroppable } from '@dnd-kit/core'

// Implementeer drag van voorraad tussen winkels
const handleDragEnd = (event) => {
  const { active, over } = event
  // Verplaats voorraad van active naar over
}
\`\`\`

### Real-time Samenwerking

Voor teams die tegelijkertijd voorstellen beoordelen:

\`\`\`typescript
// Gebruik WebSockets of Server-Sent Events
useEffect(() => {
  const ws = new WebSocket(`/api/proposals/${id}/subscribe`)
  
  ws.onmessage = (event) => {
    const update = JSON.parse(event.data)
    // Update UI met wijzigingen van andere gebruikers
  }
  
  return () => ws.close()
}, [id])
\`\`\`

### Audit Trail

Logging van alle wijzigingen voor compliance:

\`\`\`typescript
interface ProposalChange {
  timestamp: Date
  userId: string
  action: 'approve' | 'reject' | 'edit'
  changes?: {
    storeId: string
    sizeIndex: number
    oldValue: number
    newValue: number
  }[]
  comment?: string
}
\`\`\`

## Troubleshooting

### Probleem: Voortgangsbalk update niet
**Oplossing:** Zorg dat de progress bar element de class `.progress-bar-inner` heeft:
\`\`\`typescript
<div className="progress-bar-inner" style={{ width: `${progressPercentage}%` }} />
\`\`\`

### Probleem: Opslaan knop blijft disabled
**Oplossing:** Check of de custom event correct wordt afgevuurd:
\`\`\`typescript
window.dispatchEvent(new CustomEvent("proposalStateChange", {
  detail: { isBalanced, hasChanges }
}))
\`\`\`

### Probleem: Navigatie werkt niet na goedkeuring
**Oplossing:** Controleer of `batchId` correct wordt doorgegeven in de URL:
\`\`\`typescript
router.push(`/proposals/${nextId}?batchId=${batchId}`)
\`\`\`

### Probleem: Totalen kloppen niet
**Oplossing:** Verify dat alle stores worden meegenomen in de reduce:
\`\`\`typescript
const totals = proposalData.sizes.map((_, sizeIndex) => {
  return proposalData.stores.reduce(
    (acc, store) => acc + store.inventoryProposed[sizeIndex], 
    0  // ← Vergeet de initial value niet!
  )
})
\`\`\`

## Conclusie

De `app/proposals/[id]` route is een complexe maar goed gestructureerde feature die:
- Gedetailleerde voorstelinformatie toont
- Batch-verwerking ondersteunt met voortgangsindicatie
- Bewerkbare modus biedt met real-time validatie
- Intuïtieve navigatie tussen voorstellen faciliteert
- Visuele feedback geeft bij alle acties

De scheiding tussen alleen-lezen (`ProposalDetail`) en bewerkbare (`EditableProposalDetail`) componenten zorgt voor duidelijke verantwoordelijkheden en herbruikbaarheid.

# UX Improvements - Stephany Brainstormsessie

**Datum:** 5 november 2025  
**Bron:** `docs/Brainstormsessie met stephany.docx`  
**Status:** 📋 Todo - Moet geïmplementeerd worden  

---

## 📋 Overzicht

Dit document bevat de concrete UX verbeteringen uit de brainstormsessie met Stephany. Alle items (behalve het ideeënbusje voor automatische artikel selectie) moeten één voor één een plek krijgen in het project.

**Prioriteit Volgorde:**
1. 🔴 HOOG: Items die direct de workflow verbeteren
2. 🟡 MEDIUM: UI verbeteringen voor gebruikerservaring  
3. 🟢 LAAG: Nice-to-have polish items

---

## 🎯 Concrete Verbeteringen

### 1. Full Screen View zonder Scrollen (1080p Optimalisatie)
**Prioriteit:** 🟡 MEDIUM  
**Categorie:** UI Optimalisatie  
**Status:** ⏳ Todo

#### Beschrijving
Optimaliseer de layout zodat alle informatie op een 1080p scherm volledig zichtbaar is zonder te scrollen.

#### Technische Specificaties
- **Target Resolutie:** 1920x1080 pixels
- **Componenten:** Proposal detail page, comparison views
- **Aanpak:** 
  - Gebruik van compact grid layouts
  - Efficiente ruimte-verdeling
  - Mogelijk collapsable sections waar nodig

#### Acceptatie Criteria
- [ ] Alle belangrijke informatie past op 1080p scherm
- [ ] Geen verticale scroll nodig voor hoofdweergave
- [ ] Responsive design blijft behouden voor andere resoluties

#### Bestanden
- `frontend/app/proposals/[id]/page.tsx`
- `frontend/components/proposals/proposal-detail.tsx`

---

### 2. Collapsable Artikel Header (Metadata)
**Prioriteit:** 🟡 MEDIUM  
**Categorie:** UI/UX Verbetering  
**Status:** ⏳ Todo

#### Beschrijving
De header van een artikel detail pagina moet collapsable zijn. Wanneer ingeklapt blijft alleen de essentiele info zichtbaar in één compacte regel.

#### Zichtbare Info (Ingeklapt)
```
Volgnummer: xxxx | Leverancier: 0 Xxxxx | Hoofdgroep: 0 Xxxxx | Omschrijving: Xxxxx | Kleur: [Kleurnaam]
```

#### Zichtbare Info (Uitgeklapt)
- Alle metadata velden
- Alle detail informatie
- Normale full-size header

#### Technische Specificaties
- **Component:** Article metadata header
- **State Management:** useState voor collapsed/expanded state
- **Storage:** localStorage voor user preference (optioneel)
- **Animation:** Smooth expand/collapse transition

#### UI Design
```tsx
// Ingeklapt (1 regel, compact)
┌────────────────────────────────────────────────────────────┐
│ ▶ Volgnummer: 422557 | Leverancier: 0 Vendor | Hoofdg... │
└────────────────────────────────────────────────────────────┘

// Uitgeklapt (volledig)
┌────────────────────────────────────────────────────────────┐
│ ▼ Artikel Details                                          │
│                                                             │
│   Volgnummer: 422557                                       │
│   Leverancier: 0 Vendor Name                               │
│   Hoofdgroep: 0 Category                                   │
│   Omschrijving: Full Description Here                      │
│   Kleur: Zwart                                             │
│   [... meer velden ...]                                    │
└────────────────────────────────────────────────────────────┘
```

#### Acceptatie Criteria
- [ ] Header is collapsable met expand/collapse button
- [ ] Ingeklapte state toont essentiele info in één regel
- [ ] Uitgeklapte state toont alle metadata
- [ ] Smooth animatie tussen states
- [ ] User preference wordt onthouden (optioneel)

#### Bestanden
- `frontend/components/proposals/article-header.tsx` (nieuw)
- `frontend/app/proposals/[id]/page.tsx` (update)

---

### 3. Vierkantjes Visual Feedback (Border Verdikking)
**Prioriteit:** 🟢 LAAG  
**Categorie:** Visual Polish  
**Status:** ⏳ Todo

#### Beschrijving  
In het bewerk herverdelingsscherm moeten de vierkantjes (cellen met voorraad aantallen) een dikkere border krijgen wanneer voorraad > 0. Deze feedback moet dynamisch updaten tijdens het aanpassen van het voorstel.

#### Technische Specificaties
- **Component:** Voorraad cell in edit grid
- **CSS Logic:**
  ```css
  .voorraad-cell {
    border: 1px solid #ccc;  /* Default */
  }
  
  .voorraad-cell.has-stock {
    border: 3px solid #3b82f6;  /* Dikker bij voorraad > 0 */
    font-weight: 600;
  }
  ```
- **Dynamic Update:** Real-time tijdens editing
- **Visual Feedback:** Duidelijk onderscheid tussen lege en gevulde cellen

#### Acceptatie Criteria
- [ ] Cellen met voorraad > 0 hebben dikkere border
- [ ] Update gebeurt real-time tijdens editing
- [ ] Visueel duidelijk onderscheid
- [ ] Dark mode compatible

#### Bestanden
- `frontend/components/proposals/edit-grid.tsx`
- `frontend/app/proposals/[id]/edit/page.tsx`

---

### 4. Afwijzen Workflow: Eerst Corrigeren, Dan Feedback  
**Prioriteit:** 🔴 HOOG  
**Categorie:** Workflow Verbetering  
**Status:** ⏳ Todo

#### Beschrijving
Bij het afwijzen van een voorstel moet de gebruiker EERST kunnen corrigeren, en DAARNA feedback kunnen geven waarom het voorstel niet goed was. Dit is praktischer dan eerst typen en dan pas kunnen corrigeren.

#### Huidige Flow (❌ Onpraktisch)
```
1. Reject button
2. Typ feedback waarom rejected
3. Geen mogelijkheid tot direct corrigeren
```

#### Nieuwe Flow (✅ Praktisch)
```
1. Reject button
2. Open edit mode om correcties te maken
3. Na correcties: vraag om feedback waarom origineel niet goed was
4. Submit rejection met correcties + feedback
```

#### Technische Specificaties
- **Flow Control:** State machine voor rejection flow
- **Edit Mode:** Seamless overgang naar edit view
- **Feedback Form:** Modal/panel na correcties
- **Data Storage:** Zowel correcties als feedback opslaan

#### UI Flow
```
┌─────────────────────────────────────────┐
│  Voorstel Detail                        │
│  [Approve] [Reject] [Edit]              │
└─────────────────────────────────────────┘
                ↓ (Reject clicked)
┌─────────────────────────────────────────┐
│  ⚠ Voorstel Afwijzen                    │
│                                          │
│  Wil je eerst correcties maken?         │
│  [Ja, bewerk eerst] [Nee, direct afwijz]│
└─────────────────────────────────────────┘
                ↓ (Ja, bewerk eerst)
┌─────────────────────────────────────────┐
│  Edit Mode                               │
│  [Maak correcties...]                   │
│  [Klaar met correcties]                 │
└─────────────────────────────────────────┘
                ↓ (Klaar)
┌─────────────────────────────────────────┐
│  Feedback Geven                          │
│  Waarom was het origineel niet goed?    │
│  [Text area...]                         │
│  [Afwijzen met feedback]                │
└─────────────────────────────────────────┘
```

#### Acceptatie Criteria
- [ ] Reject button opent keuze: edit first of direct reject
- [ ] Edit mode is gemakkelijk toegankelijk vanuit reject flow
- [ ] Na edits: feedback form wordt getoond
- [ ] Beide correcties en feedback worden opgeslagen
- [ ] Duidelijke stappen in de workflow

#### Bestanden
- `frontend/components/proposals/reject-flow.tsx` (nieuw)
- `frontend/app/proposals/[id]/page.tsx` (update)
- `backend/routers/redistribution.py` (update rejection endpoint)

---

### 5. Routing Tabblad + Goedkeuren Workflow
**Prioriteit:** 🔴 HOOG  
**Categorie:** Nieuwe Feature  
**Status:** ⏳ Todo

#### Beschrijving
Na goedkeuring van een voorstel (of na correctie en goedkeuring), wordt de gebruiker naar een nieuw "Routing" tabblad gestuurd. Dit tabblad is de default view na goedkeuring en toont welk filiaal wat wegsstuurt naar welk ander filiaal.

#### Routing Tabblad Specificaties

**Locatie:** Nieuw tabblad naast "Vergelijking" en "Huidige Situatie"  
**Visibility:** Alleen zichtbaar NA goedkeuring  
**Default:** Wordt automatisch active tab na approve action

#### Functionaliteit
Het routing tabblad toont:
- Huidige situatie per filiaal (vóór herverdeling)
- Naar welk filiaal elke maat verhuist (in nieuwe situatie)
- "Ballonnetjes" visualisatie per maat per winkel

#### Ballonnetjes Visualisatie

**Gebaseerd op screenshot:**
```
Filiaal  | XXS | S | M | L | XL | XXL | Verkocht
---------|-----|---|---|---|----|----|----------
8 Weert  |  .  | . | . | . | 2  | 1  |    5
                           [1x 12]
                           [1x 13]
```

**Betekenis:**
- `1x 12` = 1 stuks XL gaat naar filiaal 12
- `1x 13` = 1 stuks XXL gaat naar filiaal 13
- Ballonnetjes = visuele indicators onder de voorraad cijfers

#### Technische Specificaties

**Tab Structure:**
```tsx
<Tabs defaultValue="routing">  // Na approve!
  <TabsList>
    <TabsTrigger value="vergelijking">Vergelijking</TabsTrigger>
    <TabsTrigger value="huidige">Huidige Situatie</TabsTrigger>
    <TabsTrigger value="routing">Routing</TabsTrigger>  // NEW
  </TabsList>
  
  <TabsContent value="routing">
    <RoutingOverview proposal={proposal} />
  </TabsContent>
</Tabs>
```

**Data Structure:**
```typescript
interface RoutingMove {
  fromStore: string;      // "8 Weert"
  toStore: string;        // "12" (filiaal nummer)
  toStoreName: string;    // "12 Venlo" (volledige naam)
  size: string;           // "XL"
  quantity: number;       // 1
}

interface RoutingData {
  articleNumber: string;
  moves: RoutingMove[];
  storeInventory: {
    [storeCode: string]: {
      storeName: string;
      inventory: { [size: string]: number };
      outgoing: RoutingMove[];  // Wat gaat weg
      incoming: RoutingMove[];  // Wat komt aan
    }
  }
}
```

**Visual Design:**
```
┌──────────────────────────────────────────────────────────┐
│  Routing Overzicht                                        │
│  Transacties tussen filialen                             │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Filiaal    │ XXS │  S  │  M  │  L  │  XL  │ XXL │ Verk │
│  ──────────────────────────────────────────────────────  │
│  8 Weert    │  -  │  -  │  -  │  -  │  2   │  1  │  5  │
│             │     │     │     │     │ ↓ 1→12│ ↓ 1→13│   │
│             │     │     │     │     │[1x12] │[1x13] │   │
│  ──────────────────────────────────────────────────────  │
│  12 Venlo   │  -  │  -  │  -  │  -  │  3   │  2  │  8  │
│             │     │     │     │     │ ↑ 1←8 │      │    │
│  ──────────────────────────────────────────────────────  │
│  13 Sittard │  -  │  -  │  -  │  1  │  4   │  3  │ 10  │
│             │     │     │     │     │      │ ↑ 1←8│    │
│                                                           │
│  [Minimale transacties: 2]                               │
│  [Betrokken filialen: 3]                                 │
│                                                           │
│  [< Terug naar Vergelijking] [Volgende Artikel >]       │
└──────────────────────────────────────────────────────────┘
```

**Ballonnetje Component:**
```tsx
interface BalloonProps {
  quantity: number;
  fromStore: string;
  toStore: string;
  toStoreName: string;
}

function RoutingBalloon({ quantity, fromStore, toStore, toStoreName }: BalloonProps) {
  return (
    <div className="inline-block px-2 py-1 bg-blue-100 dark:bg-blue-900 rounded border border-blue-300 text-xs">
      {quantity}x → {toStore}
      <span className="ml-1 text-muted-foreground">({toStoreName})</span>
    </div>
  );
}
```

#### Workflow Integratie

**Voor Approve:**
```
Tabs: [Vergelijking] [Huidige Situatie]
      └─ defaultValue="vergelijking"
```

**Na Approve:**
```
Tabs: [Vergelijking] [Huidige Situatie] [Routing]
      └─ defaultValue="routing"  // Auto-switch!
```

#### Acceptatie Criteria
- [ ] Routing tab bestaat en is functioneel
- [ ] Tab is NIET zichtbaar vóór goedkeuring
- [ ] Tab wordt zichtbaar NA goedkeuring
- [ ] Tab wordt automatisch active NA goedkeuring
- [ ] Ballonnetjes tonen correcte routing info (Nx → filiaal)
- [ ] Alle moves worden correct weergegeven
- [ ] Summary info: totaal transacties, betrokken filialen
- [ ] "Volgende Artikel" navigatie werkt

#### Bestanden
- `frontend/components/proposals/routing-tab.tsx` (nieuw)
- `frontend/components/proposals/routing-balloon.tsx` (nieuw)
- `frontend/components/proposals/routing-overview.tsx` (nieuw)
- `frontend/app/proposals/[id]/page.tsx` (update tabs)
- `backend/routers/redistribution.py` (routing data endpoint)

---

### 6. UX Flow Update: Voorstel → Routing → Volgende Artikel
**Prioriteit:** 🔴 HOOG  
**Categorie:** Workflow Verbetering  
**Status:** ⏳ Todo

#### Beschrijving
Na goedkeuring of correctie+goedkeuring van een voorstel, moet de flow naar het Routing tabblad gaan voor routing check. Na goedkeuring van de routing, doorgaan naar het volgende artikel.

#### Complete Flow

```
┌─────────────────────────────────────────┐
│  1. Voorstel Bekijken                   │
│     [Approve] [Reject] [Edit]           │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  2a. Approve clicked                     │
│      OF                                  │
│  2b. Edit → Save → Approve              │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  3. Auto-redirect naar Routing Tab      │
│     [Routing wordt getoond]             │
│     - Controleer transacties            │
│     - Minimale aantal moves?            │
│     - Logische verdeling?               │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  4. Routing Goedkeuren                   │
│     [Bevestig Routing] [Annuleer]       │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  5. Success → Volgende Artikel           │
│     [Naar Artikel 422558 >]             │
└─────────────────────────────────────────┘
```

#### Technische Specificaties

**State Management:**
```typescript
enum ProposalState {
  VIEWING = 'viewing',           // Initial state
  EDITING = 'editing',           // Edit mode
  APPROVED_PENDING = 'approved_pending',  // Approved, awaiting routing check
  ROUTING_CHECK = 'routing_check',   // Shown routing, awaiting confirm
  COMPLETED = 'completed'        // Routing confirmed, ready for next
}
```

**Navigation Logic:**
```tsx
function handleApprove() {
  // 1. Save approval
  await approveProposal(proposalId);
  
  // 2. Switch to routing tab
  setActiveTab('routing');
  
  // 3. Update state
  setProposalState(ProposalState.ROUTING_CHECK);
  
  // 4. Show routing confirmation UI
  setShowRoutingConfirm(true);
}

function handleRoutingConfirm() {
  // 1. Confirm routing
  await confirmRouting(proposalId);
  
  // 2. Navigate to next article
  router.push(`/proposals/${nextArticleId}`);
  
  // 3. Show success toast
  toast.success('Voorstel goedgekeurd! Doorgaan naar volgend artikel.');
}
```

#### UI Elements

**Routing Confirmation Panel:**
```tsx
{proposalState === ProposalState.ROUTING_CHECK && (
  <Card className="mt-4 border-blue-500">
    <CardHeader>
      <CardTitle>Routing Controle</CardTitle>
      <CardDescription>
        Controleer de transacties tussen filialen voordat je doorgaat.
      </CardDescription>
    </CardHeader>
    <CardContent>
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="h-5 w-5 text-green-500" />
          <span>Minimale transacties: {minimalMoves}</span>
        </div>
        <div className="flex items-center gap-2">
          <Building2 className="h-5 w-5 text-blue-500" />
          <span>Betrokken filialen: {affectedStores}</span>
        </div>
      </div>
    </CardContent>
    <CardFooter className="flex gap-2">
      <Button onClick={handleRoutingConfirm}>
        Bevestig Routing & Naar Volgend Artikel
      </Button>
      <Button variant="outline" onClick={handleRoutingCancel}>
        Annuleer
      </Button>
    </CardFooter>
  </Card>
)}
```

#### Acceptatie Criteria
- [ ] Approve action leidt naar Routing tab
- [ ] Edit + Approve leidt ook naar Routing tab
- [ ] Routing tab toont confirmation UI
- [ ] "Bevestig Routing" button navigeert naar volgend artikel
- [ ] Success feedback wordt getoond
- [ ] Annuleer button werkt correct
- [ ] Smooth transitions tussen states

#### Bestanden
- `frontend/app/proposals/[id]/page.tsx` (update flow logic)
- `frontend/components/proposals/routing-confirmation.tsx` (nieuw)
- `frontend/lib/proposal-state-machine.ts` (nieuw, optioneel)

---

## 📊 Implementatie Volgorde

### Aanbevolen Aanpak
1. **Fase 1 (Hoog Prio):** Item 4, 5, 6 - Workflow verbeteringen
2. **Fase 2 (Medium Prio):** Item 1, 2 - UI optimalisaties
3. **Fase 3 (Low Prio):** Item 3 - Visual polish

### Dependencies
- Item 6 is afhankelijk van Item 5 (routing tab moet bestaan)
- Item 5 kan parallel met Item 4 ontwikkeld worden
- Item 1, 2, 3 zijn onafhankelijk

---

## 🔗 Gerelateerde Bestanden

### Screenshots
- Screenshot aanwezig in: `docs/Brainstormsessie met stephany.docx`
- Toont ballonnetjes visualisatie bij "8 Weert" rij

### Frontend Components (Te maken/updaten)
```
frontend/components/proposals/
├── article-header.tsx (nieuw - item 2)
├── edit-grid.tsx (update - item 3)
├── reject-flow.tsx (nieuw - item 4)
├── routing-tab.tsx (nieuw - item 5)
├── routing-balloon.tsx (nieuw - item 5)
├── routing-overview.tsx (nieuw - item 5)
├── routing-confirmation.tsx (nieuw - item 6)
└── proposal-detail.tsx (update - items 1,2,5,6)
```

### Backend Endpoints (Te maken/updaten)
```
backend/routers/redistribution.py
├── GET /api/proposals/{id}/routing (nieuw - routing data)
├── POST /api/proposals/{id}/confirm-routing (nieuw - confirm flow)
└── PUT /api/proposals/{id}/reject (update - rejection with edits)
```

---

## ✅ Volgende Stappen

1. Review dit document met het team
2. Maak GitHub issues per item
3. Prioriteer en plan sprints
4. Begin met Fase 1 (hoogste prioriteit)
5. Test elke verbetering met gebruiker feedback
6. Itereer op basis van feedback

---

## 📝 Notities

### Ideeënbusje (NIET Implementeren)
Het voorstel voor automatische artikel selectie artikelnummers uit de database is een toekomstvisie en wordt NIET in deze sprint opgenomen. Dit zou een groot apart project zijn. Hiervoor kan wel een .md in /todo/ komen in de toekomst.

### Screenshot Referenties
Alle screenshots zijn beschikbaar in het originele Word document: `docs/Brainstormsessie met stephany.docx`

---

**Laatste Update:** 5 november 2025  
**Eigenaar:** Digital Resupplying Tool Team  
**Status:** Klaar voor implementatie planning

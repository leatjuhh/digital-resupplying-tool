# Digital Resupplying Tool - Complete Project Overview

## 1. Project Beschrijving

### Doel
Een geautomatiseerde tool voor het beheren van voorraadherverdelingen tussen verschillende winkellocaties. Het systeem analyseert voorraadrapporten, genereert intelligente herverdelingsvoorstellen en faciliteert de goedkeuring en uitvoering hiervan.

### Scope
- **Frontend**: Next.js applicatie met React componenten
- **Backend**: REST API (te ontwikkelen in Cursor)
- **Database**: PostgreSQL (aanbevolen) of MySQL
- **Authenticatie**: JWT-based authentication
- **File Processing**: PDF parsing en data extractie
- **AI Integration**: OpenAI API voor intelligente regeloptimalisatie

### Belangrijke Use Cases
1. Gebruikers uploaden PDF voorraadrapporten
2. Systeem genereert automatisch herverdelingsvoorstellen
3. Gebruikers beoordelen en bewerken voorstellen
4. Goedgekeurde voorstellen worden omgezet in opdrachten
5. Winkels ontvangen en verwerken opdrachten
6. Admins analyseren feedback en optimaliseren regels

---

## 2. Gebruikersrollen en Rechten

### Admin
**Volledige toegang tot het systeem**

Rechten:
- Alle functionaliteiten van User
- Gebruikersbeheer (CRUD operaties)
- Toegang tot regelset configuratie
- Toegang tot feedback analyse
- AI-gestuurde regeloptimalisatie
- Systeeminstellingen beheren
- Analytics en rapportages bekijken

Specifieke Features:
- `/admin/users` - Gebruikersbeheer interface
- `/admin/ruleset` - Regelset editor
- `/admin/feedback` - Feedback dashboard met AI-suggesties

### User (Hoofdkantoor Medewerker)
**Toegang tot voorstellen beheren en uploads**

Rechten:
- Voorraadrapporten uploaden (PDF)
- Herverdelingsvoorstellen genereren
- Voorstellen bekijken, goedkeuren, afwijzen
- Voorstellen bewerken na afwijzing
- Feedback geven op voorstellen
- Opdrachten bekijken (read-only)
- Eigen profiel beheren

Workflow:
1. Upload PDF voorraadrapporten via `/uploads`
2. Genereer voorstellen automatisch
3. Beoordeel voorstellen in batches via `/proposals`
4. Bewerk indien nodig via `/proposals/[id]/edit`
5. Keur goed of wijs af met reden
6. Monitor status via dashboard

### Store (Winkel Medewerker)
**Alleen toegang tot toegewezen opdrachten**

Rechten:
- Toegewezen opdrachten bekijken
- Opdracht details inzien
- Opdracht status updaten (in progress, completed)
- Feedback geven op opdrachten
- Eigen profiel beheren

Beperkingen:
- Kan geen voorstellen zien of bewerken
- Kan geen uploads doen
- Kan geen andere winkels' opdrachten zien
- Geen toegang tot admin functies

Interface:
- Vereenvoudigde `/assignments` pagina
- Focus op uitvoering, niet op strategie

---

## 3. Kernfunctionaliteiten

### 3.1 Dashboard
**Hoofdpagina met overzichten en snelle acties**

Componenten:
- **Statistieken Cards**: Totaal voorstellen, goedgekeurd, afgewezen, in behandeling
- **Period Selector**: Filter op week/maand/kwartaal/jaar
- **Recent Activity**: Laatste 10 acties in het systeem
- **Notifications**: Nieuwe voorstellen, urgente opdrachten
- **Pending Proposals**: Top 5 wachtende voorstellen
- **Quick Actions**: Snelkoppelingen naar veel gebruikte functies

Dynamische Data:
- Real-time statistieken
- Activiteiten stream
- Prioriteit-gebaseerde notificaties

### 3.2 Uploads Management
**Handmatige en automatische upload van voorraadrapporten**

Features:
- **Manual Upload** (`/uploads`)
  - Drag & drop PDF interface
  - Multi-file upload support
  - File validation (PDF only, max 10MB)
  - Upload progress indicator
  - Recent uploads lijst met status

- **Automatic Generation**
  - Trigger na succesvolle upload
  - PDF parsing en data extractie
  - Series aanmaken per artikel
  - Batch proposal generatie
  - Error handling en retry logic

Data Flow:
\`\`\`
PDF Upload → Parse → Extract Data → Create Series → Generate Proposals → Batch
\`\`\`

### 3.3 Proposals System
**Kern van de applicatie: voorstellen beheren**

#### Proposals Overview (`/proposals`)
- **Filtering**: Status, datum, batch, artikel
- **Sorting**: Datum, prioriteit, status
- **Batch View**: Groepeer per upload batch
- **Individual View**: Lijst alle voorstellen
- **Quick Actions**: Bulk approve/reject

#### Batch Details (`/proposals/batch/[id]`)
- Overzicht van alle voorstellen in een batch
- Serie voortgang indicator (bijv. "3/10 goedgekeurd")
- Batch-level statistieken
- Lijst van voorstellen met click-through naar details

#### Proposal Detail (`/proposals/[id]`)
**Gedetailleerde weergave van een voorstel**

Informatie:
- Artikel details (SKU, naam, beschrijving)
- Huidige voorraad per vestiging per maat
- Voorgestelde herverdeling per vestiging per maat
- Totalen en balans check
- Historische data (indien beschikbaar)

Acties:
- **Approve**: Goedkeuren en direct naar volgend voorstel
- **Reject**: Afwijzen met reden, optie om te bewerken
- **Edit**: Ga naar edit mode (alleen na rejection)
- **Feedback**: Geef algemene feedback

UI Details:
- Hover over "Approve" toont voortgang toename
- Serie voortgang zichtbaar in header
- Automatische navigatie naar volgend voorstel na approve

#### Editable Proposal (`/proposals/[id]/edit`)
**Bewerkingsmodus na afwijzing**

Features:
- **Editable Table**: Direct invoer in cells
- **Balance Validation**: Real-time check of totalen kloppen
- **Reset Option**: "Resetten naar origineel" knop in header
- **Save & Approve**: Disabled tenzij:
  - Er zijn wijzigingen gemaakt
  - De balans is correct (totaal in = totaal uit)
- **Tooltip Feedback**: Bij hover op disabled button:
  - "Ongebalanceerde herverdeling" als balans niet klopt
  - "Geen wijzigingen gemaakt" als niets veranderd is
- **Red Highlighting**: Totaal-rij cellen worden rood als balans niet klopt

Validatie Regels:
\`\`\`typescript
isBalanced = (totaalIn === totaalUit) voor elke maat
hasChanges = (currentData !== originalData)
canSave = isBalanced && hasChanges
\`\`\`

UI Gedrag:
- Bij "Opslaan & Goedkeuren" → voorstel wordt approved
- Automatisch navigatie naar volgend voorstel in serie
- Bij "Annuleren" → terug naar detail view zonder opslaan

### 3.4 Assignments System
**Goedgekeurde voorstellen als concrete opdrachten**

#### Assignments Overview (`/assignments`)
- Lijst van alle opdrachten
- Filter op status: Pending, In Progress, Completed
- Filter op winkel (voor admins)
- Sorteer op prioriteit, datum
- Status badges met kleuren

#### Assignment Batch (`/assignments/[id]`)
- Groepeer opdrachten per originele batch
- Overzicht per winkel
- Batch-level status tracking
- Download opties (PDF, CSV)

#### Assignment Detail (`/assignments/[id]/[assignmentId]`)
- Volledige opdracht details
- Artikel informatie
- Te verplaatsen hoeveelheden per maat
- Van/naar winkel informatie
- Status update opties (alleen voor store users)
- Notities en feedback sectie

Store User Experience:
- Ziet alleen eigen winkel opdrachten
- Kan status updaten: Pending → In Progress → Completed
- Kan feedback geven bij problemen
- Simplified interface, focus op uitvoering

### 3.5 Feedback System
**Verzamel en analyseer gebruikersfeedback**

#### Feedback Submission
- Formulier bij elk voorstel/opdracht
- Categorieën: Hoeveelheid, Timing, Vestiging keuze, Anders
- Vrije tekst voor details
- Rating systeem (1-5 sterren)
- Attachments support (screenshots)

#### Feedback Dashboard (`/admin/feedback`)
**Admin-only toegang**

Features:
- Lijst van alle feedback entries
- Filter op categorie, datum, gebruiker
- Sentiment analyse (positief/negatief/neutraal)
- Aggregated insights
- Link naar gerelateerd voorstel/opdracht

AI Integration:
- Automatische sentiment detectie
- Patroon herkenning in feedback
- Suggesties voor regelaanpassingen
- Clustering van vergelijkbare feedback

#### Feedback Detail (`/admin/feedback/[id]`)
- Complete feedback entry
- Gerelateerd voorstel/opdracht details
- AI-gegenereerde analyse
- Voorgestelde regelaanpassingen
- Accept/Reject suggesties
- Follow-up notities

### 3.6 Ruleset Management
**AI-gestuurde regeloptimalisatie**

#### Ruleset Editor (`/admin/ruleset`)
**Admin-only toegang**

Components:
- **Current Rules Display**: Overzicht actieve regels
- **Rule Categories**:
  - Minimum voorraadniveaus per vestiging
  - Maximum voorraadniveaus
  - Herverdeling triggers (bijv. >20% verschil)
  - Prioriteitsregels (drukke vs. rustige vestigingen)
  - Seizoensregels
  - Artikel-specifieke regels

- **AI Suggestions Panel**:
  - Gebaseerd op verzamelde feedback
  - Statistical analysis van resultaten
  - A/B testing resultaten (indien beschikbaar)
  - Confidence scores per suggestie
  - Preview van impact

- **Rule Editor**:
  - JSON/YAML editor met syntax highlighting
  - Validation tegen schema
  - Test mode: simuleer impact op historische data
  - Version control: rollback naar vorige versies

AI Features:
\`\`\`typescript
interface AISuggestion {
  id: string
  category: RuleCategory
  currentRule: Rule
  suggestedRule: Rule
  reasoning: string
  confidenceScore: number
  basedOnFeedback: FeedbackEntry[]
  estimatedImpact: {
    approvalRateChange: number
    efficiencyGain: number
  }
}
\`\`\`

Workflow:
1. Admin bekijkt AI suggesties
2. Review reasoning en confidence score
3. Test suggestie op historische data
4. Accept/Modify/Reject suggestie
5. Deploy nieuwe regelset
6. Monitor impact

### 3.7 Settings
**Gebruikers- en systeeminstellingen**

#### User Settings
- Profiel informatie (naam, email, rol - read-only)
- Wachtwoord wijzigen
- Notificatie voorkeuren
- Taal/lokalisatie
- Theme (light/dark mode)

#### API Settings
**OpenAI API Key Management**

Features:
- API key invoer via UI (niet hardcoded)
- Secure opslag in cookies
- Validatie van key bij invoer
- Test connectie functie
- Key verwijderen optie
- Status indicator (connected/disconnected)

UI Flow:
\`\`\`
Settings → API Settings → Enter OpenAI Key → Validate → Save in Cookie → Use for AI features
\`\`\`

Security:
- Key wordt NOOIT in frontend code hardcoded
- Key wordt NOOIT in git committed
- Key wordt opgeslagen in secure httpOnly cookie
- Key wordt server-side opgehaald voor API calls

---

## 4. Gedetailleerde Feature Beschrijvingen

### 4.1 PDF Upload en Processing

#### Upload Flow
\`\`\`
1. User selecteert PDF bestand(en)
2. Frontend validatie: type, size, quantity
3. Upload naar server met progress tracking
4. Server opslag in temporary directory
5. Background job: PDF parsing
6. Data extractie naar structured format
7. Series aanmaken in database
8. Proposal generatie triggeren
9. User notificatie bij completion
\`\`\`

#### PDF Parsing Requirements
**Expected PDF Format:**
- Tabel met kolommen: Artikel, SKU, Vestiging, Maat, Voorraad
- Mogelijk meerdere paginas
- Mogelijk meerdere artikelen per PDF
- Mogelijk meerdere vestigingen per artikel

**Parsing Logica:**
\`\`\`python
# Pseudo-code voor PDF parsing
for page in pdf:
    tables = extract_tables(page)
    for table in tables:
        for row in table:
            article = row['Artikel']
            sku = row['SKU']
            location = row['Vestiging']
            size = row['Maat']
            stock = row['Voorraad']
            
            # Groepeer per artikel
            if article not in series:
                series[article] = create_series(article, sku)
            
            # Voeg voorraad toe
            series[article].add_stock(location, size, stock)

# Genereer voorstellen per serie
for series in series_list:
    proposals = generate_proposals(series)
    batch.add_proposals(proposals)
\`\`\`

#### Error Handling
- Invalid PDF format → User friendly error message
- Parsing failure → Retry mechanism + admin notification
- Incomplete data → Flag for manual review
- Duplicate uploads → Detect en waarschuwen

### 4.2 Proposal Generation Algorithm

#### Input Data
\`\`\`typescript
interface InventoryData {
  article: {
    sku: string
    name: string
    category: string
  }
  locations: {
    [locationId: string]: {
      name: string
      sizes: {
        [size: string]: number // current stock
      }
    }
  }
}
\`\`\`

#### Generation Logic
\`\`\`typescript
function generateProposal(inventory: InventoryData, rules: Ruleset): Proposal {
  // 1. Bereken totale voorraad per maat
  const totalPerSize = calculateTotals(inventory)
  
  // 2. Bepaal ideale distributie per vestiging
  const idealDistribution = calculateIdealDistribution(
    inventory,
    rules.minStock,
    rules.maxStock,
    rules.priority
  )
  
  // 3. Bereken verschil tussen current en ideal
  const redistributions = []
  for (const [location, data] of Object.entries(inventory.locations)) {
    for (const [size, currentStock] of Object.entries(data.sizes)) {
      const idealStock = idealDistribution[location][size]
      const difference = idealStock - currentStock
      
      if (Math.abs(difference) >= rules.minDifference) {
        redistributions.push({
          location,
          size,
          from: currentStock,
          to: idealStock,
          quantity: difference
        })
      }
    }
  }
  
  // 4. Optimaliseer: minimaliseer aantal transfers
  const optimized = optimizeTransfers(redistributions)
  
  // 5. Valideer: totaal in == totaal uit
  if (!validateBalance(optimized)) {
    throw new Error('Unbalanced redistribution')
  }
  
  return createProposal(inventory.article, optimized)
}
\`\`\`

#### Optimization Goals
1. **Minimaliseer transfers**: Zo min mogelijk afzonderlijke verplaatsingen
2. **Prioriteer vestigingen**: Drukke winkels eerst bedienen
3. **Respecteer limieten**: Min/max voorraad niet overschrijden
4. **Seizoensaanpassingen**: Rekening houden met seizoenspatronen

### 4.3 Proposal Editing System

#### Editing Rules
- Alleen mogelijk na rejection
- Wijzigingen moeten gebalanceerd zijn
- Alle maten kunnen onafhankelijk aangepast worden
- Reset optie beschikbaar

#### Balance Validation
\`\`\`typescript
interface ProposalState {
  original: InventoryDistribution
  current: InventoryDistribution
  hasChanges: boolean
  isBalanced: boolean
}

function validateBalance(state: ProposalState): boolean {
  for (const size of Object.keys(state.current)) {
    const totalIn = sumIncoming(state.current, size)
    const totalOut = sumOutgoing(state.current, size)
    
    if (totalIn !== totalOut) {
      return false
    }
  }
  return true
}

function hasChanges(original: any, current: any): boolean {
  return JSON.stringify(original) !== JSON.stringify(current)
}
\`\`\`

#### UI State Management
\`\`\`typescript
const [proposalState, setProposalState] = useState<ProposalState>({
  original: fetchedData,
  current: fetchedData,
  hasChanges: false,
  isBalanced: true
})

// Bij elke wijziging
const handleCellChange = (location: string, size: string, value: number) => {
  const updated = updateCell(proposalState.current, location, size, value)
  setProposalState({
    original: proposalState.original,
    current: updated,
    hasChanges: hasChanges(proposalState.original, updated),
    isBalanced: validateBalance(updated)
  })
}

// Save button state
const canSave = proposalState.hasChanges && proposalState.isBalanced
\`\`\`

### 4.4 Assignment Workflow

#### Conversion: Proposal → Assignment
\`\`\`typescript
async function approveProposal(proposalId: string): Promise<Assignment[]> {
  const proposal = await getProposal(proposalId)
  const assignments: Assignment[] = []
  
  // Groepeer redistribution per winkel
  const byStore = groupByStore(proposal.redistributions)
  
  for (const [storeId, items] of Object.entries(byStore)) {
    const assignment = {
      id: generateId(),
      proposalId: proposal.id,
      storeId: storeId,
      article: proposal.article,
      items: items,
      status: 'pending',
      createdAt: new Date(),
      dueDate: calculateDueDate(proposal.priority)
    }
    
    assignments.push(assignment)
    await createAssignment(assignment)
    await notifyStore(storeId, assignment)
  }
  
  await updateProposalStatus(proposalId, 'approved')
  return assignments
}
\`\`\`

#### Assignment Structure
\`\`\`typescript
interface Assignment {
  id: string
  proposalId: string
  batchId: string
  storeId: string
  storeName: string
  article: {
    sku: string
    name: string
  }
  items: AssignmentItem[]
  status: 'pending' | 'in_progress' | 'completed'
  createdAt: Date
  dueDate: Date
  completedAt?: Date
  notes?: string
  feedback?: Feedback[]
}

interface AssignmentItem {
  size: string
  action: 'send' | 'receive'
  quantity: number
  fromStore?: string
  toStore?: string
}
\`\`\`

#### Store User Actions
\`\`\`typescript
// Status update
async function updateAssignmentStatus(
  assignmentId: string,
  newStatus: AssignmentStatus,
  userId: string
): Promise<void> {
  // Valideer: user is toegewezen aan deze winkel
  const assignment = await getAssignment(assignmentId)
  const user = await getUser(userId)
  
  if (assignment.storeId !== user.storeId) {
    throw new Error('Unauthorized')
  }
  
  // Update status
  await updateStatus(assignmentId, newStatus)
  
  // Log activity
  await logActivity({
    type: 'assignment_status_update',
    userId,
    assignmentId,
    oldStatus: assignment.status,
    newStatus
  })
  
  // Notificeer admin als completed
  if (newStatus === 'completed') {
    await notifyAdmin(assignment)
  }
}
\`\`\`

---

## 5. UI/UX Richtlijnen

### Design System

#### Kleuren
- **Primary**: Brand kleur voor belangrijke acties
- **Secondary**: Voor ondersteunende elementen
- **Success**: Groen voor goedkeuringen (#10b981)
- **Destructive**: Rood voor afwijzingen en errors (#ef4444)
- **Warning**: Geel voor waarschuwingen (#f59e0b)
- **Muted**: Voor achtergronden en disabled states

#### Typography
- **Headings**: Bold, grotere font-size
- **Body**: Regular weight, leesbare font-size (16px)
- **Labels**: Medium weight, kleinere font-size (14px)
- **Code**: Monospace font voor technische data

#### Spacing
- Consistent gebruik van 4px grid
- Standaard spacing: 4, 8, 12, 16, 24, 32, 48px
- Cards: 16px padding
- Secties: 24-32px margins

#### Components
**Gebaseerd op shadcn/ui:**
- Button: Verschillende variants (default, outline, ghost, destructive)
- Card: Voor groepering van content
- Table: Voor data displays
- Form: Input fields met labels en validation
- Badge: Voor status indicatoren
- Dialog: Voor modals en confirmaties
- Tooltip: Voor extra informatie
- Select: Voor dropdowns
- Tabs: Voor navigatie binnen paginas

### Interactie Patronen

#### Navigatie
- Sidebar voor hoofdnavigatie
- Breadcrumbs voor diepere navigatie
- Back buttons waar logisch
- Auto-navigatie na acties (bijv. na approve → volgend voorstel)

#### Feedback
- Loading states voor async acties
- Success/error toasts voor acties resultaat
- Inline validation voor forms
- Disabled states met tooltips die uitleggen waarom

#### Data Display
- Tables voor lijsten met sorting en filtering
- Cards voor gegroepeerde informatie
- Badges voor statussen
- Progress bars voor serie voortgang
- Empty states met call-to-action

#### Forms
- Clear labels boven inputs
- Placeholder text voor guidance
- Validation messages onder inputs
- Required field indicators (*)
- Submit button disabled tot form valid is

### Responsive Design
- Desktop first approach
- Breakpoints: mobile (<640px), tablet (640-1024px), desktop (>1024px)
- Collapsible sidebar op mobile
- Stacked layouts op kleinere schermen
- Touch-friendly tap targets (min 44x44px)

### Accessibility
- Semantic HTML
- ARIA labels waar nodig
- Keyboard navigation support
- Focus indicators
- Screen reader friendly
- Contrast ratios volgens WCAG guidelines

---

## 6. Datastructuren

### User
\`\`\`typescript
interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'user' | 'store'
  storeId?: string // Alleen voor role === 'store'
  storeName?: string
  createdAt: Date
  lastLogin?: Date
  isActive: boolean
  preferences: {
    theme: 'light' | 'dark'
    language: string
    notifications: {
      email: boolean
      inApp: boolean
    }
  }
}
\`\`\`

### Store/Location
\`\`\`typescript
interface Store {
  id: string
  name: string
  code: string // Winkelcode zoals in PDF
  address: string
  city: string
  priority: 'high' | 'medium' | 'low' // Voor distributie prioriteit
  isActive: boolean
  metadata: {
    size: 'small' | 'medium' | 'large'
    footfall: 'high' | 'medium' | 'low'
  }
}
\`\`\`

### Upload & Series
\`\`\`typescript
interface Upload {
  id: string
  filename: string
  uploadedBy: string // User ID
  uploadedAt: Date
  status: 'processing' | 'completed' | 'failed'
  fileSize: number
  fileUrl: string
  seriesIds: string[] // Gegenereerde series
  error?: string
}

interface Series {
  id: string
  uploadId: string
  article: {
    sku: string
    name: string
    category?: string
  }
  status: 'pending' | 'in_progress' | 'completed'
  progress: {
    total: number
    approved: number
    rejected: number
    pending: number
  }
  createdAt: Date
  proposalIds: string[]
}
\`\`\`

### Proposal
\`\`\`typescript
interface Proposal {
  id: string
  seriesId: string
  batchId: string
  article: {
    sku: string
    name: string
  }
  currentDistribution: Distribution
  proposedDistribution: Distribution
  status: 'pending' | 'approved' | 'rejected' | 'edited'
  createdAt: Date
  reviewedAt?: Date
  reviewedBy?: string // User ID
  rejectionReason?: string
  editHistory?: EditHistory[]
  metadata: {
    generatedByAI: boolean
    confidenceScore?: number
    appliedRules: string[]
  }
}

interface Distribution {
  [locationId: string]: {
    locationName: string
    sizes: {
      [size: string]: number
    }
  }
}

interface EditHistory {
  editedAt: Date
  editedBy: string
  changes: Distribution
  reason?: string
}
\`\`\`

### Assignment
\`\`\`typescript
interface Assignment {
  id: string
  proposalId: string
  batchId: string
  storeId: string
  storeName: string
  article: {
    sku: string
    name: string
  }
  items: AssignmentItem[]
  status: 'pending' | 'in_progress' | 'completed'
  priority: 'high' | 'medium' | 'low'
  createdAt: Date
  dueDate: Date
  startedAt?: Date
  completedAt?: Date
  assignedTo?: string // Store user ID
  notes: string[]
  feedback?: Feedback[]
}

interface AssignmentItem {
  size: string
  action: 'send' | 'receive'
  quantity: number
  fromStore?: string
  toStore?: string
  completed: boolean
}
\`\`\`

### Feedback
\`\`\`typescript
interface Feedback {
  id: string
  type: 'proposal' | 'assignment'
  referenceId: string // Proposal ID of Assignment ID
  userId: string
  userName: string
  category: 'quantity' | 'timing' | 'location' | 'other'
  rating: 1 | 2 | 3 | 4 | 5
  comment: string
  attachments?: string[]
  createdAt: Date
  sentiment?: 'positive' | 'negative' | 'neutral' // AI-generated
  aiAnalysis?: {
    summary: string
    suggestedActions: string[]
    relatedFeedback: string[]
  }
}
\`\`\`

### Ruleset
\`\`\`typescript
interface Ruleset {
  id: string
  version: string
  active: boolean
  createdAt: Date
  createdBy: string
  rules: {
    inventory: {
      minStockPerLocation: { [size: string]: number }
      maxStockPerLocation: { [size: string]: number }
      minDifferenceForRedistribution: number
    }
    distribution: {
      priorityWeights: { [priority: string]: number }
      seasonalAdjustments: {
        season: string
        multiplier: number
        affectedSizes: string[]
      }[]
    }
    optimization: {
      minimizeTransfers: boolean
      preferDirectTransfers: boolean
      maxTransfersPerProposal: number
    }
    validation: {
      requireBalancedDistribution: boolean
      allowNegativeStock: boolean
      maxDeviationFromIdeal: number
    }
  }
  aiSuggestions?: AISuggestion[]
  testResults?: {
    historicalAccuracy: number
    approvalRate: number
    averageEditDistance: number
  }
}

interface AISuggestion {
  id: string
  category: string
  currentValue: any
  suggestedValue: any
  reasoning: string
  confidenceScore: number
  basedOnFeedback: string[] // Feedback IDs
  estimatedImpact: {
    approvalRateChange: number
    efficiencyGain: number
    affectedProposals: number
  }
  status: 'pending' | 'accepted' | 'rejected'
}
\`\`\`

### Activity Log
\`\`\`typescript
interface ActivityLog {
  id: string
  timestamp: Date
  userId: string
  userName: string
  action: ActivityAction
  resourceType: 'proposal' | 'assignment' | 'upload' | 'user' | 'ruleset'
  resourceId: string
  details: {
    [key: string]: any
  }
  ipAddress?: string
}

type ActivityAction =
  | 'create'
  | 'update'
  | 'delete'
  | 'approve'
  | 'reject'
  | 'upload'
  | 'download'
  | 'login'
  | 'logout'
\`\`\`

---

## 7. Business Logic en Regels

### Proposal Generation Rules

#### Minimum Stock Levels
\`\`\`typescript
const MIN_STOCK_RULES = {
  // Per size minimale voorraad per locatie
  'XS': 2,
  'S': 3,
  'M': 5,
  'L': 5,
  'XL': 3,
  'XXL': 2
}
\`\`\`

#### Distribution Priority
\`\`\`typescript
const PRIORITY_WEIGHTS = {
  'high': 1.5,    // Drukke winkels krijgen 50% meer
  'medium': 1.0,  // Baseline
  'low': 0.7      // Rustige winkels krijgen 30% minder
}
\`\`\`

#### Redistribution Triggers
\`\`\`typescript
const REDISTRIBUTION_RULES = {
  // Trigger herverdeling als:
  minDifference: 2,              // Verschil >= 2 stuks
  minPercentageDifference: 0.20, // Of >= 20% verschil
  considerSeasonality: true,     // Rekening houden met seizoen
  allowEmptyStock: false         // Nooit volledig leeg maken
}
\`\`\`

### Validation Rules

#### Proposal Validation
\`\`\`typescript
function validateProposal(proposal: Proposal): ValidationResult {
  const errors: string[] = []
  
  // 1. Check balance per size
  for (const size of Object.keys(proposal.proposedDistribution)) {
    const totalCurrent = sumBySize(proposal.currentDistribution, size)
    const totalProposed = sumBySize(proposal.proposedDistribution, size)
    
    if (totalCurrent !== totalProposed) {
      errors.push(`Size ${size}: unbalanced (${totalCurrent} → ${totalProposed})`)
    }
  }
  
  // 2. Check minimum stock levels
  for (const [location, data] of Object.entries(proposal.proposedDistribution)) {
    for (const [size, quantity] of Object.entries(data.sizes)) {
      if (quantity < MIN_STOCK_RULES[size] && quantity > 0) {
        errors.push(`${location} size ${size}: below minimum (${quantity} < ${MIN_STOCK_RULES[size]})`)
      }
    }
  }
  
  // 3. Check for negative stock
  for (const [location, data] of Object.entries(proposal.proposedDistribution)) {
    for (const [size, quantity] of Object.entries(data.sizes)) {
      if (quantity < 0) {
        errors.push(`${location} size ${size}: negative stock not allowed`)
      }
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}
\`\`\`

#### Assignment Validation
\`\`\`typescript
function canUpdateAssignmentStatus(
  assignment: Assignment,
  user: User,
  newStatus: AssignmentStatus
): boolean {
  // 1. User moet store role hebben
  if (user.role !== 'store') return false
  
  // 2. User moet bij juiste winkel horen
  if (assignment.storeId !== user.storeId) return false
  
  // 3. Status flow moet kloppen
  const validTransitions = {
    'pending': ['in_progress'],
    'in_progress': ['completed', 'pending'], // Can go back
    'completed': [] // Cannot change completed
  }
  
  return validTransitions[assignment.status]?.includes(newStatus) ?? false
}
\`\`\`

### AI Analysis Rules

#### Feedback Sentiment Analysis
\`\`\`typescript
async function analyzeFeedbackSentiment(feedback: Feedback): Promise<string> {
  // Gebruik OpenAI voor sentiment analyse
  const prompt = `
    Analyseer de volgende feedback en classificeer het sentiment als positief, negatief of neutraal:
    
    Feedback: "${feedback.comment}"
    Rating: ${feedback.rating}/5
    
    Geef alleen "positive", "negative" of "neutral" terug.
  `
  
  const sentiment = await callOpenAI(prompt)
  return sentiment.toLowerCase()
}
\`\`\`

#### Rule Suggestion Generation
\`\`\`typescript
async function generateRuleSuggestions(
  currentRules: Ruleset,
  feedbackHistory: Feedback[]
): Promise<AISuggestion[]> {
  // Analyseer patronen in feedback
  const patterns = analyzePatterns(feedbackHistory)
  
  // Groepeer per categorie
  const byCategory = groupBy(patterns, 'category')
  
  const suggestions: AISuggestion[] = []
  
  for (const [category, items] of Object.entries(byCategory)) {
    if (items.length >= 5) { // Minimaal 5 feedback items
      const prompt = `
        Gegeven de volgende feedback over ${category}:
        ${items.map(i => `- ${i.comment}`).join('\n')}
        
        Huidige regel: ${JSON.stringify(currentRules.rules[category])}
        
        Suggereer een verbeterde regel en leg uit waarom.
      `
      
      const aiResponse = await callOpenAI(prompt)
      
      suggestions.push({
        id: generateId(),
        category,
        currentValue: currentRules.rules[category],
        suggestedValue: parseAIResponse(aiResponse),
        reasoning: aiResponse.reasoning,
        confidenceScore: calculateConfidence(items),
        basedOnFeedback: items.map(i => i.id),
        estimatedImpact: estimateImpact(aiResponse.suggestedValue),
        status: 'pending'
      })
    }
  }
  
  return suggestions
}
\`\`\`

---

## 8. Backend Vereisten

### Technologie Stack (Aanbevolen)

#### Core
- **Framework**: Node.js met Express of NestJS
- **Database**: PostgreSQL (of MySQL)
- **ORM**: Prisma of TypeORM
- **Authentication**: JWT met bcrypt voor wachtwoorden
- **File Storage**: AWS S3 of lokale opslag met multer

#### Processing
- **PDF Parsing**: pdf-parse of pdfjs-dist
- **Queue System**: Bull met Redis (voor async processing)
- **Caching**: Redis
- **Email**: Nodemailer of SendGrid

#### AI Integration
- **OpenAI**: openai npm package
- **Configuration**: API key via environment variables of database

#### Development
- **TypeScript**: Voor type safety
- **Validation**: Zod of Joi
- **Logging**: Winston of Pino
- **Testing**: Jest
- **API Docs**: Swagger/OpenAPI

### Database Schema

#### Tables

**users**
\`\`\`sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'user', 'store')),
  store_id UUID REFERENCES stores(id),
  is_active BOOLEAN DEFAULT true,
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP
);
\`\`\`

**stores**
\`\`\`sql
CREATE TABLE stores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  code VARCHAR(50) UNIQUE NOT NULL,
  address TEXT,
  city VARCHAR(100),
  priority VARCHAR(20) CHECK (priority IN ('high', 'medium', 'low')),
  is_active BOOLEAN DEFAULT true,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

**uploads**
\`\`\`sql
CREATE TABLE uploads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  filename VARCHAR(255) NOT NULL,
  file_url TEXT NOT NULL,
  file_size INTEGER,
  uploaded_by UUID REFERENCES users(id),
  status VARCHAR(50) DEFAULT 'processing',
  error_message TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  processed_at TIMESTAMP
);
\`\`\`

**series**
\`\`\`sql
CREATE TABLE series (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  upload_id UUID REFERENCES uploads(id) ON DELETE CASCADE,
  article_sku VARCHAR(100) NOT NULL,
  article_name VARCHAR(255) NOT NULL,
  article_category VARCHAR(100),
  status VARCHAR(50) DEFAULT 'pending',
  total_proposals INTEGER DEFAULT 0,
  approved_count INTEGER DEFAULT 0,
  rejected_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

**proposals**
\`\`\`sql
CREATE TABLE proposals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  series_id UUID REFERENCES series(id) ON DELETE CASCADE,
  batch_id UUID NOT NULL,
  article_sku VARCHAR(100) NOT NULL,
  article_name VARCHAR(255) NOT NULL,
  current_distribution JSONB NOT NULL,
  proposed_distribution JSONB NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  reviewed_by UUID REFERENCES users(id),
  reviewed_at TIMESTAMP,
  rejection_reason TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

**edit_history**
\`\`\`sql
CREATE TABLE edit_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  proposal_id UUID REFERENCES proposals(id) ON DELETE CASCADE,
  edited_by UUID REFERENCES users(id),
  changes JSONB NOT NULL,
  reason TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

**assignments**
\`\`\`sql
CREATE TABLE assignments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  proposal_id UUID REFERENCES proposals(id),
  batch_id UUID NOT NULL,
  store_id UUID REFERENCES stores(id),
  article_sku VARCHAR(100) NOT NULL,
  article_name VARCHAR(255) NOT NULL,
  items JSONB NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  priority VARCHAR(20),
  assigned_to UUID REFERENCES users(id),
  due_date DATE,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  notes TEXT[],
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

**feedback**
\`\`\`sql
CREATE TABLE feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type VARCHAR(50) CHECK (type IN ('proposal', 'assignment')),
  reference_id UUID NOT NULL,
  user_id UUID REFERENCES users(id),
  category VARCHAR(50),
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  comment TEXT NOT NULL,
  attachments TEXT[],
  sentiment VARCHAR(20),
  ai_analysis JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

**rulesets**
\`\`\`sql
CREATE TABLE rulesets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  version VARCHAR(50) NOT NULL,
  is_active BOOLEAN DEFAULT false,
  rules JSONB NOT NULL,
  ai_suggestions JSONB,
  test_results JSONB,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

**activity_logs**
\`\`\`sql
CREATE TABLE activity_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  action VARCHAR(100) NOT NULL,
  resource_type VARCHAR(50),
  resource_id UUID,
  details JSONB,
  ip_address VARCHAR(45),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

#### Indexes
\`\`\`sql
-- Performance indexes
CREATE INDEX idx_proposals_series ON proposals(series_id);
CREATE INDEX idx_proposals_status ON proposals(status);
CREATE INDEX idx_assignments_store ON assignments(store_id);
CREATE INDEX idx_assignments_status ON assignments(status);
CREATE INDEX idx_feedback_reference ON feedback(reference_id);
CREATE INDEX idx_activity_logs_user ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_created ON activity_logs(created_at);
\`\`\`

### API Architecture

#### RESTful Endpoints Structure
\`\`\`
/api/v1/
  /auth/
    POST   /login
    POST   /logout
    POST   /refresh
    POST   /forgot-password
    POST   /reset-password
    
  /users/
    GET    /
    GET    /:id
    POST   /
    PUT    /:id
    DELETE /:id
    PATCH  /:id/password
    
  /stores/
    GET    /
    GET    /:id
    POST   /
    PUT    /:id
    
  /uploads/
    GET    /
    GET    /:id
    POST   /
    DELETE /:id
    POST   /:id/process
    
  /series/
    GET    /
    GET    /:id
    GET    /:id/proposals
    
  /proposals/
    GET    /
    GET    /:id
    POST   /batch
    PUT    /:id
    POST   /:id/approve
    POST   /:id/reject
    POST   /:id/edit
    GET    /batch/:batchId
    
  /assignments/
    GET    /
    GET    /:id
    PUT    /:id/status
    POST   /:id/feedback
    GET    /batch/:batchId
    
  /feedback/
    GET    /
    GET    /:id
    POST   /
    GET    /analysis
    
  /rulesets/
    GET    /active
    GET    /
    GET    /:id
    POST   /
    PUT    /:id
    POST   /:id/activate
    POST   /ai-suggestions
    POST   /test
    
  /analytics/
    GET    /dashboard
    GET    /proposals
    GET    /assignments
    GET    /feedback
\`\`\`

---

## 9. API Endpoints Specificatie

### Authentication Endpoints

#### POST /api/v1/auth/login
**Request:**
\`\`\`json
{
  "email": "user@example.com",
  "password": "password123"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user"
    },
    "token": "jwt-token",
    "refreshToken": "refresh-token"
  }
}
\`\`\`

#### POST /api/v1/auth/logout
**Headers:** `Authorization: Bearer {token}`

**Response:**
\`\`\`json
{
  "success": true,
  "message": "Logged out successfully"
}
\`\`\`

### Upload Endpoints

#### POST /api/v1/uploads/
**Headers:** 
- `Authorization: Bearer {token}`
- `Content-Type: multipart/form-data`

**Request:**
\`\`\`
FormData {
  file: File (PDF)
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "id": "uuid",
    "filename": "voorraad-2024-01.pdf",
    "fileSize": 245678,
    "status": "processing",
    "createdAt": "2024-01-15T10:00:00Z"
  }
}
\`\`\`

#### GET /api/v1/uploads/
**Headers:** `Authorization: Bearer {token}`

**Query Params:**
- `page`: number (default: 1)
- `limit`: number (default: 20)
- `status`: string (optional)

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "uploads": [
      {
        "id": "uuid",
        "filename": "voorraad-2024-01.pdf",
        "uploadedBy": "John Doe",
        "uploadedAt": "2024-01-15T10:00:00Z",
        "status": "completed",
        "seriesCount": 3
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "pages": 3
    }
  }
}
\`\`\`

### Proposal Endpoints

#### GET /api/v1/proposals/
**Headers:** `Authorization: Bearer {token}`

**Query Params:**
- `page`: number
- `limit`: number
- `status`: string (pending|approved|rejected)
- `batchId`: string (optional)
- `seriesId`: string (optional)

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "proposals": [
      {
        "id": "uuid",
        "seriesId": "uuid",
        "batchId": "uuid",
        "article": {
          "sku": "ART-001",
          "name": "Product Name"
        },
        "status": "pending",
        "createdAt": "2024-01-15T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "pages": 8
    }
  }
}
\`\`\`

#### GET /api/v1/proposals/:id
**Headers:** `Authorization: Bearer {token}`

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "id": "uuid",
    "seriesId": "uuid",
    "batchId": "uuid",
    "article": {
      "sku": "ART-001",
      "name": "Product Name",
      "category": "Shirts"
    },
    "currentDistribution": {
      "store-1": {
        "locationName": "Store Amsterdam",
        "sizes": {
          "S": 5,
          "M": 10,
          "L": 8
        }
      },
      "store-2": {
        "locationName": "Store Rotterdam",
        "sizes": {
          "S": 2,
          "M": 15,
          "L": 3
        }
      }
    },
    "proposedDistribution": {
      "store-1": {
        "locationName": "Store Amsterdam",
        "sizes": {
          "S": 4,
          "M": 12,
          "L": 6
        }
      },
      "store-2": {
        "locationName": "Store Rotterdam",
        "sizes": {
          "S": 3,
          "M": 13,
          "L": 5
        }
      }
    },
    "status": "pending",
    "metadata": {
      "generatedByAI": true,
      "confidenceScore": 0.85,
      "appliedRules": ["min-stock", "priority-distribution"]
    },
    "createdAt": "2024-01-15T10:00:00Z"
  }
}
\`\`\`

#### POST /api/v1/proposals/:id/approve
**Headers:** `Authorization: Bearer {token}`

**Request:**
\`\`\`json
{
  "notes": "Looks good"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "proposal": {
      "id": "uuid",
      "status": "approved",
      "reviewedBy": "uuid",
      "reviewedAt": "2024-01-15T11:00:00Z"
    },
    "assignments": [
      {
        "id": "uuid",
        "storeId": "store-1",
        "status": "pending"
      }
    ],
    "nextProposal": {
      "id": "uuid",
      "seriesId": "uuid"
    }
  }
}
\`\`\`

#### POST /api/v1/proposals/:id/reject
**Headers:** `Authorization: Bearer {token}`

**Request:**
\`\`\`json
{
  "reason": "Quantities don't match demand"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "rejected",
    "rejectionReason": "Quantities don't match demand",
    "reviewedBy": "uuid",
    "reviewedAt": "2024-01-15T11:00:00Z"
  }
}
\`\`\`

#### PUT /api/v1/proposals/:id/edit
**Headers:** `Authorization: Bearer {token}`

**Request:**
\`\`\`json
{
  "proposedDistribution": {
    "store-1": {
      "locationName": "Store Amsterdam",
      "sizes": {
        "S": 5,
        "M": 11,
        "L": 6
      }
    },
    "store-2": {
      "locationName": "Store Rotterdam",
      "sizes": {
        "S": 2,
        "M": 14,
        "L": 5
      }
    }
  },
  "reason": "Adjusted based on recent sales data"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "edited",
    "proposedDistribution": { /* updated distribution */ },
    "editHistory": [
      {
        "editedAt": "2024-01-15T11:30:00Z",
        "editedBy": "uuid",
        "reason": "Adjusted based on recent sales data"
      }
    ]
  }
}
\`\`\`

#### GET /api/v1/proposals/batch/:batchId
**Headers:** `Authorization: Bearer {token}`

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "batchId": "uuid",
    "seriesId": "uuid",
    "uploadId": "uuid",
    "article": {
      "sku": "ART-001",
      "name": "Product Name"
    },
    "progress": {
      "total": 10,
      "approved": 3,
      "rejected": 1,
      "pending": 6
    },
    "proposals": [
      {
        "id": "uuid",
        "status": "pending",
        "createdAt": "2024-01-15T10:00:00Z"
      }
    ]
  }
}
\`\`\`

### Assignment Endpoints

#### GET /api/v1/assignments/
**Headers:** `Authorization: Bearer {token}`

**Query Params:**
- `page`: number
- `limit`: number
- `status`: string (pending|in_progress|completed)
- `storeId`: string (optional, auto-filtered for store users)

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "assignments": [
      {
        "id": "uuid",
        "proposalId": "uuid",
        "storeId": "store-1",
        "storeName": "Store Amsterdam",
        "article": {
          "sku": "ART-001",
          "name": "Product Name"
        },
        "status": "pending",
        "priority": "high",
        "dueDate": "2024-01-20",
        "createdAt": "2024-01-15T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 35,
      "pages": 2
    }
  }
}
\`\`\`

#### GET /api/v1/assignments/:id
**Headers:** `Authorization: Bearer {token}`

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "id": "uuid",
    "proposalId": "uuid",
    "batchId": "uuid",
    "storeId": "store-1",
    "storeName": "Store Amsterdam",
    "article": {
      "sku": "ART-001",
      "name": "Product Name"
    },
    "items": [
      {
        "size": "M",
        "action": "send",
        "quantity": 2,
        "toStore": "Store Rotterdam",
        "completed": false
      },
      {
        "size": "L",
        "action": "receive",
        "quantity": 3,
        "fromStore": "Store Utrecht",
        "completed": false
      }
    ],
    "status": "pending",
    "priority": "high",
    "dueDate": "2024-01-20",
    "notes": [],
    "createdAt": "2024-01-15T10:00:00Z"
  }
}
\`\`\`

#### PUT /api/v1/assignments/:id/status
**Headers:** `Authorization: Bearer {token}`

**Request:**
\`\`\`json
{
  "status": "in_progress",
  "notes": "Started processing"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "in_progress",
    "startedAt": "2024-01-16T09:00:00Z"
  }
}
\`\`\`

#### POST /api/v1/assignments/:id/feedback
**Headers:** `Authorization: Bearer {token}`

**Request:**
\`\`\`json
{
  "category": "quantity",
  "rating": 4,
  "comment": "Most items matched, but size M was 1 short"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "id": "uuid",
    "assignmentId": "uuid",
    "userId": "uuid",
    "category": "quantity",
    "rating": 4,
    "comment": "Most items matched, but size M was 1 short",
    "createdAt": "2024-01-16T10:00:00Z"
  }
}
\`\`\`

### Feedback Endpoints

#### GET /api/v1/feedback/
**Headers:** `Authorization: Bearer {token}` (Admin only)

**Query Params:**
- `page`: number
- `limit`: number
- `type`: string (proposal|assignment)
- `category`: string
- `sentiment`: string

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "feedback": [
      {
        "id": "uuid",
        "type": "proposal",
        "referenceId": "uuid",
        "userName": "John Doe",
        "category": "quantity",
        "rating": 3,
        "comment": "Quantities seem off",
        "sentiment": "negative",
        "createdAt": "2024-01-15T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 89,
      "pages": 5
    }
  }
}
\`\`\`

#### GET /api/v1/feedback/:id
**Headers:** `Authorization: Bearer {token}` (Admin only)

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "id": "uuid",
    "type": "proposal",
    "referenceId": "uuid",
    "user": {
      "id": "uuid",
      "name": "John Doe",
      "role": "user"
    },
    "category": "quantity",
    "rating": 3,
    "comment": "Quantities seem off for size M",
    "sentiment": "negative",
    "aiAnalysis": {
      "summary": "User suggests quantities for size M are too low",
      "suggestedActions": [
        "Review minimum stock rules for size M",
        "Check if size M has higher demand than estimated"
      ],
      "relatedFeedback": ["uuid-1", "uuid-2"]
    },
    "createdAt": "2024-01-15T12:00:00Z"
  }
}
\`\`\`

### Ruleset Endpoints

#### GET /api/v1/rulesets/active
**Headers:** `Authorization: Bearer {token}` (Admin only)

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "id": "uuid",
    "version": "1.2.0",
    "isActive": true,
    "rules": {
      "inventory": {
        "minStockPerLocation": {
          "S": 3,
          "M": 5,
          "L": 5
        },
        "maxStockPerLocation": {
          "S": 20,
          "M": 30,
          "L": 25
        },
        "minDifferenceForRedistribution": 2
      },
      "distribution": {
        "priorityWeights": {
          "high": 1.5,
          "medium": 1.0,
          "low": 0.7
        }
      }
    },
    "createdAt": "2024-01-10T10:00:00Z"
  }
}
\`\`\`

#### POST /api/v1/rulesets/ai-suggestions
**Headers:** `Authorization: Bearer {token}` (Admin only)

**Request:**
\`\`\`json
{
  "feedbackIds": ["uuid-1", "uuid-2", "uuid-3"]
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "id": "uuid",
        "category": "inventory.minStockPerLocation",
        "currentValue": {
          "M": 5
        },
        "suggestedValue": {
          "M": 6
        },
        "reasoning": "Based on 15 feedback entries, size M consistently runs low. Increasing minimum from 5 to 6 would reduce stock-outs by ~30%.",
        "confidenceScore": 0.82,
        "basedOnFeedback": ["uuid-1", "uuid-2", "uuid-3"],
        "estimatedImpact": {
          "approvalRateChange": 0.12,
          "efficiencyGain": 0.08,
          "affectedProposals": 45
        },
        "status": "pending"
      }
    ]
  }
}
\`\`\`

#### POST /api/v1/rulesets/
**Headers:** `Authorization: Bearer {token}` (Admin only)

**Request:**
\`\`\`json
{
  "version": "1.3.0",
  "rules": {
    "inventory": {
      "minStockPerLocation": {
        "S": 3,
        "M": 6,
        "L": 5
      }
    }
  },
  "activateImmediately": false
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "id": "uuid",
    "version": "1.3.0",
    "isActive": false,
    "rules": {
      "inventory": {
        "minStockPerLocation": {
          "S": 3,
          "M": 6,
          "L": 5
        }
      }
    },
    "createdAt": "2024-01-17T10:00:00Z"
  }
}
\`\`\`

#### POST /api/v1/rulesets/:id/activate
**Headers:** `Authorization: Bearer {token}` (Admin only)

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "id": "uuid",
    "version": "1.3.0",
    "isActive": true,
    "activatedAt": "2024-01-17T11:00:00Z"
  }
}
\`\`\`

### User Management Endpoints

#### GET /api/v1/users/
**Headers:** `Authorization: Bearer {token}` (Admin only)

**Query Params:**
- `page`: number
- `limit`: number
- `role`: string (optional)
- `isActive`: boolean (optional)

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": "uuid",
        "email": "user@example.com",
        "name": "John Doe",
        "role": "user",
        "isActive": true,
        "lastLogin": "2024-01-15T10:00:00Z",
        "createdAt": "2024-01-01T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 25,
      "pages": 2
    }
  }
}
\`\`\`

#### POST /api/v1/users/
**Headers:** `Authorization: Bearer {token}` (Admin only)

**Request:**
\`\`\`json
{
  "email": "newuser@example.com",
  "name": "Jane Smith",
  "password": "securepassword",
  "role": "store",
  "storeId": "store-uuid"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "newuser@example.com",
    "name": "Jane Smith",
    "role": "store",
    "storeId": "store-uuid",
    "createdAt": "2024-01-17T10:00:00Z"
  }
}
\`\`\`

---

## 10. Implementatie Prioriteiten

### Fase 1: Core Functionaliteit (Weken 1-4)
**Doel: Minimale werkende applicatie**

1. **Database Setup**
   - Schema implementatie
   - Seed data voor testing
   - Basis indexes

2. **Authentication & Authorization**
   - JWT implementatie
   - User management
   - Role-based access control
   - Password reset flow

3. **Upload & Processing**
   - File upload endpoint
   - PDF parsing implementatie
   - Series aanmaken
   - Basic error handling

4. **Proposal System - Basis**
   - Proposal CRUD operations
   - Basic generation algorithm
   - Approve/Reject functionaliteit
   - Lijst en detail views

### Fase 2: Advanced Features (Weken 5-8)
**Doel: Volledige workflow**

1. **Proposal System - Advanced**
   - Edit functionaliteit
   - Balance validation
   - Batch processing
   - Series progress tracking
   - Auto-navigation

2. **Assignment System**
   - Conversie van proposals naar assignments
   - Assignment status updates
   - Store user filtering
   - Notifications

3. **Feedback System**
   - Feedback submission
   - Categorisatie
   - Basic analytics
   - Admin dashboard

### Fase 3: AI Integration (Weken 9-12)
**Doel: Intelligente optimalisatie**

1. **OpenAI Integration**
   - API key management
   - Sentiment analysis
   - Feedback pattern recognition

2. **Ruleset Management**
   - Rule editor
   - AI suggestion generation
   - Impact analysis
   - Version control

3. **Analytics & Reporting**
   - Dashboard metrics
   - Trend analysis
   - Performance insights
   - Export functionality

### Fase 4: Polish & Optimization (Weken 13-16)
**Doel: Production-ready**

1. **Performance Optimization**
   - Query optimization
   - Caching implementation
   - Background job optimization
   - Response time improvements

2. **Testing**
   - Unit tests
   - Integration tests
   - E2E tests
   - Load testing

3. **Documentation**
   - API documentation
   - Deployment guide
   - User manual
   - Admin guide

4. **Security Hardening**
   - Security audit
   - Penetration testing
   - Vulnerability fixes
   - Rate limiting

---

## 11. Testing Strategy

### Unit Testing
**Focus op individuele functies en business logic**

\`\`\`typescript
// Voorbeeld: Proposal validation tests
describe('Proposal Validation', () => {
  test('should validate balanced distribution', () => {
    const proposal = createTestProposal({
      current: { store1: { M: 10 }, store2: { M: 5 } },
      proposed: { store1: { M: 8 }, store2: { M: 7 } }
    })
    
    expect(validateBalance(proposal)).toBe(true)
  })
  
  test('should reject unbalanced distribution', () => {
    const proposal = createTestProposal({
      current: { store1: { M: 10 }, store2: { M: 5 } },
      proposed: { store1: { M: 8 }, store2: { M: 8 } }
    })
    
    expect(validateBalance(proposal)).toBe(false)
  })
  
  test('should enforce minimum stock levels', () => {
    const proposal = createTestProposal({
      proposed: { store1: { M: 1 } } // Below minimum
    })
    
    const result = validateProposal(proposal)
    expect(result.isValid).toBe(false)
    expect(result.errors).toContain('below minimum')
  })
})
\`\`\`

### Integration Testing
**Test API endpoints en database interacties**

\`\`\`typescript
describe('Proposal API', () => {
  test('POST /proposals/:id/approve should create assignments', async () => {
    const proposal = await createTestProposal()
    const response = await request(app)
      .post(`/api/v1/proposals/${proposal.id}/approve`)
      .set('Authorization', `Bearer ${adminToken}`)
      .send({ notes: 'Test approval' })
    
    expect(response.status).toBe(200)
    expect(response.body.data.assignments).toHaveLength(2)
    
    const assignments = await getAssignmentsByProposal(proposal.id)
    expect(assignments).toHaveLength(2)
  })
})
\`\`\`

### E2E Testing
**Test complete gebruikersflows**

\`\`\`typescript
describe('Proposal Review Flow', () => {
  test('should complete full approval flow', async () => {
    // 1. Login as user
    const loginResponse = await login('user@example.com', 'password')
    const token = loginResponse.token
    
    // 2. Upload PDF
    const uploadResponse = await uploadPDF(token, testPDF)
    expect(uploadResponse.status).toBe('processing')
    
    // 3. Wait for processing
    await waitForProcessing(uploadResponse.id)
    
    // 4. Get generated proposals
    const proposals = await getProposals(token)
    expect(proposals.length).toBeGreaterThan(0)
    
    // 5. Approve first proposal
    const approveResponse = await approveProposal(token, proposals[0].id)
    expect(approveResponse.status).toBe('approved')
    
    // 6. Verify assignments created
    const assignments = await getAssignments(token)
    expect(assignments.length).toBeGreaterThan(0)
  })
})
\`\`\`

---

## 12. Deployment & DevOps

### Environment Setup

#### Development
\`\`\`env
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://user:pass@localhost:5432/resupply_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev-secret-key
JWT_EXPIRES_IN=7d
OPENAI_API_KEY=sk-...
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
CORS_ORIGIN=http://localhost:3001
\`\`\`

#### Production
\`\`\`env
NODE_ENV=production
PORT=8080
DATABASE_URL=postgresql://user:pass@prod-db:5432/resupply_prod
REDIS_URL=redis://prod-redis:6379
JWT_SECRET=secure-production-secret
JWT_EXPIRES_IN=1d
OPENAI_API_KEY=sk-...
UPLOAD_DIR=/var/uploads
MAX_FILE_SIZE=10485760
CORS_ORIGIN=https://resupply.example.com
SENTRY_DSN=https://...
\`\`\`

### Docker Setup

**Dockerfile:**
\`\`\`dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source
COPY . .

# Build TypeScript
RUN npm run build

# Expose port
EXPOSE 8080

# Start application
CMD ["npm", "start"]
\`\`\`

**docker-compose.yml:**
\`\`\`yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/resupply
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - uploads:/var/uploads

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=resupply
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
  uploads:
\`\`\`

### CI/CD Pipeline

**GitHub Actions example:**
\`\`\`yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test
      - run: npm run lint

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/build-push-action@v4
        with:
          push: true
          tags: resupply:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # Deploy script here
\`\`\`

---

## 13. Monitoring & Logging

### Logging Strategy

**Winston Logger Setup:**
\`\`\`typescript
import winston from 'winston'

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
})

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple(),
  }))
}
\`\`\`

**Log Levels:**
- `error`: Errors en exceptions
- `warn`: Waarschuwingen (bijv. deprecated endpoints)
- `info`: Belangrijke events (bijv. proposal approved)
- `debug`: Gedetailleerde debug informatie

**Logging Examples:**
\`\`\`typescript
// Successful operation
logger.info('Proposal approved', {
  proposalId: proposal.id,
  userId: user.id,
  timestamp: new Date()
})

// Error
logger.error('PDF parsing failed', {
  uploadId: upload.id,
  error: error.message,
  stack: error.stack
})

// Performance monitoring
logger.debug('Query execution time', {
  query: 'getProposals',
  duration: Date.now() - startTime
})
\`\`\`

### Monitoring

**Health Check Endpoint:**
\`\`\`typescript
app.get('/health', async (req, res) => {
  const health = {
    uptime: process.uptime(),
    timestamp: Date.now(),
    status: 'OK',
    services: {
      database: await checkDatabase(),
      redis: await checkRedis(),
      storage: await checkStorage()
    }
  }
  
  const hasErrors = Object.values(health.services).some(s => !s.healthy)
  res.status(hasErrors ? 503 : 200).json(health)
})
\`\`\`

**Metrics to Monitor:**
- Request rate (requests/second)
- Response time (average, p95, p99)
- Error rate
- Database query performance
- PDF processing time
- Queue length (pending jobs)
- Memory usage
- CPU usage

---

## 14. Security Best Practices

### Authentication & Authorization
- JWT tokens met korte expiry (1 day)
- Refresh tokens voor langere sessies
- Password hashing met bcrypt (min 10 rounds)
- Rate limiting op login endpoint
- Account lockout na meerdere failed attempts

### API Security
- CORS configuratie
- Helmet.js voor security headers
- Input validation met Zod/Joi
- SQL injection preventie via ORM
- XSS preventie
- CSRF tokens voor state-changing operations

### Data Security
- Encrypt sensitive data at rest
- Use HTTPS in production
- Secure file uploads (type checking, size limits)
- Sanitize user input
- Environment variables voor secrets (NEVER in code)

### Access Control
\`\`\`typescript
// Middleware voorbeeld
const requireRole = (roles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Unauthorized' })
    }
    
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Forbidden' })
    }
    
    next()
  }
}

// Gebruik
app.get('/api/v1/admin/users', 
  authenticate, 
  requireRole(['admin']), 
  getUsersHandler
)
\`\`\`

---

## 15. Toekomstige Uitbreidingen

### Fase 5: Advanced Features
1. **Real-time Updates**
   - WebSocket implementation voor live updates
   - Real-time notifications
   - Collaborative editing

2. **Mobile App**
   - React Native app voor store users
   - Barcode scanning
   - Offline mode

3. **Advanced Analytics**
   - Predictive analytics
   - Demand forecasting
   - Seasonal trend analysis
   - Custom reports

4. **Integrations**
   - ERP system integration
   - Warehouse management system
   - Shipping providers
   - Email notifications

5. **Multi-tenant Support**
   - Support voor meerdere organisaties
   - Tenant isolation
   - Custom branding per tenant

6. **Advanced AI Features**
   - Image recognition (upload fotos ipv PDFs)
   - Natural language queries
   - Automated decision making (met approval threshold)
   - Anomaly detection

---

## 16. Technical Debt & Known Limitations

### Current Limitations
1. **PDF Parsing**: Afhankelijk van specifiek PDF format
2. **Single Tenant**: Geen multi-tenant support
3. **Sync Processing**: Upload processing is sync (zou async moeten)
4. **No Real-time**: Geen WebSocket ondersteuning
5. **Limited Analytics**: Basic statistieken alleen

### Technical Debt to Address
1. **Error Handling**: Inconsistent error handling
2. **Type Safety**: Niet overal strict typing
3. **Test Coverage**: Tests ontbreken voor sommige features
4. **Documentation**: API docs niet volledig
5. **Performance**: Geen caching layer

---

## Samenvatting

Dit document bevat alle informatie die nodig is om de backend van de Digital Resupplying Tool te ontwikkelen. Het beschrijft:

- Alle gebruikersrollen en hun rechten
- Alle features en hun werking in detail
- Datastructuren en database schema
- Volledige API specificatie met voorbeelden
- Business logic en validatie regels
- Implementatie prioriteiten en roadmap
- Testing, deployment en monitoring strategie
- Security best practices

Gebruik dit document als complete referentie bij het ontwikkelen van de backend in Cursor. Begin met Fase 1 (Core Functionaliteit) en werk stapsgewijs naar de meer geavanceerde features toe.

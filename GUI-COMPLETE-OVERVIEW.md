# Digital Resupplying Tool - Complete GUI Overzicht

Dit document bevat een volledig overzicht van alle pagina's, elementen, componenten en hun eigenschappen in de Digital Resupplying Tool GUI.

---

## Inhoudsopgave

1. [Globale Navigatie](#globale-navigatie)
2. [Dashboard Pagina](#dashboard-pagina)
3. [Genereren Pagina](#genereren-pagina)
4. [Herverdelingsvoorstellen Pagina](#herverdelingsvoorstellen-pagina)
5. [Reeks Detail Pagina](#reeks-detail-pagina)
6. [Voorstel Detail Pagina](#voorstel-detail-pagina)
7. [Voorstel Bewerken Pagina](#voorstel-bewerken-pagina)
8. [Opdrachten Pagina](#opdrachten-pagina)
9. [Instellingen Pagina](#instellingen-pagina)

---

## Browser Metadata

**Pagina Titel**: "DRT - Digital Resupplying Tool"
- Weergave: Browser tab en venster titel
- Format: Kort acroniem gevolgd door volledige naam

**Meta Beschrijving**: "DRT: Verwerk en keur herverdelingsvoorstellen goed voor damesmodewinkels"
- Gebruikt voor: SEO en browser preview
- Lengte: Beknopt en beschrijvend

**Favicon**: `/mc-company-logo.png`
- Bestand: MC Company logo als icoon
- Formaat: PNG
- Weergave: Browser tab en bookmarks

**HTML Lang Attribuut**: "nl" (Nederlands)
- Accessibility: Screen readers en vertaling
- Standaard taal: Nederlands

---

## Globale Navigatie

### Sidebar (AppSidebar)

**Locatie**: Linkerzijde van het scherm, altijd zichtbaar op alle pagina's

**Elementen**:

#### 1. Header Sectie
- **Logo**: MC Company PNG logo
  - Bestand: `/mc-company-logo.png`
  - Grootte: 48x48px
  - Container: Witte achtergrond met shadow (bg-white dark:bg-white/95 p-2 rounded-lg shadow-sm)
  - Link: Externe link naar `https://mc-company.nl/` (opent in nieuw tabblad)
  - Functie: Bedrijfsbranding

- **Applicatie Naam**: 
  - Primair: "DRT" (font-bold text-lg)
  - Secundair: "Digital Resupplying Tool" (text-[10px] text-muted-foreground)
  - Layout: Verticaal gestapeld (flex flex-col)
  - Link: Onderdeel van externe link naar `https://mc-company.nl/`
  - Functie: Applicatie identificatie

- **Sidebar Toggle Button**: 
  - Component: SidebarTrigger
  - Functie: Klapt sidebar in/uit
  - Positie: Rechts in header

#### 2. Navigatie Menu Items

**Dashboard**
- Icon: LayoutDashboard (16x16px)
- Label: "Dashboard"
- Link: "/"
- Actief wanneer: pathname === "/"
- Zichtbaar voor: Alle gebruikersrollen

**Genereren** (alleen voor Admin/User)
- Icon: FileUp (16x16px)
- Label: "Genereren"
- Link: "/uploads"
- Actief wanneer: pathname === "/uploads"
- Zichtbaar voor: Admin en User rollen
- Verborgen voor: Store rol

**Herverdelingsvoorstellen** (alleen voor Admin/User)
- Icon: BarChart3 (16x16px)
- Label: "Herverdelingsvoorstellen"
- Link: "/proposals"
- Actief wanneer: pathname.startsWith("/proposals")
- Zichtbaar voor: Admin en User rollen
- Verborgen voor: Store rol

**Opdrachten** (alleen voor Store)
- Icon: ClipboardList (16x16px)
- Label: "Opdrachten"
- Link: "/assignments"
- Actief wanneer: pathname.startsWith("/assignments")
- Zichtbaar voor: Store rol
- Verborgen voor: Admin en User rollen

**Instellingen**
- Icon: Settings (16x16px)
- Label: "Instellingen"
- Link: "/settings"
- Actief wanneer: pathname === "/settings"
- Zichtbaar voor: Alle gebruikersrollen

#### 3. Footer Sectie

**Gebruiker Profiel**
- **Avatar**: 
  - Grootte: 32x32px (h-8 w-8)
  - Vorm: Cirkel (rounded-full)
  - Achtergrond: bg-primary/10
  - Inhoud: Initialen gebruiker (bijv. "AB")
  - Typografie: text-xs font-medium

- **Gebruiker Naam**: "Admin Beheerder"
  - Typografie: text-sm font-medium

- **Email**: "admin@example.com"
  - Typografie: text-xs text-muted-foreground

**Mode Toggle Button**
- Component: ModeToggle
- Functie: Schakelt tussen light/dark mode
- Positie: Rechts naast gebruikersprofiel

**Uitloggen Button**
- Icon: LogOut (16x16px)
- Label: "Uitloggen"
- Variant: outline
- Grootte: sm
- Functie: Logt gebruiker uit
- Breedte: Volledige breedte (mt-2)

---

## Dashboard Pagina

**Route**: `/`

**Layout**: DashboardShell met responsive grid layout

### Header Sectie

**Hoofdtitel**: "Dashboard"
- Typografie: Groot, bold (via DashboardHeader component)
- Kleur: Primaire tekstkleur

**Subtitel**: "Overzicht van herverdelingsvoorstellen en activiteiten"
- Typografie: text-sm text-muted-foreground

**Period Selector**
- Component: PeriodSelector
- Positie: Rechts in header (op desktop)
- Functie: Selecteert tijdsperiode voor statistieken
- Responsive: Onder header op mobiel

### Statistieken Sectie (DashboardStats)

**Layout**: Grid met 4 kolommen op desktop (md:grid-cols-2 lg:grid-cols-4)

#### 1. Totaal Voorstellen Card
- **Icon**: FileCheck (16x16px, text-muted-foreground)
- **Titel**: "Totaal Voorstellen"
  - Typografie: text-sm font-medium
- **Waarde**: "142"
  - Typografie: text-2xl font-bold
- **Trend Indicator**:
  - Icon: ArrowUpRight (groen) of ArrowDownRight (rood)
  - Grootte: 12x12px (h-3 w-3)
  - Tekst: "+12% vergeleken met vorig jaar"
  - Typografie: text-xs text-muted-foreground
- **Functie**: Toont totaal aantal voorstellen met jaar-op-jaar vergelijking

#### 2. In Behandeling Card
- **Icon**: FileClock (16x16px, text-muted-foreground)
- **Titel**: "In Behandeling"
  - Typografie: text-sm font-medium
- **Waarde**: "24"
  - Typografie: text-2xl font-bold
- **Trend Indicator**:
  - Icon: ArrowUpRight
  - Tekst: "+7 sinds vorige periode"
  - Typografie: text-xs text-muted-foreground
- **Functie**: Toont aantal voorstellen in behandeling

#### 3. Afgekeurd Card
- **Icon**: FileX (16x16px, text-muted-foreground)
- **Titel**: "Afgekeurd"
  - Typografie: text-sm font-medium
- **Waarde**: "18"
  - Typografie: text-2xl font-bold
- **Percentage**: "5% van alle voorstellen"
  - Typografie: text-xs text-muted-foreground
- **Trend**: "-2%" (rood)
- **Functie**: Toont aantal afgekeurde voorstellen met percentage

#### 4. Actieve Winkels Card
- **Icon**: Users (16x16px, text-muted-foreground)
- **Titel**: "Actieve Winkels"
  - Typografie: text-sm font-medium
- **Waarde**: "32"
  - Typografie: text-2xl font-bold
- **Trend**: "+2 vergeleken met vorige periode"
  - Typografie: text-xs text-muted-foreground
- **Functie**: Toont aantal actieve winkels

### Hoofdinhoud Sectie

**Layout**: Grid met 3 kolommen (lg:col-span-2 voor links, 1 kolom voor rechts)

#### Wachtende Reeksen Card (PendingProposals)

**Positie**: Links, neemt 2/3 van de breedte op desktop

**Header**:
- **Titel**: "Wachtende Reeksen"
  - Typografie: CardTitle
- **Subtitel**: "Reeksen met voorstellen die op beoordeling wachten"
  - Typografie: text-sm text-muted-foreground
- **"Alle bekijken" Button**:
  - Variant: ghost
  - Grootte: sm
  - Link: "/proposals"
  - Positie: Rechts in header

**Reeks Items** (4 items getoond):

Voor elke reeks:
- **Titel**: Klikbare link naar batch detail
  - Typografie: text-sm font-medium leading-none
  - Link: `/proposals/batch/{seriesId}`
  - Hover: underline
  - Voorbeeld: "Herverdeling voor week 12 2025"

- **Metadata Rij**:
  - Datum: "24 maart 2025"
    - Typografie: text-sm text-muted-foreground
  - Separator: "·" (px-1 text-muted-foreground)
  - Aantal: "42 voorstellen"
    - Typografie: text-sm text-muted-foreground

- **"Beoordelen" Button**:
  - Variant: outline
  - Grootte: sm (h-8)
  - Icon: ArrowRight (16x16px)
  - Link: `/proposals/{nextProposalId}`
  - Functie: Navigeert naar eerste onbeoordeelde voorstel

- **Voortgangsbalk**:
  - **Tekst boven**: "12 van 42 beoordeeld" | "28%"
    - Typografie: text-xs
  - **Balk**:
    - Hoogte: 8px (h-2)
    - Achtergrond: bg-secondary
    - Vulling: bg-blue-500
    - Vorm: rounded-full
    - Breedte: Dynamisch op basis van percentage

#### Recente Activiteit Card (RecentActivity)

**Positie**: Rechts boven, neemt 1/3 van de breedte op desktop

**Header**:
- **Titel**: "Recente Activiteit"
  - Typografie: CardTitle

**Activiteit Items** (4 items getoond):

Voor elke activiteit:
- **Avatar**:
  - Grootte: 32x32px (h-8 w-8)
  - Vorm: Cirkel
  - Inhoud: Initialen of afbeelding
  - Fallback: Initialen met achtergrondkleur

- **Gebruikersnaam**: "Marieke"
  - Typografie: text-sm font-medium leading-none

- **Actie**: "heeft een voorstel goedgekeurd"
  - Typografie: text-sm font-medium leading-none
  - Gecombineerd met gebruikersnaam

- **Voorstel**: "Voorstel #1234"
  - Typografie: text-sm text-muted-foreground

- **Tijd**: "2 minuten geleden"
  - Typografie: text-xs text-muted-foreground

#### Notificaties Card (NotificationsList)

**Positie**: Rechts onder, onder Recente Activiteit

**Header**:
- **Titel**: "Notificaties"
  - Typografie: text-base (CardTitle)
- **Badge**: Aantal ongelezen notificaties
  - Component: Badge
  - Inhoud: Getal (bijv. "2")
  - Positie: Rechts in header

**Notificatie Items** (3 items getoond):

Voor elke notificatie:
- **Container**:
  - Padding: p-3
  - Achtergrond: bg-muted (indien ongelezen), transparant (indien gelezen)
  - Vorm: rounded-lg

- **Icon**: Bell
  - Grootte: 20x20px (h-5 w-5)
  - Kleur: text-primary (ongelezen) of text-muted-foreground (gelezen)

- **Titel**: "Nieuw voorstel ontvangen"
  - Typografie: text-sm font-medium leading-none

- **Beschrijving**: "Er is een nieuw herverdelingsvoorstel voor Amsterdam Centrum"
  - Typografie: text-sm text-muted-foreground

- **Tijd**: "5 minuten geleden"
  - Typografie: text-xs text-muted-foreground

---

## Genereren Pagina

**Route**: `/uploads`

**Zichtbaar voor**: Admin en User rollen

### Header Sectie

**Hoofdtitel**: "Genereer Herverdelingsvoorstellen"
- Typografie: Groot, bold

**Subtitel**: "Genereer automatisch nieuwe voorstellen of upload handmatig rapporten"
- Typografie: text-sm text-muted-foreground

### Tabs Component

**Tab Lijst**:
- **Tab 1**: "Automatisch Genereren"
  - Standaard actief
- **Tab 2**: "Handmatig Uploaden"

#### Tab 1: Automatisch Genereren (GenerateProposals)

**Card Header**:
- **Titel**: "Genereer Nieuwe Herverdelingsvoorstellen"
  - Typografie: CardTitle
- **Beschrijving**: "Start het geautomatiseerde proces om nieuwe herverdelingsvoorstellen te genereren op basis van de laatste verkoop- en voorraadgegevens"
  - Typografie: CardDescription

**Formulier Velden**:

1. **Naam van de reeks**
   - Label: "Naam van de reeks"
   - Component: Input
   - Standaardwaarde: Automatisch gegenereerd (bijv. "Herverdeling voor week 12 2025")
   - Help tekst: "Automatisch gegenereerd op basis van het huidige weeknummer en jaar"
     - Typografie: text-xs text-muted-foreground
   - Disabled tijdens generatie

2. **Collectie**
   - Label: "Collectie"
   - Component: Select dropdown
   - Opties:
     - "Alle collecties" (standaard)
     - "Voorjaar Voorkoop 2025"
     - "Zomer 2024"
     - "Herfst 2024"
     - "Winter 2024"
   - Disabled tijdens generatie

3. **Artikelnummers (optioneel)**
   - Label: "Artikelnummers (optioneel)"
   - Component: Input
   - Placeholder: "Kommagescheiden lijst van artikelcodes"
   - Help tekst: "Laat leeg om automatisch kandidaten te selecteren"
     - Typografie: text-xs text-muted-foreground
   - Disabled tijdens generatie

4. **Opties** (Checkboxes)
   - Label: "Opties"
   - Layout: Grid 2 kolommen op desktop
   
   Checkboxes:
   - ☑ "Alleen positieve voorraad" (standaard aangevinkt)
   - ☑ "Minimaal 3 winkels per artikel" (standaard aangevinkt)
   - ☑ "Outlet winkels negeren" (standaard aangevinkt)
   - ☑ "Verkoopcijfers gebruiken" (standaard aangevinkt)
   
   Alle disabled tijdens generatie

**Voortgangsindicator** (tijdens generatie):
- **Progress Bar**:
  - Hoogte: 8px (h-2)
  - Breedte: Volledige breedte
  - Kleur: Primaire kleur
  - Animatie: Vult van 0% naar 100%

- **Status Tekst**:
  - Huidige fase: "Verzamelen van artikelnummers..."
    - Typografie: text-sm text-muted-foreground font-medium
  - Percentage: "45% voltooid"
    - Typografie: text-sm text-muted-foreground
    - Positie: Rechts uitgelijnd

**Fasen tijdens generatie**:
1. "Verzamelen van artikelnummers met run_all.py..." (0-10%)
2. "Genereren van interfiliaalverdeling vooraf rapportages..." (10-30%)
3. "Inlezen rapportages in database..." (30-50%)
4. "Uitvoeren herverdelingsalgoritme..." (50-80%)
5. "Opslaan van voorstellen..." (80-95%)
6. "Afronden van generatie proces..." (95-100%)

**Succes Melding** (na voltooiing):
- Component: Alert
- Icon: Check (16x16px)
- Titel: "Het generatieproces is voltooid"
  - Typografie: AlertTitle
- Beschrijving: "Er zijn {aantal} nieuwe herverdelingsvoorstellen gegenereerd in reeks "{naam}"."
  - Typografie: AlertDescription
- Link: "Bekijk voorstellen"
  - Variant: link
  - Link: `/proposals/batch/{seriesId}`

**Genereer Button**:
- Tekst: "Genereer Voorstellen" (normaal) of "Bezig met genereren..." (tijdens generatie)
- Icon: Play (normaal) of AlertCircle met pulse animatie (tijdens generatie)
- Grootte: 16x16px
- Breedte: Volledige breedte (w-full)
- Disabled: Tijdens generatie
- Functie: Start het generatieproces

#### Tab 2: Handmatig Uploaden (ManualFileUploader)

**Card Header**:
- **Titel**: "Upload Voorraadrapporten"
- **Beschrijving**: "Upload handmatig PDF-rapporten om herverdelingsvoorstellen te genereren"

**Upload Zone**:
- **Drag & Drop Area**:
  - Achtergrond: Gestippelde border
  - Hover state: Gewijzigde achtergrondkleur
  - Icon: Upload cloud icon
  - Tekst: "Sleep bestanden hierheen of klik om te uploaden"
  - Ondersteunde formaten: "PDF bestanden tot 10MB"

- **Bestand Selectie Button**:
  - Tekst: "Selecteer Bestanden"
  - Variant: outline

**Geüploade Bestanden Lijst**:
- Toont geselecteerde bestanden met:
  - Bestandsnaam
  - Bestandsgrootte
  - Verwijder button (X icon)

**Upload Button**:
- Tekst: "Upload en Verwerk"
- Disabled: Wanneer geen bestanden geselecteerd
- Functie: Upload bestanden en start verwerking

### Recente Reeksen Sectie (RecentSeries)

**Positie**: Onder de tabs

**Titel**: "Recente Reeksen"
- Typografie: text-lg font-semibold

**Tabel met kolommen**:
1. Reeks ID
2. Naam
3. Datum
4. Aantal voorstellen
5. Status
6. Acties

---

## Herverdelingsvoorstellen Pagina

**Route**: `/proposals`

**Zichtbaar voor**: Admin en User rollen

### Header Sectie

**Hoofdtitel**: "Herverdelingsvoorstellen"
- Typografie: Groot, bold

**Subtitel**: "Bekijk en beheer alle herverdelingsvoorstellen per reeks"
- Typografie: text-sm text-muted-foreground

**Action Buttons** (rechts in header):
- **Exporteren Button**:
  - Icon: Download (16x16px)
  - Label: "Exporteren"
  - Variant: outline
  - Grootte: sm
  - Functie: Exporteert voorstellen naar bestand

- **Notificaties Button**:
  - Icon: Mail (16x16px)
  - Label: "Notificaties"
  - Variant: outline
  - Grootte: sm
  - Functie: Beheert notificatie-instellingen

### Filter Sectie (ProposalsFilter)

**Filters**:
- Status filter (dropdown)
- Datum filter (date picker)
- Winkel filter (dropdown)
- Zoekbalk voor reeks ID of beschrijving

### Reeksen Tabel (ProposalBatches)

**Card Header**:
- **Titel**: "Reeksen Herverdelingsvoorstellen"
  - Typografie: CardTitle
- **Beschrijving**: "Overzicht van alle gegenereerde reeksen met herverdelingsvoorstellen"
  - Typografie: CardDescription

**Tabel Kolommen**:

1. **Reeks ID**
   - Breedte: 100px
   - Sorteerbaar: Ja (klik op header)
   - Formaat: "#2025032301"
   - Typografie: font-medium
   - Sort icons: ChevronUp/ChevronDown (16x16px)

2. **Beschrijving**
   - Min breedte: 180px
   - Bevat:
     - Type icon: BarChart (blauw, auto) of Box (oranje, manual)
       - Grootte: 16x16px
     - Tekst: "Herverdeling voor week 12 2025"

3. **Datum**
   - Sorteerbaar: Ja
   - Icon: Calendar (16x16px, text-muted-foreground)
   - Formaat: "23 maart 2025"

4. **Aantal**
   - Sorteerbaar: Ja
   - Uitlijning: Gecentreerd
   - Formaat: Getal (bijv. "42")

5. **Voortgang**
   - Sorteerbaar: Ja
   - Bevat:
     - **Status tekst**: "12 goedgekeurd, 3 afgekeurd, 27 wachtend"
       - Typografie: text-xs
     - **Percentage**: "36%"
       - Typografie: text-xs font-medium
       - Positie: Rechts
     - **Progress bar**:
       - Hoogte: 8px (h-2)
       - Achtergrond: bg-secondary
       - Vulling: bg-blue-500 (in behandeling) of bg-green-500 (voltooid)
       - Vorm: rounded-full

6. **Acties**
   - Uitlijning: Rechts
   - Bevat:
     - **"Bekijken" Button**:
       - Icon: Eye (16x16px)
       - Label: "Bekijken"
       - Variant: ghost
       - Grootte: sm
       - Link: `/proposals/batch/{batchId}`
     
     - **"Naar Opdrachten" Button** (alleen bij 100% voortgang):
       - Icon: ClipboardList (16x16px)
       - Label: "Naar Opdrachten"
       - Variant: outline
       - Grootte: sm
       - Kleur: text-green-600
       - Functie: Opent conversie dialog

**Conversie Dialog**:
- **Titel**: "Converteer naar Opdrachten"
  - Typografie: DialogTitle
- **Beschrijving**: "Weet u zeker dat u deze reeks wilt converteren naar opdrachten voor de winkels? Dit zal de goedgekeurde voorstellen omzetten in concrete opdrachten die de winkels kunnen uitvoeren."
  - Typografie: DialogDescription
- **Buttons**:
  - "Annuleren" (variant: outline)
  - "Converteer naar Opdrachten" (bg-green-600 hover:bg-green-700)

---

## Reeks Detail Pagina

**Route**: `/proposals/batch/{id}`

**Zichtbaar voor**: Admin en User rollen

### Header Sectie

**Terug Button**:
- Icon: ArrowLeft (16x16px)
- Label: "Terug"
- Variant: ghost
- Grootte: sm
- Link: "/proposals"

**Hoofdtitel**: "Reeks #{id}"
- Typografie: Groot, bold
- Voorbeeld: "Reeks #2025032301"

**Subtitel**: "Bekijk en beheer alle voorstellen in deze reeks"
- Typografie: text-sm text-muted-foreground

**Action Buttons** (rechts in header):
- **Exporteren Button**:
  - Icon: Download (16x16px)
  - Label: "Exporteren"
  - Variant: outline
  - Grootte: sm

- **Notificaties Button**:
  - Icon: Mail (16x16px)
  - Label: "Notificaties"
  - Variant: outline
  - Grootte: sm

### Reeks Details Card (BatchDetails)

**Informatie weergegeven**:
- Reeks naam
- Aanmaakdatum
- Totaal aantal voorstellen
- Status verdeling (goedgekeurd/afgekeurd/wachtend)
- Voortgangspercentage
- Type (automatisch/handmatig)

### Voorstellen Lijst (BatchProposalsList)

**Tabel Kolommen**:

1. **Voorstel ID**
   - Klikbaar: Ja
   - Link: `/proposals/{id}?batchId={batchId}`
   - Formaat: "#423264"
   - Typografie: font-medium text-blue-600 hover:underline

2. **Artikelcode**
   - Formaat: "ART-12345"

3. **Artikelnaam**
   - Formaat: "Zomerjurk Blauw"

4. **Aantal Winkels**
   - Formaat: Getal (bijv. "5")

5. **Totaal Artikelen**
   - Formaat: Getal (bijv. "24")

6. **Status**
   - Component: Badge
   - Varianten:
     - "Wachtend" (outline, geel)
     - "Goedgekeurd" (default, groen)
     - "Afgekeurd" (destructive, rood)

7. **Acties**
   - **"Bekijken" Button**:
     - Icon: Eye (16x16px)
     - Variant: ghost
     - Grootte: sm
     - Link: `/proposals/{id}?batchId={batchId}`

---

## Voorstel Detail Pagina

**Route**: `/proposals/{id}?batchId={batchId}`

**Zichtbaar voor**: Admin en User rollen

### Header Sectie

**Terug Button**:
- Icon: ArrowLeft (16x16px)
- Label: "Terug"
- Variant: ghost
- Grootte: sm
- Link: `/proposals/batch/{batchId}` (indien batchId aanwezig) of "/proposals"

**Hoofdtitel**: "Voorstel #{id}"
- Typografie: Groot, bold
- Voorbeeld: "Voorstel #423264"

**Subtitel**: "Interfiliaalverdeling voorstel"
- Typografie: text-sm text-muted-foreground

**Action Buttons** (ProposalActions, rechts in header):

- **Voortgangsindicator** (indien deel van batch):
  - Tekst: "Voorstel 12 van 42"
    - Typografie: text-sm text-muted-foreground
  - Progress bar:
    - Hoogte: 4px
    - Breedte: 120px
    - Achtergrond: bg-secondary
    - Vulling: bg-blue-500

- **"Goedkeuren" Button**:
  - Icon: Check (16x16px)
  - Label: "Goedkeuren"
  - Kleur: bg-green-600 hover:bg-green-700
  - Grootte: sm
  - Tooltip bij hover: "Voortgang wordt {newPercentage}%"
  - Functie: Keurt voorstel goed en navigeert naar volgend voorstel

- **"Afkeuren & Bewerken" Button**:
  - Icon: X (16x16px)
  - Label: "Afkeuren & Bewerken"
  - Variant: outline
  - Grootte: sm
  - Kleur: text-red-600
  - Link: `/proposals/{id}/edit?batchId={batchId}`

### Voorstel Details Card (ProposalDetail)

**Artikel Informatie Sectie**:

**Titel**: "Artikel Informatie"
- Typografie: text-lg font-semibold mb-4

**Informatie Grid** (2 kolommen op desktop):
- **Artikelcode**: "ART-12345"
  - Label: "Artikelcode"
  - Typografie: text-sm text-muted-foreground (label), font-medium (waarde)

- **Artikelnaam**: "Zomerjurk Blauw"
  - Label: "Artikelnaam"
  - Typografie: text-sm text-muted-foreground (label), font-medium (waarde)

- **Collectie**: "Zomer 2024"
  - Label: "Collectie"
  - Typografie: text-sm text-muted-foreground (label), font-medium (waarde)

- **Categorie**: "Dames Jurken"
  - Label: "Categorie"
  - Typografie: text-sm text-muted-foreground (label), font-medium (waarde)

**Herverdeling Tabel**:

**Titel**: "Voorgestelde Herverdeling"
- Typografie: text-lg font-semibold mb-4

**Tabel Structuur**:

**Header Rij**:
- Kolom 1: "Winkel" (sticky left)
- Kolom 2-N: Maten (bijv. "XS", "S", "M", "L", "XL")
  - Uitlijning: Gecentreerd
  - Typografie: text-sm font-medium
- Laatste kolom: "Totaal"
  - Uitlijning: Gecentreerd
  - Typografie: text-sm font-medium

**Data Rijen** (per winkel):
- **Winkelnaam**: "Amsterdam Centrum"
  - Typografie: text-sm font-medium
  - Breedte: Sticky left kolom

- **Huidig aantal** (per maat):
  - Formaat: Getal
  - Uitlijning: Gecentreerd
  - Typografie: text-sm
  - Achtergrond: Lichte achtergrondkleur

- **Pijl indicator**:
  - Icon: ArrowRight (16x16px)
  - Kleur: text-muted-foreground
  - Uitlijning: Gecentreerd

- **Nieuw aantal** (per maat):
  - Formaat: Getal
  - Uitlijning: Gecentreerd
  - Typografie: text-sm font-medium
  - Kleur: 
    - Groen (text-green-600) bij toename
    - Rood (text-red-600) bij afname
    - Normaal bij gelijk

- **Verschil indicator** (per maat):
  - Formaat: "+3" of "-2"
  - Typografie: text-xs
  - Kleur: Groen (positief) of rood (negatief)
  - Positie: Onder nieuw aantal

- **Totaal kolom**:
  - Formaat: "Huidig → Nieuw (verschil)"
  - Voorbeeld: "12 → 15 (+3)"
  - Typografie: text-sm font-medium

**Totaal Rij** (onderaan):
- Achtergrond: bg-muted
- Typografie: font-bold
- Bevat totalen per maat en overall totaal
- **Validatie**: Rode achtergrond (bg-red-100) indien totaal niet klopt

**Opmerkingen Sectie** (indien aanwezig):

**Titel**: "Opmerkingen"
- Typografie: text-lg font-semibold mb-4

**Opmerking Card**:
- Achtergrond: bg-muted
- Padding: p-4
- Vorm: rounded-lg
- Inhoud: Tekst van opmerking
- Typografie: text-sm

---

## Voorstel Bewerken Pagina

**Route**: `/proposals/{id}/edit?batchId={batchId}`

**Zichtbaar voor**: Admin en User rollen

### Header Sectie

**Terug Button**:
- Icon: ArrowLeft (16x16px)
- Label: "Terug naar voorstel"
- Variant: ghost
- Grootte: sm
- Link: `/proposals/{id}?batchId={batchId}`

**Hoofdtitel**: "Voorstel #{id} bewerken"
- Typografie: Groot, bold
- Voorbeeld: "Voorstel #423264 bewerken"

**Subtitel**: "Pas de voorgestelde herverdeling aan"
- Typografie: text-sm text-muted-foreground

**Action Buttons** (rechts in header):

- **"Annuleren" Button**:
  - Label: "Annuleren"
  - Variant: outline
  - Grootte: sm
  - Link: `/proposals/{id}?batchId={batchId}`

- **"Opslaan & Goedkeuren" Button**:
  - Label: "Opslaan & Goedkeuren"
  - Kleur: bg-blue-600 hover:bg-blue-700
  - Grootte: sm
  - Disabled: Wanneer niet gebalanceerd of geen wijzigingen
  - Tooltip (bij disabled):
    - Titel: "Ongebalanceerde herverdeling" of "Geen wijzigingen"
    - Beschrijving: Uitleg waarom button disabled is
    - Max breedte: 300px
  - Functie: Slaat wijzigingen op, keurt goed, toont checkmark overlay, navigeert naar volgend voorstel
  - Rationale: Blauw voor "opslaan" acties; groen is gereserveerd voor pure "goedkeuren" acties

### Bewerkbare Herverdeling Tabel (EditableProposalDetail)

**Artikel Informatie** (read-only):
- Zelfde layout als detail pagina
- Niet bewerkbaar

**Bewerkbare Tabel**:

**Structuur**: Vergelijkbaar met detail pagina, maar met bewerkbare cellen

**Bewerkbare Cellen** (nieuw aantal per maat):
- **Input Field**:
  - Type: number
  - Min: 0
  - Breedte: 60px
  - Uitlijning: Gecentreerd
  - Typografie: text-sm
  - Border: Zichtbare border
  - Focus state: Geaccentueerde border

- **Drag & Drop Functionaliteit**:
  - Cursor: grab (bij hover)
  - Cursor: grabbing (tijdens slepen)
  - Drag indicator: Visuele feedback tijdens slepen
  - Drop zone: Gemarkeerd bij hover met sleepbaar item
  - Validatie: Alleen dezelfde maat kan naar andere winkel gesleept worden

- **Wijzigingsindicator**:
  - Achtergrond: Licht geel (bg-yellow-50) bij wijziging
  - Icon: Kleine indicator dat cel gewijzigd is

- **Reset Button** (per cel):
  - Icon: RotateCcw (12x12px)
  - Tooltip: "Reset naar origineel"
  - Zichtbaar: Bij hover over gewijzigde cel
  - Functie: Herstelt originele waarde

**Verschil Weergave**:
- Real-time update bij wijzigingen
- Kleurcodering: Groen (toename), rood (afname)
- Formaat: "+3" of "-2"

**Totaal Rij Validatie**:
- **Gebalanceerd**:
  - Achtergrond: Normaal (bg-muted)
  - Totaal: Zwart
  
- **Ongebalanceerd**:
  - Achtergrond: Rood (bg-red-100 dark:bg-red-900/20)
  - Totaal: Rood (text-red-600)
  - Tooltip: "Ongebalanceerde herverdeling - totaal moet gelijk blijven"

**Visuele Feedback bij Opslaan**:
- **Overlay**:
  - Achtergrond: bg-green-500/20
  - Positie: fixed inset-0
  - Z-index: 50
  - Transitie: opacity 500ms

- **Checkmark Icon**:
  - Grootte: 48x48px
  - Kleur: text-green-500
  - Achtergrond: Witte cirkel met schaduw
  - Animatie: Fade in/out

- **Progress Bar Update**:
  - Animatie: width 500ms ease-in-out
  - Nieuwe breedte: Gebaseerd op nieuwe voortgang

**State Management**:
- Wijzigingen worden bijgehouden in component state
- Custom event "proposalStateChange" wordt gefired bij wijzigingen
- Event bevat: { isBalanced: boolean, hasChanges: boolean }

---

## Opdrachten Pagina

**Routes**: 
- `/assignments` - Opdrachten lijst overzicht (alle opdrachten voor de winkel)
- `/assignments/{id}` - Reeks detail niveau (specifieke reeks opdrachten)
- `/assignments/{id}/{assignmentId}` - Individuele opdracht detail

**Zichtbaar voor**: Store rol

**Route Structuur Toelichting**:
De assignments hebben een geneste structuur met drie niveaus:
1. **Lijst niveau** (`/assignments`): Overzicht van alle opdracht reeksen
2. **Reeks niveau** (`/assignments/{id}`): Alle opdrachten binnen één reeks
3. **Detail niveau** (`/assignments/{id}/{assignmentId}`): Detail van één specifieke opdracht

### Header Sectie (Lijst Niveau)

**Hoofdtitel**: "Mijn Opdrachten"
- Typografie: Groot, bold

**Subtitel**: "Bekijk en verwerk de herverdelingsopdrachten voor uw winkel"
- Typografie: text-sm text-muted-foreground

### Opdrachten Lijst (AssignmentsList)

**Card Header**:
- **Titel**: "Herverdelingsopdrachten"
  - Typografie: CardTitle
- **Beschrijving**: "Overzicht van alle opdrachten voor uw winkel"
  - Typografie: CardDescription

**Tabel Kolommen**:

1. **Reeks ID**
   - Breedte: 100px
   - Sorteerbaar: Ja
   - Formaat: "#2025031501"
   - Typografie: font-medium

2. **Beschrijving**
   - Min breedte: 180px
   - Icon: ClipboardCheck (16x16px, text-blue-500)
   - Tekst: "Herverdeling voor week 11 2025"

3. **Datum**
   - Sorteerbaar: Ja
   - Icon: Calendar (16x16px, text-muted-foreground)
   - Formaat: "15 maart 2025"

4. **Aantal**
   - Sorteerbaar: Ja
   - Uitlijning: Gecentreerd
   - Formaat: Getal (bijv. "12")

5. **Voortgang**
   - Sorteerbaar: Ja
   - Bevat:
     - Status tekst: "5 verwerkt, 7 openstaand"
       - Typografie: text-xs
     - Percentage: "42%"
       - Typografie: text-xs font-medium
     - Progress bar:
       - Hoogte: 8px (h-2)
       - Achtergrond: bg-secondary
       - Vulling: bg-blue-500 (in behandeling) of bg-green-500 (voltooid)

6. **Status**
   - Component: Badge
   - Varianten:
     - "Voltooid" (default, groen)
     - "In behandeling" (outline, blauw)
     - "Nieuw" (secondary, grijs)

7. **Acties**
   - **"Bekijken" Button**:
     - Icon: Eye (16x16px)
     - Label: "Bekijken"
     - Variant: ghost
     - Grootte: sm
     - Link: `/assignments/{assignmentId}`

---

## Instellingen Pagina

**Route**: `/settings`

**Zichtbaar voor**: Alle gebruikersrollen

### Tabs Structuur

**Tab Lijst**:
- "Algemeen"
- "Gebruikers" (alleen Admin)
- "Regels" (alleen Admin/User)
- "API" (alleen Admin)

#### Tab 1: Algemeen

**Sectie: Applicatie Instellingen**

**Velden**:
1. **Applicatie Naam**
   - Label: "Applicatie Naam"
   - Component: Input
   - Standaardwaarde: "Digital Resupplying"

2. **Taal**
   - Label: "Taal"
   - Component: Select
   - Opties: Nederlands, Engels

3. **Tijdzone**
   - Label: "Tijdzone"
   - Component: Select
   - Opties: Verschillende tijdzones

4. **Notificaties**
   - Label: "E-mail notificaties"
   - Component: Checkbox
   - Beschrijving: "Ontvang e-mail notificaties voor nieuwe voorstellen"

**Opslaan Button**:
- Label: "Instellingen Opslaan"
- Variant: default
- Functie: Slaat instellingen op

#### Tab 2: Gebruikers (alleen Admin)

**Gebruikers Tabel**:

**Kolommen**:
1. Naam
2. E-mail
3. Rol
4. Status
5. Laatste login
6. Acties

**Action Buttons**:
- "Nieuwe Gebruiker" button (rechtsboven)
- "Bewerken" button per gebruiker
- "Verwijderen" button per gebruiker

#### Tab 3: Regels (alleen Admin/User)

**Regelset Editor**:

**Sectie: Herverdelingsregels**

**Velden**:
1. **Minimum voorraad per winkel**
   - Label: "Minimum voorraad per winkel"
   - Component: Input (number)
   - Standaardwaarde: 2

2. **Maximum voorraad per winkel**
   - Label: "Maximum voorraad per winkel"
   - Component: Input (number)
   - Standaardwaarde: 10

3. **Minimum aantal winkels**
   - Label: "Minimum aantal winkels per artikel"
   - Component: Input (number)
   - Standaardwaarde: 3

4. **Verkoopcijfers periode**
   - Label: "Verkoopcijfers periode (dagen)"
   - Component: Input (number)
   - Standaardwaarde: 30

**Opslaan Button**:
- Label: "Regels Opslaan"
- Variant: default

#### Tab 4: API (alleen Admin)

**Sectie: API Configuratie**

**OpenAI API Key**:
- Label: "OpenAI API Key"
- Component: Input (password type)
- Placeholder: "sk-..."
- Help tekst: "Vereist voor AI-suggesties en analyse"

**Validatie Button**:
- Label: "Valideer API Key"
- Variant: outline
- Functie: Test of API key geldig is

**Status Indicator**:
- Icon: Check (groen) of X (rood)
- Tekst: "API key is geldig" of "API key is ongeldig"

**Opslaan Button**:
- Label: "API Instellingen Opslaan"
- Variant: default

---

## Algemene UI Componenten

### Buttons

**Varianten**:
- **default**: Primaire kleur, witte tekst
- **outline**: Border met primaire kleur, transparante achtergrond
- **ghost**: Geen border, transparante achtergrond, hover effect
- **link**: Geen styling, gedraagt zich als link

**Groottes**:
- **sm**: Kleine button (h-8, text-sm)
- **default**: Normale button (h-10)
- **lg**: Grote button (h-12, text-lg)

### Cards

**Structuur**:
- **CardHeader**: Bevat titel en beschrijving
- **CardTitle**: Hoofdtitel van card
- **CardDescription**: Subtitel/beschrijving
- **CardContent**: Hoofdinhoud
- **CardFooter**: Footer met acties

**Styling**:
- Border: Subtiele border
- Achtergrond: bg-card
- Schaduw: Lichte schaduw
- Vorm: rounded-lg

### Badges

**Varianten**:
- **default**: Primaire kleur
- **outline**: Border, transparante achtergrond
- **secondary**: Secundaire kleur
- **destructive**: Rode kleur voor errors/warnings
- **success**: Groene kleur voor succes (custom)

**Typografie**: text-xs font-medium

### Tables

**Structuur**:
- **TableHeader**: Header rij met kolom titels
- **TableBody**: Data rijen
- **TableRow**: Individuele rij
- **TableHead**: Header cel
- **TableCell**: Data cel

**Styling**:
- Border: border-b op rijen
- Hover: bg-muted/50 op rijen
- Padding: p-4 op cellen

### Progress Bars

**Eigenschappen**:
- Hoogte: Meestal 8px (h-2)
- Achtergrond: bg-secondary
- Vulling: bg-blue-500 (in behandeling) of bg-green-500 (voltooid)
- Vorm: rounded-full
- Animatie: Smooth transition bij wijziging

### Icons

**Bron**: lucide-react library

**Standaard grootte**: 16x16px (h-4 w-4)

**Kleuren**:
- Primair: Primaire kleur
- Muted: text-muted-foreground
- Success: text-green-500/600
- Error: text-red-500/600
- Warning: text-yellow-500/600

### Tooltips

**Eigenschappen**:
- Achtergrond: Donker (dark mode) of licht (light mode)
- Typografie: text-sm
- Padding: p-2
- Max breedte: Meestal 300px
- Positie: Configureerbaar (top, bottom, left, right)
- Delay: Kort (200ms)

### Dialogs/Modals

**Structuur**:
- **DialogTrigger**: Element dat dialog opent
- **DialogContent**: Hoofdinhoud van dialog
- **DialogHeader**: Header met titel
- **DialogTitle**: Titel van dialog
- **DialogDescription**: Beschrijving/uitleg
- **DialogFooter**: Footer met actie buttons

**Styling**:
- Overlay: Semi-transparante achtergrond
- Content: Witte card met schaduw
- Max breedte: Meestal 500px
- Animatie: Fade in/out

### Alerts

**Varianten**:
- **default**: Informatief (blauw)
- **destructive**: Error/waarschuwing (rood)
- **success**: Succes (groen, custom)

**Structuur**:
- Icon (links)
- AlertTitle (bold)
- AlertDescription (normale tekst)

**Styling**:
- Border: Gekleurde border links
- Achtergrond: Lichte achtergrondkleur
- Padding: p-4
- Vorm: rounded-lg

### Beschikbare UI Component Library

**Bron**: shadcn/ui + custom components

**Basis Componenten** (primair in gebruik):
- **Accordion**: Uitklapbare secties
- **Alert** & **Alert Dialog**: Meldingen en bevestigingsdialogen
- **Avatar**: Gebruikersprofielen
- **Badge**: Status labels
- **Breadcrumb**: Navigatie pad
- **Button** & **Button Group**: Actieknoppen en knoppengroepen
- **Calendar**: Datum selectie
- **Card** (Header, Title, Description, Content, Footer): Container voor content
- **Carousel**: Afbeeldingen carousel
- **Chart**: Data visualisatie
- **Checkbox**: Meervoudige selectie
- **Collapsible**: Inklapbare content
- **Command**: Command palette
- **Dialog**: Modale dialogen
- **Dropdown Menu**: Dropdown opties
- **Input** & **Label**: Form invoervelden
- **Popover**: Zwevendeen informatie
- **Progress**: Voortgangsbalken
- **Select**: Dropdown selectie
- **Separator**: Visuele scheiding
- **Sidebar**: Zijbalk navigatie
- **Skeleton**: Loading placeholders
- **Switch**: Toggle schakelaar
- **Table** (Header, Body, Row, Head, Cell): Data tabellen
- **Tabs** (List, Trigger, Content): Tabbladen
- **Toast** & **Toaster**: Notificaties
- **Tooltip**: Hover informatie

**Uitgebreide Componenten** (beschikbaar voor gebruik):
- **Aspect Ratio**: Aspect ratio container
- **Context Menu**: Rechtermuisklik menu
- **Drawer**: Zijpaneel
- **Empty**: Lege staat componenten
- **Field**: Form veld wrapper
- **Form**: Formulier management
- **Hover Card**: Hover preview kaart
- **Input Group** & **Input OTP**: Gegroepeerde inputs en OTP velden
- **Item**: Lijst items
- **Kbd**: Toetsenbord shortcuts weergave
- **Menubar**: Menu balk
- **Navigation Menu**: Hoofdnavigatie menu
- **Pagination**: Pagina nummering
- **Radio Group**: Enkele keuze optie
- **Resizable**: Versleepbare panelen
- **Scroll Area**: Scrollbare gebieden
- **Sheet**: Schuifbaar paneel
- **Slider**: Waarde slider
- **Sonner**: Geavanceerde toast notificaties
- **Spinner**: Loading animatie
- **Textarea**: Multi-line tekst invoer
- **Toggle** & **Toggle Group**: Toggle knoppen

**Custom Hooks**:
- **use-mobile**: Detecteert mobiele viewport (breakpoint check)
- **use-toast**: Toast notificatie management en queueing

**Component Conventies**:
- Alle componenten volgen shadcn/ui design patterns
- Volledig themeable via Tailwind CSS variabelen
- TypeScript type definities voor alle componenten
- Accessible (WCAG AA compliant)
- Responsive design ingebouwd
- Dark mode support

**Locatie**: `/frontend/components/ui/`

---

## Typografie Systeem

### Font Families

**Sans-serif** (standaard):
- Gebruikt voor: Alle UI tekst
- Font: System font stack

**Monospace**:
- Gebruikt voor: Code, IDs
- Font: Monospace font stack

### Font Sizes

- **text-xs**: 12px - Kleine labels, help tekst
- **text-sm**: 14px - Normale body tekst, table cellen
- **text-base**: 16px - Card titels, belangrijke tekst
- **text-lg**: 18px - Sectie titels
- **text-xl**: 20px - Pagina subtitels
- **text-2xl**: 24px - Statistiek waardes
- **text-3xl**: 30px - Pagina titels

### Font Weights

- **font-normal**: 400 - Normale tekst
- **font-medium**: 500 - Licht geaccentueerde tekst
- **font-semibold**: 600 - Sectie titels
- **font-bold**: 700 - Belangrijke waardes, hoofdtitels

### Line Heights

- **leading-none**: 1 - Compacte tekst
- **leading-tight**: 1.25 - Titels
- **leading-normal**: 1.5 - Normale body tekst
- **leading-relaxed**: 1.625 - Comfortabele leesafstand

---

## Kleurensysteem

### Primaire Kleuren

**Light Mode**:
- **background**: Wit (#FFFFFF)
- **foreground**: Donkergrijs (#0A0A0A)
- **primary**: Blauw (#2563EB)
- **primary-foreground**: Wit (#FFFFFF)

**Dark Mode**:
- **background**: Donkergrijs (#0A0A0A)
- **foreground**: Wit (#FAFAFA)
- **primary**: Lichtblauw (#60A5FA)
- **primary-foreground**: Donkergrijs (#1E293B)

### Secundaire Kleuren

- **secondary**: Lichtgrijs (light) / Donkergrijs (dark)
- **muted**: Zeer lichtgrijs (light) / Zeer donkergrijs (dark)
- **accent**: Accentkleur voor hover states

### Status Kleuren

- **Success**: Groen (#10B981)
- **Error/Destructive**: Rood (#EF4444)
- **Warning**: Geel/Oranje (#F59E0B)
- **Info**: Blauw (#3B82F6)

### Border Kleuren

- **border**: Subtiele grijze border
- **input**: Border voor input velden
- **ring**: Focus ring kleur

---

## Responsive Breakpoints

### Breakpoints

- **sm**: 640px - Kleine tablets
- **md**: 768px - Tablets
- **lg**: 1024px - Kleine laptops
- **xl**: 1280px - Desktops
- **2xl**: 1536px - Grote schermen

### Responsive Patterns

**Grid Layouts**:
- Mobiel: 1 kolom
- Tablet (md): 2 kolommen
- Desktop (lg): 3-4 kolommen

**Sidebar**:
- Mobiel: Inklapbaar overlay
- Desktop: Altijd zichtbaar, vast

**Tables**:
- Mobiel: Horizontaal scrollbaar
- Desktop: Volledige breedte

**Buttons**:
- Mobiel: Volledige breedte (w-full)
- Desktop: Auto breedte

---

## Animaties en Transities

### Standaard Transities

**Duration**:
- Snel: 150ms - Hover effects
- Normaal: 300ms - State changes
- Langzaam: 500ms - Page transitions

**Easing**:
- ease-in-out: Meeste transities
- ease-in: Fade in
- ease-out: Fade out

### Specifieke Animaties

**Progress Bar**:
- Property: width
- Duration: 500ms
- Easing: ease-in-out

**Checkmark Overlay**:
- Property: opacity
- Duration: 500ms
- Easing: ease-in-out

**Hover Effects**:
- Property: background-color, color
- Duration: 150ms
- Easing: ease-in-out

**Pulse** (loading states):
- Animation: pulse
- Duration: 2s
- Iteration: infinite

---

## Toegankelijkheid (A11y)

### Keyboard Navigation

- Alle interactieve elementen zijn bereikbaar via Tab
- Focus indicators zijn duidelijk zichtbaar
- Escape sluit dialogs en dropdowns
- Enter/Space activeert buttons

### Screen Reader Support

- Alle images hebben alt tekst
- Buttons hebben beschrijvende labels
- Form inputs hebben labels
- ARIA labels waar nodig

### Color Contrast

- Alle tekst voldoet aan WCAG AA standaard
- Minimum contrast ratio: 4.5:1 voor normale tekst
- Minimum contrast ratio: 3:1 voor grote tekst

### Focus Management

- Focus ring is duidelijk zichtbaar
- Focus wordt correct beheerd bij dialogs
- Focus keert terug naar trigger bij sluiten

---

## Interactie Patronen

### Hover States

**Buttons**:
- Achtergrond wordt donkerder
- Cursor: pointer

**Links**:
- Underline verschijnt
- Kleur wordt donkerder
- Cursor: pointer

**Table Rows**:
- Achtergrond: bg-muted/50
- Cursor: pointer (indien klikbaar)

**Cards**:
- Lichte schaduw wordt sterker
- Lichte lift effect (transform)

### Click/Tap Feedback

**Buttons**:
- Lichte scale down (transform: scale(0.98))
- Ripple effect (optioneel)

**Checkboxes/Radio**:
- Checkmark animatie
- Achtergrond kleur transitie

### Loading States

**Buttons**:
- Disabled state
- Loading spinner of pulse animatie
- Tekst verandert naar "Laden..." of "Bezig..."

**Progress Bars**:
- Smooth width transitie
- Percentage update

**Skeletons**:
- Pulse animatie
- Placeholder content

### Error States

**Form Inputs**:
- Rode border
- Error message onder veld
- Error icon rechts in veld

**Alerts**:
- Rode achtergrond
- Error icon
- Duidelijke foutmelding

### Success States

**Toasts**:
- Groene achtergrond
- Success icon
- Auto-dismiss na 3-5 seconden

**Inline Feedback**:
- Groene tekst
- Checkmark icon
- Fade in animatie

---

## Development & Debug Pagina's

### Test Pagina

**Route**: `/test`

**Zichtbaar voor**: Development only (niet in productie)

**Doel**: 
- Component testing en verificatie
- Layout testing en responsive design checks
- API endpoint testing
- UI component showcase
- Development debugging

**Gebruik**:
De test pagina is bedoeld voor ontwikkelaars om snel componenten te testen zonder door de hele applicatie te navigeren. Deze route wordt typisch niet getoond in navigatie en is alleen toegankelijk via directe URL.

**Implementatie**:
- Bestand: `/frontend/app/test/page.tsx`
- Niet gelinkt vanuit navigatie
- Bevat experimentele code en testing scenarios

**Productie**:
⚠️ **Belangrijk**: Deze route zou verwijderd of beveiligd moeten worden in productie builds om te voorkomen dat gebruikers toegang hebben tot ontwikkel-functionaliteit.

**Aanbeveling**:
```typescript
// Voorbeeld beveiliging in page.tsx
if (process.env.NODE_ENV === 'production') {
  return <div>404 - Page not found</div>
}
```

---

## Einde Document

Dit document bevat een volledig overzicht van alle pagina's, elementen en hun eigenschappen in de Digital Resupplying Tool GUI. Het kan gebruikt worden als referentie voor ontwikkeling, testing en documentatie doeleinden.

**Laatste update**: 31 oktober 2025
**Versie**: 2.0 - Gesynchroniseerd met Cursor frontend implementatie
**Status**: ✅ Volledig gesynchroniseerd met actuele code

### Changelog
- **31 oktober 2025**: Volledige synchronisatie met Cursor frontend
  - Logo en branding bijgewerkt (MC Company)
  - Browser metadata sectie toegevoegd
  - Button kleur gecorrigeerd (blauw voor opslaan)
  - Assignments routes structuur gedocumenteerd (3 niveaus)
  - Volledige UI component library lijst toegevoegd
  - Development/test pagina gedocumenteerd

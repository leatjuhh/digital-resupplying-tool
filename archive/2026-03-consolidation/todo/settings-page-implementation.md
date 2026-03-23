# Settings Page - Implementatie Plan

## Overzicht
Volledige implementatie van de Instellingen pagina met 4 tabs en rol-gebaseerde toegangscontrole.

## Prioriteit
🔴 **KRITIEK** - Gebruikers krijgen nu 404 bij navigeren naar /settings

## Probleem
De sidebar bevat een link naar `/settings`, maar deze route bestaat niet in de frontend. Dit resulteert in een 404 error voor gebruikers.

## Technische Vereisten

### Basis Structuur
- **Route**: `/frontend/app/settings/page.tsx`
- **Layout**: DashboardShell met Tabs component
- **Rol checks**: Admin, User, Store (verschillende zichtbaarheid per tab)

### Tab 1: Algemeen (Alle rollen)
**Component**: `frontend/components/settings/settings-general.tsx`

**Te implementeren velden:**
- [ ] Applicatie naam input
  - Label: "Applicatie Naam"
  - Component: Input
  - Default: "Digital Resupplying"
  
- [ ] Taal selector
  - Label: "Taal"
  - Component: Select
  - Opties: Nederlands, Engels
  
- [ ] Tijdzone selector
  - Label: "Tijdzone"
  - Component: Select
  - Opties: Verschillende tijdzones (Europe/Amsterdam als default)
  
- [ ] E-mail notificaties checkbox
  - Label: "E-mail notificaties"
  - Component: Checkbox
  - Beschrijving: "Ontvang e-mail notificaties voor nieuwe voorstellen"
  
- [ ] Opslaan button
  - Label: "Instellingen Opslaan"
  - Variant: default
  - Functie: PUT /api/settings

**Voorbeeld code structuur:**
```typescript
export function SettingsGeneral() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Applicatie Instellingen</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="app-name">Applicatie Naam</Label>
          <Input id="app-name" defaultValue="Digital Resupplying" />
        </div>
        {/* Meer velden... */}
      </CardContent>
      <CardFooter>
        <Button>Instellingen Opslaan</Button>
      </CardFooter>
    </Card>
  )
}
```

### Tab 2: Gebruikers (Alleen Admin)
**Component**: `frontend/components/settings/settings-users.tsx`

**Te implementeren:**
- [ ] Gebruikers tabel met kolommen:
  - Naam
  - E-mail
  - Rol (Admin/User/Store)
  - Status (Actief/Inactief)
  - Laatste login
  - Acties (Bewerken/Verwijderen)
  
- [ ] "Nieuwe Gebruiker" button
  - Positie: Rechtsboven in card header
  - Opent: Dialog voor gebruiker toevoegen
  
- [ ] Gebruiker toevoegen dialog
  - Velden: Naam, Email, Rol, Wachtwoord
  - Validatie: Email format, wachtwoord sterkte
  - Actie: POST /api/users
  
- [ ] Gebruiker bewerken dialog
  - Velden: Naam, Email, Rol, Status
  - Actie: PUT /api/users/{id}
  
- [ ] Gebruiker verwijderen confirmatie
  - Dialog met waarschuwing
  - Actie: DELETE /api/users/{id}

**Rol check:**
```typescript
if (userRole !== 'admin') {
  return <Alert>Alleen administrators hebben toegang tot gebruikersbeheer</Alert>
}
```

### Tab 3: Regels (Admin & User)
**Component**: `frontend/components/settings/settings-rules.tsx`

**Te implementeren velden:**
- [ ] Minimum voorraad per winkel
  - Label: "Minimum voorraad per winkel"
  - Component: Input (type="number")
  - Default: 2
  - Min: 0
  
- [ ] Maximum voorraad per winkel
  - Label: "Maximum voorraad per winkel"
  - Component: Input (type="number")
  - Default: 10
  - Min: 1
  
- [ ] Minimum aantal winkels
  - Label: "Minimum aantal winkels per artikel"
  - Component: Input (type="number")
  - Default: 3
  - Min: 1
  
- [ ] Verkoopcijfers periode
  - Label: "Verkoopcijfers periode (dagen)"
  - Component: Input (type="number")
  - Default: 30
  - Min: 1, Max: 365
  
- [ ] Opslaan button
  - Label: "Regels Opslaan"
  - Variant: default
  - Validatie: Check min < max, alle waarden > 0
  - Actie: PUT /api/settings/rules

**Rol check:**
```typescript
if (!['admin', 'user'].includes(userRole)) {
  return <Alert>Deze sectie is alleen beschikbaar voor administrators en gebruikers</Alert>
}
```

### Tab 4: API (Alleen Admin)
**Component**: `frontend/components/settings/settings-api.tsx`

**Te implementeren:**
- [ ] OpenAI API Key input
  - Label: "OpenAI API Key"
  - Component: Input (type="password")
  - Placeholder: "sk-..."
  - Help tekst: "Vereist voor AI-suggesties en analyse"
  
- [ ] Valideer API Key button
  - Label: "Valideer API Key"
  - Variant: outline
  - Functie: POST /api/settings/validate-api-key
  - Response: Success/Error feedback
  
- [ ] Status indicator
  - Success: Check icon (groen) + "API key is geldig"
  - Error: X icon (rood) + "API key is ongeldig"
  - Component: Alert met icon
  
- [ ] Opslaan button
  - Label: "API Instellingen Opslaan"
  - Variant: default
  - Actie: PUT /api/settings/api

**Rol check:**
```typescript
if (userRole !== 'admin') {
  return <Alert>Alleen administrators hebben toegang tot API instellingen</Alert>
}
```

## Main Settings Page Structuur

**Bestand**: `frontend/app/settings/page.tsx`

```typescript
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SettingsGeneral } from "@/components/settings/settings-general"
import { SettingsUsers } from "@/components/settings/settings-users"
import { SettingsRules } from "@/components/settings/settings-rules"
import { SettingsApi } from "@/components/settings/settings-api"

export default function SettingsPage() {
  // TODO: Get user role from auth context
  const userRole = "admin" // Placeholder
  
  return (
    <DashboardShell>
      <DashboardHeader
        heading="Instellingen"
        text="Beheer applicatie instellingen en voorkeuren"
      />
      <Tabs defaultValue="general" className="mt-6">
        <TabsList>
          <TabsTrigger value="general">Algemeen</TabsTrigger>
          {userRole === "admin" && (
            <TabsTrigger value="users">Gebruikers</TabsTrigger>
          )}
          {["admin", "user"].includes(userRole) && (
            <TabsTrigger value="rules">Regels</TabsTrigger>
          )}
          {userRole === "admin" && (
            <TabsTrigger value="api">API</TabsTrigger>
          )}
        </TabsList>
        
        <TabsContent value="general">
          <SettingsGeneral />
        </TabsContent>
        
        {userRole === "admin" && (
          <TabsContent value="users">
            <SettingsUsers />
          </TabsContent>
        )}
        
        {["admin", "user"].includes(userRole) && (
          <TabsContent value="rules">
            <SettingsRules />
          </TabsContent>
        )}
        
        {userRole === "admin" && (
          <TabsContent value="api">
            <SettingsApi />
          </TabsContent>
        )}
      </Tabs>
    </DashboardShell>
  )
}
```

## API Endpoints Benodigd

**Backend endpoints die moeten bestaan of aangemaakt worden:**

```python
# General settings
GET  /api/settings          # Alle instellingen ophalen
PUT  /api/settings          # Algemene instellingen updaten

# Users (Admin only)
GET    /api/users           # Alle gebruikers ophalen
POST   /api/users           # Nieuwe gebruiker aanmaken
GET    /api/users/{id}      # Specifieke gebruiker ophalen
PUT    /api/users/{id}      # Gebruiker updaten
DELETE /api/users/{id}      # Gebruiker verwijderen

# Rules (Admin/User)
GET  /api/settings/rules    # Herverdelingsregels ophalen
PUT  /api/settings/rules    # Herverdelingsregels updaten

# API (Admin only)
POST /api/settings/validate-api-key  # Valideer OpenAI API key
PUT  /api/settings/api               # API instellingen updaten
```

## Dependencies

**Reeds beschikbaar:**
- shadcn/ui components: Tabs, Input, Select, Checkbox, Button, Table, Card, Alert, Dialog
- DashboardShell en DashboardHeader
- Layout components

**Mogelijk nieuw benodigd:**
- `useUserRole` hook (indien nog niet bestaat voor rol-gebaseerde toegang)
- API client functies in `/frontend/lib/api.ts`

## Testing Checklist

- [ ] Settings pagina is bereikbaar via sidebar
- [ ] Alle 4 tabs zijn zichtbaar voor Admin rol
- [ ] Gebruikers tab is verborgen voor User en Store rollen
- [ ] Regels tab is zichtbaar voor Admin en User, verborgen voor Store
- [ ] API tab is alleen zichtbaar voor Admin
- [ ] Formulieren hebben werkende validatie
- [ ] API calls werken correct
- [ ] Error handling werkt (netwerk fouten, validatie fouten)
- [ ] Success feedback wordt getoond na opslaan
- [ ] Settings worden persistent opgeslagen
- [ ] Page styling matcht rest van applicatie

## Acceptatie Criteria

✅ **Functioneel:**
- [ ] Alle 4 tabs zijn geïmplementeerd en functioneel
- [ ] Rol-gebaseerde zichtbaarheid werkt correct
- [ ] Alle formulieren hebben validatie
- [ ] API integratie werkt met error handling
- [ ] Settings worden correct opgeslagen en opgehaald

✅ **UI/UX:**
- [ ] Styling consistent met GUI-COMPLETE-OVERVIEW.md
- [ ] Responsive design werkt op alle schermformaten
- [ ] Loading states zijn geïmplementeerd
- [ ] Error states zijn duidelijk gecommuniceerd
- [ ] Success feedback is aanwezig

✅ **Code Kwaliteit:**
- [ ] TypeScript types zijn correct
- [ ] Components zijn herbruikbaar
- [ ] Error handling is robuust
- [ ] Code volgt project conventies

## Geschatte Tijd

**Totaal: 4-6 uur**

- Settings page setup: 30 min
- Tab 1 (Algemeen): 45 min
- Tab 2 (Gebruikers): 90 min (meest complex)
- Tab 3 (Regels): 45 min
- Tab 4 (API): 45 min
- API integratie: 60 min
- Testing & bug fixes: 60 min

## Referenties

- GUI-COMPLETE-OVERVIEW.md - Sectie "Instellingen Pagina" (regel ~900-1050)
- Bestaande pagina's als voorbeeld: `/app/uploads/page.tsx`, `/app/proposals/page.tsx`
- shadcn/ui documentatie: https://ui.shadcn.com/

## Status

- [ ] TODO - Nog niet gestart
- [ ] IN PROGRESS - Bezig met implementatie
- [ ] REVIEW - Klaar voor review
- [ ] DONE - Geïmplementeerd en getest

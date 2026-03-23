# Recent Uploads Component - Verificatie & Cleanup

## Doel
Bepalen welk component (`recent-series.tsx` vs `recent-uploads.tsx`) actief gebruikt wordt en of het andere veilig verwijderd kan worden.

## Prioriteit
🟢 **LAAG** - Geen impact op functionaliteit, wel code cleanup en onderhoudbaarheid

## Probleem
Er zijn twee vergelijkbare componenten in de uploads directory:
- `frontend/components/uploads/recent-series.tsx`
- `frontend/components/uploads/recent-uploads.tsx`

Het is onduidelijk:
1. Welk component wordt daadwerkelijk gebruikt?
2. Wat is het verschil in functionaliteit?
3. Is één component legacy/oud en kan het verwijderd worden?
4. Of hebben beide een unieke functie?

## Verificatie Stappen

### Stap 1: Check Huidige Gebruik
**Actie:** Bekijk welk component geïmporteerd wordt in de uploads pagina

**Te controleren bestanden:**
- [ ] `/frontend/app/uploads/page.tsx` - Welk component wordt geïmporteerd?
- [ ] Check import statement: `RecentSeries` of `RecentUploads`?

**Verwachte uitkomst:**
```typescript
// In page.tsx, een van deze twee:
import { RecentSeries } from "@/components/uploads/recent-series"
// OF
import { RecentUploads } from "@/components/uploads/recent-uploads"
```

### Stap 2: Functionaliteit Vergelijking
**Actie:** Open beide component bestanden en vergelijk

**Te vergelijken:**
- [ ] Props interfaces - Welke props accepteert elk component?
- [ ] Data fetching - Waar halen ze data vandaan?
- [ ] Rendering logica - Wat tonen ze precies?
- [ ] Tabel kolommen - Verschillen in weergegeven data?
- [ ] Functionaliteit - Unieke features per component?

**Template voor vergelijking:**
```markdown
| Aspect              | RecentSeries        | RecentUploads       |
|---------------------|---------------------|---------------------|
| Props               | ...                 | ...                 |
| Data source         | ...                 | ...                 |
| Weergave            | ...                 | ...                 |
| Kolommen            | ...                 | ...                 |
| Unieke features     | ...                 | ...                 |
```

### Stap 3: Dependency Check
**Actie:** Zoek in hele codebase naar gebruik

**Commands om uit te voeren:**
```bash
# Windows PowerShell
cd frontend
Get-ChildItem -Recurse -Include *.tsx,*.ts | Select-String "RecentSeries" -List
Get-ChildItem -Recurse -Include *.tsx,*.ts | Select-String "RecentUploads" -List
```

**Te noteren:**
- [ ] Aantal bestanden dat `RecentSeries` importeert: _____
- [ ] Aantal bestanden dat `RecentUploads` importeert: _____
- [ ] Locaties waar gebruikt: _____

### Stap 4: Git Geschiedenis Check (Optioneel)
**Actie:** Bekijk git log voor context

```bash
git log --oneline --all -- frontend/components/uploads/recent-series.tsx
git log --oneline --all -- frontend/components/uploads/recent-uploads.tsx
```

**Te achterhalen:**
- [ ] Wanneer is elk component aangemaakt?
- [ ] Was er een specifieke reden voor twee componenten?
- [ ] Zijn er commit messages die context geven?

## Beslisboom

### Scenario A: Beide Componenten Identiek
**Als:** Beide componenten doen exact hetzelfde

**Actie:**
- [ ] Kies één component als "source of truth" (meestal de nieuwste of best onderhouden)
- [ ] Verwijder het andere component
- [ ] Update alle imports
- [ ] Test dat alles nog werkt
- [ ] Update GUI-COMPLETE-OVERVIEW.md indien nodig

### Scenario B: Beide Componenten Verschillend
**Als:** Componenten hebben unieke functionaliteit

**Actie:**
- [ ] Documenteer het verschil in functionaliteit
- [ ] Hernoem indien naam misleidend is
- [ ] Update GUI-COMPLETE-OVERVIEW.md met beide componenten
- [ ] Voeg comments toe in code voor toekomstige developers

**Documentatie template:**
```markdown
## Recent Series vs Recent Uploads

### RecentSeries
- **Doel**: [Beschrijving]
- **Data bron**: [API endpoint]
- **Gebruik**: [Wanneer te gebruiken]

### RecentUploads
- **Doel**: [Beschrijving]
- **Data bron**: [API endpoint]
- **Gebruik**: [Wanneer te gebruiken]
```

### Scenario C: Eén Component Ongebruikt
**Als:** Eén component wordt nergens geïmporteerd

**Actie:**
- [ ] Verplaats ongebruikt component naar `archive/` of `deprecated/`
- [ ] Voeg opmerking toe waarom het bewaard wordt (of verwijder compleet)
- [ ] Update documentatie indien nodig

## Aanbevolen Naamgeving

Als beide componenten blijven bestaan, overweeg duidelijkere namen:

**Huidige namen:**
- `recent-series.tsx` → Onduidelijk wat "series" betekent
- `recent-uploads.tsx` → Onduidelijk wat "uploads" betekent

**Betere alternatieven (indien beide nodig):**
- `recent-proposal-batches.tsx` - Voor reeksen/batches van voorstellen
- `recent-pdf-uploads.tsx` - Voor individuele PDF uploads
- `recent-generation-runs.tsx` - Voor generatie runs
- etc.

## Impact Analyse

### Bij verwijderen van component:
**Voordelen:**
- ✅ Minder code om te onderhouden
- ✅ Duidelijkere codebase
- ✅ Geen verwarring over welke te gebruiken

**Risico's:**
- ⚠️ Mogelijk verlies van functionaliteit als verkeerd component verwijderd
- ⚠️ Broken imports als niet goed getest

### Bij behouden van beide:
**Voordelen:**
- ✅ Geen risico op functieverlies
- ✅ Beide use cases blijven ondersteund

**Nadelen:**
- ❌ Verhoogde onderhoudskosten
- ❌ Mogelijke verwarring voor developers

## Uitvoering Checklist

### Voorafgaand aan wijzigingen:
- [ ] Maak git branch: `git checkout -b cleanup/recent-uploads-verification`
- [ ] Maak backup van beide bestanden
- [ ] Noteer huidige functionaliteit

### Na beslissing:
- [ ] Voer geplande wijzigingen uit (verwijderen/hernoemen/documenteren)
- [ ] Run `npm run build` om TypeScript errors te checken
- [ ] Test de uploads pagina in browser
- [ ] Controleer dat alle data correct geladen wordt
- [ ] Update `GUI-COMPLETE-OVERVIEW.md` indien nodig
- [ ] Commit met duidelijke message

### Git commit voorbeelden:
```bash
# Als component verwijderd
git commit -m "cleanup: Remove unused recent-uploads component

RecentSeries is the active component used in /uploads page.
RecentUploads was legacy code from initial V0 export."

# Als beide behouden
git commit -m "docs: Clarify RecentSeries vs RecentUploads usage

Added documentation explaining the difference:
- RecentSeries: Shows proposal batch history
- RecentUploads: Shows PDF upload history
Both serve different purposes and are both in use."
```

## Verwachte Uitkomsten

### Meest waarschijnlijk scenario:
Op basis van de file structuur en naamgeving is het waarschijnlijk dat:
- `RecentSeries` de actieve component is (past bij "Recente Reeksen" in documentatie)
- `RecentUploads` mogelijk legacy is van eerdere iteratie

### Verificatie bevestigt dit als:
- `page.tsx` importeert alleen `RecentSeries`
- `RecentUploads` heeft geen imports elders
- Git history toont `RecentSeries` als nieuwer

### Dan actie:
1. Verwijder `recent-uploads.tsx`
2. Behoud `recent-series.tsx`
3. Documentatie is al correct (vermeldt "Recente Reeksen")

## Geschatte Tijd

**Totaal: 15-30 minuten**

- Stap 1 (Check gebruik): 5 min
- Stap 2 (Vergelijking): 5 min
- Stap 3 (Dependency check): 5 min
- Stap 4 (Git history): 5 min (optioneel)
- Uitvoering & testing: 10 min

## Referenties

- GUI-COMPLETE-OVERVIEW.md - Sectie "Genereren Pagina > Recente Reeksen Sectie"
- `/frontend/app/uploads/page.tsx` - De pagina die component gebruikt
- `/frontend/components/uploads/` - Component directory

## Status

- [ ] TODO - Nog niet gestart
- [ ] IN PROGRESS - Bezig met verificatie
- [ ] DECISION MADE - Beslissing genomen, klaar voor uitvoering
- [ ] DONE - Verificatie compleet en wijzigingen doorgevoerd

## Bevindingen

_Noteer hier je bevindingen tijdens de verificatie:_

### Huidige gebruik:
- Component gebruikt in page.tsx: _____
- Aantal imports RecentSeries: _____
- Aantal imports RecentUploads: _____

### Functionaliteit verschillen:
- _____

### Beslissing:
- [ ] Verwijder RecentUploads (ongebruikt)
- [ ] Verwijder RecentSeries (ongebruikt)
- [ ] Behoud beide (unieke functionaliteit)
- [ ] Hernoem voor duidelijkheid

### Reden:
_____

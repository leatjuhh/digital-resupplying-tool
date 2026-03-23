# Digital Resupplying Tool

Een consolidatie-reset van de bestaande codebasis, zonder de werkende kernflow te breken.

## Start Hier

Gebruik voor nieuwe sessies alleen deze drie documenten:

1. [README.md](README.md)
2. [docs/technical/current-state.md](docs/technical/current-state.md)
3. [todo/master-backlog.md](todo/master-backlog.md)

[docs/PROJECT_CONTEXT_INDEX.md](docs/PROJECT_CONTEXT_INDEX.md) blijft de routekaart voor aanvullende en historische documentatie.

## Leidende Kernflow

De huidige productkern is:

`PDF ingest -> proposal generatie/opslag -> proposal detail/edit/review`

Deze flow is leidend tijdens de consolidatie. Routepaden en payloadvormen van de actieve proposalflow horen in deze fase niet te veranderen.

## Wat Nu Leidt

- Backend API voor PDF ingest en proposal-opslag
- Frontend proposal detail- en editflow
- Lokale startflow via `.\dev.ps1`
- De drie startdocumenten hierboven

## Wat Bewust Niet Leidend Is

Deze onderdelen blijven voorlopig bereikbaar, maar horen niet bij de stabiele kern:

- Assignments UI
- Settings-varianten met placeholder- of mockgedrag
- Dashboardbreedte buiten de proposal-kern
- Verdere baseline-uitbouw van het algoritme

Niet-leidende schermen worden tijdens consolidatie expliciet als zodanig gemarkeerd.

## Snel Starten

Aanbevolen:

```powershell
.\dev.ps1
```

Als `3000` of `8000` nog bezet is door een vorige sessie:

```powershell
.\dev.ps1 -Restart
```

Alternatief:

```powershell
npm run dev
```

Standaard URLs:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

Zie [docs/getting-started/quick-start.md](docs/getting-started/quick-start.md) voor run- en debugdetails.

## Documentatiestatus

- Actieve waarheid: `README.md`, `docs/technical/current-state.md`, `todo/master-backlog.md`
- Aanvullende documentatie: `docs/getting-started/`, `docs/guides/`, geselecteerde `docs/technical/`
- Historische context: `archive/` en `docs/sessions/`

Tijdens de consolidatie van maart 2026 zijn ingehaalde roadmap-, analyse- en handoffbestanden verplaatst naar `archive/2026-03-consolidation/`.

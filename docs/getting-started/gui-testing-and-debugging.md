---
title: GUI Testing and Debugging
category: getting-started
tags: [gui, testing, debugging, playwright, browser]
last_updated: 2026-03-23
related:
  - quick-start.md
  - browser-debugging.md
  - ../guides/authentication-testing.md
  - ../../README.md
---

# GUI Testing and Debugging

Korte handleiding om de app lokaal te starten, via de GUI te testen en browserproblemen snel te debuggen.

## Inhoudsopgave
- [Snelste workflow](#snelste-workflow)
- [Handmatig testen via de GUI](#handmatig-testen-via-de-gui)
- [Leidende Kernflow Regressiecheck](#leidende-kernflow-regressiecheck)
- [Settings en RBAC Regressiecheck](#settings-en-rbac-regressiecheck)
- [Dashboard Sanity Check](#dashboard-sanity-check)
- [Debuggen in een echte browser](#debuggen-in-een-echte-browser)
- [Snelle browsertest](#snelle-browsertest)
- [Belangrijke paden](#belangrijke-paden)

---

## Snelste workflow

Start vanuit de project-root:

```powershell
.\dev.ps1
```

Als je direct een hangende vorige frontend/backend-sessie wilt vervangen:

```powershell
.\dev.ps1 -Restart
```

Dit script:
- controleert de backend-venv
- initialiseert de database als dat nodig is
- controleert frontend dependencies
- start backend en frontend samen

Met `-Restart` stopt het script eerst de processen die poort `3000` of `8000` bezet houden en start daarna beide servers opnieuw.

Open daarna:
- Frontend GUI: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`

## Handmatig testen via de GUI

Gebruik de app in de browser zoals een normale gebruiker:

1. Start de app met `.\dev.ps1`.
2. Open `http://localhost:3000`.
3. Test de gewenste flow in de GUI, bijvoorbeeld login, navigatie of batchschermen.
4. Controleer backend-calls in Swagger via `http://localhost:8000/docs` als je wilt verifiëren of een endpoint werkt.

Voor snelle basiscontrole is de loginpagina de eenvoudigste eerste check:
- `http://localhost:3000/login`

## Leidende Kernflow Regressiecheck

Gebruik deze compacte checklist na wijzigingen aan auth, ingest of proposalflow.

1. Start de app met `.\dev.ps1`.
2. Open `http://localhost:3000/login`.
3. Bevestig dat:
   - het loginformulier zichtbaar wordt
   - "Authenticatie controleren..." weer verdwijnt
4. Log in als `admin / Admin123!`.
5. Open `/uploads`.
6. Upload een bekende test-PDF uit `dummyinfo/`, bij voorkeur `422557.pdf`.
7. Open de gegenereerde batch proposals.
8. Open één proposal detailpagina.
9. Controleer de happy path:
   - reject
   - edit
   - approve
10. Bevestig dat de flow zonder zichtbare console- of API-fouten doorloopt.

Praktische noot:
- blijft de auth-loader hangen na eerdere sessies of cache-issues, doe eerst een harde refresh (`Ctrl+F5`) of leeg browser storage.

## Settings en RBAC Regressiecheck

Gebruik deze check na wijzigingen aan auth, permissies, users, rollen of settings-routes.

1. Start de app met `.\dev.ps1`.
2. Log in als `admin / Admin123!`.
3. Open `/settings`.
4. Bevestig dat de tabs `Algemeen`, `Regels`, `Gebruikers`, `Rollen` en `API` zichtbaar zijn.
5. Wijzig een algemene setting tijdelijk, bevestig dat de save slaagt en zet de waarde daarna terug.
6. Maak via `Gebruikers` een tijdelijke store-user aan met `store_code` en `store_name`, controleer dat deze verschijnt en verwijder hem weer.
7. Open `Rollen`, wijzig tijdelijk permissies voor een niet-adminrol en sla op.
8. Log uit en log in met die rol om te bevestigen dat tabzichtbaarheid of read-only gedrag meeverandert.
9. Log daarna opnieuw in als admin en herstel de permissies.
10. Log in als `store / Store123!` en bevestig dat `Instellingen` niet in de sidebar staat en directe navigatie naar `/settings` terugstuurt.

## Dashboard Sanity Check

Gebruik deze check na wijzigingen aan het dashboard, de samenvatting of de overzichtsschermen.

1. Start de app met `.\dev.ps1`.
2. Log in als `admin / Admin123!`.
3. Open `/`.
4. Bevestig dat de kaarten echte data tonen en geen samplewaarden.
5. Controleer dat `Wachtende reeksen`, `Recente systeemevents` en `Aandachtspunten` zichtbaar zijn.
6. Controleer dat de periodeselectie alleen meldt dat er nog geen historische vergelijking beschikbaar is.
7. Open een voorstel, batch en assignment-link vanuit de dashboardoverzichten en bevestig dat de navigatie klopt.

## Debuggen in een echte browser

Voor live browserdebugging gebruik je drie terminals.

### Terminal 1: app starten

```powershell
.\dev.ps1
```

Als de pre-flight check meldt dat poorten al in gebruik zijn:

```powershell
.\dev.ps1 -Restart
```

### Terminal 2: debugbrowser openen

```powershell
npm run browser:debug
```

Dit opent Edge of Chrome met een apart debugprofiel en remote debugging op poort `9222`.

### Terminal 3: browser watcher starten

```powershell
npm run browser:watch
```

De watcher logt live:
- console errors en warnings
- uncaught page errors
- mislukte requests
- responses met status `400+`

Reproduceer daarna het probleem in de geopende browser. Bekijk de meldingen in de watcher-terminal of in `browser-artifacts/`.

## Snelle browsertest

Er is een bestaande Playwright smoke test voor:
- bereikbaarheid van `/login`
- backend health endpoint `/health`
- admin settings-tabs
- user settingsrechten (`Algemeen` read-only, `Regels` bewerkbaar)
- store redirect weg van `/settings` en assignments-toegang
- dashboardweergave met echte summary cards, pending reeksen, systeemevents en aandachtspunten

Run:

```powershell
npm run browser:smoke
```

Belangrijk:
- start eerst de app met `.\dev.ps1`
- Playwright verwacht standaard frontend op `http://127.0.0.1:3000`
- de backend health check gebruikt standaard `http://127.0.0.1:8000`

Bij failures worden trace, screenshot en video bewaard voor analyse.

## Belangrijke paden

- Debugbrowser-profiel: `C:\Codex\DRT\.browser-debug-profile`
- Browserlogs: `C:\Codex\DRT\browser-artifacts`
- Playwright report: `C:\Codex\DRT\playwright-report`
- Testbestand: `C:\Codex\DRT\tests\browser\smoke.spec.ts`

## Wanneer welke methode gebruiken

- Gebruik `.\dev.ps1` voor normaal lokaal werken.
- Gebruik `npm run browser:debug` en `npm run browser:watch` als een GUI-bug lastig reproduceerbaar is.
- Gebruik `npm run browser:smoke` voor een snelle regressiecheck na wijzigingen.

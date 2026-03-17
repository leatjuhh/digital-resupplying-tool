---
title: GUI Testing and Debugging
category: getting-started
tags: [gui, testing, debugging, playwright, browser]
last_updated: 2026-03-17
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
- [Debuggen in een echte browser](#debuggen-in-een-echte-browser)
- [Snelle browsertest](#snelle-browsertest)
- [Belangrijke paden](#belangrijke-paden)

---

## Snelste workflow

Start vanuit de project-root:

```powershell
.\dev.ps1
```

Dit script:
- controleert de backend-venv
- initialiseert de database als dat nodig is
- controleert frontend dependencies
- start backend en frontend samen

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

## Debuggen in een echte browser

Voor live browserdebugging gebruik je drie terminals.

### Terminal 1: app starten

```powershell
.\dev.ps1
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

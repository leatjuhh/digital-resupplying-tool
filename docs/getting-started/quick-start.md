---
title: Quick Start
category: getting-started
tags: [quick-start, setup, development]
last_updated: 2026-03-30
related:
  - installation.md
  - troubleshooting.md
  - gui-testing-and-debugging.md
  - ../../README.md
---

# Quick Start

De standaardmanier om de app lokaal te starten is nu bewust simpel gehouden: gebruik altijd dezelfde launcher vanuit de project-root.

## Starten

Aanbevolen:

```powershell
.\dev.ps1
```

Als frontend of backend nog draait en je vanuit dezelfde launcher schoon wilt herstarten:

```powershell
.\dev.ps1 -Restart
```

Alternatief:

```powershell
npm run dev
```

`npm run dev` is nu alleen een wrapper rond `.\dev.ps1`. Er is dus nog maar één echte startflow.

## Wat `.\dev.ps1` doet

1. Controleert of de backend virtual environment bestaat.
2. Controleert of de database bestaat en initialiseert die indien nodig.
3. Controleert of frontend dependencies aanwezig zijn.
4. Controleert of poorten `3000` en `8000` vrij zijn.
5. Start backend en frontend met kleurgecodeerde logs in dezelfde terminal.

Met `-Restart` doet hetzelfde script nog een extra stap:

6. Stopt eerst de processen die `3000` en `8000` bezet houden, inclusief child processes, en start daarna beide servers opnieuw.

## URLs

- Frontend: `http://127.0.0.1:3000`
- Login: `http://127.0.0.1:3000/login`
- Backend API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

Extra sanity check na een correcte start:

- open `http://127.0.0.1:3000/proposals`
- bevestig dat de kaart `Externe Algoritmestatus` zichtbaar is

## Losse startopties

Alleen backend:

```powershell
npm run dev:backend
```

Alleen frontend:

```powershell
npm run dev:frontend
```

Setup eenmalig of na een verse pull:

```powershell
npm run setup
```

## Stoppen

Druk `Ctrl+C` in de terminal waar de servers draaien.

Als een vorige sessie niet netjes is afgesloten en poorten bezet blijven, gebruik:

```powershell
.\dev.ps1 -Restart
```

## Opmerking over `start-dev.ps1`

`.\start-dev.ps1` bestaat nog, maar opent alleen een nieuw PowerShell-venster dat `.\dev.ps1` start. Gebruik voor normale development direct `.\dev.ps1`.

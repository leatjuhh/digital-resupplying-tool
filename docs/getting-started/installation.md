---
title: Installation
category: getting-started
tags: [installation, setup, node, python]
last_updated: 2026-03-17
related:
  - quick-start.md
  - troubleshooting.md
  - ../../README.md
---

# Installation

Deze gids beschrijft de minimale setup om DRT stabiel lokaal te draaien na een clone of pull.

## Vereisten

- Windows met PowerShell
- Python `3.11+`
- Node.js `18.17+` en `<23`
- npm `9+`

## Eerste setup

Voer vanuit de project-root uit:

```powershell
npm run setup
```

Dit doet:
- backend virtual environment aanmaken als die ontbreekt
- backend dependencies installeren
- database initialiseren als die nog niet bestaat
- frontend dependencies installeren

## Daarna starten

Gebruik voortaan:

```powershell
.\dev.ps1
```

Of, als je liever via npm werkt:

```powershell
npm run dev
```

Beide gebruiken nu dezelfde startflow.

## Deelsetup

Alleen backend:

```powershell
npm run setup:backend
```

Alleen frontend:

```powershell
npm run setup:frontend
```

## Handmatige verificatie

Na starten horen deze URLs te werken:

- `http://127.0.0.1:3000/login`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Veelvoorkomende valkuilen

- Gebruik niet meer oude losse startcommando's als primaire route.
- Gebruik niet `start-dev.ps1` als standaardworkflow; dat is nu alleen een wrapper naar `dev.ps1`.
- Zorg dat Node en npm echt lokaal beschikbaar zijn; de repo verwacht geen pnpm als primaire package manager.

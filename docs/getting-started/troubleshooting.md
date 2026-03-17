---
title: Troubleshooting
category: getting-started
tags: [troubleshooting, debugging, setup]
last_updated: 2026-03-17
related:
  - quick-start.md
  - installation.md
  - gui-testing-and-debugging.md
---

# Troubleshooting

Gebruik eerst altijd de standaardroute:

```powershell
.\dev.ps1
```

Veel problemen ontstaan juist door oude handmatige startstappen.

## Poort 3000 of 8000 al in gebruik

Controleer welke processen luisteren:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 3000,8000
```

Stop daarna het relevante proces met de juiste PID:

```powershell
Stop-Process -Id <PID> -Force
```

## Backend virtual environment ontbreekt

Run:

```powershell
npm run setup:backend
```

## Frontend dependencies ontbreken

Run:

```powershell
npm run setup:frontend
```

## `npm` of `node` niet gevonden

Installeer Node.js LTS opnieuw en heropen je terminal.

Controle:

```powershell
node --version
npm --version
```

## Database ontbreekt

Normaal maakt `.\dev.ps1` die zelf aan. Als dat niet lukt:

```powershell
npm run setup:backend
```

## Alleen backend of frontend starten voor diagnose

Backend:

```powershell
npm run dev:backend
```

Frontend:

```powershell
npm run dev:frontend
```

## Browserbugs debuggen

Gebruik hiervoor de aparte gids:

- [Browser Debugging](browser-debugging.md)
- [GUI Testing and Debugging](gui-testing-and-debugging.md)

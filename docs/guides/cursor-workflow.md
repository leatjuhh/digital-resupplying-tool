---
title: Cursor Workflow
category: guides
tags: [cursor, workflow, development]
last_updated: 2026-03-17
related:
  - ../getting-started/quick-start.md
  - ../getting-started/gui-testing-and-debugging.md
  - ../../README.md
---

# Cursor Workflow

De huidige Cursor-workflow is bewust teruggebracht naar weinig varianten. Minder startpaden betekent minder kans dat lokale omgevingen na een pull uit elkaar lopen.

## Aanbevolen workflow

### Terminal 1: app runnen

```powershell
.\dev.ps1
```

Hier zie je backend- en frontendlogs samen met prefixes `[BACKEND]` en `[FRONTEND]`.

### Terminal 2: optionele test of debug

Voor browserdebugging:

```powershell
npm run browser:debug
```

Voor browser watcher:

```powershell
npm run browser:watch
```

Voor smoke test:

```powershell
npm run browser:smoke
```

## Wanneer losse servers handig zijn

Alleen backend:

```powershell
npm run dev:backend
```

Alleen frontend:

```powershell
npm run dev:frontend
```

Gebruik dit alleen als je heel gericht één kant wilt debuggen. Voor dagelijks werk blijft `.\dev.ps1` de standaard.

## Waarom deze workflow

- één bron van waarheid voor starten
- minder shell-afhankelijk gedrag
- minder kans op breuk na een pull
- logs blijven goed leesbaar voor development en debugging

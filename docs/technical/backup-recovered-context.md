---
title: Backup Recovered Context
category: technical
tags: [backup, uploads, recovery, product-context]
last_updated: 2026-03-14
related:
  - ../PROJECT_CONTEXT_INDEX.md
  - ../../todo/consolidated-priorities-2026-03-14.md
  - ../../frontend/PROJECT-OVERVIEW.md
---

# Backup Recovered Context

Dit document legt context vast die teruggevonden is in de backup op:

`H:\Backup_Rogue_Pre_M2\DigitalResupplyingAutomation\digital-resupplying-tool`

De backup bevat geen generiek "nieuwere codebasis" dan `C:\Codex\DRT`, maar wel een paar stukken product- en workflowcontext die in de huidige repository niet meer direct zichtbaar zijn.

## Wat inhoudelijk relevant bleek

### 1. Verlies van PDF testfixtures in `dummyinfo/`

De huidige repo miste meerdere PDF-bestanden die wel door tests en analyses worden verondersteld, waaronder:

- `422557.pdf`
- `424123.pdf`
- `424128.pdf`
- `424205.pdf`
- `424784.pdf`
- `54448.pdf`
- `Interfiliaalverdeling vooraf - 423264.pdf`

Dit is relevant omdat bijvoorbeeld `backend/test_verkocht_fix.py` expliciet `dummyinfo/424205.pdf` gebruikt.

### 2. Oude uploads-flow bevatte productintentie die nu deels uit de code verdwenen is

In de backup stonden frontend-componenten die nu ontbreken:

- `frontend/components/uploads/manual-file-uploader.tsx`
- `frontend/components/uploads/generate-proposals.tsx`
- `frontend/components/uploads/recent-series.tsx`
- `frontend/components/uploads/recent-uploads.tsx`

Daaruit komt de volgende nog steeds bruikbare productcontext naar voren.

## Herstelde productcontext voor uploads

### Handmatige upload was oorspronkelijk rijker bedoeld

De backup laat zien dat de handmatige uploadflow niet alleen "upload PDF's" was, maar expliciet deze use cases had:

- drag-and-drop upload
- meerdere PDF's tegelijk
- voortgangsindicator tijdens upload
- keuze tussen:
  - nieuwe reeks aanmaken
  - toevoegen aan bestaande reeks
- laden van bestaande succesvolle batches als selectielijst
- duidelijkere foutfeedback per bestand

Dit is belangrijk, omdat de huidige pagina in [`frontend/app/uploads/page.tsx`](C:/Codex/DRT/frontend/app/uploads/page.tsx) wel een werkende basisflow heeft, maar de optie "toevoegen aan bestaande reeks" en het rijkere statusmodel niet meer bevat.

### Automatisch genereren was functioneel verder uitgewerkt als productflow

De backupcomponent `generate-proposals.tsx` bevatte nog geen echte backend-integratie, maar legde wel expliciet vast welke stappen en instellingen verwacht werden:

- automatische reeksnaam op basis van weeknummer en jaar
- selectie van collectie
- optionele beperking op artikelnummers
- generatie-opties zoals:
  - alleen positieve voorraad
  - minimaal aantal winkels per artikel
  - outlet negeren
  - verkoopcijfers gebruiken
- een meervoudige stage/progress-weergave voor het generatieproces

De huidige frontend noemt automatische generatie vooral als "nog niet aangesloten". De backup bevestigt dus dat hier een echte productflow achter zat, niet alleen een placeholder-tab.

### "Recent Series" was de bedoelde samenvattende batchweergave

De backupcomponent `recent-series.tsx` gebruikte echte batch- en proposaldata om:

- de laatste reeksen te tonen
- status af te leiden uit batchstatus plus proposalstatus
- voortgang binnen een reeks zichtbaar te maken
- fouten op batchniveau te tonen

Dat is relevanter dan de oude `recent-uploads.tsx`, die puur sample data bevatte. De backup bevestigt daarmee dat "reeksen" het juiste domeinconcept is voor de uploads-overzichtslaag.

## Interpretatie voor de huidige codebasis

De backup levert vooral drie concrete inzichten op:

1. `dummyinfo/` is niet alleen testdata, maar een noodzakelijke fixturemap voor reproductie van proposal- en `Verkocht`-issues.
2. De uploads-module hoort productmatig batch/reeks-georiënteerd te zijn, niet alleen file-upload-georiënteerd.
3. De automatische generatieflow heeft al vastgelegde functionele eisen, ook al is de huidige implementatie nog niet aangesloten.

## Wat is geïntegreerd

### Reeds uitgevoerd

- ontbrekende PDF-bestanden uit de backup zijn teruggezet in `dummyinfo/`

### In documentatie / planning verwerkt

- de herstelde upload-context is meegenomen in de geconsolideerde prioriteitenlijst
- deze backup-analyse is vastgelegd zodat de context niet opnieuw verloren gaat

## Aanbevolen vervolg

- Gebruik `recent-series.tsx` uit de backup als referentie bij het opnieuw opbouwen van het uploads-/batch-overzicht.
- Gebruik de recovered flow uit `manual-file-uploader.tsx` als input voor een latere iteratie van de uploads-UX.
- Behandel automatische generatie voortaan als uitgewerkte productfeature met bekende requirements, niet als vrijblijvende placeholder.

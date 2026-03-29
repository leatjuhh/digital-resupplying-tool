# Master Backlog

Dit is de enige actieve backlog van het project.

## P0 Nu stabiliseren

### Titel
Schone frontend production-build herstellen

**Waarom dit nu telt**  
De leidende kernflow is niet betrouwbaar releasebaar zolang `next build` faalt op `/login`.

**Concrete ingreep**  
Plaats `useSearchParams()` in een geldige Suspense/CSR-constructie op de loginpagina en bevestig dat de build daarna schoon doorloopt.

**Afhankelijkheden**  
Geen.

**Acceptatiecriteria**  
`npm run build` in `frontend/` slaagt zonder prerender-error op `/login`.

**Status**  
done

### Titel
Kernflow regressiecheck vastleggen

**Waarom dit nu telt**  
Na consolidatie moet de leidende flow expliciet gevalideerd blijven in plaats van impliciet vertrouwd te worden.

**Concrete ingreep**  
Voer een gecontroleerde check uit op PDF ingest, batch proposals, proposal detail, reject, edit en approve en leg de resultaten vast.

**Afhankelijkheden**  
Schone frontend production-build herstellen.

**Acceptatiecriteria**  
Er is één herhaalbare checklist of testset waarmee de leidende kernflow end-to-end bevestigd kan worden.

**Status**  
done

## P1 Daarna afmaken

### Titel
Assignments-flow van sample UI naar echte uitvoeringsflow brengen

**Waarom dit nu telt**  
De app stopt functioneel nu bij proposal review; uitvoering voor winkels bestaat nog niet als echte backend- en frontendflow.

**Concrete ingreep**  
Bouw assignment-model, backendroutes en echte store-facing UI op basis van goedgekeurde proposals.

**Afhankelijkheden**  
Kernflow regressiecheck vastleggen.

**Acceptatiecriteria**  
Goedgekeurde proposals kunnen worden omgezet naar echte assignments met detail- en statusupdates.

**Status**  
done

### Titel
Settings- en RBAC-frontend op echte backend aansluiten

**Waarom dit nu telt**  
De backend bevat al settings-, users- en roles-routes, maar de frontend gebruikt nog placeholders en mockcalls.

**Concrete ingreep**  
Vervang mock- en samplegedrag in settings door echte backendkoppelingen en respecteer echte gebruikersrechten.

**Afhankelijkheden**  
Kernflow regressiecheck vastleggen.

**Acceptatiecriteria**  
Settings-tabs tonen echte data en voeren echte backendmutaties uit binnen de geldende permissies.

**Status**  
done

## P2 Geparkeerd

### Titel
Dashboard en overzichten data-gedreven maken

**Waarom dit nu telt**  
De huidige UI toont nog te veel breedte zonder dat alle onderliggende data echt is aangesloten.

**Concrete ingreep**  
Vervang placeholder-overzichten door echte backenddata en verwijder samplepatronen.

**Afhankelijkheden**  
Assignments-flow en settings/RBAC-frontend op echte backend aansluiten.

**Acceptatiecriteria**  
Dashboard, batch- en aanvullende overzichtspagina's draaien op echte data zonder misleidende placeholderclaims.

**Fase-update 2026-03-23**  
De dashboard-slice is afgerond: een auth-beschermde `dashboard/summary` endpoint levert nu echte KPI's, pending batches, systeemevents en aandachtspunten; de dashboardcards en overzichten lezen die data direct in, de period selector is eerlijk gemaakt en de proposals-overview gebruikt nu echte sortering zonder samplefilters.

**Status**  
done

### Titel
Baseline-algoritme verder uitbouwen

**Waarom dit nu telt**  
De huidige algoritmelaag werkt technisch, maar volgt nog niet volledig de gewenste manuele werkwijze.

**Concrete ingreep**  
Werk situatieclassificatie, strategieën, categoriebeleid, prioritering, compensatie en feedbackloop gefaseerd uit.

**Fase-update 2026-03-23**  
Fase 1 is afgerond: situatieclassificatie in shadow mode (`LOW_STOCK`, `MEDIUM_STOCK`, `HIGH_STOCK`, `PARTIJ`) draait nu mee in proposalgeneratie via `applied_rules`, inclusief een lokale offline evaluatiehaak tegen de 2 momenteel geïmporteerde weken / 2 manuele herverdelingen. Verdere strategie-, categorie-, prioriterings-, compensatie- en feedbackfasen blijven onder dit umbrella-item open.

**Fase-update 2026-03-29**
De read-only importslice naar het externe project `Herverdelingsalgoritme` is nu geland. DRT kan datasetstatus, weekevaluaties en proposalvergelijking per artikel inlezen en tonen, zodat handmatige beslissingen, baseline-output en modelhints zichtbaar zijn in de reviewflow zonder de bestaande proposalgenerator te veranderen. De volgende uitvoerbare stap onder dit umbrella-item is daarmee een eerste echte strategie- of ranking-assistfase kiezen en toetsen op deze vergelijkdata.

**Afhankelijkheden**  
Stabiele leidende kernflow.

**Acceptatiecriteria**  
De volgende baselinefase is gekozen, gespecificeerd en aantoonbaar getest tegen bestaande data.

**Status**  
todo

## P3 Historisch / later heroverwegen

### Titel
SQL-first of alternatieve databron evalueren

**Waarom dit nu telt**  
Dit is strategisch relevant, maar geen blokkade voor het stabiliseren van de huidige PDF-kern.

**Concrete ingreep**  
Herbeoordeel of de bronarchitectuur moet verschuiven en documenteer alleen daarna een migratiepad.

**Afhankelijkheden**  
Stabiele leidende kernflow en opgeschoonde backlog.

**Acceptatiecriteria**  
Er is een expliciete beslissing om PDF-first te behouden of om gecontroleerd richting SQL-first te bewegen.

**Status**  
todo

### Titel
Historische context alleen op aanvraag heropenen

**Waarom dit nu telt**  
De repo bevat veel bruikbare maar niet-leidende context die toekomstige sessies anders opnieuw diffuus maakt.

**Concrete ingreep**  
Gebruik alleen materiaal uit `archive/2026-03-consolidation/` als een actuele taak daar aantoonbaar op leunt.

**Afhankelijkheden**  
Geen.

**Acceptatiecriteria**  
Nieuwe sessies starten vanuit `README.md`, `docs/technical/current-state.md` en dit bestand, niet vanuit losse historische notities.

**Status**  
todo

## Reeds Uitgevoerd In De Consolidatie

### Titel
Actieve waarheid teruggebracht naar drie leidende documenten

**Waarom dit nu telt**  
Zonder vaste bron van waarheid blijft iedere nieuwe sessie opnieuw interpreteren wat actueel is.

**Concrete ingreep**  
`README.md`, `docs/technical/current-state.md` en `todo/master-backlog.md` zijn leidend gemaakt.

**Afhankelijkheden**  
Geen.

**Acceptatiecriteria**  
De primaire leesvolgorde is eenduidig en terug te vinden in repo-documentatie en `AGENTS.md`.

**Status**  
done

### Titel
Ingehaalde roadmap- en todo-bestanden gearchiveerd

**Waarom dit nu telt**  
Dubbele of achterhaalde planning mag niet meer actief meewegen in nieuwe sessies.

**Concrete ingreep**  
Historische docs en todo's zijn verplaatst naar `archive/2026-03-consolidation/`.

**Afhankelijkheden**  
Geen.

**Acceptatiecriteria**  
`todo/` bevat nog maar één actief backlogdocument en actieve indexen verwijzen niet meer naar oude roadmapbestanden.

**Status**  
done

### Titel
Niet-kernschermen expliciet als niet-leidend markeren

**Waarom dit nu telt**  
Bereikbare maar onvolwassen schermen mogen niet meer aanvoelen als stabiele productkern.

**Concrete ingreep**  
Assignments- en settingsroutes tonen een gedeelde consolidatiewaarschuwing en worden visueel onderscheiden in de navigatie.

**Afhankelijkheden**  
Geen.

**Acceptatiecriteria**  
Gebruikers zien dat deze routes bereikbaar zijn, maar niet tot de leidende kernflow behoren.

**Status**  
done

### Titel
Lokale dev launcher kan hangende servers schoon herstarten

**Waarom dit nu telt**  
Tijdens lokale validatie en browser smoke mag een vastgelopen vorige sessie niet telkens handmatig moeten worden opgeruimd.

**Concrete ingreep**  
`.\dev.ps1` ondersteunt nu `-Restart`, stopt bezette `3000`/`8000`-processen en start daarna backend en frontend opnieuw op.

**Afhankelijkheden**  
Leidende startflow via `.\dev.ps1`.

**Acceptatiecriteria**  
De standaard startflow blijft gelijk, maar bezette poorten kunnen vanuit dezelfde launcher gecontroleerd worden vrijgemaakt en opnieuw gestart.

**Status**  
done

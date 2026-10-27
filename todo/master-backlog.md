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

### Titel
Kritieke security-hardening op de API (production-readiness Fase 1)

**Waarom dit nu telt**  
Muterende endpoints waren anoniem aanroepbaar en `SECRET_KEY` had een publiek bekende fallback — directe risico's op ongeautoriseerde mutaties en tokenvervalsing.

**Concrete ingreep**  
Auth/permissies op alle muterende endpoints, `SECRET_KEY` verplicht (fail-fast), upload-filename-sanitisering + groottelimiet, idempotente approve, smallere refresh-foutafhandeling en werkende `ALLOWED_ORIGINS`. Zie `docs/engineering/PRODUCTION_READINESS_PLAN.md` Fase 1.

**Afhankelijkheden**  
Geen.

**Acceptatiecriteria**  
`backend/test_security_hardening.py` is groen (o.a. 401 op elk muterend endpoint zonder token, fail-fast zonder `SECRET_KEY`).

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

### Titel
Week-inventarisatie van manuele herverdeeldata (scanner)

**Waarom dit nu telt**  
Er is van veel meer weken manuele herverdeeldata beschikbaar dan de 4 verwerkte weken (12, 13, 14, 16). Voordat die data het algoritme kan verbeteren, moet per week vaststaan of `Ingevoerd.xlsx` en de Interfiliaalverdeling-PDF's compleet en consistent zijn, en uit welke werkwijze-periode de week stamt (zie "Domeinkennis Manuele Herverdeling" in `docs/technical/current-state.md`).

**Concrete ingreep**  
Een read-only, niet-interactief script in `tools/baseline-pipeline/` (bv. `inventory_weeks.py`) dat alle mappen `Z:\Herverdeellijsten\Jaar YYYY\Week N\` scant en per week één regel naar een CSV schrijft. Het script schrijft nooit in de bronmap. Bouwen en draaien op de werkmachine: alleen daar is `Z:` bereikbaar en alleen daar zijn de echte mapvarianten te testen. De bestaande per-week-controles in `run_week_update.py` (`check_excel_pdf_mismatch`) en `week_pipeline.py` (`analysis.json`) zijn het vertrekpunt.

Per week:
- Bronbestanden aanwezig: `Ingevoerd.xlsx` en een PDF-map. Mapnamen variëren (`Interfiliaallijsten`, `print pdf`, mogelijk `pdf_print`); de scanner rapporteert welke variant hij vond in plaats van een week stil over te slaan.
- Kruiscontrole op volgnummer: Excel-artikelen zonder PDF (onbruikbaar, geen voorraadbeeld) en PDF's zonder Excel-regel (zwak "niets nodig"-signaal).
- PDF's parsebaar via `pdf_extract`; winkeltotalen aanwezig.
- Moves passen bij de voorraad: de donor had volgens de PDF minstens het verplaatste aantal van die maat. Zo niet, dan is de PDF waarschijnlijk op een ander moment geprint dan het moment van beslissen.
- Ongeldige filiaalcodes en niet-numerieke aantallen.
- Periode: vóór of na de BV-samenvoeging en de overstap naar kriskrasverdeling (wisselweken als configuratie).
- Cooldown: hoe vaak een artikel binnen een week na een eerdere verplaatsing opnieuw verplaatst werd.
- Kwaliteitsvlaggen voor afwijkende weken (bv. veel moves die niet bij de voorraad passen, uitzonderlijk aantal moves), ter beoordeling door de eigenaar.

Uitkomstlabel per week: compleet / bruikbaar / onbruikbaar.

**Afhankelijkheden**  
Toegang tot `Z:\Herverdeellijsten` (werkmachine). De weken waarin de BV-samenvoeging en de kriskrasverdeling ingingen (bij benadering), nog op te geven door de eigenaar.

**Acceptatiecriteria**  
Eén commando levert een CSV met één regel per beschikbare week en bovenstaande kolommen. De 4 al verwerkte weken komen overeen met hun bestaande `analysis.json` (week 12–14: geen ontbrekende PDF's; week 16: 8 van 91 Excel-artikelen zonder PDF). De bronmap blijft onaangeroerd.

**Status**  
todo

### Titel
Scorebord over alle bruikbare weken met oefen- en controleweken

**Waarom dit nu telt**  
Met 4 weken wordt elke algoritme-aanpassing afgestemd op dezelfde weken waarop gemeten wordt, waardoor verbeteringen groter lijken dan ze zijn. Met veel weken is een eerlijke meting mogelijk.

**Concrete ingreep**  
1. Bruikbare weken van ná de werkwijzewijzigingen verwerken met de bestaande pipeline (`run_week_update.py --non-interactive`).
2. Verwerkte JSON in de repo; ruwe Excel- en PDF-bestanden niet in gewone git (de repo wordt dan te zwaar voor beide machines), maar in een gesynchroniseerde map of via Git LFS. De eigenaar heeft bevestigd dat de data buiten de werkmachine en in git mag staan.
3. Weken splitsen: het oudste deel om op af te stemmen, het nieuwste deel als controleset die niet bij het afstemmen gebruikt wordt.
4. Eén commando dat `backend/backtest_drt.py` en `tools/evaluate_proposals.py` over alle weken draait en per foutcategorie (A–F) rapporteert, apart voor oefen- en controleweken. Weken die de eigenaar als minder betrouwbaar markeert tellen niet mee.
5. Daarna gericht de grootste foutcategorieën aanpakken (gemeten op week 16: juiste artikel maar andere maat 36,5%, juiste maat maar andere filialen 30,2%).

**Afhankelijkheden**  
Week-inventarisatie van manuele herverdeeldata.

**Acceptatiecriteria**  
Het scorebord is met één commando reproduceerbaar. Een algoritmewijziging wordt alleen aangenomen als de score op de controleweken verbetert.

**Status**  
todo

### Titel
Cooldown-regel: geen herverdeling van recent verplaatste artikelen

**Waarom dit nu telt**  
In de manuele werkwijze wordt een artikel na verplaatsing minimaal 1 week niet opnieuw herverdeeld, en wordt heen-en-weer schuiven tussen filialen vermeden. DRT kijkt niet naar eerdere batches en kan dus een artikel voorstellen dat vorige week al verplaatst is.

**Concrete ingreep**  
Bij proposalgeneratie artikelen uitsluiten (of markeren) die binnen het cooldownvenster in een goedgekeurd voorstel van een eerdere batch zaten, en geen move voorstellen die een recente verplaatsing terugdraait. Venster configureerbaar, standaard 1 week; definitief af te stemmen op de cooldown-meting van de scanner.

**Afhankelijkheden**  
Geen harde afhankelijkheid: de regel leunt op goedgekeurde voorstellen in de DRT-database, niet op `Z:`, en kan op elke machine gebouwd worden. Niet tegelijk met ander werk op de andere machine uitvoeren.

**Acceptatiecriteria**  
Een test met twee opeenvolgende batches toont dat een in batch 1 goedgekeurd artikel binnen het venster in batch 2 geen moves krijgt, en buiten het venster wel.

**Status**  
todo

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
Werk situatieclassificatie, strategieën, categoriebeleid, prioritering, compensatie en de feedbackloop gefaseerd uit, met de eerstvolgende nadruk op voorstel- en feedbacklogging, feature-snapshots per beslissing, periodieke AI-analyse en gecontroleerde regelverfijning bovenop het bestaande algoritme.

**Fase-update 2026-03-23**  
Fase 1 is afgerond: situatieclassificatie in shadow mode (`LOW_STOCK`, `MEDIUM_STOCK`, `HIGH_STOCK`, `PARTIJ`) draait nu mee in proposalgeneratie via `applied_rules`, inclusief een lokale offline evaluatiehaak tegen de 2 momenteel geïmporteerde weken / 2 manuele herverdelingen. Verdere strategie-, categorie-, prioriterings-, compensatie- en feedbackfasen blijven onder dit umbrella-item open.

**Fase-update 2026-03-29**
De read-only importslice naar het externe project `Herverdelingsalgoritme` is nu geland. DRT kan datasetstatus, weekevaluaties en proposalvergelijking per artikel inlezen en tonen, zodat handmatige beslissingen, baseline-output en modelhints zichtbaar zijn in de reviewflow zonder de bestaande proposalgenerator te veranderen.

**Fase-update 2026-03-30**
Het algoritme is vereenvoudigd van ~2.800 naar ~1.400 LOC. Multi-factor scoring (series/efficiency), de move-consolidatie-optimizer en size sequence detectie zijn verwijderd. Scoring is nu puur demand-gebaseerd. Dit vereenvoudigde algoritme is het vertrekpunt voor toekomstige iteraties. Eerstvolgende stap: valideren tegen 3-5 eerdere handmatige herverdelingen en demand-drempels bijstellen op basis van resultaten.

**Fase-update 2026-04-17**
De AI-richting is aangescherpt als feedbackgedreven verfijning van het bestaande deterministische algoritme. De eerstvolgende feedback-slice richt zich op voorstel- en feedbacklogging, feature-snapshots per beslissing, periodieke AI-analyse via OpenAI en gecontroleerde omzetting van verbetervoorstellen naar versioneerde regels. Realtime AI-sturing of modelgestuurde herordening van proposals is hierbij expliciet niet de eerstvolgende stap.

**Fase-update 2026-04-17 (sessie 2)**
Het herverdelingsalgoritme is fundamenteel herschreven van gemiddelde-drempel logica naar demand-gedreven donor/ontvanger scoring (baseline-stijl uit `Herverdelingsalgoritme`). Gevalideerd op weken 12, 13, 14 en 16: van 0 moves naar ~1100 moves over 241 artikelen (27% precisie, 16% recall op exact match basis). BV-configuratie bijgewerkt: alle 8 MC-winkels onder Lumitex B.V., filiaal 5 (Panningen) apart. Eerstvolgende stap: store-niveau metrics toevoegen (totale voorraadpositie winkel, verkoopvloer m²/capaciteit) als tiebreaker bij gelijke demand score.

**Fase-update 2026-04-18**
Store-niveau capaciteitsprofielen geland (`store_profiles.py`): vloeroppervlak en max-capaciteit per filiaal als tiebreaker bij gelijke demand-score. Maatreekslogica toegevoegd aan het algoritme: moves die een aaneengesloten maatreeks bij de donor breken worden geblokkeerd. Feedback-router en uitgebreid `ProposalFeedback` DB-model zijn de basis voor de ML-feedbackloop (batchmatige AI-analyse van approve/edit/reject-acties). Architectuurdocument `fase1-ml-feedback-loop.md` vastgelegd.

**Fase-update 2026-04-18 (sessie 2)**
De externe sibling-map `Herverdelingsalgoritme/` is niet langer vereist voor een werkende DRT-setup. De algoritmedata (4 weken JSON + aggregate, ~37MB) staat nu intern in `backend/algorithm_data/` en de historische baseline-pipeline is als bevroren tooling opgenomen in `tools/baseline-pipeline/` inclusief `legacy_redistribution/` (niet verwarren met het actieve `backend/redistribution/`). `algorithm_import/config.py` wijst standaard naar de interne locatie; `EXTERNAL_ALGORITHM_DATA_ROOT` blijft beschikbaar voor overrides. Dit maakt hybride werken op meerdere machines wrijvingsloos: `git pull` + setup-scripts volstaat.

**Fase-update 2026-10-27**
Nieuwe meting op weken 12, 13, 14 en 16 met de huidige `backend/redistribution/`-code via `backend/backtest_drt.py` en `tools/evaluate_proposals.py`: exacte recall 8,1% en semantische recall 17,1% over 2.008 manuele moves; DRT stelt 872 moves voor. De eerder genoemde 27% precisie / 16% recall is daarmee niet meer actueel. Het vervolg loopt via de P1-items week-inventarisatie, scorebord en cooldown-regel; de domeinkennis die daarvoor is vastgelegd staat in `docs/technical/current-state.md`.

**Afhankelijkheden**  
Stabiele leidende kernflow.

**Acceptatiecriteria**  
De volgende baselinefase is gekozen, gespecificeerd en aantoonbaar getest tegen bestaande data, inclusief een expliciete opzet voor decision logging, feedback capture, batchmatige AI-analyse en versioneerde regelverfijning zonder realtime AI-besluitvorming.

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

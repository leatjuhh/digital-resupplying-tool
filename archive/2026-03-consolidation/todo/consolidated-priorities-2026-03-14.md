# Geconsolideerde Prioriteitenlijst

**Datum:** 2026-03-14  
**Doel:** bestaande taken uit `todo/` prioriteren, toetsen aan de huidige codebasis en aanvullen met ontbrekend werk op basis van de actuele app-status.

## Uitgangspunt

Deze prioritering is gebaseerd op:

- de bestaande bestanden in `todo/`
- de actuele productscope in `README.md` en `frontend/PROJECT-OVERVIEW.md`
- de huidige implementatie in frontend en backend

Bij tegenstrijdigheden is de actuele code leidend geweest. Daardoor zijn enkele oudere todo-bestanden deels achterhaald.

## Samenvatting

De grootste gaten zitten niet meer in losse UI-schermen, maar in **betrouwbare end-to-end werking**:

1. datakwaliteit van `Verkocht` en voorsteluitleg
2. echte integratie van proposal detail/edit flows
3. ontbreken van een echte assignments-uitvoeringsflow
4. settings- en RBAC-koppeling die in backend al bestaat maar in frontend nog deels gesimuleerd is
5. verdere doorontwikkeling van het algoritme naar de gewenste baseline/manuele werkwijze

## Geconsolideerde Prioriteiten

## P0 - Eerst uitvoeren

### 1. Verifieer en corrigeer de datastroom van `Verkocht` [VOLTOOID]
**Waarom eerst:** dit raakt direct de betrouwbaarheid van de kernfunctionaliteit: voorstellen mogen niet op foutieve verkoopdata gebaseerd zijn.

**Bron in bestaande todo's:**
- `bug_verkocht_kolom_summing_instead_of_source.md`
- `verify_proposals_use_extracted_sales.md`
- `review_proposal_optimaal_verdeeld_422557.md`
- `next_session_checklist.md`

**Code-analyse:**
- In `backend/routers/pdf_ingest.py` wordt `verkocht` slechts op het eerste maatrecord per filiaal opgeslagen en daarna op `0` gezet.
- In `GET /api/pdf/proposals/{id}/full` wordt `record.verkocht` per maat in `sales[size]` gezet en daarna per winkel opgeteld.
- Daardoor is de kans groot dat de UI technisch het totaal behoudt, maar via een kwetsbare opslag-/mappingconstructie werkt die eerst bewezen moet worden.
- De badge "Optimaal Verdeeld" in `frontend/components/proposals/proposal-detail.tsx` hangt nu alleen af van "geen verschillen tussen current en proposed", niet van een expliciete businessregel of audit trail.

**Concreet werk:**
- Traceer `Verkocht` van PDF-extractie tot UI-weergave.
- Bevestig met minimaal 1 concreet artikel dat bron-PDF, database, API en UI identiek zijn.
- Leg vast waarom voorstel `422557` als "Optimaal Verdeeld" wordt gemarkeerd, of corrigeer die logica.
- Verwijder de huidige ambiguïteit in opslag/mapping als die onjuist of fragiel blijkt.

**Afgerond op 2026-03-14:**
- `Verkocht` wordt nu expliciet als filiaal-totaal behandeld in backend API en algoritmelogica, niet meer als pseudo-maatdata.
- `GET /api/pdf/proposals/{id}/full` geeft nu correcte winkelverkoop terug zonder fragiele maatmapping.
- de "Optimaal Verdeeld"-status komt nu expliciet uit de backend in plaats van alleen uit een frontend-heuristiek.
- concreet geverifieerd met `422557.pdf`: parser, database en API gaven allemaal totaal `Verkocht = 61`.

### 2. Maak de proposal-flow volledig echt in plaats van deels gesimuleerd [VOLTOOID]
**Waarom eerst:** proposal review en bewerken is de hoofdworkflow van de app.

**Bron in bestaande todo's:**
- impliciet uit proposal-gerelateerde todo's
- deels uit oude analysebestanden waar API-integratie nog ontbrak

**Code-analyse:**
- `frontend/app/proposals/[id]/page.tsx` gebruikt hardcoded batch-progress info.
- `frontend/app/proposals/[id]/edit/page.tsx` gebruikt ook gesimuleerde batchdata.
- De editpagina bevat nog een expliciete TODO voor opslaan.
- `frontend/components/proposals/proposals-table.tsx` bevat nog sample data.

**Concreet werk:**
- Haal batchprogress en navigatie uit echte API-data.
- Koppel "Opslaan & Goedkeuren" aan de bestaande proposal update/approve endpoints.
- Zorg dat proposal lists, detail en edit één consistente datastroom gebruiken.
- Voeg regressietests toe voor approve/reject/edit.

**Afgerond op 2026-03-14:**
- proposal detail- en editroutes gebruiken nu echte batchcontext uit de API voor naam, voortgang en volgende navigatie.
- `Opslaan & Goedkeuren` voert nu echt `update` + `approve` uit.
- `Afwijzen` en `Afwijzen & Bewerken` gebruiken nu correct aangesloten backendcalls.
- de editflow is gestabiliseerd: change-detectie werkt, save-enable werkt, en de React update-loop bij `Afwijzen & Bewerken` is opgelost.
- functioneel getest in de UI: goedkeuren, afkeuren, afwijzen+bewerken, batchterugkeer en voortgangsupdates werken op echte data.

### 2a. Herstel een schone frontend production-build
**Waarom direct na punt 2:** de proposal-flow is nu functioneel te testen, maar een schone `next build` faalt nog. Dat blokkeert betrouwbare release-validatie en maskeert nieuwe regressies achter bestaande buildruis.

**Ontdekt tijdens uitvoering van punt 2:**
- na het opschonen van `.next` compileert de frontend grotendeels succesvol
- de actuele buildfout zit in `/login`
- `useSearchParams()` op `frontend/app/login/page.tsx` moet in een Suspense boundary worden geplaatst of anders uit de prerender-flow worden gehaald

**Concreet werk:**
- repareer de `/login` pagina zodat `next build` zonder prerender-error slaagt
- voer daarna opnieuw een schone frontend-build uit
- houd build-validatie gescheiden van devserver-ruis (`.next` lock / gegenereerde types)

## P1 - Hoog

### 3. Bouw de assignments-flow echt af
**Waarom hoog:** de productscope eindigt niet bij goedkeuren van een voorstel; winkels moeten opdrachten kunnen uitvoeren.

**Bron in bestaande documentatie:**
- `frontend/PROJECT-OVERVIEW.md`

**Code-analyse:**
- `frontend/components/assignments/assignments-list.tsx` gebruikt sample data.
- `assignment-details.tsx` en `assignment-item-detail.tsx` werken nog met sample data.
- Er is geen assignments-router of assignment-model in het backend.

**Concreet werk:**
- Definieer assignment-datamodel en statusflow.
- Zet goedgekeurde proposals om naar assignments.
- Bouw backend endpoints voor assignment-overzichten, detail en statusupdates.
- Koppel de store-user frontend aan echte data.

### 4. Rond settings en role-based access in de frontend af
**Waarom hoog:** backend-functionaliteit bestaat grotendeels al, maar de frontend vertrouwt nog op placeholders en gesimuleerde API-calls.

**Bron in bestaande todo's:**
- `settings-page-implementation.md`
- auth-gerelateerde todo's

**Code-analyse:**
- `frontend/app/settings/page.tsx` gebruikt `const userRole = "admin"`.
- `frontend/components/settings/settings-general.tsx`, `settings-rules.tsx`, `settings-api.tsx` en `settings-users.tsx` simuleren calls.
- Backend heeft echte routers voor `settings`, `users` en `roles`.
- Backend-validatie van OpenAI API keys in `backend/routers/settings.py` is nog mock-logica.

**Concreet werk:**
- Gebruik `AuthContext`/permissions in de settings-route.
- Koppel settings tabs aan de echte backend endpoints.
- Koppel users/roles-beheer aan de bestaande CRUD-routes.
- Vervang mock API-key validatie door echte validatie of beperk de feature expliciet.

### 5. Maak dashboard- en overzichtspagina's data-gedreven
**Waarom hoog:** de app oogt breed, maar een deel van de navigatie toont nog statische of semistatische content.

**Code-analyse:**
- dashboardcomponenten bevatten placeholder/sample patronen
- proposal tabellen en assignment-overzichten zijn nog niet overal op echte data aangesloten
- de backup bevestigt dat de uploads-overzichtslaag oorspronkelijk reeks-/batch-georiënteerd was, inclusief voortgang en foutstatus per reeks

**Concreet werk:**
- Koppel dashboardstatistieken, recente activiteit en notificaties aan backend-data.
- Zorg dat filters en overzichten op proposals en batches echt werken.
- Verwijder sample-data componenten zodra equivalenten op echte data draaien.

### 5a. Herstel de review-workflow uit de Stephany-brainstorm
**Waarom hoog:** het bronbestand `Brainstormsessie met stephany.docx` maakt duidelijk dat de gewenste operationele flow anders is dan de huidige proposal-review.

**Bevestigd vanuit het bronbestand:**
- bij afwijzen niet eerst verplicht feedback typen; eerst corrigeren, daarna feedback op het originele voorstel
- na approve of correctie+approve niet direct afronden, maar eerst een routing-check uitvoeren
- routing moet zichtbaar maken: welk filiaal stuurt welke maat naar welk ander filiaal
- pas na goedkeuren van routing door naar het volgende artikel

**Concreet werk:**
- pas reject-flow aan naar: corrigeren -> feedback -> opslaan
- voeg een `Routing`-weergave toe aan de proposal-flow
- maak approve-flow sequentieel: proposal review -> routing check -> volgend artikel
- leg minimale transacties en herkomst/bestemming per move zichtbaar vast in de UI

## P2 - Middel

### 6. Breng het herverdelingsalgoritme naar de gewenste baseline
**Waarom middel en niet eerst:** de app heeft nu vooral nog integratie- en betrouwbaarheidsgaten; baseline-uitbreiding heeft pas waarde als de huidige flow vertrouwd is.

**Bron in bestaande todo's:**
- `baseline-phase-1-situation-classifier.md`
- `baseline-phase-2-strategies.md`
- `baseline-phase-3-categories.md`
- `baseline-phase-4-priority.md`
- `baseline-phase-5-compensation.md`
- `baseline-phase-6-feedback.md`

**Concreet werk in volgorde:**
- Fase 1: situatieclassificatie
- Fase 2: strategieën per voorraadsituatie
- Fase 3: artikelcategoriebeleid
- Fase 4: intelligente prioritering
- Fase 5: maatcompensatie
- Fase 6: feedback loop

**Opmerking:** deze fase blijft inhoudelijk belangrijk, maar pas na P0/P1 is het verstandig om de huidige algorithm-output verder te verfijnen.

### 7. Verbeter voorsteluitleg en auditability
**Waarom middel:** de app moet niet alleen een voorstel tonen, maar ook uitlegbaar maken waarom het voorstel logisch is.

**Code-analyse:**
- redenen en regels worden opgeslagen, maar de UI laat nog beperkt zien waarom een voorstel goed, afgekeurd of "optimaal verdeeld" is
- er is geen duidelijke auditlaag of reviewgeschiedenis buiten statusvelden

**Concreet werk:**
- Toon herkomst van kernbeslissingen in proposal detail.
- Leg applied rules, score-factoren en afkeur-/editgeschiedenis zichtbaar vast.
- Voeg logging of audit-events toe waar nodig.

### 8. Test- en kwaliteitslaag verbreden
**Waarom middel:** er bestaan losse Python-testscripts, maar de kritieke gebruikersflows missen nog een duidelijke geautomatiseerde regressielaag.

**Concreet werk:**
- API-tests voor proposals, settings, users en assignments.
- Frontend flowtests voor login, upload, review, edit en settings.
- Regressietests rond `Verkocht` en voorstelstatussen.

## P3 - Lager, maar wel relevant

### 9. SQL-bron als volgende grote datastap voorbereiden
**Bron in bestaande todo's:**
- `sql_connection_and_sizedisplay_logic-old-CHATGPT_logic.md`

**Waarom lager:** dit is een strategische uitbreiding, geen blokkade voor het stabiliseren van de huidige PDF-flow.

**Concreet werk:**
- Beslis of SQL de primaire bron wordt.
- Werk maatbalkmapping en transformatielaag uit.
- Plan migratiepad van PDF-first naar SQL-first zonder huidige flow te breken.

### 10. UX-verbeteringen uitwerken na functionele stabilisatie
**Bron in bestaande todo's:**
- `ux-improvements-stephany-brainstorm.md`
- herstelde context uit `docs/technical/backup-recovered-context.md`

**Concreet werk:**
- compactere proposal layouts
- collapsable metadata header
- 1080p optimalisatie
- overige workflowverbeteringen uit de brainstorm

### 10a. Uploads-flow herstellen naar bedoelde productscope
**Waarom lager dan P1 maar expliciet benoemd:** de backup laat zien dat de huidige uploads-pagina een versimpelde variant is van een rijker bedoelde workflow.

**Herstelde context uit backup:**
- keuze tussen nieuwe reeks aanmaken en toevoegen aan bestaande reeks
- rijkere foutfeedback per bestand
- recente reeksen met voortgang en foutstatus
- automatische generatie met bekende opties en stages

**Concreet werk:**
- bepaal welke delen uit de backup-productflow terug moeten komen
- voeg batch/reeks-semantiek weer expliciet toe aan de uploads-UX
- gebruik recovered upload-context als input voor een latere functionele iteratie

### 11. Security hardening voor externe hosting
**Bron in bestaande todo's:**
- `auth-security-implementation.md`

**Waarom lager:** relevant zodra deployment verder gaat dan intern netwerk / lokale omgeving.

**Concreet werk:**
- HTTPS, rate limiting, security headers, audit logging, secrets management, SQLite -> PostgreSQL

### 12. Documentatie en todo-opschoning
**Waarom lager:** nuttig, maar niet productkritisch.

**Concreet werk:**
- werk verouderde todo-bestanden bij of archiveer ze
- markeer welke auth-taken al voltooid zijn
- verwijder oude referenties naar niet-bestaande componenten of achterhaalde plannen

## Bestanden Uit `todo/` Die Deels Achterhaald Zijn

- `authentication-flow-implementation.md`: grote delen zijn inmiddels gebouwd.
- `auth-next-steps.md`: grotendeels voltooid; alleen wachtwoordwissel blijft expliciet open.
- `settings-page-implementation.md`: route en basisstructuur bestaan al, maar backend-koppeling nog niet.
- `recent-uploads-verification.md`: de genoemde componenten lijken niet meer in de actuele frontend aanwezig; eerst vaststellen of deze taak nog bestaat.
- `NEW_CHAT_PROMPT.md`: historische handoff, geen leidend todo-document meer.

## Aanbevolen Uitvoervolgorde

1. Schone frontend production-build herstellen (`2a`).
2. Assignments backend + frontend realiseren.
3. Settings/users/roles frontend koppelen aan bestaande backend.
4. Dashboard- en overzichtsschermen van echte data voorzien.
5. Daarna pas de baseline-fases van het algoritme doorvoeren.
6. Vervolgens SQL-transitie, UX-polish en deployment hardening plannen.

## Resultaat Van Deze Analyse

De app heeft al een bruikbare kern: auth, PDF ingest, proposal-opslag en een eerste redistributie-engine bestaan. Wat nog ontbreekt is vooral de laag die van "technisch prototype" naar "betrouwbare operationele tool" gaat: correcte verkoopdata, echte workflow-integratie, uitvoerbare opdrachten en consistente rol-/instellingenkoppeling.

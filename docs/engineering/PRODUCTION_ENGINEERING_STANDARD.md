---
title: Production Engineering Standard
category: engineering
tags: [engineering-standaard, power-of-ten, production-readiness, governance, holzmann]
last_updated: 2026-07-13
status: canoniek — actief
related:
  - docs/references/P10.pdf
  - docs/engineering/PRODUCTION_READINESS_AUDIT.md
  - docs/engineering/PRODUCTION_READINESS_PLAN.md
  - docs/engineering/AI_SESSION_HANDOFF.md
  - AGENTS.md
  - CLAUDE.md
  - CHATGPT_PROJECT_INSTRUCTIONS.md
  - docs/PROJECT_CONTEXT_INDEX.md
---

# Production Engineering Standard

> **Dit is het canonieke, gezaghebbende engineeringdocument van deze repository.** Elke technische beslissing over structuur, betrouwbaarheid, foutafhandeling, security en kwaliteitsbewaking wordt tegen dit document getoetst. Er geldt de volgende documenthiërarchie:
>
> 1. **`docs/references/P10.pdf`** — de oorspronkelijke bron ("The Power of Ten – Rules for Developing Safety Critical Code", Gerard J. Holzmann, NASA/JPL). Ongewijzigd, alleen ter referentie.
> 2. **Dit document** — de projectspecifieke, canonieke vertaling en uitwerking van die bron naar de stack en architectuur van dit project. Bij twijfel over interpretatie of bij conflict met elk ander document in deze repository **wint dit document**.
> 3. **`AGENTS.md`, `CLAUDE.md`, `CHATGPT_PROJECT_INSTRUCTIONS.md`** — tool-/adapterdocumenten. Zij verwijzen naar dit document en mogen de hierin vastgelegde regels toelichten of operationaliseren voor een specifieke AI-tool, maar mogen **geen eigen, afwijkende regels definiëren**.
> 4. **Taak-, sessie- en handoffdocumenten** (waaronder `docs/engineering/AI_SESSION_HANDOFF.md`, sessielogs, PR-beschrijvingen) — definiëren **nooit** eigen normen. Zij mogen uitzonderingen op dit document registreren volgens het proces in hoofdstuk 15, niet de regels zelf wijzigen.
>
> Bij twijfel over wat Holzmann oorspronkelijk bedoelde: raadpleeg `docs/references/P10.pdf`. Bij twijfel over hoe dat vertaalt naar deze codebase: dit document is leidend, niet het geheugen van een individuele AI-sessie.

---

## 1. Doel en toepassingsgebied

Dit document bestaat omdat het project — een multi-store retail resupply/herverdelingsplanner (PDF-ingest → voorstel-generatie → review/goedkeuring → winkel-picklijsten) — gecontroleerd naar production-ready gebracht moet worden. "Gecontroleerd" betekent: op basis van een vaste, verifieerbare set regels in plaats van ad-hoc oordelen per sessie of per ontwikkelaar. De standaard is de projectspecifieke vertaling van Holzmanns "Power of Ten" (`docs/references/P10.pdf`) naar de daadwerkelijke stack van dit project.

De standaard bevordert drie eigenschappen:
- **Betrouwbaarheid** — het systeem gedraagt zich voorspelbaar, ook bij onverwachte input, gedeeltelijke fouten en gelijktijdig gebruik.
- **Controleerbaarheid** — regels zijn zo geformuleerd dat naleving (nu of in de toekomst) door een linter, typechecker, test of code review is vast te stellen, niet alleen door interpretatie.
- **Onderhoudbaarheid** — nieuwe bijdragers (mens of AI-sessie) kunnen de codebase begrijpen en veilig wijzigen zonder de volledige geschiedenis te kennen.

**Toepassingsgebied:** deze standaard geldt voor de volledige repository — `backend/`, `frontend/`, `tools/`, `scripts/` — met dien verstande dat de striktheid van handhaving per component verschilt naar risicoklasse (zie hoofdstuk 14). Een experimentele ML-pipeline in `tools/baseline-pipeline/` wordt niet met dezelfde striktheid behandeld als `backend/redistribution/algorithm.py`, maar valt wel onder dezelfde principes zodra deze productiedata raakt.

**Risico's die deze standaard beperkt:**
- **Dataverlies/-corruptie** van voorraad- en voorstel-data (bv. dubbele of verweesde rijen door niet-atomaire batchverwerking, ontbrekende constraints).
- **Stille fouten** — fouten die niet worden opgemerkt omdat ze breed worden opgevangen, gemaskeerd of niet gelogd.
- **Onbegrensde uitvoering** — lussen, retries of resourcegebruik zonder bovengrens die de service kunnen laten hangen of uitputten.
- **Security-incidenten** — ongeautoriseerde toegang tot muterende endpoints, gelekte secrets, path traversal via bestandsnamen.
- **Onherstelbare deployments** — wijzigingen (met name database-migraties) die niet reproduceerbaar of terug te draaien zijn.

---

## 2. Bron en herkomst

De tien regels in hoofdstuk 3 zijn afkomstig uit **"The Power of Ten – Rules for Developing Safety Critical Code"** van Gerard J. Holzmann (NASA/JPL Laboratory for Reliable Software, Pasadena, CA), oorspronkelijk geschreven voor safety-critical C-code (bv. ruimtevaartsoftware). De oorspronkelijke tekst is ongewijzigd opgeslagen in deze repository op:

- **Locatie:** `docs/references/P10.pdf`
- **SHA-256:** `2217f41df961b9ed25cc072700b6332d6193799ed09d83be48bf791d05025f54`
- **Status:** ongewijzigde kopie van de brontekst.

De inhoud van `docs/references/P10.pdf` **MAG NOOIT gewijzigd worden**. Elke wijziging aan de checksum hierboven duidt op een integriteitsprobleem en moet onderzocht worden voordat het bestand nog als bron wordt vertrouwd.

Dit project is geen safety-critical embedded C-systeem; het is een web-backend (Python/FastAPI) met een web-frontend (Next.js/TypeScript). De tien regels zijn daarom niet letterlijk overgenomen, maar per regel **geïnterpreteerd naar hun onderliggende doel** en vertaald naar een equivalente, toetsbare projectregel (hoofdstuk 3). Waar de vertaling in dit document onduidelijk lijkt of een editor twijfelt of een interpretatie recht doet aan de oorspronkelijke bedoeling, is `docs/references/P10.pdf` de bron om op terug te vallen — niet het geheugen van een eerdere sessie of dit document alleen.

---

## 3. De tien oorspronkelijke principes

Voor elke regel geldt dezelfde vaste structuur. "Verplichte projectregel"-items zijn genummerd `R<regelnummer>.<volgnummer>` (bijvoorbeeld `R2.1`) zodat ernaar verwezen kan worden vanuit code, PR's, de audit en het verbeterplan.

### Regel 1 — Eenvoudige, expliciete control flow

**Classificatie:** Aangepast toepasbaar — `goto` en `setjmp`/`longjmp` bestaan niet in Python/TypeScript, dus die letterlijke verboden zijn niet van toepassing. Het verbod op recursie is in moderne, niet-embedded talen niet absoluut, maar het onderliggende doel (een aantoonbaar begrensde, goed te volgen aanroepstructuur) blijft volledig relevant.

**Oorspronkelijke bedoeling:** Holzmann verbiedt `goto`, `setjmp`/`longjmp` en directe of indirecte recursie om een acyclische functie-aanroepgrafiek te garanderen. Dat maakt het voor tools mogelijk statisch te bewijzen dat uitvoeringen die begrensd moeten zijn, dat ook daadwerkelijk zijn. Eén punt van terugkeer per functie wordt niet geëist — een vroege foutretour mag de eenvoudigste oplossing zijn.

**Risico dat hiermee wordt beperkt:** onbegrensde recursiediepte (stack-uitputting), ondoorzichtige sprongen in controlestroom die code-analyse en testdekking bemoeilijken, functies waarvan het gedrag niet meer in één keer te overzien is.

**Vertaling naar dit project:** Python en TypeScript kennen geen `goto`; wel is ongecontroleerde of onbegrensde recursie mogelijk (bv. bij boom-/lijsttraversal, geneste retries, recursieve parsing). Analoog verboden: recursie zonder bewezen dieptelimiet, gebruik van exceptions om normale (niet-foutieve) controlestroom te sturen, en diep geneste conditionele/callback-structuren die de daadwerkelijke uitvoeringsvolgorde verbergen.

**Verplichte projectregel:**
- **R1.1** Recursieve functies MOETEN een expliciete, statisch afleesbare dieptelimiet hebben, of BEHOREN vervangen te worden door een iteratieve variant.
- **R1.2** Nieuwe code MAG GEEN exceptions gebruiken om normale (verwachte) controlestroom te sturen; exceptions zijn uitsluitend voor foutcondities.
- **R1.3** Functies BEHOREN niet meer dan circa 3 à 4 geneste niveaus te hebben; early return is toegestaan en heeft de voorkeur boven diepe nesting.
- **R1.4** Elke recursieve functie MOET een basisgeval hebben waarvan de bereikbaarheid vóór de eerste aanroep aantoonbaar is.

**Automatische controle:** beoogd: complexiteitsregels in `ruff`/ESLint (`max-depth`, cyclomatische complexiteit) die diepe nesting en recursie signaleren. Huidige status: er is geen `ruff`-, `mypy`- of ESLint-configuratie in deze repository (zie hoofdstuk 11 en `docs/engineering/PRODUCTION_READINESS_PLAN.md` fase 2). Interim: code review, aangevuld met een gerichte `grep` naar functies die zichzelf aanroepen.

**Handmatige controle:** bij elke nieuwe of gewijzigde functie: bevat deze recursie, en zo ja, is er een bewezen bovengrens? Is de nestingdiepte beperkt? Wordt een exception gebruikt voor iets anders dan een fout?

**Toegestane uitzonderingen:** recursieve algoritmen waarvoor iteratieve herschrijving de leesbaarheid ernstig zou verslechteren (bv. traversal van een klein, begrensd boomstructuur) zijn toegestaan mits de dieptelimiet expliciet is vastgelegd. Documentatie op de plek zelf: codecommentaar `AFWIJKING: R1.x — <reden + bewezen bovengrens>`; vermelding in de PR-beschrijving of `docs/engineering/AI_SESSION_HANDOFF.md`; vereiste extra controle: een test die de grensdiepte daadwerkelijk uitoefent.

**Huidige toestand:** Voldoet gedeeltelijk. De kritieke domeinlogica in `backend/redistribution/algorithm.py` is overwegend iteratief opgebouwd met expliciete guard-tellers (zie Regel 2); tijdens deze verificatie is geen onbegrensde recursie in dit bestand aangetroffen. Voor de volledige codebase is dit **niet vastgesteld** (geen uitputtende doorlichting van alle modules uitgevoerd) — dit blijft een openstaand punt totdat automatische controle beschikbaar is.

---

### Regel 2 — Elke lus heeft een bewezen bovengrens

**Classificatie:** Aangepast toepasbaar — "statisch bewijsbaar door een tool" in de strikte C-zin is in een dynamische taal als Python niet 1:1 haalbaar, maar het principe (geen runaway iteratie) is volledig van toepassing en gedeeltelijk al correct geïmplementeerd in dit project.

**Oorspronkelijke bedoeling:** elke lus moet een vaste bovengrens hebben; wordt die overschreden, dan faalt een assertion en retourneert de functie een foutconditie. Voor bewust oneindige lussen (bv. een scheduler) geldt het omgekeerde: bewijs dat ze niet termineren.

**Risico dat hiermee wordt beperkt:** runaway loops, resource-uitputting, hangende requests, oneindige `while`-lussen bij onverwachte of vervuilde invoerdata.

**Vertaling naar dit project:** elke lus over externe of niet-triviaal begrensde data (PDF-regels, DB-resultaten, retries, polling) MOET een expliciete bovengrens hebben. Het project bevat al een correct voorbeeld van dit patroon.

**Verplichte projectregel:**
- **R2.1** Elke `while`-lus waarvan de terminatievoorwaarde niet triviaal begrensd is door een vaste, kleine constante MOET een expliciete guard-teller met maximum en een loggingactie bij overschrijding hebben — conform het patroon in `backend/redistribution/algorithm.py:492-500`.
- **R2.2** Retries (HTTP, database, bestand) MOETEN een maximumaantal pogingen, een timeout per poging en een backoff-strategie hebben; een oneindige retry-lus is verboden.
- **R2.3** Databasequery's die een resultaatset over meerdere rijen kunnen opleveren BEHOREN een `LIMIT` of paginering te hebben, tenzij de resultaatgrootte inherent begrensd is door het domein (bv. het aantal winkels).
- **R2.4** Batchverwerking (bv. meerdere PDF's per upload) MOET een maximumaantal items per batch afdwingen, of expliciet documenteren waarom dat niet nodig is.

**Automatische controle:** beoogd: een AST-gebaseerde CI-check of custom lintregel die `while`-lussen zonder guard-patroon signaleert. Huidige status: niet geconfigureerd. Interim: `grep -rn "while True\|while 1:" backend/` als eerste screening, gecombineerd met code review.

**Handmatige controle:** bij elke lus over externe of variabele data: is er een bovengrens? Wat gebeurt er bij overschrijding — een stille hang, of een expliciete fout met logging? Zijn retries begrensd in aantal en tijd?

**Toegestane uitzonderingen:** lussen die aantoonbaar begrensd zijn door een klein, vast domein (bv. itereren over de acht winkelprofielen in `backend/redistribution/store_profiles.py`) hoeven geen aparte guard-teller te hebben — de collectiegrootte zelf is dan de bovengrens, mits dat in commentaar benoemd wordt.

**Huidige toestand:** Voldoet gedeeltelijk. Geverifieerd positief bewijs: `backend/redistribution/algorithm.py:492-500` implementeert het guard-counter-patroon correct — een teller (`guard`) die bij overschrijding van 200 iteraties een waarschuwing logt en de lus met `break` afbreekt. Of ditzelfde patroon consistent is toegepast op alle overige onbegrensde lussen in de codebase, en of externe HTTP-aanroepen (bv. in `backend/algorithm_import/`) een timeout/backoff-strategie hebben, is tijdens deze verificatie **niet vastgesteld** — geen volledige doorlichting uitgevoerd. Dit is een aandachtspunt voor de audit, niet een bevestigde afwezigheid.

---

### Regel 3 — Begrensd resourcegebruik

**Classificatie:** Niet letterlijk toepasbaar, maar het onderliggende principe is relevant — Python en TypeScript zijn garbage-collected talen; handmatig geheugenbeheer zoals in C is hier niet aan de orde. Het achterliggende doel (voorspelbaar, begrensd resourcegebruik) blijft onverkort relevant.

**Oorspronkelijke bedoeling:** geen dynamische geheugenallocatie na initialisatie, om onvoorspelbaar allocator-/garbage-collector-gedrag en klassieke geheugenfouten (lekken, use-after-free, out-of-bounds) te vermijden; alles moet binnen een vooraf vastgestelde geheugenruimte passen.

**Risico dat hiermee wordt beperkt:** ongebreidelde geheugengroei (bv. een volledig bestand of response in het geheugen laden), onbegrensd schijfgebruik door uploads, netwerkverbindingen zonder timeout, resource-uitputting die de service onderuit haalt.

**Vertaling naar dit project:** begrens uploadgrootte, gebruik streaming in plaats van alles-in-geheugen waar mogelijk, begrens de omvang van querysets, zet timeouts op alle I/O (HTTP-clients, database-connecties), vermijd caches of lijsten die ongelimiteerd meegroeien met gebruikersinvoer.

**Verplichte projectregel:**
- **R3.1** Uploadendpoints MOETEN een maximale bestandsgrootte afdwingen; verzoeken die de limiet overschrijden MOETEN met een 4xx-fout geweigerd worden vóórdat het volledige bestand is weggeschreven.
- **R3.2** Externe HTTP-aanroepen (bv. naar de OpenAI-API, toekomstige ERP-koppelingen) MOETEN een expliciete timeout hebben; een aanroep zonder timeout is niet toegestaan.
- **R3.3** Query's die potentieel een volledige tabel kunnen retourneren BEHOREN een limiet of streaming-aanpak te gebruiken in plaats van alles in één keer in het geheugen te laden.
- **R3.4** Uploadverwerking BEHOORT te streamen naar schijf (zoals nu al gebeurt) in plaats van eerst volledig in het geheugen te lezen.

**Automatische controle:** beoogd: request-size-limieten op webserver-/reverse-proxy-niveau, plus een CI-check op ontbrekende timeout-parameters bij bekende HTTP-clientaanroepen. Statische detectie hiervan is beperkt automatiseerbaar. Huidige status: geen limieten geconfigureerd, geen tooling. Interim: code review bij elke nieuwe I/O-aanroep.

**Handmatige controle:** bij elke nieuwe upload-, netwerk- of query-aanroep: is er een expliciete grens (bestandsgrootte, timeout, `LIMIT`)? Wat gebeurt er bij overschrijding?

**Toegestane uitzonderingen:** intern, door de applicatie zelf gegenereerde datasets met een bekende kleine bovengrens (bv. het resultaat van het herverdelingsalgoritme voor één artikel) hoeven geen aparte limiet te hebben, mits de bovengrens elders al is afgedwongen (bv. via een R2.1-guard).

**Huidige toestand:** Voldoet niet. Geverifieerd: in `backend/routers/pdf_ingest.py` en `backend/routers/batches.py` is geen maximale-uploadgrootte-controle aangetroffen. Bestandsschrijven gebeurt wel al streamend via `shutil.copyfileobj` (positief, zie `pdf_ingest.py:170-171` en `batches.py:79-80`), maar zonder voorafgaande grootte- of typecontrole. Dit is bestaande technische schuld.

---

### Regel 4 — Kleine functies en modules met één verantwoordelijkheid

**Classificatie:** Aangepast toepasbaar — de exacte "60 regels op één vel papier"-vuistregel is een conventie uit de tijd van gedrukte C-listings; het onderliggende doel (een functie als begrijpelijke, verifieerbare eenheid) blijft onverkort van toepassing, met een moderne richtwaarde in plaats van een harde grens.

**Oorspronkelijke bedoeling:** elke functie moet een logische eenheid zijn die als geheel te begrijpen en te verifiëren is; buitensporig lange functies zijn vaak een teken van slecht gestructureerde code.

**Risico dat hiermee wordt beperkt:** onbegrijpelijke, moeilijk testbare en moeilijk te reviewen code; verborgen koppeling van verantwoordelijkheden; grotere kans op regressies bij wijzigingen.

**Vertaling naar dit project:** richtwaarde van circa 60 regels per functie en circa 400 regels per module voor nieuwe code; single-responsibility per functie/module; routers blijven een dunne HTTP-laag (zie hoofdstuk 5) in plaats van domeinlogica te bevatten.

**Verplichte projectregel:**
- **R4.1** Nieuwe of herschreven functies BEHOREN niet langer te zijn dan circa 60 regels; overschrijding vereist een korte motivatie in de PR of handoff.
- **R4.2** Een functie MAG NIET meerdere, onderling onafhankelijke verantwoordelijkheden combineren (bv. parsen + valideren + persisteren + notificeren in één functie); dit MOET gesplitst worden.
- **R4.3** Nieuwe modules BEHOREN niet groter te worden dan circa 400 regels; bij overschrijding BEHOORT opsplitsing overwogen te worden vóórdat verdere functionaliteit wordt toegevoegd.
- **R4.4** Business-logica MAG NIET in FastAPI-routerfuncties leven; routers roepen domeinfuncties aan (zie hoofdstuk 5).

**Automatische controle:** beoogd: complexiteits-/lengteregels in `ruff` (bv. functie-/bestandslengtemetrics) en ESLint (`max-lines-per-function`, `max-lines`). Huidige status: niet geconfigureerd. Interim: `wc -l` per bestand als grove indicator, aangevuld met code review op functiegrootte.

**Handmatige controle:** heeft de functie één duidelijk te benoemen taak? Kan de functie gesplitst worden in benoembare deelstappen zonder dat de samenhang verloren gaat?

**Toegestane uitzonderingen:** bestaande, niet-gerefactorde legacy-functies gelden als technische schuld, niet als goedgekeurde uitzondering. Nieuwe code met een lange maar puur sequentiële, niet-vertakkende reeks stappen (bv. een lineaire datatransformatie) MAG langer zijn dan de richtwaarde, mits elke stap becommentarieerd is, er geen verborgen vertakking optreedt, en de afwijking gemotiveerd is.

**Huidige toestand:** Voldoet niet. Geverifieerd met regeltellingen: `backend/routers/pdf_ingest.py` telt 913 regels, `backend/redistribution/algorithm.py` 880 regels, `backend/pdf_extract/pipeline.py` 528 regels. Dit zijn moduleomvangen, geen individuele functielengtes, maar de omvang wijst — in combinatie met de bevindingen in hoofdstuk 5 (business-logica in routers) — op te grote, te veel verantwoordelijkheden combinerende eenheden. Vastgesteld als bestaande technische schuld; de norm wordt niet verzwakt om aan de huidige code te voldoen.

---

### Regel 5 — Pre-/postcondities, invarianten en defensieve validatie

**Classificatie:** Aangepast toepasbaar — Python's kale `assert`-statement wordt weggeoptimaliseerd bij het `-O`-vlag en is daarom ongeschikt als productiemechanisme. Het onderliggende doel (systematische conditiecontrole met expliciete herstelactie) wordt vertaald naar Pydantic-validatie, expliciete precondition-checks en databaseconstraints.

**Oorspronkelijke bedoeling:** gemiddeld minimaal twee assertions per functie, bijwerkingsvrij, als Booleaanse test; bij falen volgt een expliciete herstelactie (bv. een foutretour aan de aanroeper). Assertions verifiëren pre-/postcondities, parameterwaarden, retourwaarden en lus-invarianten.

**Risico dat hiermee wordt beperkt:** onopgemerkte schendingen van aannames (bv. negatieve voorraad, een ongeldige status-overgang) die zich pas later, moeilijk herleidbaar, als datacorruptie of onjuist algoritmegedrag manifesteren.

**Vertaling naar dit project:** Pydantic-modellen op alle systeemgrenzen (HTTP-body en -response) in plaats van losse dicts; expliciete precondition-checks in kritieke domeinfuncties die bij schending een domeinfout opwerpen; invariant-checks in het herverdelingsalgoritme (voorraadbehoud, min-3-regel — zie hoofdstuk 10); databaseconstraints voor statusvelden en niet-negatieve aantallen.

**Verplichte projectregel:**
- **R5.1** Python's kale `assert`-statement MAG NIET gebruikt worden voor validatie die in productie moet blijven werken; gebruik een expliciete conditie die een uitzondering opwerpt of een foutresultaat teruggeeft.
- **R5.2** Elk endpoint dat request-data ontvangt MOET die data via een Pydantic-model valideren; ongetypeerde `dict`/`List[dict]`-bodies zijn niet toegestaan in nieuwe code.
- **R5.3** Kritieke domeinfuncties (herverdeling, ingest, goedkeuring) BEHOREN expliciete pre- en postconditiecontroles te bevatten (bv.: invoervoorraad ≥ 0, som na verdeling gelijk aan som vóór verdeling) met een expliciete herstelactie bij schending.
- **R5.4** Kolommen die per definitie niet-negatief zijn of tot een vaste waardenverzameling behoren (aantallen, statusvelden) BEHOREN een `CheckConstraint` te krijgen.

**Automatische controle:** beoogd: `mypy`/Pydantic voor typedwang, een lintregel tegen kaal `assert` buiten testcode. Huidige status: geen `mypy`/`ruff` geconfigureerd. Interim: code review, aangevuld met `grep -rn "^\s*assert " backend --include=*.py` (buiten testbestanden) als screening.

**Handmatige controle:** is elke externe input Pydantic-gevalideerd? Zijn er kale `assert`-statements in productiepaden? Zijn invarianten van kritieke domeinlogica expliciet gecontroleerd?

**Toegestane uitzonderingen:** `assert` MAG gebruikt worden binnen testcode (pytest); daarbuiten alleen als tijdelijk hulpmiddel tijdens ontwikkeling, nooit gecommit op de standaardbranch. Documentatie bij afwijking: `AFWIJKING: R5.x — <reden>` in code, plus vermelding in PR/handoff.

**Huidige toestand:** Voldoet gedeeltelijk. `backend/db_models.py` bevat wel `UniqueConstraint`s (bv. regel 174 en 204, plus kolomniveau `unique=True` op meerdere plekken) maar tijdens deze verificatie is **geen enkele `CheckConstraint`** aangetroffen in het bestand. `ArtikelVoorraad` (`db_models.py:285-321`) heeft geen unieke of niet-negativiteitsconstraint op voorraadaantallen. `Proposal.moves` is een ongetypeerde `JSON`-kolom (`db_models.py:125`) zonder schemavalidatie op databaseniveau; de endpointlaag valideert dit evenmin consistent (zie Regel 9 en hoofdstuk 7, `backend/routers/pdf_ingest.py:707-720`). Dit is bestaande technische schuld.

---

### Regel 6 — Kleinste scope, minimale gedeelde mutable state

**Classificatie:** Letterlijk toepasbaar — het principe van data-hiding en kleinste scope vertaalt zich rechtstreeks naar Python en TypeScript zonder aanpassing.

**Oorspronkelijke bedoeling:** data-objecten moeten op het kleinst mogelijke scope-niveau gedeclareerd worden. Dit vergemakkelijkt foutdiagnose (minder plekken waar een waarde toegekend kan zijn) en ontmoedigt hergebruik van variabelen voor meerdere, incompatibele doelen.

**Risico dat hiermee wordt beperkt:** module-level mutable state die door meerdere requests of threads gedeeld wordt, leidt tot moeilijk reproduceerbare bugs, race conditions en state-lekkage tussen gebruikers of sessies.

**Vertaling naar dit project:** geen nieuwe module-level mutable singletons in backend-code; per-request state hoort in een FastAPI-dependency of functieparameter, niet in een globale variabele; React-state hoort lokaal bij het component of expliciet in gedeelde state-management (context/store), nooit in module-scope buiten React om.

**Verplichte projectregel:**
- **R6.1** Nieuwe backend-code MAG GEEN module-level mutable variabelen introduceren die tussen requests gedeeld en gewijzigd worden; gebruik dependency injection (`Depends(...)`) of een expliciet doorgegeven context-object.
- **R6.2** Variabelen MOETEN gedeclareerd worden in de kleinste scope die hun gebruik toelaat; hergebruik van dezelfde variabele voor incompatibele doelen binnen één functie is verboden.
- **R6.3** Frontend-state BEHOORT lokaal bij het component te blijven tenzij er een aantoonbare noodzaak tot deling bestaat; gedeelde state MOET expliciet via context/store lopen, niet via module-level variabelen in `lib/`.

**Automatische controle:** beoogd: lintregels die module-level `global`-gebruik en mutable module-exports signaleren (backend en frontend). Huidige status: niet geconfigureerd. Interim: `grep -rn "^global \|^_[a-zA-Z_]* = " backend --include=*.py` als screening bij review.

**Handmatige controle:** bevat een nieuwe module state die door meerdere aanroepen gemuteerd wordt? Is er een `global`-statement? Kan dit via dependency injection?

**Toegestane uitzonderingen:** caches met een expliciete, gedocumenteerde invalidatiestrategie (bv. een klein, read-mostly configuratiecache) mogen als module-level singleton bestaan, mits thread-veiligheid is overwogen en gedocumenteerd. Bestaande singletons (zie hoofdstuk 15) zijn erkende, geregistreerde afwijkingen — geen precedent voor nieuwe code.

**Huidige toestand:** Voldoet niet voor twee bestaande, geregistreerde modules (zie hoofdstuk 15): `backend/redistribution/bv_config.py:241` declareert `_global_bv_config: Optional[BVConfig] = None` als module-level singleton, gemuteerd via `get_bv_config()`. `backend/redistribution/store_profiles.py:35` declareert `_active_profiles: Dict[str, StoreProfile] = dict(_DEFAULT_PROFILES)` als module-level mutable state; deze wordt herschreven via een `global`-statement in `set_store_profiles()` op regel 48. *(Correctie ten opzichte van eerdere aantekeningen: de singleton-declaratie zelf staat op regel 35, niet op regel 48 — regel 48 is de `global`-toewijzing binnen de setterfunctie.)* Voor de overige backend-modules is dit **niet vastgesteld** (geen uitputtende doorlichting uitgevoerd).

---

### Regel 7 — Retourwaarden, parameters en externe reacties controleren

**Classificatie:** Aangepast toepasbaar — "elke non-void functie se retourwaarde checken" is in de strikte C-zin niet 1:1 vertaalbaar naar Python (waar exceptions het gangbare foutmechanisme zijn), maar het onderliggende doel — geen stilzwijgend genegeerde fouten of resultaten — is direct van toepassing.

**Oorspronkelijke bedoeling:** retourwaarden van functies moeten door de aanroeper gecontroleerd worden, parameters moeten binnen de functie gevalideerd worden. Expliciet negeren mag, maar moet gemarkeerd of beargumenteerd zijn, niet impliciet gebeuren.

**Risico dat hiermee wordt beperkt:** stilzwijgend genegeerde fouten (bv. een mislukte parse of een gefaalde subverwerking die niet wordt opgemerkt) leiden tot corrupte of onvolledige data die pas later, moeilijk herleidbaar, aan het licht komt.

**Vertaling naar dit project:** resultaten van bestands-I/O, databaseoperaties, HTTP-aanroepen en parse-stappen MOETEN gecontroleerd worden; een brede `except Exception` zonder logging en zonder motivatie is verboden; frontend-fetches MOETEN foutafhandeling en een timeout hebben.

**Verplichte projectregel:**
- **R7.1** Een `except Exception`-clausule MAG NIET gebruikt worden zonder (a) logging van de oorspronkelijke fout en (b) een gedocumenteerde motivatie waarom een brede vangst nodig is.
- **R7.2** Interne foutdetails (stack traces, exception-tekst, querystrings) MOGEN NIET rechtstreeks in een client-gerichte foutmelding terechtkomen (zie hoofdstuk 7).
- **R7.3** Toegang tot extern aangeleverde of gedeserialiseerde data (bv. move-dictionaries) MOET via een gevalideerd model of met expliciete aanwezigheidscontrole gebeuren, niet via directe key-indexering die een ongevangen `KeyError` kan veroorzaken.
- **R7.4** Frontend API-aanroepen BEHOREN een foutafhandelingspad en een timeout te hebben; een fetch zonder foutstatuscontrole is niet toegestaan in nieuwe code.

**Automatische controle:** beoogd: lintregels tegen brede `except`-clausules en tegen ongevalideerde dict-toegang (backend), plus `mypy` voor type-veilige toegang in plaats van losse dicts. Huidige status: niet geconfigureerd. Interim: `grep -rn "except Exception" backend --include=*.py` als screeninglijst voor review.

**Handmatige controle:** is elke `except`-clausule specifiek genoeg? Wordt de fout gelogd? Gebeurt dict-indexering op externe data via `.get()` of een validatiestap?

**Toegestane uitzonderingen:** een brede `except Exception` op de buitenste laag van een achtergrondtaak (om te voorkomen dat één taak het hele proces meesleurt) MAG, mits gelogd met stacktrace en gedocumenteerd met `AFWIJKING: R7.x`.

**Huidige toestand:** Voldoet niet, op meerdere geverifieerde punten. `backend/routers/auth.py:173` vangt in de refresh-tokenhandler `except Exception as e` en retourneert in alle gevallen HTTP 401 ("Token kon niet vernieuwd worden"), ongeacht de daadwerkelijke oorzaak — serverfouten worden zo gemaskeerd als authenticatiefouten. `backend/routers/batches.py:81-82` lekt de ruwe exception-tekst naar de client (`detail=f"Failed to save file: {str(e)}"`). `backend/routers/pdf_ingest.py:707-720` gebruikt directe dict-indexering (`move["from_store"]`, `move["to_store"]`, `move["size"]`, `move["qty"]`) zonder voorafgaande validatie, met een reëel `KeyError`-risico bij onvolledige move-data. Dit zijn bevestigde technische-schuldpunten.

---

### Regel 8 — Beperking van verborgen codegeneratie en configuratievarianten

**Classificatie:** Niet letterlijk toepasbaar, maar het onderliggende principe is relevant — Python en TypeScript kennen geen C-preprocessor. Het analoge risico is ondoorzichtige metaprogrammering, `eval`/`exec`, en een combinatorische explosie van feature-flag-/configuratievarianten die elk afzonderlijk getest moeten worden.

**Oorspronkelijke bedoeling:** preprocessorgebruik beperken tot includes en eenvoudige macro's; conditionele compilatie zoveel mogelijk vermijden, omdat elke extra flag het aantal te testen codevarianten potentieel verdubbelt.

**Risico dat hiermee wordt beperkt:** onvoorspelbaar gedrag door dynamisch gegenereerde code, en een niet-geteste combinatie van configuratiestanden die voor het eerst in productie wordt geraakt.

**Vertaling naar dit project:** geen `eval`/`exec`/dynamische codegeneratie op basis van externe input; feature flags en omgevingsgedreven gedragsvarianten (zoals `ALGORITHM_ASSIST_MODE`) MOETEN minimaal gehouden worden en elke ondersteunde stand MOET afzonderlijk getest zijn; nieuwe flags MOETEN gedocumenteerd worden in `.env.example`.

**Verplichte projectregel:**
- **R8.1** `eval`/`exec`/dynamische codegeneratie op basis van externe of gebruikersinvoer is verboden.
- **R8.2** Elke omgevingsvariabele die het gedrag van de applicatie vertakt MOET gedocumenteerd worden in `.env.example` met de toegestane waarden.
- **R8.3** Voor `ALGORITHM_ASSIST_MODE` geldt specifiek: elke ondersteunde stand (`off`, `shadow`, `rank_assist`) MOET een eigen geautomatiseerde test hebben die het gedrag in die stand verifieert; een niet-geteste stand MAG NIET als ondersteund gedocumenteerd worden.
- **R8.4** Het aantal onafhankelijke configuratievarianten BEHOORT bewust laag gehouden te worden; nieuwe flags vereisen een motivatie waarom ze nodig zijn in plaats van enkelvoudig gedrag.

**Automatische controle:** beoogd: een lintregel tegen `eval`/`exec` en een CI-testmatrix die elke ondersteunde `ALGORITHM_ASSIST_MODE`-stand afzonderlijk test. Huidige status: geen tooling, geen CI-matrix. Interim: `grep -rn "eval(\|exec(" backend --include=*.py` en handmatige inventarisatie van env-gedreven vertakkingen.

**Handmatige controle:** is een nieuwe env-vertakking noodzakelijk? Is elke ondersteunde stand getest? Staat de flag in `.env.example`?

**Toegestane uitzonderingen:** `eval`/`exec` in geïsoleerde, niet-productiematige ontwikkel- of analysetools (bv. `tools/baseline-pipeline/`) MAG, mits nooit gevoed met ongecontroleerde externe input en expliciet gemotiveerd.

**Huidige toestand:** Voldoet gedeeltelijk. Geverifieerd: `backend/algorithm_import/config.py:8` definieert `SUPPORTED_ASSIST_MODES = {"off", "shadow", "rank_assist"}`, met standaardwaarde `"off"` afgeleid uit de omgevingsvariabele (regels 18-22). Of elke stand — met name `shadow` en `rank_assist` — een eigen geautomatiseerde test heeft, is tijdens deze verificatie **niet vastgesteld**; dit vereist een nadere inventarisatie van de testsuite (zie `docs/engineering/PRODUCTION_READINESS_AUDIT.md`) en wordt behandeld als openstaand aandachtspunt, niet als bevestigde naleving.

---

### Regel 9 — Beperking van ondoorzichtige indirectie

**Classificatie:** Niet letterlijk toepasbaar, maar het onderliggende principe is relevant — Python en TypeScript kennen geen pointers. Het analoge risico is reflection/`getattr`-magie, dynamische dispatch en ongetypeerde data die systeemgrenzen oversteekt, wat statische analyse en het volgen van de datastroom bemoeilijkt.

**Oorspronkelijke bedoeling:** pointergebruik beperken tot één dereferentieniveau, geen verborgen dereferenties, function pointers verboden tenzij sterk gemotiveerd — omdat ze het volgen van datastroom en aanroephiërarchie door tools ernstig bemoeilijken.

**Risico dat hiermee wordt beperkt:** code waarvan de daadwerkelijke controle- of datastroom niet meer statisch te herleiden is, wat foutopsporing en geautomatiseerde analyse ondermijnt.

**Vertaling naar dit project:** geen reflection/`getattr`-gebaseerde dynamische dispatch op basis van externe input; geen ongetypeerde `dict`/`Any` over systeemgrenzen; expliciete typing (Pydantic/TypeScript-interfaces) in plaats van impliciete structuren; korte, expliciete callbackketens in plaats van diep geneste callbacks/decorators die controlestroom verbergen.

**Verplichte projectregel:**
- **R9.1** Systeemgrenzen (HTTP-body/response, databasekolommen die structuur bevatten) MOGEN GEEN ongetypeerde `dict`/`Any`/`List[dict]` gebruiken; er MOET een expliciet Pydantic-model of TypeScript-interface zijn.
- **R9.2** Dynamische attribuuttoegang (`getattr`/`setattr` met een niet-statisch bekende naam) op basis van externe input is verboden, tenzij binnen een smalle, gevalideerde whitelist.
- **R9.3** Callbackketens/decorators BEHOREN maximaal enkele niveaus diep te zijn; wanneer de daadwerkelijke uitvoeringsvolgorde niet meer in één oogopslag te herleiden is, MOET dit herzien worden.

**Automatische controle:** beoogd: `mypy --strict` voor het afdwingen van typing in plaats van `Any`/dict (backend), ESLint `no-explicit-any` (frontend). Huidige status: geen `mypy`, geen ESLint-configuratie aanwezig. Interim: `grep -rn "List\[dict\]\|: dict\b\|: Any" backend --include=*.py` als screeninglijst.

**Handmatige controle:** is de payload op een nieuwe of gewijzigde systeemgrens getypeerd? Is er `getattr`/dynamische dispatch op basis van gebruikersinvoer?

**Toegestane uitzonderingen:** interne, niet-systeemgrensoverschrijdende helperfuncties mogen tijdelijk `dict` gebruiken tijdens vroege prototyping, mits vóór het mergen naar de standaardbranch vervangen door een getypeerd model, of expliciet gemotiveerd als afwijking.

**Huidige toestand:** Voldoet niet op het geverifieerde kernpunt. `Proposal.moves` wordt behandeld als ongetypeerde structuur: `backend/db_models.py:125` slaat `moves` op als generieke `JSON`-kolom, en `backend/routers/pdf_ingest.py:707-720` leest de moves-lijst uit met directe dict-indexering (`move["from_store"]`, `move["to_store"]`, `move["size"]`, `move["qty"]`) zonder een Pydantic-model ertussen. Dit is bevestigde technische schuld en een concreet voorbeeld van precies het probleem dat Regel 9 wil voorkomen.

---

### Regel 10 — Nul onverklaarde warnings en verplichte geautomatiseerde analyse

**Classificatie:** Letterlijk toepasbaar — dit principe vertaalt zich zonder aanpassing naar elke taal: compileer-/lint-/typecheck-waarschuwingen worden vanaf dag één op de strengste stand ingeschakeld, en de codebase bouwt zonder waarschuwingen.

**Oorspronkelijke bedoeling:** alle code wordt vanaf de eerste ontwikkeldag gecompileerd met alle compilerwaarschuwingen op de meest pedante stand, zonder waarschuwingen; dagelijkse controle met ten minste één, bij voorkeur meerdere, statische analysers, met nul waarschuwingen. Zelfs een vermoedelijk onterechte waarschuwing wordt opgelost door de code te herschrijven, niet genegeerd.

**Risico dat hiermee wordt beperkt:** onopgemerkte reële fouten die tussen de ruis van genegeerde waarschuwingen verdwijnen; een build die "toevallig werkt" zonder dat type- of stijlfouten zijn uitgesloten.

**Vertaling naar dit project:** backend — `ruff` (lint) + `mypy` (typecheck); frontend — een werkende ESLint-configuratie + `tsc --noEmit` zonder `ignoreBuildErrors`; beide als verplichte gate in CI (zie hoofdstuk 11).

**Verplichte projectregel:**
- **R10.1** Backend-Python MOET, zodra deze tooling is ingevoerd, foutloos door `ruff` (of een gelijkwaardige linter) en `mypy` gaan voordat het gemerged wordt.
- **R10.2** Frontend-TypeScript MOET foutloos door `tsc --noEmit` en een werkende ESLint-configuratie gaan; `ignoreBuildErrors: true` in `next.config.mjs` MAG NIET blijvend gebruikt worden om typefouten te maskeren.
- **R10.3** Een waarschuwing MAG NOOIT genegeerd worden op de aanname dat de tool het "toch fout heeft"; bij twijfel wordt de code herschreven tot de waarschuwing verdwijnt, of wordt een onderdrukking regel-specifiek en gemotiveerd toegepast — nooit globaal.
- **R10.4** Zodra de CI-pipeline (hoofdstuk 11) operationeel is: een falende lint-/typecheck-gate blokkeert de merge; gates MOGEN NIET tijdelijk uitgeschakeld worden om een taak te laten slagen.

**Automatische controle:** beoogd: `ruff check`, `mypy backend/`, `npm run lint`, `tsc --noEmit` als verplichte CI-stappen. Huidige status — **de grootste kloof van alle tien regels**: er is geen `ruff`-configuratie, geen `mypy`-configuratie, geen werkende ESLint-configuratie, geen Prettier-configuratie en geen CI (geen `.github/`-map aangetroffen in de repository). Invoering is uitgewerkt in `docs/engineering/PRODUCTION_READINESS_PLAN.md` fase 2. Interim: code review is het enige huidige vangnet.

**Handmatige controle:** reviewer controleert visueel op evidente type-inconsistenties en past, zodra beschikbaar, lokaal `tsc --noEmit`/`ruff`/`mypy` toe vóór het indienen van een PR.

**Toegestane uitzonderingen:** een regelspecifieke, gemotiveerde onderdrukking (bv. `# noqa: <code>  # AFWIJKING: R10.3 — <reden>`, of TypeScript `// @ts-expect-error — <reden>`) MAG; een bestandsbrede of projectbrede onderdrukking (zoals het huidige `ignoreBuildErrors: true`) MAG NIET als structurele oplossing dienen.

**Huidige toestand:** Voldoet niet. Geverifieerd: `frontend/next.config.mjs` bevat `typescript: { ignoreBuildErrors: true }`, terwijl `frontend/tsconfig.json` `"strict": true` heeft staan — een interne tegenstelling: strikte typing wordt tijdens ontwikkeling afgedwongen, maar typefouten worden bij de productie-build genegeerd. Er is geen `ruff`/`mypy`-configuratiebestand, geen werkende ESLint-configuratie en geen `.github/`-map aangetroffen. Dit is de grootste en meest urgente afwijking van de tien regels; de aanpak staat uitgewerkt in `docs/engineering/PRODUCTION_READINESS_PLAN.md`.

---

## 4. Projectspecificatie van de tien regels

De tien P10-regels vertalen naar tien moderne engineeringonderwerpen. Elk onderwerp verwijst naar de bijbehorende `R`-nummers uit hoofdstuk 3.

| # | Onderwerp | Regel(s) | Kern |
|---|---|---|---|
| 1 | Eenvoudige, expliciete control flow | R1.1–R1.4 | Begrensde recursie, beperkte nesting, geen exceptions als normale controlestroom |
| 2 | Begrensde lussen, retries, wachtrijen, paginering, batches | R2.1–R2.4 | Elke lus/retry/batch heeft een expliciete bovengrens en, waar relevant, een backoff-strategie |
| 3 | Begrensd geheugen-, schijf-, netwerk- en resourcegebruik | R3.1–R3.4 | Uploadlimieten, timeouts op I/O, streaming boven alles-in-geheugen |
| 4 | Kleine functies/modules met één verantwoordelijkheid | R4.1–R4.4 | Richtwaarden voor omvang, single responsibility, domeinlogica niet in routers |
| 5 | Pre-/postcondities, invarianten, defensieve validatie | R5.1–R5.4 | Pydantic op systeemgrenzen, geen kaal `assert`, DB-constraints |
| 6 | Minimale scope, minimale gedeelde mutable state | R6.1–R6.3 | Geen nieuwe module-level singletons, kleinste scope voor variabelen |
| 7 | Controle van invoer, retourwaarden, fouten, externe reacties | R7.1–R7.4 | Geen stille brede `except`, geen ongevalideerde dict-toegang, foutafhandeling in frontend-fetches |
| 8 | Beperking van verborgen codegeneratie, feature flags, configuratievarianten | R8.1–R8.4 | Geen `eval`/`exec`; elke `ALGORITHM_ASSIST_MODE`-stand (`off`/`shadow`/`rank_assist`) afzonderlijk getest |
| 9 | Beperking van ondoorzichtige indirectie, dynamische dispatch, reflection, callbackketens | R9.1–R9.3 | Getypeerde systeemgrenzen, geen `getattr`-magie, ondiepe callbackketens |
| 10 | Nul onverklaarde warnings, verplichte geautomatiseerde analyse | R10.1–R10.4 | `ruff`/`mypy`/ESLint/`tsc --noEmit` zonder onderdrukkingen, verplichte CI-gate |

---

## 5. Architectuur

**Componentgrenzen:**

| Laag | Modules | Verantwoordelijkheid |
|---|---|---|
| HTTP-laag | `backend/routers/*.py` | Request-/response-mapping, input-deserialisatie, afdwingen van authenticatie/autorisatie, aanroepen van domeinfuncties. Geen domeinlogica. |
| Domeinlaag | `backend/redistribution/` (o.a. `algorithm.py`, `bv_config.py`, `store_profiles.py`, `constraints.py`), `backend/pdf_extract/`, `backend/algorithm_import/`, `backend/assignment_service.py` | Bedrijfsregels: herverdelingsalgoritme, PDF-extractie, ML-assist-scoring, assignment-generatie. Geen kennis van HTTP. |
| Infrastructuur | `backend/database.py`, `backend/db_models.py` | Database-verbinding, sessiebeheer, ORM-modellen. Geen bedrijfsregels. |
| API-toegang (frontend) | `frontend/lib/` | HTTP-communicatie met de backend, tokenbeheer. Geen domeinlogica; presentatielogica hoort in componenten. |

**Afhankelijkheidsrichting:** de domeinlaag MAG NIET afhangen van de HTTP-laag — routers roepen domeinfuncties aan, nooit andersom. Infrastructuur (`database.py`/`db_models.py`) mag door zowel domein als routers gebruikt worden, maar bevat zelf geen domeinregels. Circulaire afhankelijkheden tussen modules zijn niet toegestaan.

**Scheiding domeinlogica/infrastructuur:** ORM-modellen (`db_models.py`) beschrijven persistentie, geen gedrag; validatie- en berekeningslogica hoort in de domeinlaag of in Pydantic-schema's, niet in de modelklassen zelf.

**Expliciete interfaces met externe systemen:** momenteel bestaat één externe interface — bestandssysteem-artifacts die `backend/algorithm_import/` leest vanaf een configureerbaar pad (`EXTERNAL_ALGORITHM_DATA_ROOT`, met standaardwaarde `backend/algorithm_data/`, zie `backend/algorithm_import/config.py:6-7`). Toekomstige ERP-koppelingen MOETEN via een expliciete, getypeerde interfacelaag lopen — niet rechtstreeks vanuit routers of vanuit domeincode zonder abstractie.

**Vastgestelde afwijking (technische schuld):** `backend/routers/pdf_ingest.py` (913 regels) bevat aanzienlijke domeinlogica rechtstreeks in de routerlaag — parsing-orchestratie, het toepassen van moves op voorraad, en het aanmaken van `Feedback`-records gebeuren in routerfuncties in plaats van in een domeinmodule. Dit is een schending van de architectuurgrens in dit hoofdstuk en van R4.4. De norm wordt hierdoor niet verzwakt; de afwijking is vastgesteld en behoort tot de saneringsscope in `docs/engineering/PRODUCTION_READINESS_PLAN.md`.

---

## 6. Data-integriteit

**Schema-/invoervalidatie:** Pydantic MOET gebruikt worden op alle systeemgrenzen (R5.2, R9.1). Vastgestelde afwijking: `Proposal.moves` is een ongetypeerde `JSON`-kolom (`db_models.py:125`) en wordt in `backend/routers/pdf_ingest.py:707-720` met directe dict-indexering gelezen, zonder Pydantic-model.

**Databaseconstraints:** `backend/db_models.py` bevat diverse `unique=True`-kolommen en twee `UniqueConstraint`-definities (`uq_assignment_series_batch_store` op regel 174, `uq_assignment_item_proposal_route` op regel 204). Er zijn tijdens deze verificatie **geen `CheckConstraint`s** aangetroffen voor statusvelden of niet-negatieve aantallen. `ArtikelVoorraad` (`db_models.py:285-321`) heeft geen unieke constraint over de combinatie batch/artikel/filiaal/maat — een herhaalde ingest van dezelfde PDF kan daardoor dubbele voorraadrijen opleveren.

**Transacties:** multi-step writes MOETEN atomair zijn; commits midden in een verwerkingslus zijn niet toegestaan tenzij elke stap zelfstandig consistent en herstelbaar is. Vastgestelde afwijking: `save_to_database()` in `backend/routers/pdf_ingest.py` commit tweemaal per verwerkt bestand (regel 327 en regel 342) en wordt aangeroepen vanuit de per-bestand-lus (lus start regel 164, aanroep op regel 199). Een crash halverwege een meerbestands-batch laat daardoor een deel van de bestanden gecommit achter en een deel niet, terwijl de batch zelf al bij aanvang is gecommit (`pdf_ingest.py:149`, vóór verwerking van enig bestand) — dit kan een `PENDING`-batch zonder bijbehorende voorraaddata achterlaten.

**Idempotentie:** dubbele acties MOGEN NIET tot dubbele database-rijen leiden. Vastgestelde afwijking: het goedkeuren van een voorstel (`backend/routers/pdf_ingest.py:775-798`) controleert niet of het voorstel al `approved` is voordat het per move een nieuw `Feedback`-record aanmaakt (regels 785-794); een herhaalde aanroep van dezelfde approve-actie levert dubbele `Feedback`-rijen op.

**Gelijktijdige wijzigingen:** het `Proposal`-model (`db_models.py:104-156`) heeft geen versiekolom of ander optimistic-locking-mechanisme; twee gelijktijdige wijzigingen aan hetzelfde voorstel kunnen elkaar zonder waarschuwing overschrijven.

**Migraties:** er is geen Alembic of vergelijkbaar migratieframework. Schema-aanpassingen lopen via `Base.metadata.create_all()` (`backend/main.py:36`) plus `ensure_runtime_schema()` (`backend/database.py:31-73`), die ad-hoc `ALTER TABLE`-statements uitvoert op basis van kolominspectie. Dit is een ongecontroleerde, niet-reproduceerbare migratieroute en MAG NIET de structurele oplossing blijven (zie hoofdstuk 12).

**Audit trail:** `Feedback`-records leggen `category`/`action_taken` per move vast (`db_models.py:213-254`), maar bevatten geen verwijzing naar de uitvoerende gebruiker; `Proposal` heeft een `reviewed_at`-tijdstempel maar geen `reviewed_by`/`approved_by`-kolom. Wie welk voorstel heeft goedgekeurd of afgekeurd is dus **niet vastgesteld** in het datamodel — een gat ten opzichte van de eis in hoofdstuk 8.

**Herstel bij gedeeltelijk mislukte operaties:** er is geen expliciet compensatie- of rollbackmechanisme voor de hierboven beschreven per-bestand-commits. `backend/reset_database.py` bestaat als destructief hulpmiddel (volledige reset), niet als een gecontroleerd, getest herstelpad (zie hoofdstuk 12).

---

## 7. Foutafhandeling

**Geen stil genegeerde fouten:** elke opgevangen fout MOET gelogd worden of expliciet en gemotiveerd worden genegeerd (R7.1). Vastgesteld: `backend/routers/auth.py:173` vangt alle exceptions in de refresh-tokenhandler en retourneert zonder onderscheid HTTP 401 — een serverfout (bv. een databasefout) wordt onherkenbaar van een ongeldig token.

**Bruikbare meldingen zonder interne details naar de client:** foutmeldingen aan de client MOGEN GEEN stack traces, exception-tekst of interne padinformatie bevatten (R7.2). Vastgesteld: `backend/routers/batches.py:81-82` retourneert `detail=f"Failed to save file: {str(e)}"` — de ruwe exceptiontekst wordt rechtstreeks doorgegeven.

**Onderscheid gebruikersfout / tijdelijke fout / programmeerfout:**
- **Gebruikersfout (4xx):** ongeldige input, ontbrekende autorisatie — direct en specifiek gecommuniceerd naar de client.
- **Tijdelijke fout:** netwerk-/externe-service-timeouts — BEHOORT met een begrensde retry (R2.2) afgehandeld te worden vóór het als fout wordt gerapporteerd.
- **Programmeerfout (5xx):** onverwachte interne staat — MOET gelogd worden met voldoende context voor diagnose, en MAG NOOIT de interne foutdetails aan de client tonen.

**Retries:** MOETEN een maximum aantal pogingen, een timeout per poging en een backoff-strategie hebben (R2.2); geen enkele retry-implementatie hiervoor is tijdens deze verificatie aangetroffen in `backend/algorithm_import/` — **niet vastgesteld** of dit ontbreekt of elders zit.

**Veilige afhandeling van gedeeltelijke successen:** een batch met deels gelukte, deels mislukte bestanden (zoals het huidige ingest-endpoint, dat `PARTIAL_SUCCESS` als status kent, `pdf_ingest.py:236-241`) BEHOORT dat gedeeltelijke succes expliciet en volledig te communiceren, inclusief per bestand welke stap faalde. De huidige implementatie doet dit al gedeeltelijk (per-bestand resultaatlijst) — een positief punt dat behouden moet blijven bij toekomstige wijzigingen.

**Geen brede exception handlers zonder motivatie en logging:** zie R7.1. Elke `except Exception` zonder specifieke foutafhandeling MOET voorzien zijn van logging en een motivatie in commentaar waarom een bredere vangst noodzakelijk is.

---

## 8. Logging en observability

**Gestructureerde logging, één centrale configuratie:** logconfiguratie hoort op één plek te staan, niet verspreid via `logging.basicConfig()`-aanroepen in individuele modules. Vastgesteld: `logging.basicConfig(level=logging.INFO)` komt voor in zowel `backend/routers/pdf_ingest.py:27` als `backend/pdf_extract/pipeline.py:34` — twee afzonderlijke, module-lokale configuraties in plaats van één centrale opzet. Dit leidt tot niet-deterministisch gedrag afhankelijk van importvolgorde en is niet uitbreidbaar naar gestructureerd (bv. JSON-)loggen.

**Logniveaus:** MOETEN consistent gebruikt worden (DEBUG voor ontwikkelinformatie, INFO voor normale operationele gebeurtenissen, WARNING voor herstelde afwijkingen, ERROR voor fouten die aandacht vereisen).

**Correlation-/request-ID's:** niet aangetroffen in de huidige codebase (**niet vastgesteld** dat dit volledig ontbreekt, wel dat er geen centrale middleware voor is gevonden bij het lezen van `backend/main.py`). Zonder request-ID is het herleiden van een specifieke fout door de laag routers → domein → database niet goed mogelijk bij gelijktijdige requests.

**Metrics:** geen metrics-infrastructuur (bv. Prometheus-achtige exporters) aangetroffen.

**Health checks:** `backend/main.py:120-123` biedt een `/health`-endpoint dat statisch `{"status": "healthy"}` retourneert, zonder databaseconnectiviteit te controleren. Een health check die niet de daadwerkelijke afhankelijkheden (database) test, geeft een vals gevoel van gezondheid tijdens een database-uitval.

**Auditlogging voor mutaties:** wie welk voorstel goedkeurde of afkeurde MOET herleidbaar zijn. Zoals vastgesteld in hoofdstuk 6, ontbreekt dit vandaag in het datamodel (`Proposal` heeft geen `reviewed_by`, `Feedback` heeft geen `user_id`) — dit is een concrete, benoemde tekortkoming.

**Geen persoonsgegevens/wachtwoorden/tokens/secrets in logs:** logregels MOGEN NOOIT wachtwoorden, JWT's, API-keys of andere secrets bevatten, ook niet bij debug-logging. Vastgesteld risico: `backend/check_secret_key.py` print de actieve `SECRET_KEY`-waarde naar stdout (`print(f"🔑 SECRET_KEY from env: {secret_key}")`) — een script dat, als het per ongeluk in een gedeeld logbestand terechtkomt, het secret blootlegt. Dit script is een hulpmiddel, geen logging-pad in de productieapplicatie zelf, maar het patroon (secrets naar stdout/log printen) MAG niet in productiecode voorkomen.

---

## 9. Security

**Secrets buiten broncode:** `SECRET_KEY` MOET uit de omgeving komen, zonder fallback-default. Vastgesteld: `backend/auth.py:26` bevat `SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")` — een hardcoded fallback die, als de omgevingsvariabele ontbreekt, een voor iedereen bekende sleutel gebruikt om JWT's te ondertekenen. Dit is een kritieke bevinding.

**Least privilege:** RBAC-machinerie is aanwezig (`require_permission`, 38 toepassingen gevonden in `backend/routers/*.py`), maar niet consistent toegepast (zie hieronder).

**Dependencycontrole:** geen `pip-audit`/`npm audit`-uitvoering in CI aangetroffen (geen CI aanwezig, zie hoofdstuk 11). `backend/requirements.txt` is wel volledig gepind met exacte versies (`==`) — een positief punt dat reproduceerbare installaties mogelijk maakt, maar géén vervanging voor periodieke kwetsbaarheidscontrole.

**Input sanitization:** uploadbestandsnamen MOETEN gesaneerd worden voordat ze in een bestandspad gebruikt worden. Vastgesteld: `backend/routers/pdf_ingest.py:169` bouwt het opslagpad met `os.path.join(batch_dir, file.filename)`, waarbij `file.filename` ongefilterd van de client komt — een bestandsnaam als `../../etc/whatever` kan in theorie buiten de bedoelde uploadmap schrijven (path traversal). Ter vergelijking: `backend/routers/batches.py:73-75` bouwt de bestandsnaam wél met een tijdstempel-prefix (`safe_filename = f"{timestamp}_{file.filename}"`), maar saniteert het onderliggende `file.filename` evenmin — het risico op padtraversal via `../`-segmenten blijft ook daar aanwezig omdat de ruwe bestandsnaam ongewijzigd wordt meegenomen.

**Authenticatie en autorisatie op alle muterende endpoints:** MOET gelden voor elk endpoint dat data wijzigt. Vastgesteld: in `backend/routers/pdf_ingest.py`, `backend/routers/batches.py`, `backend/routers/articles.py` en `backend/routers/redistribution.py` is tijdens deze verificatie **geen enkele** `Depends(get_current_...)`- of `require_permission`-aanroep aangetroffen — de ingest-, approve-, reject- en delete-operaties in deze routers zijn niet beschermd door authenticatie of autorisatie, terwijl RBAC elders in de codebase (38 toepassingen, o.a. in gebruikers-/rollenrouters) wél consequent wordt gebruikt. Dit is een kritieke bevinding.

**Veilige defaults:** CORS is momenteel effectief hardcoded in plaats van omgevingsgestuurd. Vastgesteld: `backend/main.py:40-53` berekent `allowed_origins`/`allowed_origins_str` uit de omgevingsvariabele `ALLOWED_ORIGINS`, maar `app.add_middleware(CORSMiddleware, ...)` op regel 55-61 gebruikt in plaats daarvan een hardcoded `allow_origin_regex` — de berekende `allowed_origins`-lijst wordt nergens doorgegeven aan de middleware. De omgevingsvariabele heeft dus geen effect; dit is een bug, geen bewuste beveiligingskeuze.

**Bescherming van bedrijfsgegevens:** voorraaddata is bedrijfsgevoelig. Vastgesteld risico: drie databasebackup-bestanden zijn in git getrackt (`backend/database.db.backup_20251029_002226` — 241.664 bytes met data, plus twee lege bestanden van 0 bytes met dezelfde naamgeving) — een productie-achtig databasebestand met mogelijk echte voorraad-/gebruikersdata staat daarmee in de git-geschiedenis.

**Veilige verwerking van uploads en externe bestanden:** zie ook Regel 3 (R3.1). Geen uploadgrootte-limiet en geen bestandstype-validatie voorafgaand aan opslag aangetroffen in `pdf_ingest.py`/`batches.py` (validatie van PDF-geldigheid gebeurt wel ná het schrijven, zie `batches.py:85-87`). PDF-parsing (`backend/pdf_extract/`) is een systeemgrens: het verwerkt bestanden van buiten de applicatie en MOET behandeld worden als potentieel vijandige input (defensieve parsing, begrensde verwerkingstijd — zie R2/R3).

**Overige vastgestelde risico's:** het OpenAI-API-key wordt onversleuteld opgeslagen (`backend/routers/settings.py:349-351`, kolomcommentaar luidt letterlijk "Store as JSON for encryption later" — de encryptie is nooit geïmplementeerd); JWT-tokens worden in `localStorage` (bij "onthoud mij") of anders `sessionStorage` bewaard (`frontend/lib/token-storage.ts`), wat XSS-gevoelig is; er is geen rate limiting op het login-endpoint aangetroffen (`backend/routers/auth.py`, rond de `login`-functie). Positief: wachtwoordsterkte wordt wel gevalideerd via `validate_password_strength()` (`backend/auth.py:50`, toegepast in `backend/routers/users.py:241` en `:536`).

---

## 10. Teststrategie

**Wanneer welk testtype nodig is**, gekoppeld aan de risicoklassen uit hoofdstuk 14:
- **Unit tests** — verplicht voor alle domeinlogica in de klasse Kritiek (met name `backend/redistribution/`), voor validatiefuncties en voor pure transformatiefuncties.
- **Integratietests** — verplicht voor endpoint-flows die meerdere lagen doorlopen (ingest → proposal → approve → assignment), met name in de klassen Kritiek en Belangrijk.
- **Contracttests** — BEHOREN ingevoerd te worden zodra de frontend/backend-API-grens stabiliseert, om te voorkomen dat backend-wijzigingen de frontend stilzwijgend breken.
- **Regressietests** — verplicht bij elke bugfix in Kritieke of Belangrijke componenten: de test die het defect reproduceert wordt onderdeel van de suite.
- **End-to-end (e2e) tests** — voor de kernflow (upload → voorstel → goedkeuring → assignment) in een realistische omgeving.
- **Property-based tests** — BEHOREN overwogen te worden voor het herverdelingsalgoritme, gezien de combinatorische aard van voorraad-/winkelcombinaties.
- **Foutpadtests** — verplicht voor elk expliciet foutafhandelingspad beschreven in hoofdstuk 7 (4xx/5xx-onderscheid, retries, gedeeltelijke successen).
- **Grenswaardetests** — verplicht voor elke expliciete bovengrens uit hoofdstuk 3/4 (Regel 2/R2.x): guard-tellers, uploadlimieten, batchgroottes.
- **Migratietests** — verplicht zodra een gecontroleerd migratieframework is ingevoerd (hoofdstuk 12): elke migratie moet getest worden op een representatieve dataset.
- **Smoke tests** — verplicht als snelle post-deploymentcontrole (hoofdstuk 12).

**Verplicht te testen invarianten voor de kritieke domeinlogica (herverdeling):**
- **(a) Min-3-regel:** elke ontvangende winkel eindigt na herverdeling met 0 of ten minste `min_items_per_receiver` stuks — nooit een aantal daartussenin.
- **(b) BV-groepsscheiding:** de scheiding tussen BV-groepen (`backend/redistribution/bv_config.py`) wordt nooit geschonden door een voorgestelde move.
- **(c) Voorraadbehoud:** de som van de voorraad vóór herverdeling is gelijk aan de som ná herverdeling — er worden nooit units verzonnen of verloren.
- **(d) Geen negatieve voorraden:** geen enkele winkel/maat-combinatie heeft na toepassing van de moves een negatieve voorraad.
- **(e) Geldige winkels:** moves vinden alleen plaats tussen winkels die als geldig/actief bekend staan.

**Testconventie:** `pytest` is het te gebruiken testframework; nieuwe tests horen naast een toekomstige `backend/tests/`-structuur te komen in plaats van los in de backend-root.

**Huidige toestand:** Voldoet gedeeltelijk. Geverifieerd: er zijn 21 bestanden met het patroon `test_*.py` in de backend-root; `backend/test_bundle_planner.py` bevat 9 daadwerkelijke `pytest`-testfuncties (positief, dekt een deel van de min-3-regel-logica). Het merendeel van de overige 20 bestanden is — conform eerdere verkenning — grotendeels procedureel opgezet (print-gebaseerde scripts in plaats van `assert`-gebaseerde tests); dit is tijdens deze verificatie niet bestand-voor-bestand herbevestigd en blijft in zoverre **niet volledig vastgesteld**, maar het aantal (21 bestanden, waarvan er maar één met zekerheid 9 echte tests bevat) wijst op een aanzienlijke kloof. `pytest` staat niet in `backend/requirements.txt`. De frontend heeft geen unit tests. Voor e2e-dekking is precies één Playwright-specbestand aangetroffen, `tests/browser/smoke.spec.ts`, met 7 test-definities. Dit is bestaande technische schuld; uitbreiding staat in `docs/engineering/PRODUCTION_READINESS_PLAN.md`.

---

## 11. CI/CD en quality gates

**Verplichte minimale pipeline** (voor zover van toepassing per ontwikkelfase, zie `docs/engineering/PRODUCTION_READINESS_PLAN.md`):
1. Formatting-check
2. Lint (`ruff` backend, ESLint frontend)
3. Typecheck (`mypy` backend, `tsc --noEmit` frontend)
4. Unit tests
5. Integratietests
6. Security-/dependencyscan (`pip-audit`, `npm audit`)
7. Buildcontrole (frontend build zonder `ignoreBuildErrors`)
8. Migratiecontrole (zodra een migratieframework is ingevoerd)
9. Artifactgeneratie (waar van toepassing)
10. Deploymentvalidatie (zodra er een deploymentdoel is, zie hoofdstuk 12)

**Regel:** een pull request MAG NIET gemerged worden bij een falende verplichte gate. Gates MOGEN NIET uitgeschakeld of verzwakt worden om een taak te laten slagen — dit geldt zowel voor menselijke bijdragers als voor AI-sessies die in deze repository werken.

**Huidige toestand:** Voldoet niet. Er is geen `.github/`-map en dus geen CI-pipeline aangetroffen in deze repository. Invoering van de bovenstaande gates is uitgewerkt als gefaseerd traject in `docs/engineering/PRODUCTION_READINESS_PLAN.md` (fase 2). Tot die tijd is code review het enige kwaliteitspoort.

---

## 12. Deployment en herstel

**Reproduceerbare builds:** backend-dependencies zijn volledig gepind (`backend/requirements.txt`, alle pakketten met `==`), wat reproduceerbare installaties ondersteunt — een positief punt. Voor de frontend is de reproduceerbaarheid van de lockfile tijdens deze verificatie **niet vastgesteld**.

**Omgevingsconfiguratie:** alle omgevingsvariabelen (waaronder `SECRET_KEY`, `ALLOWED_ORIGINS`, `ALGORITHM_ASSIST_MODE`, `EXTERNAL_ALGORITHM_DATA_ROOT`) MOETEN gedocumenteerd zijn in een `.env.example`-bestand met de toegestane waarden en een duidelijke aanduiding welke variabelen verplicht zijn zonder fallback (met name `SECRET_KEY`, zie R-verwijzing in hoofdstuk 9).

**Databasebackups:** MOETEN geautomatiseerd zijn en het herstel ervan MOET periodiek getest worden. Huidige toestand: er is geen geautomatiseerd backupmechanisme; `backend/reset_database.py` is een destructief hulpmiddel, geen backup-/herstelvoorziening. De drie in git getrackte `database.db.backup_*`-bestanden (hoofdstuk 9) zijn geen vervanging voor een echte backupstrategie — ze zijn ad-hoc kopieën die per ongeluk in versiebeheer zijn beland.

**Migratieprocedure:** MOET gecontroleerd en reproduceerbaar zijn. Huidige toestand: geen Alembic; `ensure_runtime_schema()` (`backend/database.py:31-73`) voert ad-hoc `ALTER TABLE`-statements uit op basis van runtime-kolominspectie. Dit MAG NIET de blijvende structurele oplossing zijn (zie hoofdstuk 6).

**Rollbackstrategie:** niet gedocumenteerd, niet aangetroffen.

**Deploymentchecklist en post-deploymentvalidatie:** niet aangetroffen; MOET ontwikkeld worden vóórdat een eerste productiedeployment plaatsvindt.

**Incidentprocedure:** niet aangetroffen.

**Deploymentdoel:** **Onbekend.** Lokale ontwikkeling gebeurt Windows-first via `dev.ps1` in de repository-root; er is geen Dockerfile, geen `.github/`-workflow en geen documentatie van een beoogd productie-hostingdoel aangetroffen. Zolang het deploymentdoel onbekend is, kunnen de bovenstaande punten (reproduceerbare builds, backups, rollback) niet volledig concreet worden ingevuld — dit is een expliciete blokkerende onbekende voor `docs/engineering/PRODUCTION_READINESS_PLAN.md` fase 4.

---

## 13. Documentatie

De volgende documentatie MOET synchroon met de code bijgewerkt worden zodra de betreffende code wijzigt:

| Wijziging in code | Bij te werken documentatie |
|---|---|
| Architectuur/componentgrenzen | `README.md`, architectuurdocumentatie in `docs/technical/` |
| Configuratie/omgevingsvariabelen | `.env.example`, installatie-/setupdocumentatie |
| Installatie-/opstartprocedure | `docs/getting-started/` |
| Deployment | deploymentdocumentatie/runbooks zodra die bestaan (hoofdstuk 12) |
| Databaseschema | `CHANGELOG.md` én `docs/guides/database.md` |
| API-contracten (endpoints, request-/responsemodellen) | relevante API-referentiedocumentatie |
| Bekende beperkingen/technische schuld | `docs/engineering/PRODUCTION_READINESS_AUDIT.md` |

Voor plaatsing en registratie van nieuwe documentatie blijven `docs/DOCUMENTATION_GUIDELINES.md` en `docs/PROJECT_CONTEXT_INDEX.md` leidend — dit document definieert géén eigen, afwijkende regels over waar documentatie hoort of hoe zij benoemd wordt. Bij twijfel over de plaatsing van een nieuw document: raadpleeg die twee documenten, niet dit hoofdstuk.

---

## 14. Risicogebaseerde strengheid

Niet elk onderdeel van deze repository draagt hetzelfde risico. Vier klassen, van strengst naar minst streng:

| Klasse | Betekenis | Verplichte regels/gates |
|---|---|---|
| **Kritiek** | Muteert productiedata, beïnvloedt voorraad, voert migraties uit, of neemt operationeel uitgevoerde beslissingen | Alle regels uit hoofdstuk 3 volledig van toepassing; unit- + integratietests verplicht vóór merge; geen ongeteste configuratievariant; code review verplicht |
| **Belangrijk** | Ondersteunt de kernflow maar muteert geen kritieke data direct, of is de gebruikersinterface daarvoor | Hoofdstuk 3-regels van toepassing met iets meer ruimte voor gefaseerde invoering; tests verplicht voor nieuwe/gewijzigde logica |
| **Ondersteunend** | Ontwikkel-/operationele hulpmiddelen, niet in het directe kritieke pad | Basisregels (geen secrets, geen destructieve acties zonder bevestiging); lichtere reviewlat |
| **Experimenteel** | Onderzoek/ML-prototyping, nog niet productierijp | Mag afwijken van striktere regels, MAAR MAG NIET met productiedata/-processen werken zonder expliciete vrijgave |

**Classificatie van bestaande componenten:**

| Component | Klasse |
|---|---|
| `backend/redistribution/` (o.a. `algorithm.py`, `bv_config.py`, `store_profiles.py`, `constraints.py`) | Kritiek |
| `backend/routers/pdf_ingest.py` (ingest/approve) | Kritiek |
| `backend/assignment_service.py` | Kritiek |
| `backend/db_models.py` + `backend/database.py` | Kritiek |
| `backend/auth.py` + `backend/routers/auth.py`/`users.py`/`roles.py` | Kritiek |
| `backend/pdf_extract/` | Belangrijk |
| `backend/routers/dashboard.py`/`settings.py`/`feedback.py` | Belangrijk |
| Frontend proposal-/assignment-flows | Belangrijk |
| `scripts/`, `dev.ps1`, `check_*`/`debug_*`-scripts | Ondersteunend |
| `backend/algorithm_import/` (shadow/rank-assist ML) | Experimenteel |
| `tools/baseline-pipeline/` | Experimenteel |

**Regels voor klasseovergang:**
- Een Experimentele component MAG NIET met productiedata of productieprocessen werken zonder expliciete vrijgave door de projecteigenaar.
- Zodra een component **productiedata wijzigt**, **voorraad beïnvloedt**, **migraties uitvoert**, **bestanden automatisch verwerkt**, **operationeel uitgevoerde beslissingen genereert**, of **gekoppeld is aan een ERP/database/extern systeem**, geldt automatisch de **strengste toepasselijke klasse (Kritiek)** — ongeacht de map waarin het bestand staat. Dit betekent onder meer dat `backend/algorithm_import/` zodra het van `shadow` naar `rank_assist` overgaat in een productieomgeving, feitelijk Kritiek-niveau striktheid vereist, niet meer Experimenteel-niveau.

---

## 15. Uitzonderingsproces

Elke afwijking van een regel in dit document volgt een vast, viervoudig proces:

1. **Technische motivatie op de plek zelf** — codecommentaar in het formaat `AFWIJKING: <regelnr> — <reden>` direct bij de afwijkende code.
2. **Vermelding in PR-beschrijving of handoff** — conform het format van `docs/engineering/AI_SESSION_HANDOFF.md`.
3. **Registratie in de uitzonderingentabel hieronder** — datum, regel, locatie, motivatie, compenserende controle, eigenaar.
4. **Compenserende test of controle** — verplicht; een uitzondering zonder compenserende maatregel is niet geldig.

**Uitzonderingentabel:**

| Datum | Regel | Locatie | Motivatie | Compenserende controle | Eigenaar |
|---|---|---|---|---|---|
| 2026-07-13 | R6.1 | `backend/redistribution/bv_config.py:241` (`_global_bv_config`) | Bestaande module-level singleton voor BV-configuratie, aangetroffen bij audit; vervanging vereist een bredere refactor van hoe configuratie door het algoritme wordt doorgegeven | Geen — geregistreerd als openstaande technische schuld, geen compenserende test aanwezig; op te nemen in saneringsscope | Projecteigenaar |
| 2026-07-13 | R6.1 | `backend/redistribution/store_profiles.py:35` (`_active_profiles`, herschreven via `global` op regel 48) | Bestaande module-level singleton voor winkelprofielen, aangetroffen bij audit; dezelfde reden als hierboven | Geen — geregistreerd als openstaande technische schuld | Projecteigenaar |
| 2026-07-13 | R4.1–R4.3 | `backend/routers/pdf_ingest.py` (913 regels) | Grote legacy-module die routerlaag en domeinlogica vermengt; aantoonbaar functionerend, maar niet-conform de architectuurgrens uit hoofdstuk 5 | Geen structurele compenserende controle aanwezig; op te nemen in de saneringsscope van `docs/engineering/PRODUCTION_READINESS_PLAN.md` | Projecteigenaar |
| 2026-07-13 | R4.1–R4.3 | `backend/redistribution/algorithm.py` (880 regels) | Grote, samenhangende domeinmodule voor het herverdelingsalgoritme; splitsing vereist zorgvuldige afbakening om de min-3-regel-logica niet te breken | 9 bestaande tests in `backend/test_bundle_planner.py` dekken een deel van het kritieke gedrag; verdere testdekking vereist vóór verdere opsplitsing | Projecteigenaar |

Deze eerste vier rijen zijn bij het opstellen van dit document geregistreerd als reeds bestaande, bewuste afwijkingen (technische schuld), niet als nieuw goedgekeurde uitzonderingen voor toekomstige code. Nieuwe afwijkingen die vanaf nu ontstaan MOETEN op dezelfde wijze geregistreerd worden, met een concrete compenserende controle — het enkel noteren van de afwijking zonder compensatie volstaat niet voor nieuwe code.

---

## 16. Wijzigingsbeheer

Elke inhoudelijke wijziging aan dit document vereist een nieuwe rij in onderstaande tabel: datum, reden, betrokken regels, impact op tooling/CI, eventuele migratie van bestaande code, en de reviewer/eigenaar (indien bekend).

| Datum | Reden | Betrokken regels | Impact op tooling/CI | Codemigratie | Reviewer/eigenaar |
|---|---|---|---|---|---|
| 2026-07-13 | Initiële vastlegging op basis van `docs/references/P10.pdf` (Holzmann, Power of Ten) en repository-audit | Alle regels (R1–R10) | Geen — documentatie-only, geen tooling of CI gewijzigd | Geen | Projecteigenaar |

Toekomstige wijzigingen aan dit document MOETEN via een nieuwe rij vastgelegd worden, niet door bestaande rijen te overschrijven — de wijzigingsgeschiedenis van de standaard zelf is onderdeel van de controleerbaarheid die dit document nastreeft.

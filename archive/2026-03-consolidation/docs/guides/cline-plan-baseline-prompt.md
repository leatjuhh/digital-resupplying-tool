# Prompt voor Cline (Cursor PLAN-modus) — Baseline Herverdelingsalgoritme

Gebruik onderstaande prompttekst als input voor Cline in PLAN-modus wanneer je een eerste baseline van het herverdelingsalgoritme wilt laten uitdenken. De prompt is opgesteld op basis van de huidige manuele werkwijze en houdt rekening met de applicatiecontext.

---

```
DOEL
- Ontwerp een baseline voor het herverdelingsalgoritme van de Digital Resupplying Tool.
- Zorg dat het algoritme de uitkomsten en afwegingen van het huidige manuele herverdelingsproces zo dicht mogelijk benadert.
- Lever zowel een conceptueel plan (regels, beslisbomen, uitzonderingen) als concrete rekensuggesties waarmee we de baseline kunnen implementeren.

CONTEXT
- Inputdata: de applicatie leest Interfiliaalverdeling-rapportages (PDF) uit en zet deze om naar een gestructureerde database-export. Het algoritme krijgt dus gestructureerde data (voorraadstanden, verkopen, stamgegevens per artikel, winkel, maat, BV, etc.).
- De tool toont de voorgestelde herverdelingen aan de gebruiker, die de voorstellen kan beoordelen (goedkeuren/afkeuren) en van feedback voorzien.
- De feedbackmodule gebruikt de OpenAI API om de regels iteratief te verfijnen; uiteindelijk moet het algoritme autonoom kunnen functioneren.

MANUELE REFERENTIEWERKWIJZE
1. Start altijd met de stamgegevens van het artikel (artikelgroep, type, seizoenskenmerken, prijspunt). Bepaal of het om een categorie gaat met specifieke beleidsregels (bijvoorbeeld (winter)jassen behouden lage aantallen in meer winkels, omdat ze opvallend en prijzig zijn).
2. Kijk vervolgens naar de verkoopaantallen per winkel en bepaal per BV de prioriteit/demand (hoog, medium, laag).
3. Inventariseer de totale voorraad per maat per BV. Herverdelingen tussen verschillende BV's zijn niet toegestaan; optimaliseer binnen elke BV.
4. Streef ernaar zoveel mogelijk winkels een zo compleet mogelijke maatserie te geven, met behoud van gezonde voorraden in goed verkopende winkels.
5. Houd rekening met de cooldown: herverdelen mag pas 2 weken na de initiële levering vanuit het centrale magazijn.

TYPISCHE SITUATIES
- Situatie 1: Ruime voorraad (bijna alle winkels hebben een serie van 3-4 maten, totale voorraad vergelijkbaar met initiële partijgrootte van 40-56 stuks). Doel: aanvullen van ontbrekende maten bij goed verkopende winkels zonder andere winkels leeg te trekken; behoud zoveel mogelijk ononderbroken maatseries in veel winkels.
- Situatie 2: Lage voorraad (totale voorraad < ~20-25 stuks). Doel: bepaal het optimale aantal topprioriteit-winkels door de beschikbare aantallen per maat te inventariseren en te groeperen. Bereken hoeveel winkels kunnen worden bevoorraad met een ononderbroken maatserie van de meest voorkomende middelste maten. Winkels met lage prioriteit worden (bijna) leeggetrokken naar deze topprioriteit-winkels. Voor winkels die net buiten de top vallen maar wel voorraad krijgen, compenseer ontbrekende maten met buitenliggende maten (S/XXL) of dubbele toewijzingen indien aantallen dit toelaten. Voorbeeld: bij 6 winkels met totaal S=3, M=5, L=4, XL=6, XXL=1 → herverdeel naar 5 winkels waarbij prioriteit 1-4 de middelste serie M-L-XL compleet krijgen, en prioriteit 5 compensatie krijgt met S of XXL voor de ontbrekende L.

VRAAG AANPAK
- Stel een plan op dat per situatie beschrijft welke variabelen en KPI's gemonitord worden (bijv. aantal complete maatseries, minimale voorraad per winkel, aantal verplaatsingen, dekking van prioriteitswinkels).
- Geef aan hoe het algoritme omgaat met artikelcategorieën (zoals jassen versus basisartikelen) en andere stamgegevens.
- Beschrijf hoe we prioriteiten per BV en winkel bepalen op basis van verkoopratio's en voorraadniveaus.
- Geef concrete rekenvoorbeelden of pseudocode waar mogelijk (bijv. scoring, sorteren van winkels, toewijzingsregels per maat).
- Benoem aannames en beslisregels die mogelijk tijdens iteraties moeten worden gevalideerd of verfijnd (zoals maximale zendingen per winkel, minimale restvoorraad).
- Stel een iteratief verbeterplan voor: hoe verzamelen we gebruikersfeedback, hoe verwerken we die feedback tot nieuwe regels, en hoe meten we of de baseline verbetert.

DELIVERABLES
- Een gestructureerde lijst met algoritmeregels/criteria.
- Een conceptuele workflow (flowchart-achtige beschrijving) van het besluitvormingsproces.
- Lijst van KPI's en evaluatiecriteria, inclusief prioriteitsvolgorde per situatie.
- Voorstel voor feedbackloop en iteratie-aanpak.

WERKWIJZE PLAN-MODUS
- Vraag om verduidelijking als gegevens of beslisregels ontbreken.
- Werk in iteraties: stel eerst de high-level structuur op, verfijn daarna met details en rekenvoorbeelden.
- Identificeer open vragen en risico's zodat de product owner ze kan adresseren.
```

---

Plaats deze prompt in Cursor, kies PLAN-modus en volg de voorgestelde stappen om samen met Cline de baseline van het herverdelingsalgoritme uit te werken.

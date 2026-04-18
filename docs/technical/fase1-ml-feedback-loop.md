---
title: AI Feedback Loop Architecture
category: technical
tags: [ai, feedback-loop, llm, redistribution, architecture]
last_updated: 2026-04-17
related:
  - ./current-state.md
  - ../../todo/master-backlog.md
  - ../guides/redistribution-algorithm.md
---

# AI Feedback Loop Architecture

Dit document beschrijft de beoogde AI-architectuur voor DRT als aanvullende laag bovenop het bestaande herverdelingsalgoritme.

## Uitgangspunt

DRT gebruikt een bestaand, deterministisch herverdelingsalgoritme dat is opgebouwd vanuit handmatige en praktijkgebaseerde beslissingen. Dat algoritme blijft de vaste basis van het systeem.

De AI-integratie is nadrukkelijk niet bedoeld om:

- het basisalgoritme te vervangen
- zelfstandig herverdelingsvoorstellen te genereren
- realtime runtime-beslissingen te nemen tijdens proposal-generatie

De AI-laag heeft maar een doel: het bestaande algoritme verbeteren op basis van gebruikersfeedback op voorstellen die al door DRT zijn gegenereerd.

## Waarom deze architectuur

Deze keuze bewaakt drie productprincipes:

- De bestaande logica is gebaseerd op bewezen praktijkkennis en moet behouden blijven.
- Operationele beslissingen moeten transparant en reproduceerbaar blijven; een black-box beslisser is daarom onwenselijk.
- Gebruikersfeedback is de meest waardevolle verbeterbron, omdat die direct de realiteit van winkels en artikelgedrag weerspiegelt.

Daarom blijft de gebruiker de eindbeslisser en blijft AI adviserend.

## Doel en niet-doel

### Doel

Gebruik periodieke AI-analyse om patronen te vinden in goedgekeurde, afgewezen en aangepaste voorstellen, en zet die patronen om in concrete verbeterregels voor het bestaande algoritme.

### Niet-doel

- Geen realtime LLM-calls tijdens proposal-generatie
- Geen directe OpenAI-afhankelijkheid in de runtime flow van voorstellen
- Geen automatische toepassing van AI-uitvoer zonder menselijke controle
- Geen productclaim dat AI zelfstandig herverdelingen bepaalt

## Feedback-loop

Elke herverdelingsbeslissing moet later analyseerbaar zijn. Daarvoor hoort DRT per voorstel of move conceptueel de volgende informatie vast te leggen:

- `proposal/move decision log`
  - welke verplaatsing is voorgesteld
  - van welke winkel naar welke winkel
  - maat en aantallen
- `feature snapshot`
  - relevante kenmerken op het moment van de beslissing
  - bijvoorbeeld voorraadniveaus, verkoopratio's, maatdekking en verdelingscontext
- `feedback action type`
  - goedgekeurd
  - afgewezen
  - aangepast
- `user comment / reason`
  - optionele toelichting of reden van de gebruiker

Deze combinatie vormt de basis voor een trainings- en analysedataset.

## Batchmatige AI-analyse

De AI-laag werkt batchmatig, bijvoorbeeld dagelijks of wekelijks.

De analyseflow is:

1. Verzamel gelogde voorstellen, feature snapshots en feedback.
2. Bundel die data tot een analysebatch.
3. Laat een LLM via de OpenAI API patronen herkennen in afwijzingen en edits.
4. Laat de LLM expliciete verbetervoorstellen formuleren voor de algoritmische logica.
5. Beoordeel die voorstellen menselijk voordat ze worden vertaald naar programmeerbare regels.

Belangrijk:

- deze analyse hoort niet thuis in de runtime van proposal-generatie
- de analyse is adviserend en asynchroon
- de bestaande generator moet zonder AI-call kunnen blijven draaien

## Verwachte AI-uitvoer

De output van AI bestaat niet uit nieuwe herverdelingsmoves, maar uit gestructureerde verbetervoorstellen voor het algoritme.

Voorbeelden:

- verhoog prioriteit voor winkels met hoge sell-through en lage voorraad
- verlaag score voor transfers vanuit winkels met beperkte maatdekking
- voeg een extra correctieregel toe voor patronen die vaak handmatig worden aangepast

De AI vervangt de kernberekening dus niet, maar helpt impliciete gebruikersvoorkeuren te vertalen naar expliciete logica.

## Toepassing in DRT

Nieuwe AI-inzichten worden toegepast als correctielaag bovenop het bestaande algoritme.

Dat betekent:

- het basisalgoritme genereert nog steeds de primaire voorstellen
- aanvullende regels kunnen scores of prioriteiten gecontroleerd bijsturen
- wijzigingen worden versioneerd via een `versioned rule set`
- regels moeten controleerbaar en terug te draaien zijn

Zo blijven beslissingen transparant, reproduceerbaar en uitlegbaar.

## Runtime flow

De beoogde operationele flow is:

1. Data ophalen
2. Basisalgoritme genereert herverdelingsvoorstellen
3. Scores berekenen binnen de bestaande logica
4. Geactiveerde correctieregels toepassen
5. Voorstellen tonen in de interface
6. Gebruikersfeedback opslaan
7. Periodieke AI-analyse draaien op verzamelde feedback
8. Nieuwe of aangepaste regels beoordelen, versioneren en gecontroleerd toevoegen

De gebruiker houdt daarbij steeds de controle over goedkeuren, afkeuren en aanpassen.

## Eerste implementatie v0.1

Voor een eerste versie van deze architectuur is het voldoende om:

- alle voorstellen en relevante moves te loggen
- feature snapshots per beslissing op te slaan
- gebruikeracties en toelichting vast te leggen
- de data periodiek via de OpenAI API te analyseren
- een eerste set AI-gegenereerde regels nog handmatig naar code te vertalen

v0.1 introduceert dus nog geen automatische regeltoepassing door de LLM zelf.

## Langere termijn

Op langere termijn kan deze aanpak worden uitgebreid met traditionele machine-learningmodellen, zoals logistic regression of gradient boosting.

In dat scenario:

- blijft de LLM bruikbaar voor interpretatie, samenvatting en uitleg
- leren voorspellende modellen efficiënter patronen uit de opgebouwde feedbackdataset
- blijft DRT architectonisch deterministisch, versieerbaar en controleerbaar

De kern blijft hetzelfde: AI ondersteunt en verfijnt, maar het bestaande algoritme blijft de basis en de gebruiker behoudt de controle.

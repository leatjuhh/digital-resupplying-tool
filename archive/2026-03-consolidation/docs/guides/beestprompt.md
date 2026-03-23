MIJN EERSTE PROMPT IN DIT GESPREK:

Stel me vragen over stukken waar ik onduidelijk ben geweest alsjeblieft. Na het beantwoorden van jouw eventuele vragen wil ik dat we de inhoud voor het DOEL opstellen (door wijzigingen aan te brengen in onderstaande prompt) zodat ik hem als opdracht aan Cline kan geven in PLAN mode.


DOEL: Maak een uitgebreide prompt voor Cline in cursor in PLAN mode:

Bedenk hoe we een nieuwe baseline voor het herverdelings algoritme kunnen bewerkstelligen.
Ik wil dat de manier van beoordelen vergelijkbaar is met de manier van manueel herverdelen. 

Manueel herverdelen is de huidige manier van het werkproces "Herverdeling". Dit vindt nog plaats op pen en papier. Het papier bevat een printversie van de Interfiliaalverdeling rapportages die nu als input PDF gaan gelden voor de Digital Resupplying Tool.


Eerst kijkt men naar de eigenschappen (stamgegevens) van het artikel. Wat voor een artikel is het? O.a. hoofd (artikel)groep uitlezen.
Bijvoorbeeld: Wanneer een (winter)jas wordt herverdeeld, houdt dat in dat in sommige gevallen hij anders herverdeeld moet worden dan artikelen die geen (winter)jas zijn zoals T-shirts, jurken of broeken. (Winter)jassen kunnen volgens het beleid dat tijdens manueel herverdelen gevoerd wordt, vaak beter in méér winkels blijven hangen in lage aantallen in tegenstelling tot andere artikelen. Jassen zijn relatief duur in stuksprijs en vallen op (groot, gewatteerd), dus kunnen altijd manueel besteld worden bij andere winkels buiten het herverdelen om.

Vervolgens kijk ik naar de verkoopaantallen per winkel, waarop ik mijn prioriteit (demand) bepaal per BV.

Daarna kijk ik naar de totale aantallen per maat per BV, wetende dat ik geen herverdelings "transacties" tussen de BV's mag doen. Alle aanwezige BV's moeten onderling een optimale voorraadpositie zien te bereiken.

Dan probeer ik een inschatting te maken hoeveel winkels ik een zo compleet mogelijke serie kan geven.


Bij het bekijken van de voorraad uit de database (gevoed door de Interfiliaalverdeling rapportages PDF) zijn er in principe 2 herkenbare situaties die kunnen voorvallen:

Situatie 1:

Er is nog véél voorraad van een artikel. 

"Je zou kunnen zeggen dat er veel voorraad is op het moment dat (bijna) alle aanwezige winkels in elk geval een maatserie van 3 of 4 breed hebben. Een ander kenmerk is dat je dit kunt aflezen aan het totaal aantal maten van alle winkels bij elkaar. Doorgaans heeft een serie bij initiële levering (vanuit Magazijn) 40-56 stuks. Wanneer er meer dan zoveel items zijn, gaat het vaak om Partij aantallen of artikelen die een hergebruikte code hebben van eerdere jaren."

Pas na een artikel 2 weken in de winkel is (minimale periode na levering vanuit Centraal Magazijn) mag deze herverdeeld worden om er voor te zorgen dat de filialen het artikel zelf kunnen verkopen (cooldown periode).

Wanneer de 2 weken voorbij zijn & het artikel herverdeeld wordt, worden winkels die relatief (tot andere filialen) goed verkocht hebben "beloond" met aanvulling van ontbrekende maten vanuit winkels die relatief minder verkocht hebben.

Het is hierbij de kunst om niet onnodig winkels compleet leeg te halen en daarmee goed (en middelmatig) verkopende winkels dubbel te gaan bevoorraadden. Zo lang er zo veel mogelijk niet-doorbroken maatseries in zo veel mogelijk winkels kunnen blijven, spreek je in deze situatie van een optimale herverdeling.


Situatie 2:

Er is nog weinig voorraad over (ruwweg <20-25 stuks over totaal van alle maten van alle winkels bij elkaar).
Dit is het moment dat we opdrachten geven aan filialen met voorraad die minder dan de top (prioriteit) X aantal winkels om artikelen compleet weg te sturen. Die X aantal winkels wordt bepaald aan de hand van de volgende afweging:

Tel de maten van de BV waar deze winkels onder vallen bij elkaar en maak groepen voor al deze maten.

Bijvoorbeeld, bij deze aantallen, wanneer ik 6 winkels in totaal heb met voorraad:

S	3

M	5

L	4

XL	6

XXL	1

Zou ik een verdeling maken over 5 winkels totaal (en er dus één compleet leeghalen). Omdat ik dan in ieder geval 4 winkels met de 3 middelste maten (van M t/m XL) een onafgebroken serie maten kan geven.
De 5e winkel (laagste prio, minst aantal verkocht) mist in dit geval dan zijn maat L. Die zijn reeds vergeven aan winkels met prioriteit 1 t/m 4. Dit gemis bij prioriteit 5 kan ik compenseren door bijvoorbeeld een buiten-liggende maat (S of XXL) of een andere maat dubbel te geven wanneer de aantallen het toelaten.


----

Vergeet niet: Er is niet één goede oplossing voor een herverdeling, er zijn er veel. Maar er is er altijd maar één de beste! Het doel is om die te vinden door het algoritme te blijven itereren!




HIEROP ANTWOORDDE CODEX:

Ik heb een paar verduidelijkende vragen om ervoor te zorgen dat ik je doelstelling goed begrijp:

Welke inputdata moet Cline precies als uitgangspunt nemen? Bijvoorbeeld: werkt het met ruwe PDF-data, een gestructureerde database-export, of een reeds voorverwerkte dataset?

Hoe wil je dat Cline de huidige manuele regels vertaalt naar een “baseline”-algoritme? Moet het bijvoorbeeld concrete rekenregels/stappen produceren, of volstaat een conceptueel plan met criteria per artikelcategorie (zoals jassen versus andere kleding)?

Zijn er specifieke KPI’s of evaluatiecriteria die je wilt dat het algoritme optimaliseert (bijvoorbeeld minimale lege winkels, maximale complete maatseries, minimale verplaatsingen)?

Verwacht je dat Cline ook rekening houdt met operationele beperkingen zoals maximale aantallen zendingen per winkel of minimale voorraadniveaus die een winkel altijd moet behouden?

Moeten er voorbeelden of historische cases in de prompt komen ter illustratie, of wil je alleen algemene richtlijnen en het beleid verwoord zien?

Laat me weten wat je voorkeuren zijn; daarna kan ik de prompt aanpassen zodat die klaar is voor gebruik in PLAN-modus.


IK QUOTE EN BEANTWOORD DE VRAGEN:

Welke inputdata moet Cline precies als uitgangspunt nemen? Bijvoorbeeld: werkt het met ruwe PDF-data, een gestructureerde database-export, of een reeds voorverwerkte dataset?

Er zijn een aantal functies aanwezig in de applicatie die de PDF-data uitlezen en daar inderdaad een gestructureerde database-export van maken. Het is de bedoeling dat de applicatie de gebruiker toestaat om voorstellen, goed of af te keuren, die gegenereerd worden op basis van die database-export.


Hoe wil je dat Cline de huidige manuele regels vertaalt naar een “baseline”-algoritme? Moet het bijvoorbeeld concrete rekenregels/stappen produceren, of volstaat een conceptueel plan met criteria per artikelcategorie (zoals jassen versus andere kleding)?

Ik denk dat een combinatie van beide opties die je voorstelt toepasselijk zijn. Het idee is dat we nu een baseline opzetten waar we de gebruiker via de UI toestaan commentaar te geven, om iedere keer beter te worden met als uiteindelijke doel om een consistente algoritme te produceren. De feedback module zal in verbinding staan met OpenAI API om iteraties te maken op het herverdelingsalgoritme, zodat dit uiteindelijk autonoom kan werken zonder tussenkomst van OpenAI API.

Zijn er specifieke KPI’s of evaluatiecriteria die je wilt dat het algoritme optimaliseert (bijvoorbeeld minimale lege winkels, maximale complete maatseries, minimale verplaatsingen)? 
Mijn gevoel zegt: Ja die zijn er! Maar op dit moment is het nog te abstract voor mijzelf (als ervaren manueel herverdeel-maker).
Alle voorbeelden die je noemt zijn Absoluut relevant, maar de vraag zit 'm meer in welke evaluatiecriteria meer prioriteit krijgen over andere in welke situatie.

Verwacht je dat Cline ook rekening houdt met operationele beperkingen zoals maximale aantallen zendingen per winkel of minimale voorraadniveaus die een winkel altijd moet behouden?

Ik denk het wel, maar ook dit is iets wat we tijdens het itereren zullen moeten determineren.


Moeten er voorbeelden of historische cases in de prompt komen ter illustratie, of wil je alleen algemene richtlijnen en het beleid verwoord zien?

Als dit iets toe kan voegen en nergens afbreuk doet, ben ik voorstander!
Whatever is needed to reach our goal efficiently & precisely!
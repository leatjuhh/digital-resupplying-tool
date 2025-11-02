# Bug: "Verkocht" kolom telt op i.p.v. bronwaarde te tonen
Datum: 2025-11-02

## Observatie
- Rechts op X-as "Verkocht" loopt op alsof er een optel (+) functie actief is.
- Verwachting: "Verkocht" == exact overgenomen waarde uit bron-PDF extract (per filiaal, per artikel).

## Te verifiëren (zonder aannames)
- [ ] Locatie van extractie van "Verkocht" uit PDF (functie/bestand).
- [ ] Waar en hoe "Verkocht" wordt opgeslagen (model/structuur).
- [ ] Datapad naar UI-tabellen (API-responses/props/state).
- [ ] Bestaan van enige aggregatie of reduce die "Verkocht" wijzigt.
- [ ] Verschil tussen "huidige situatie" vs "voorgesteld" weergave voor "Verkocht".

## Minimale Repro
- [ ] Kies 1 artikel en noteer "Verkocht" per filiaal uit de bron-PDF.
- [ ] Vergelijk met getoonde waardes in de UI (screens/route + screenshot/waarde).
- [ ] Noteer exacte mismatch.

## Definition of Done
- [ ] Gedocumenteerd waar de fout ontstaat (extract, opslag, mapping of UI).
- [ ] Exacte correctie-richting beschreven (zonder te implementeren).
- [ ] Voorbeeld-case toegevoegd met juiste vs onjuiste waarde.
- Bewijs / Links:
  - URLs, bestandslocaties, request/response voorbeelden.

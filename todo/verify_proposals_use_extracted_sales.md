# Verifiëren: voorstellen gebruiken "Verkocht" uit PDF-extract
Datum: 2025-11-02

## Doel
- Bevestigen dat het herverdelingsvoorstel de "Verkocht"-data gebruikt die uit de PDF-extract komt (vereist, cruciaal).

## Te verifiëren
- [ ] Waar haalt de voorstel-generatie "Verkocht" vandaan?
- [ ] Is er een alternatieve bron of tussenstap die waarden wijzigt (normalisatie, cumulatie, moving window)?
- [ ] Wordt dezelfde "Verkocht" waarde gebruikt in:
      - Vergelijkingstab ("huidige" vs "voorgesteld")
      - Goedkeuren/afkeuren scherm
      - Editor (bij inladen van voorstel)
- [ ] Consistentie tussen batchId en proposalId resolutie (geen mismatch).

## Controle-stappen
- [ ] Traceer pipeline: extract → persist → fetch voor proposal-generatie.
- [ ] Inspecteer voorbeeldpayload van voorstel (veldnaam(-namen) die "Verkocht" representeren).
- [ ] Kruiscontrole met PDF-waarden.

## Definition of Done
- [ ] Schriftelijke bevestiging van de bron en ongewijzigde doorvoer van "Verkocht".
- [ ] Indien niet conform: duidelijk probleemkader + voorgestelde correctiepunten (locaties).
- Bewijs / Links:
  - Requests/Responses, bestandslocaties, scherm-URL's.

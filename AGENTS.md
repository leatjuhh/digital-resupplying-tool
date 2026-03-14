# Agent Working Notes

Gebruik deze repository-structuur als vaste ingang voor toekomstige prompts.

## Eerste documenten om te lezen

1. `README.md`
   Projectoverzicht, startcommando's, hoofdmodules en links naar documentatie.
2. `docs/PROJECT_CONTEXT_INDEX.md`
   Snelle kaart van de relevante `.md` bestanden: wat actueel is, wat leidend is en waar specifieke onderwerpen staan.
3. `docs/DOCUMENTATION_GUIDELINES.md`
   Regels voor waar nieuwe documentatie hoort en welke naamgeving gebruikt moet worden.

## Documenthiërarchie

- `README.md`
  Gebruik als algemene entry point.
- `docs/getting-started/`
  Gebruik voor setup, opstarten en troubleshooting.
- `docs/guides/`
  Gebruik voor functionele workflows en feature-uitleg.
- `docs/technical/`
  Gebruik voor architectuur, analyses en technische beslissingen.
- `docs/sessions/`
  Gebruik voor tijdgebonden sessielogs.
- `todo/`
  Gebruik voor open werk, losse analyses en prompt-handoffs; informatief maar niet automatisch leidend.
- `archive/`
  Alleen als historische referentie gebruiken; niet als primaire bron als dezelfde informatie ook in `docs/` of `README.md` staat.
- `frontend/PROJECT-OVERVIEW.md`
  Brede productschets en UX/functionele scope; nuttig voor intentie en gewenste eindtoestand.
- `backend/README.md`
  Backend-start en API-basis; controleer tegen actuele code als implementatiedetails belangrijk zijn.

## Werkwijze voor toekomstige prompts

- Begin bij `README.md` en `docs/PROJECT_CONTEXT_INDEX.md`.
- Geef voorrang aan bestanden in `docs/` boven `archive/` en oude handoff-notities.
- Behandel `todo/NEW_CHAT_PROMPT.md` en vergelijkbare bestanden als tijdsgebonden context, niet als blijvende waarheid.
- Als je nieuwe projectkennis toevoegt, werk dan bij voorkeur een bestaand document bij en houd je aan `docs/DOCUMENTATION_GUIDELINES.md`.

# Agent Working Notes

Gebruik deze repository-structuur als vaste ingang voor toekomstige prompts.

## Engineeringstandaard (verplicht)

Elke agent (Codex, GPT, Claude, Cline of anderen) MOET vóór het doorvoeren van code- of configuratiewijzigingen `docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md` lezen en toepassen. Dat document is de canonieke, projectspecifieke vertaling van P10 ("The Power of Ten — Rules for Developing Safety Critical Code", Holzmann/NASA-JPL; bron: `docs/references/P10.pdf`).

Documenthiërarchie bij conflict:

1. `docs/references/P10.pdf` — oorspronkelijke bron.
2. `docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md` — canonieke projectstandaard; bij conflict met elk ander document altijd leidend.
3. Dit bestand (`AGENTS.md`), `CLAUDE.md`, `CHATGPT_PROJECT_INSTRUCTIONS.md`, `.clinerules` — tool-adapters; zij voegen geen eigen afwijkende regels toe.
4. Taak- of sessiedocumenten (ingevulde `docs/sessions/*.md`, PR-beschrijvingen e.d.) — definiëren nooit eigen regels.

Zie ook: `docs/engineering/PRODUCTION_READINESS_AUDIT.md` (bevindingen met bewijs) en `docs/engineering/PRODUCTION_READINESS_PLAN.md` (gefaseerd verbeterplan).

## Niet-onderhandelbare beslisregels

- Onderzoek vóór wijzigen; maak geen aannames die uit code/tests/config verifieerbaar zijn.
- Repareer de oorzaak, niet alleen het symptoom.
- Houd wijzigingen klein en logisch afgebakend; voeg of wijzig tests bij gedragswijzigingen.
- Stel expliciete grenzen in voor lussen, retries, batches, uploads en resourcegebruik.
- Valideer alle data bij systeemgrenzen; controleer fouten en retourwaarden van bestanden, databases, processen en API's.
- Gebruik transacties of compensatiegedrag bij meervoudige datamutaties.
- Negeer geen warnings; geen brede suppressions/ignore-regels zonder lokale motivatie.
- Schakel tests, securitycontroles of typechecks NOOIT uit om een groene pipeline te krijgen; verwijder of verzwak geen quality gates.
- Behoud backward compatibility tenzij een gecontroleerde migratie is ontworpen.
- Stop bij mogelijk verlies van productiegegevens of secrets; lees/toon/commit geen secrets.
- Rapporteer onzekerheid expliciet; documenteer iedere bewuste uitzondering (proces: hoofdstuk 15 van `docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md`).
- Rond een taak pas af na passende verificatie (relevante tests/checks draaien en resultaat rapporteren).

## Eerste documenten om te lezen

1. `README.md`
   Projectoverzicht, leidende kernflow en startcommando's.
2. `docs/technical/current-state.md`
   Enige actuele status- en roadmapbron tijdens de consolidatie.
3. `todo/master-backlog.md`
   Enige actieve backlog met prioriteiten, afhankelijkheden en acceptatiecriteria.

Lees `docs/PROJECT_CONTEXT_INDEX.md` alleen als routekaart naar aanvullende of historische documentatie.

## Documenthiërarchie

- `README.md`
  Algemene entry point.
- `docs/technical/current-state.md`
  Leidende actuele status.
- `todo/master-backlog.md`
  Leidende werkbacklog.
- `docs/getting-started/`
  Setup, opstarten en troubleshooting.
- `docs/guides/`
  Functionele workflows en feature-uitleg.
- `docs/technical/`
  Technische achtergrond die niet leidend is voor planning tenzij expliciet genoemd.
- `docs/engineering/`
  Engineeringstandaard, audit en verbeterplan; leidend voor hoe-/kwaliteitsvragen (zie hierboven).
- `docs/sessions/`
  Tijdgebonden sessielogs; historisch.
- `archive/`
  Historische referentie; niet als primaire bron gebruiken als dezelfde informatie actueel elders bestaat.
- `frontend/PROJECT-OVERVIEW.md`
  Productschets en intentie, niet de actuele statusbron.
- `backend/README.md`
  Backend-start en basis-API-info; controleer tegen actuele code.

## Commando's

- Dev-start: `.\dev.ps1` of `npm run dev` (Windows; backend uvicorn op :8000, frontend next op :3000)
- Backend tests: `cd backend` + `<venv>\Scripts\python.exe -m pytest <testbestand> -v` (pytest staat nog niet in `requirements.txt` — bekend hiaat, zie audit)
- Frontend build/lint: `cd frontend && npm run build` / `npm run lint` (ESLint-config ontbreekt nog en `next.config.mjs` negeert TS-fouten — bekende hiaten, zie audit; verzwijg dit niet)
- Typecheck frontend: `cd frontend && npx tsc --noEmit`
- E2E smoke: `npm run browser:smoke` (vereist draaiende app + geseede database)

## Werkwijze voor toekomstige prompts

- Begin bij `README.md`, `docs/technical/current-state.md` en `todo/master-backlog.md`.
- Lees en pas `docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md` toe vóór wijzigingen.
- Geef voorrang aan actuele code boven documentatie.
- Gebruik `docs/PROJECT_CONTEXT_INDEX.md` om aanvullende of historische bestanden bewust op te zoeken, niet als primaire statusbron.
- Behandel `archive/` en sessielogs als historische context.
- Werk bij nieuwe projectkennis bij voorkeur een bestaand leidend document bij.

## Rapportage bij afronding

Rapporteer bij het einde van een sessie of overdracht volgens het sjabloon in `docs/engineering/AI_SESSION_HANDOFF.md`: wat is gewijzigd, wat is getest en wat blijft onzeker.

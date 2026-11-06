# Filiaalnummering-migratie 2026

## Reden

Op 5 november 2026 heeft MC Company (Lumitex B.V.) een deel van de filiaalnummers gewijzigd in de centrale bedrijfssoftware (EasyVORAS/EasyPOS). Zelfontwikkelde projecten die filiaalnummers hardcoded hadden, moesten hierop worden aangepast zonder functionaliteit te verliezen.

## Oude en nieuwe nummering

| Oud | Nieuw | Winkel |
|---|---|---|
| 14 | 42 | Outlet Weert |
| 15 | 43 | Outlet Sittard |
| 16 | 44 | Outlet Roermond |
| 17 | 45 | Outlet Tilburg |
| 31 | **14** | Tilburg regulier |
| 38 | **15** | Tegelen regulier |
| 27 | 98 | Klachten Magazijn Lumitex |
| 39 | 39 | Outlet Blerick (ongewijzigd) |

**Kernrisico:** 14 en 15 zijn hergebruikt — vóór de wissel waren dit outlets (Weert/Sittard), erna zijn het reguliere winkels (Tilburg/Tegelen). Een filiaalnummer "14" of "15" zonder datumcontext is dus ambigu.

Actuele volledige lijst reguliere winkels: 05 Panningen, 06 Echt, 08 Weert, 09 Stein, 11 Brunssum, 12 Kerkrade, 13 Budel, 14 Tilburg, 15 Tegelen. Outlets: 39 Blerick, 42 Weert, 43 Sittard, 44 Roermond, 45 Tilburg. Overig: 98 Klachten Magazijn.

## Architectuurbeslissing: datumbewuste configuratie i.p.v. statische mapping

DRT bewaart per batch een eigen `filiaal_code`/`filiaal_naam`-snapshot (string, geen centrale stores-tabel, geen foreign key). Er is dus geen eenmalige SQL-migratie van bestaande records nodig — het risico zit volledig in de **code-configuratie** die filiaalnummers aan betekenis koppelt (herverdeelbaarheid, capaciteit, BV-toewijzing).

Omdat niet zeker is of een batch van vóór 5 november 2026 ooit opnieuw door het algoritme wordt gehaald, is gekozen voor een datumbewuste resolver in plaats van een simpele key-rename:

- `backend/redistribution/store_config.py` — `NON_REDISTRIBUTION_STORES` (geldig vanaf `MIGRATION_DATE = 2026-11-05`) en `NON_REDISTRIBUTION_STORES_PRE_MIGRATION` (geldig vóór die datum). `is_redistribution_candidate(store_code, as_of=...)` kiest de juiste set op basis van `as_of` (standaard: vandaag).
- `backend/redistribution/store_profiles.py` — zelfde patroon met `_DEFAULT_PROFILES`/`_PRE_MIGRATION_PROFILES`.
- `backend/redistribution/data_loading.py` — geeft `batch.created_at.date()` door aan beide functies, zodat nieuwe batches automatisch de nieuwe configuratie gebruiken en een eventuele herberekening van een oude batch automatisch de destijds geldige configuratie gebruikt.

Dit bouwt voort op het bestaande dependency-injection-patroon (`profiles`/`bv_config` als optionele parameters) en is een niet-brekende toevoeging: geen bestaande aanroep hoeft te wijzigen om het oude gedrag te behouden.

**Bij een volgende filiaalwissel:** voeg een nieuwe `_PRE_...`-set toe (de huidige wordt de nieuwe "pre"-set) in plaats van de bestaande te overschrijven, zodat alle eerdere migraties historisch herberekenbaar blijven.

## Gewijzigde onderdelen

| Project | Bestand | Wijziging |
|---|---|---|
| DRT | `backend/redistribution/store_config.py` | `NON_REDISTRIBUTION_STORES` → outlets 42-45 + Klachten 98; datumbewuste `is_redistribution_candidate` |
| DRT | `backend/redistribution/store_profiles.py` | Profielen 31/38 → 14/15; datumbewuste `get_store_profile`/`get_all_profiles` |
| DRT | `backend/redistribution/data_loading.py` | Batchdatum doorgegeven aan bovenstaande functies |
| DRT | `bv_mapping.json` (root + `backend/`) | `store_to_bv` keys 31/38 → 14/15 |
| DRT | `frontend/lib/stores.ts` | `STORE_LIST` codes 31/38 → 14/15 |
| DRT | `backend/redistribution/test_store_config_migration.py` (nieuw) | Regressietests pre-/post-migratie |
| DRT | `AGENTS.md` | Nieuwe sectie "Filiaalconfiguratie" voor toekomstige AI-agents |
| OCRManualHerver | `interfiliaal_parser.py` | `ACTIVE_DESTINATION_FILIALS` → 14/15 i.p.v. 31/38; `VALID_FILIALEN` uitgebreid met 42-45/98 (niets verwijderd, historische codes blijven geldig); TODO's bij OCR-cijferdisambiguatie voor het nieuwe 14/15/45-verwarrisico; testfixtures bijgewerkt |
| Ingevoerd Excel splitsen voor winkels | `split_herverdeling.py` | `STORE_NAMES` 31/38 → 14/15; `OUTLET_DESTINATION_NAMES` 14/15/16/17 → 42/43/44/45; testsuite bijgewerkt + nieuw testgeval |
| Outlet retouropdrachten | `settings.py`, `analyse_xlsx.py` | `FILIAAL_NAMEN` en `TARGET_STORE_CODES` (laatste niet eerder gevonden in de analysefase) bijgewerkt |
| Afprijslijst_automatiseren | `afprijslijst_distributie/config.yaml` | `target_stores` 31/38 → 14/15 |
| Top40_Winkels | `settings.py` | `FILIALEN`-dict keys 31/38 → 14/15; `top40_pdf_parser.py` was al nummer-agnostisch |
| Z:\Herverdeellijsten\Macro\Python_scriptv2 | `process_doorgestuurd_outlook.py` | `EXPECTED_STORES`-labels 31/38 → 14/15 (rapportage-only, geen routeringsfunctie) |
| `.codex/CLAUDE.md` | — | Filiaalcodes-sectie vervangen door actuele structuur + waarschuwing over hergebruik 14/15 |

**Bewust niet aangepast / apart getraceerd:**
- `DRT/DRT/` — bevestigde verweesde/stale kloon van dezelfde repo (branch `main` @ april 2026 vs. actieve `feature/week-inventory-scanner` @ oktober 2026); niet aangeraakt.
- `schema.org optimalisatie` (WordPress `mc-schema`-plugin, publieke winkelpagina's) en de "Shop the look"-pagina — apart ingepland door Alain, Todoist-taak met deadline 16-11-2026.
- `OCRManualHerver`'s OCR-cijferherkenning (digit-disambiguatie) is getuned op de oude 31/38-verwarring; dit vereist een gerichte retuning met echte handgeschreven voorbeelddocumenten met "14"/"15"/"45" — gemarkeerd met TODO-comments, niet blind herschreven zonder testdata.
- `DRT/backend/compare_extraction.py`, `DRT/backend/test_bundle_planner.py` — testfixtures met oude codes (P3, dev-only, geen productie-impact); niet gewijzigd.

## Uitgevoerde tests

- **DRT backend:** volledige testsuite gedraaid vóór en na de wijziging (baseline-vergelijking via `git stash`). Resultaat beide keren identiek: 8 voorbestaande, omgevingsgerelateerde failures (ontbrekende `requests`-module, ontbrekende seed-data voor auth-tests) — **geen regressie**. Nieuwe migratietests: 8/8 geslaagd.
- **OCRManualHerver:** `test_interfiliaal_parser.py` — 2 tests die het oude gedrag verwachtten zijn bijgewerkt; resultaat 15 passed, 3 skipped (ongerelateerd).
- **Excel Splitter:** `test_split_herverdeling.py` — 14 passed, 1 bewust "gefaalde" test: een golden-file regressietest tegen een echt archiefbestand van vóór de wissel (code "38") geeft nu terecht een `ValueError` in plaats van stil verkeerd resultaat. Dit is gewenst fail-safe gedrag voor archiefdata, geen bug — toegelicht in de test zelf.
- **Afprijslijst_automatiseren:** volledige testsuite — 55 passed, 0 failed.
- **Top40_Winkels, Outlet retouropdrachten, Python_scriptv2:** geen geautomatiseerde tests aanwezig; wijzigingen handmatig geverifieerd door leescontrole van alle aanroepplekken.

## Bekende beperkingen

1. **OCR-nauwkeurigheid (OCRManualHerver):** de cijferdisambiguatie-heuristiek is specifiek getuned op 31/38; het nieuwe verwarrisico van 14/15/45 (1↔4, 1↔5, 1↔7) is gemarkeerd met TODO's maar niet getest tegen echte handgeschreven documenten — dit vereist een testset die nog niet beschikbaar was tijdens deze migratie.
2. **`DRT/DRT/`** blijft een onopgehelderde verweesde kloon; aanbevolen om dit apart met Alain af te handelen (behouden, archiveren of verwijderen).
3. **schema.org/mc-schema en "Shop the look"** vallen buiten deze migratieronde; gepland voor week van 9-16 november 2026.
4. **Outletcode 45 (Outlet Tilburg)** is voor het eerst toegevoegd aan `NON_REDISTRIBUTION_STORES` — de oude code 17 stond daar niet in (mogelijk was deze outlet niet eerder in DRT-scope). Als blijkt dat Outlet Tilburg toch niet in DRT gebruikt wordt, heeft dit geen effect (code komt dan nooit voor in data).
5. Geen van de aangepaste projecten behalve DRT en Afprijslijst_automatiseren heeft een git-historie; wijzigingen daar staan alleen als bestandswijziging op schijf, niet in een commit.

## Status

Fase 1-5 (analyse, plan, implementatie, tests) afgerond voor alle in-scope projecten behalve het apart ingeplande schema.org-traject. Zie `Filwissel_gevolgen/analyse-migratieplan-filiaalnummering-2026.md` voor het volledige analyserapport en de besluitvorming per openstaand punt (§8).

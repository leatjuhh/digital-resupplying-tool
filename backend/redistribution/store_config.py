"""
Configuratie voor niet-herverdeelbare filialen.

Filialen in deze lijst worden volledig uitgesloten als bron én bestemming
in het herverdelingsalgoritme. Voorraad op deze filialen telt niet mee
als herverdeelbaar, ongeacht de hoeveelheid of verkoopcijfers.

Categorieën:
  - Administratieve filialen: artikelen zijn onderweg (magazijn/retour/klacht)
    en zijn om administratieve redenen niet beschikbaar voor herverdeling.
  - Outletfilialen: voeren andere collecties dan reguliere winkels;
    kruislingse herverdeling is incorrect.
  - Gesloten filialen: geen actieve verkoopfunctie meer.

Filiaalwissel 5 november 2026 (MC Company): filiaalnummers 31 (Tilburg) en
38 (Tegelen) zijn vervallen; die winkels heten nu 14 en 15. Die codes waren
vóór de wissel in gebruik door Outlet Weert/Sittard (nu 42/43). Zie
docs/filiaalnummering-migratie-2026.md. Omdat batches hun eigen
filiaal_code/filiaal_naam-snapshot bewaren (geen centrale stores-tabel),
gebruikt `is_redistribution_candidate` de datum van de batch om te bepalen
welke set van toepassing is — nieuwe batches krijgen automatisch de huidige
set; een eventuele herberekening van een batch van vóór de wissel gebruikt
de toen geldige set.
"""

from datetime import date

# Datum waarop de nieuwe filiaalnummering actief werd in EasyVORAS/EasyPOS.
MIGRATION_DATE: date = date(2026, 11, 5)

# Geldig vanaf MIGRATION_DATE.
NON_REDISTRIBUTION_STORES: frozenset[str] = frozenset({
    "0",   # Centraal M    — centraal beheer / magazijn
    "2",   # Lumitex       — hoofdkantoor
    "3",   # Mag Part.     — magazijn particulier
    "35",  # Etten-Leur    — gesloten filiaal
    "39",  # OL Blerick    — outlet (ongewijzigd)
    "42",  # OL Weert      — outlet (was 14)
    "43",  # OL Sittard    — outlet (was 15)
    "44",  # OL Roermond   — outlet (was 16)
    "45",  # OL Tilburg    — outlet (nieuw in deze lijst, was niet eerder uitgesloten als 17)
    "98",  # Klachten      — klachtenafhandeling / retourverwerking (was 27)
    "99",  # Verschil      — administratief verschilsaldo
})

# Geldig t/m MIGRATION_DATE (exclusief) — voor herberekening van oude batches.
NON_REDISTRIBUTION_STORES_PRE_MIGRATION: frozenset[str] = frozenset({
    "0",   # Centraal M    — centraal beheer / magazijn
    "2",   # Lumitex       — hoofdkantoor
    "3",   # Mag Part.     — magazijn particulier
    "14",  # OL Weert      — outlet (nu 42; nu Tilburg regulier)
    "15",  # OL Sittard    — outlet (nu 43; nu Tegelen regulier)
    "16",  # OL Roermon    — outlet (nu 44)
    "27",  # Klachten      — klachtenafhandeling / retourverwerking (nu 98)
    "35",  # Etten-Leur    — gesloten filiaal
    "39",  # OL Blerick    — outlet
    "99",  # Verschil      — administratief verschilsaldo
})


def is_redistribution_candidate(store_code: str, as_of: date | None = None) -> bool:
    """Geeft True als dit filiaal kan deelnemen aan herverdeling.

    `as_of` is de datum waarop dit filiaalnummer geldig was/is (doorgaans de
    batchdatum). Standaard (None) wordt vandaag gebruikt, wat voor nieuwe
    batches altijd de juiste (nieuwe) set oplevert.
    """
    reference_date = as_of if as_of is not None else date.today()
    stores = (
        NON_REDISTRIBUTION_STORES
        if reference_date >= MIGRATION_DATE
        else NON_REDISTRIBUTION_STORES_PRE_MIGRATION
    )
    return store_code not in stores

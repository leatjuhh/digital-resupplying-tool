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
"""

NON_REDISTRIBUTION_STORES: frozenset[str] = frozenset({
    "0",   # Centraal M    — centraal beheer / magazijn
    "2",   # Lumitex       — hoofdkantoor
    "3",   # Mag Part.     — magazijn particulier
    "14",  # OL Weert      — outlet
    "15",  # OL Sittard    — outlet
    "16",  # OL Roermon    — outlet
    "27",  # Klachten      — klachtenafhandeling / retourverwerking
    "35",  # Etten-Leur    — gesloten filiaal
    "39",  # OL Blerick    — outlet
    "99",  # Verschil      — administratief verschilsaldo
})


def is_redistribution_candidate(store_code: str) -> bool:
    """Geeft True als dit filiaal kan deelnemen aan herverdeling."""
    return store_code not in NON_REDISTRIBUTION_STORES

"""
Store-niveau configuratie voor het herverdelingsalgoritme.
Vaste eigenschappen per filiaal: vloeroppervlak en maximale capaciteitsschatting.

Pas max_capacity aan op basis van werkelijke tellingen in je batches.
floor_area_m2 is documentatief; max_capacity stuurt de algoritme-scoring.
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class StoreProfile:
    """Vaste eigenschappen van een filiaal"""
    store_code: str
    floor_area_m2: int   # Verkoopvloer m² (documentatief)
    max_capacity: int    # Schatting max stuks totaalvoorraad in DRT-context


# MC Company standaard profielen
# max_capacity = ruwe schatting van "vol" in DRT-batchcontext.
# Valideer en pas aan op basis van typische batchgroottes per winkel.
_DEFAULT_PROFILES: Dict[str, StoreProfile] = {
    "6":  StoreProfile("6",  floor_area_m2=120, max_capacity=240),
    "8":  StoreProfile("8",  floor_area_m2=150, max_capacity=300),
    "9":  StoreProfile("9",  floor_area_m2=100, max_capacity=200),
    "11": StoreProfile("11", floor_area_m2=80,  max_capacity=160),
    "12": StoreProfile("12", floor_area_m2=90,  max_capacity=180),
    "13": StoreProfile("13", floor_area_m2=70,  max_capacity=140),
    "31": StoreProfile("31", floor_area_m2=200, max_capacity=400),
    "38": StoreProfile("38", floor_area_m2=110, max_capacity=220),
}

# `_DEFAULT_PROFILES` is de read-only standaardconfiguratie. De vorige
# muteerbare module-global (`_active_profiles`) plus setter is verwijderd
# (Fase 3.3, PR-020): afwijkende profielen worden nu expliciet meegegeven via de
# `profiles`-parameter (dependency injection) i.p.v. gedeelde state te muteren.


def get_store_profile(
    store_code: str, profiles: Optional[Dict[str, StoreProfile]] = None
) -> Optional[StoreProfile]:
    """Geef het profiel van een winkel; gebruikt de standaardprofielen tenzij een
    expliciete `profiles`-map wordt meegegeven."""
    return (profiles if profiles is not None else _DEFAULT_PROFILES).get(store_code)


def get_all_profiles(
    profiles: Optional[Dict[str, StoreProfile]] = None
) -> Dict[str, StoreProfile]:
    """Geef een kopie van de (standaard- of meegegeven) winkelprofielen."""
    return dict(profiles if profiles is not None else _DEFAULT_PROFILES)

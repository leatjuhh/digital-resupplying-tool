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

_active_profiles: Dict[str, StoreProfile] = dict(_DEFAULT_PROFILES)


def get_store_profile(store_code: str) -> Optional[StoreProfile]:
    return _active_profiles.get(store_code)


def get_all_profiles() -> Dict[str, StoreProfile]:
    return dict(_active_profiles)


def set_store_profiles(profiles: Dict[str, StoreProfile]) -> None:
    """Overschrijf actieve profielen — bruikbaar voor tests of runtime config."""
    global _active_profiles
    _active_profiles = profiles

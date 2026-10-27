"""Gedeelde maatreeks-helper voor het herverdelingsalgoritme (Fase 3, PR-022).

`_series_width` wordt gebruikt door zowel de legacy per-maat-planner als de
bundle-planner en staat daarom los, zodat beide er zonder onderlinge
afhankelijkheid gebruik van kunnen maken.
"""
from typing import Dict, List


def _series_width(inventory: Dict[str, int], all_sizes: List[str]) -> int:
    """Bereken breedte van de langste aaneengesloten maatreeks met voorraad."""
    best = 0
    current = 0
    for size in all_sizes:
        if inventory.get(size, 0) > 0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best

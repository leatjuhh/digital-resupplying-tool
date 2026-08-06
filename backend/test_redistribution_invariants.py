"""Property-based invariant-tests voor de kern van het herverdelingsalgoritme.

Vangnet vóór de architectuur-refactors in Fase 3 (o.a. singletons -> dependency
injection). Voert `generate_moves_for_article` uit over veel deterministisch
gegenereerde scenario's en controleert de invarianten uit hoofdstuk 10 van
`docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md`:

- (a) Min-3-regel: elke winkel eindigt op 0 of >= min_items_per_receiver, met
      als enige uitzondering de consolidatie van een totale pool < min naar één
      winkel (die dan < min mag houden).
- (c) Voorraadbehoud: som vóór == som ná (geen units verzonnen of verloren).
- (d) Geen negatieve voorraden na toepassing van de moves.
- (e) Geldige winkels: moves verwijzen alleen naar bestaande winkels.

Belangrijk (methodische keuze): deze tests draaien met
`enforce_bv_separation=False`. De BV-scheiding (invariant (b)) wordt niet hier
getest maar in `test_bundle_planner.py`, met échte, consistente winkelcodes.
Reden: `enforce_bv_separation=True` gate't moves via `validate_bv_move`, dat de
BV-groep uit de *configuratie* afleidt op basis van winkel-CODE. Synthetische,
willekeurig toegewezen `bv_name`-waarden zouden dan tegenstrijdig zijn met die
configuratie en een onrepresentatieve wereld testen. Met `enforce=False` wordt
de pure bundle-planner-logica getest, config-onafhankelijk — precies het gedrag
dat een refactor niet mag breken.

Geen database nodig — alles in-memory. Run vanuit backend/:
    python -m pytest test_redistribution_invariants.py -v
"""
from __future__ import annotations

import random
from typing import Dict, List, Tuple

import pytest

from redistribution.algorithm import generate_moves_for_article
from redistribution.constraints import RedistributionParams
from redistribution.domain import ArticleStock, SizeType, StoreInventory

SIZES = ["S", "M", "L", "XL"]
SEEDS = list(range(120))
PARAMS = RedistributionParams(enforce_bv_separation=False)
MIN_QTY = PARAMS.min_items_per_receiver


def _build_scenario(seed: int) -> Tuple[ArticleStock, Dict[str, Dict[str, int]]]:
    """Bouw een deterministisch, willekeurig artikel-scenario voor een seed."""
    rng = random.Random(seed)
    n_stores = rng.randint(2, 7)
    stores: List[StoreInventory] = []
    for i in range(n_stores):
        inventory = {sz: rng.randint(0, 4) for sz in SIZES if rng.random() < 0.6}
        store = StoreInventory(
            store_code=str(i),
            store_name=f"Store{i}",
            bv_name="BV_ALL",  # één groep; niet relevant bij enforce=False
            inventory=inventory,
            sales={"TOTAL": rng.randint(0, 9)} if rng.random() < 0.7 else {},
        )
        store.calculate_metrics(
            batch_total=sum(inventory.values()),
            store_total=rng.randint(100, 700),
        )
        stores.append(store)

    article = ArticleStock(volgnummer="INV", omschrijving="Invariant", batch_id=1)
    article.all_sizes = list(SIZES)
    article.size_type = SizeType.LETTER
    for store in stores:
        article.stores[store.store_code] = store
    article.calculate_aggregates()

    working = {
        code: {sz: store.inventory.get(sz, 0) for sz in SIZES}
        for code, store in article.stores.items()
    }
    return article, working


def _total(working: Dict[str, Dict[str, int]]) -> int:
    return sum(sum(inv.values()) for inv in working.values())


def _store_totals(working: Dict[str, Dict[str, int]]) -> Dict[str, int]:
    return {code: sum(v for v in inv.values() if v > 0) for code, inv in working.items()}


@pytest.mark.parametrize("seed", SEEDS)
def test_inventory_is_conserved(seed: int):
    """(c) De totale voorraad blijft gelijk vóór en ná herverdeling."""
    article, working = _build_scenario(seed)
    before = _total(working)
    generate_moves_for_article(article, PARAMS, working)
    assert before == _total(working), f"seed={seed}: {before} -> {_total(working)}"


@pytest.mark.parametrize("seed", SEEDS)
def test_no_negative_inventory(seed: int):
    """(d) Geen enkele winkel/maat-combinatie eindigt negatief."""
    article, working = _build_scenario(seed)
    generate_moves_for_article(article, PARAMS, working)
    negatives = [
        (code, sz, v)
        for code, inv in working.items()
        for sz, v in inv.items()
        if v < 0
    ]
    assert not negatives, f"seed={seed}: negatieve voorraad {negatives}"


@pytest.mark.parametrize("seed", SEEDS)
def test_min_3_rule_holds(seed: int):
    """(a) Elke winkel eindigt op 0 of >= min, behalve de under-min consolidatie
    (één overgebleven winkel wanneer de totale pool < min is)."""
    article, working = _build_scenario(seed)
    generate_moves_for_article(article, PARAMS, working)
    totals = _store_totals(working)
    non_zero = [t for t in totals.values() if t > 0]
    # Uitzondering: als slechts één winkel niet-leeg is, mag die < min houden
    # (volledige consolidatie van een pool < min).
    if len(non_zero) > 1:
        offenders = {c: t for c, t in totals.items() if 0 < t < MIN_QTY}
        assert not offenders, (
            f"seed={seed}: winkel(s) eindigen op 1..{MIN_QTY - 1} naast andere "
            f"niet-lege winkels: {offenders} (alle totalen: {totals})"
        )


@pytest.mark.parametrize("seed", SEEDS)
def test_moves_reference_existing_stores(seed: int):
    """(e) Elke move verwijst naar winkels die in het artikel bestaan."""
    article, working = _build_scenario(seed)
    moves, _ = generate_moves_for_article(article, PARAMS, working)
    for move in moves:
        assert move.from_store in article.stores, f"seed={seed}: onbekende bron {move.from_store}"
        assert move.to_store in article.stores, f"seed={seed}: onbekende bestemming {move.to_store}"

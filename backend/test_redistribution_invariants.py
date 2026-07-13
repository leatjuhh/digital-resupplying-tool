"""Property-based invariant-tests voor de kern van het herverdelingsalgoritme.

Vangnet vóór de architectuur-refactors in Fase 3 (o.a. singletons -> dependency
injection). Voert `generate_moves_for_article` uit over veel deterministisch
gegenereerde scenario's en controleert de invarianten uit hoofdstuk 10 van
`docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md`:

- (c) Voorraadbehoud: som vóór == som ná (geen units verzonnen of verloren).
- (d) Geen negatieve voorraden na toepassing van de moves.
- (b) BV-groepsscheiding: bij enforce_bv_separation geen cross-BV moves.
- (e) Geldige winkels: moves verwijzen alleen naar bestaande winkels.

Let op: de min-3-regel (a) wordt hier bewust NIET als universele property
geassert — verkennende runs tonen een kleine edge-case (~1% van willekeurige
scenario's) waarin een winkel op 1-2 stuks eindigt terwijl zijn BV meerdere
niet-lege winkels heeft. Dat is een bestaand, apart te onderzoeken punt in de
algoritmelogica; de scenario-gebaseerde min-3-tests staan in
`test_bundle_planner.py`. Dit vangnet legt het huidige, correcte gedrag van de
overige invarianten vast zodat een refactor ze niet ongemerkt breekt.

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
BV_GROUPS = ["BV_A", "BV_B"]
SEEDS = list(range(80))


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
            bv_name=rng.choice(BV_GROUPS),
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


@pytest.mark.parametrize("enforce_bv", [True, False])
@pytest.mark.parametrize("seed", SEEDS)
def test_inventory_is_conserved(seed: int, enforce_bv: bool):
    """(c) De totale voorraad blijft gelijk vóór en ná herverdeling."""
    article, working = _build_scenario(seed)
    before = _total(working)
    generate_moves_for_article(
        article, RedistributionParams(enforce_bv_separation=enforce_bv), working
    )
    after = _total(working)
    assert before == after, f"seed={seed} enforce={enforce_bv}: {before} -> {after}"


@pytest.mark.parametrize("enforce_bv", [True, False])
@pytest.mark.parametrize("seed", SEEDS)
def test_no_negative_inventory(seed: int, enforce_bv: bool):
    """(d) Geen enkele winkel/maat-combinatie eindigt negatief."""
    article, working = _build_scenario(seed)
    generate_moves_for_article(
        article, RedistributionParams(enforce_bv_separation=enforce_bv), working
    )
    negatives = [
        (code, sz, v)
        for code, inv in working.items()
        for sz, v in inv.items()
        if v < 0
    ]
    assert not negatives, f"seed={seed} enforce={enforce_bv}: negatieve voorraad {negatives}"


@pytest.mark.parametrize("seed", SEEDS)
def test_no_cross_bv_moves_when_enforced(seed: int):
    """(b) Met enforce_bv_separation=True zijn er geen cross-BV moves."""
    article, working = _build_scenario(seed)
    moves, _ = generate_moves_for_article(
        article, RedistributionParams(enforce_bv_separation=True), working
    )
    for move in moves:
        from_bv = article.stores[move.from_store].bv_name
        to_bv = article.stores[move.to_store].bv_name
        assert from_bv == to_bv, (
            f"seed={seed}: cross-BV move {move.from_store}({from_bv}) -> "
            f"{move.to_store}({to_bv})"
        )


@pytest.mark.parametrize("enforce_bv", [True, False])
@pytest.mark.parametrize("seed", SEEDS)
def test_moves_reference_existing_stores(seed: int, enforce_bv: bool):
    """(e) Elke move verwijst naar winkels die in het artikel bestaan."""
    article, working = _build_scenario(seed)
    moves, _ = generate_moves_for_article(
        article, RedistributionParams(enforce_bv_separation=enforce_bv), working
    )
    for move in moves:
        assert move.from_store in article.stores, f"seed={seed}: onbekende bron {move.from_store}"
        assert move.to_store in article.stores, f"seed={seed}: onbekende bestemming {move.to_store}"

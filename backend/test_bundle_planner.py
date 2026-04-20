"""
Unit-tests voor de artikel-level bundle-planner (harde min-3 regel).

Geen database nodig — bouwt ArticleStock en StoreInventory in-memory.
Run vanuit backend/ met: python -m pytest test_bundle_planner.py -v
"""

from typing import Dict, List

import pytest

from redistribution.algorithm import generate_moves_for_article
from redistribution.constraints import RedistributionParams
from redistribution.domain import ArticleStock, SizeType, StoreInventory


# ---------- Helpers ----------

def _store(
    code: str,
    bv: str,
    inventory: Dict[str, int],
    sales: int = 0,
    store_total: int = 0,
):
    s = StoreInventory(
        store_code=code,
        store_name=f"Store{code}",
        bv_name=bv,
        inventory=dict(inventory),
        sales={"TOTAL": sales} if sales > 0 else {},
    )
    s.calculate_metrics(batch_total=sum(inventory.values()), store_total=store_total)
    return s


def _article(stores: List[StoreInventory], sizes: List[str]) -> ArticleStock:
    a = ArticleStock(volgnummer="TEST", omschrijving="Test", batch_id=1)
    a.all_sizes = list(sizes)
    a.size_type = SizeType.LETTER
    for s in stores:
        a.stores[s.store_code] = s
    a.calculate_aggregates()
    return a


def _working_inv(article: ArticleStock) -> Dict[str, Dict[str, int]]:
    return {
        code: {sz: store.inventory.get(sz, 0) for sz in article.all_sizes}
        for code, store in article.stores.items()
    }


def _apply(
    working: Dict[str, Dict[str, int]], moves
) -> Dict[str, Dict[str, int]]:
    """Past moves NIET toe (working is al bijgewerkt door planner); alleen
    voor assertions over eindstand gebruiken we working zelf."""
    return working


def _totals_per_store(working: Dict[str, Dict[str, int]]) -> Dict[str, int]:
    return {code: sum(v for v in inv.values() if v > 0) for code, inv in working.items()}


# ---------- Tests ----------

def test_min_3_hard_rule_no_store_ends_with_1_or_2():
    """R1: elke winkel eindigt op 0 of >=3."""
    params = RedistributionParams()

    stores = [
        _store("6", "BV_A", {"M": 1}, sales=0, store_total=450),
        _store("9", "BV_A", {"L": 1, "XL": 1}, sales=0, store_total=380),
        _store("8", "BV_A", {"S": 2, "M": 2, "L": 2}, sales=3, store_total=600),
        _store("11", "BV_A", {}, sales=8, store_total=420),
        _store("12", "BV_A", {"S": 1, "M": 1}, sales=2, store_total=500),
    ]
    article = _article(stores, ["S", "M", "L", "XL"])
    working = _working_inv(article)

    moves, rules = generate_moves_for_article(article, params, working)

    totals = _totals_per_store(working)
    for code, total in totals.items():
        assert total == 0 or total >= 3, (
            f"Store {code} eindigt op {total} — regel: 0 of >=3"
        )
    assert any("Bundle Planner" in r for r in rules)


def test_under_3_total_all_to_one_store():
    """R1-uitzondering: pool < 3 → alles naar top-ranked winkel."""
    params = RedistributionParams()

    stores = [
        _store("6", "BV_A", {"M": 1}, sales=0, store_total=450),
        _store("9", "BV_A", {"L": 1}, sales=0, store_total=380),
        _store("8", "BV_A", {}, sales=5, store_total=600),
    ]
    article = _article(stores, ["M", "L"])
    working = _working_inv(article)

    generate_moves_for_article(article, params, working)

    totals = _totals_per_store(working)
    non_zero = [code for code, t in totals.items() if t > 0]
    assert len(non_zero) == 1, f"Expected 1 receiver, got {non_zero}"
    # Top-verkoper wint (Weert heeft sales=5)
    assert non_zero[0] == "8"


def test_sales_tie_lower_store_total_wins_as_receiver():
    """R3: bij sales-gelijkspel (beide 0) wint winkel met lagere store_total.

    Scenario: pool van 4 stuks bij 2 verkoop-loze winkels. Pool/3 = 1 receiver,
    dus er MOET gekozen worden. Tiebreaker = lagere store_total.
    """
    params = RedistributionParams()

    stores = [
        _store("6", "BV_A", {"M": 1, "L": 1}, sales=0, store_total=450),
        _store("9", "BV_A", {"L": 1, "XL": 1}, sales=0, store_total=380),
    ]
    article = _article(stores, ["M", "L", "XL"])
    working = _working_inv(article)

    generate_moves_for_article(article, params, working)

    totals = _totals_per_store(working)
    # Stein (lagere store_total) moet receiver zijn, Echt moet leeg
    assert totals["9"] >= 3, f"Stein (lower store_total) moet receiver zijn: {totals}"
    assert totals["6"] == 0, f"Echt moet leeg: {totals}"


def test_bv_scope_respected_no_cross_bv_moves():
    """R5: enforce_bv_separation=True → geen cross-BV moves."""
    params = RedistributionParams(enforce_bv_separation=True)

    stores = [
        _store("6", "BV_A", {"M": 1}, sales=0, store_total=450),
        _store("31", "BV_B", {"L": 1, "XL": 1}, sales=5, store_total=500),
    ]
    article = _article(stores, ["M", "L", "XL"])
    working = _working_inv(article)

    moves, _ = generate_moves_for_article(article, params, working)

    for move in moves:
        from_bv = article.stores[move.from_store].bv_name
        to_bv = article.stores[move.to_store].bv_name
        assert from_bv == to_bv, (
            f"Cross-BV move gevonden: {move.from_store}({from_bv}) → "
            f"{move.to_store}({to_bv})"
        )


def test_top_seller_gets_most_inventory():
    """R2: best-verkopende winkel krijgt de meeste stuks."""
    params = RedistributionParams()

    stores = [
        _store("6", "BV_A", {"M": 1}, sales=0, store_total=450),
        _store("9", "BV_A", {"L": 1, "XL": 1}, sales=0, store_total=380),
        _store("8", "BV_A", {"S": 2, "M": 2, "L": 2}, sales=3, store_total=600),
        _store("11", "BV_A", {}, sales=8, store_total=420),  # top verkoper
        _store("12", "BV_A", {"S": 1, "M": 1}, sales=2, store_total=500),
    ]
    article = _article(stores, ["S", "M", "L", "XL"])
    working = _working_inv(article)

    generate_moves_for_article(article, params, working)

    totals = _totals_per_store(working)
    # Brunssum (11) is top-verkoper en moet receiver zijn met meest
    assert totals["11"] >= 3, f"Brunssum moet receiver zijn: {totals}"
    # En niet minder dan anderen (op gelijke hoogte mag, minder niet)
    max_qty = max(totals.values())
    assert totals["11"] == max_qty, (
        f"Top-verkoper Brunssum moet max voorraad hebben: {totals}"
    )


def test_pool_divides_into_correct_number_of_receivers():
    """Pool van 9 stuks → 3 receivers (9 / 3 = 3), geen 1-stuks winkels."""
    params = RedistributionParams()

    stores = [
        _store("6", "BV_A", {"S": 3, "M": 3, "L": 3}, sales=0, store_total=500),
        _store("8", "BV_A", {}, sales=5, store_total=400),
        _store("9", "BV_A", {}, sales=4, store_total=300),
        _store("11", "BV_A", {}, sales=3, store_total=200),
        _store("12", "BV_A", {}, sales=2, store_total=250),
    ]
    article = _article(stores, ["S", "M", "L"])
    working = _working_inv(article)

    generate_moves_for_article(article, params, working)

    totals = _totals_per_store(working)
    receivers = [c for c, t in totals.items() if t > 0]
    assert len(receivers) <= 3, f"Te veel receivers: {receivers} — {totals}"
    # Elke receiver minimaal 3
    for code in receivers:
        assert totals[code] >= 3, f"Receiver {code} heeft {totals[code]} < 3"


def test_isolated_bv_with_under_3_consolidates_within_bv():
    """BV met <3 stuks consolideert binnen BV naar beste winkel, niet cross-BV."""
    params = RedistributionParams(enforce_bv_separation=True)

    stores = [
        _store("6", "BV_A", {"M": 1}, sales=0, store_total=450),
        _store("9", "BV_A", {"L": 1}, sales=2, store_total=380),
        _store("31", "BV_B", {"S": 3, "M": 3}, sales=5, store_total=600),
    ]
    article = _article(stores, ["S", "M", "L"])
    working = _working_inv(article)

    moves, _ = generate_moves_for_article(article, params, working)

    # Verwachting: BV_A (totaal 2) consolideert naar Stein (sales=2); BV_B blijft
    totals = _totals_per_store(working)
    bv_a_stores = {"6", "9"}
    bv_a_non_zero = [c for c in bv_a_stores if totals[c] > 0]
    assert len(bv_a_non_zero) == 1, f"BV_A moet naar 1 winkel: {totals}"
    # Geen cross-BV moves
    for move in moves:
        assert (
            article.stores[move.from_store].bv_name
            == article.stores[move.to_store].bv_name
        )


def test_total_moves_conserve_inventory():
    """Sanity check: totaal inventory voor == totaal na (alleen herverdeeld)."""
    params = RedistributionParams()
    stores = [
        _store("6", "BV_A", {"M": 1}, sales=0, store_total=450),
        _store("9", "BV_A", {"L": 1, "XL": 1}, sales=0, store_total=380),
        _store("8", "BV_A", {"S": 2, "M": 2, "L": 2}, sales=3, store_total=600),
        _store("11", "BV_A", {}, sales=8, store_total=420),
    ]
    article = _article(stores, ["S", "M", "L", "XL"])
    working_before = _working_inv(article)
    total_before = sum(sum(v for v in inv.values()) for inv in working_before.values())

    working = _working_inv(article)
    generate_moves_for_article(article, params, working)

    total_after = sum(sum(max(v, 0) for v in inv.values()) for inv in working.values())
    assert total_before == total_after, (
        f"Voorraad niet behouden: {total_before} → {total_after}"
    )


def test_feature_flag_off_falls_back_to_legacy():
    """enable_bundle_planner=False schakelt terug naar oud pad."""
    from redistribution.algorithm import (
        generate_redistribution_proposals_for_article,
    )
    # Dit is een smoketest dat de feature-flag bestaat; volledige legacy-test
    # staat in test_redistribution_algo.py.
    params = RedistributionParams(enable_bundle_planner=False)
    assert params.enable_bundle_planner is False

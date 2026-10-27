"""Tests dat de config-dependency-injection in het herverdelingsalgoritme
daadwerkelijk doorpropageert (Fase 3.3, PR-020).

Compenserende controle bij het verwijderen van de module-level mutable
singletons (`_global_bv_config`, `_active_profiles`): configuratie wordt nu
expliciet meegegeven i.p.v. via gedeelde globale state. Deze tests bewijzen dat
een geïnjecteerde `bv_config`/`profiles` het gedrag stuurt — van het leaf-niveau
(`validate_bv_move`) tot en met de volledige bundle-planner.
"""
from __future__ import annotations

from typing import Dict, List

from redistribution.algorithm import generate_moves_for_article
from redistribution.bv_config import BVConfig, validate_bv_move
from redistribution.constraints import RedistributionParams
from redistribution.domain import ArticleStock, SizeType, StoreInventory
from redistribution.store_profiles import StoreProfile, get_store_profile


def _bv_config(mapping: Dict[str, str]) -> BVConfig:
    """Bouw een BVConfig met een expliciete winkel→BV-mapping (test-injectie)."""
    cfg = BVConfig()
    cfg.store_to_bv = dict(mapping)
    cfg._build_reverse_mapping()
    return cfg


def _store(code: str, bv: str, inventory: Dict[str, int], sales: int = 0) -> StoreInventory:
    s = StoreInventory(
        store_code=code,
        store_name=f"Store{code}",
        bv_name=bv,
        inventory=dict(inventory),
        sales={"TOTAL": sales} if sales > 0 else {},
    )
    s.calculate_metrics(batch_total=sum(inventory.values()), store_total=0)
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


# --- Leaf-niveau: validate_bv_move gebruikt de geïnjecteerde config -----------

def test_validate_bv_move_uses_injected_config():
    same_bv = _bv_config({"1": "A", "2": "A"})
    diff_bv = _bv_config({"1": "A", "2": "B"})

    assert validate_bv_move("1", "2", True, config=same_bv)[0] is True
    assert validate_bv_move("1", "2", True, config=diff_bv)[0] is False


# --- Store-profielen worden geïnjecteerd --------------------------------------

def test_get_store_profile_uses_injected_profiles():
    custom = {"99": StoreProfile("99", floor_area_m2=10, max_capacity=999)}
    assert get_store_profile("99", custom).max_capacity == 999
    # Zonder injectie valt code "99" buiten de standaardprofielen.
    assert get_store_profile("99") is None


# --- Propagatie door de volledige bundle-planner ------------------------------

def test_injected_bv_config_propagates_through_planner():
    """Twee winkels in dezelfde synthetische BV-groep (zodat `_group_by_bv` ze
    samen neemt); de config-by-code-gate bepaalt of een move mag. Zo bewijzen we
    dat de geïnjecteerde config van generate_moves_for_article tot in
    validate_bv_move doorwerkt."""
    params = RedistributionParams()  # enforce_bv_separation=True, min 3

    def build():
        donor = _store("1", "G", {"S": 3, "M": 3}, sales=5)
        receiver = _store("2", "G", {}, sales=10)  # lege, hoog-verkopende ontvanger
        return _article([donor, receiver], ["S", "M"])

    # Zelfde config-BV: cross-move 1 -> 2 is toegestaan.
    article_same = build()
    moves_same, _ = generate_moves_for_article(
        article_same, params, _working_inv(article_same),
        bv_config=_bv_config({"1": "SAME", "2": "SAME"}),
    )

    # Verschillende config-BV: dezelfde move wordt geblokkeerd.
    article_diff = build()
    moves_diff, _ = generate_moves_for_article(
        article_diff, params, _working_inv(article_diff),
        bv_config=_bv_config({"1": "LEFT", "2": "RIGHT"}),
    )

    assert any(m.from_store == "1" and m.to_store == "2" for m in moves_same), (
        "Met dezelfde config-BV zou er een move 1->2 moeten zijn"
    )
    assert not any(m.to_store == "2" for m in moves_diff), (
        "Met verschillende config-BV mag winkel 2 niets ontvangen"
    )

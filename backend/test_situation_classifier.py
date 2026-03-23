from __future__ import annotations

from typing import Iterable

from database import get_db
from db_models import ArtikelVoorraad
from redistribution.algorithm import (
    generate_redistribution_proposals_for_article,
    generate_redistribution_proposals_for_batch,
)
from redistribution.constraints import DEFAULT_PARAMS
from redistribution.domain import ArticleSituation, ArticleStock, StoreInventory
from redistribution.situation import (
    SITUATION_RULE_PREFIX,
    classify_article_situation,
    extract_situation_rule,
)


def build_article(
    article_id: str,
    store_rows: Iterable[tuple[str, dict[str, int], int]],
) -> ArticleStock:
    article = ArticleStock(
        volgnummer=article_id,
        omschrijving=f"Article {article_id}",
        batch_id=0,
    )

    all_sizes = sorted(
        {
            size
            for _, inventory, _ in store_rows
            for size in inventory
        }
    )
    article.all_sizes = all_sizes

    for store_code, inventory, sold in store_rows:
        store = StoreInventory(
            store_code=store_code,
            store_name=f"Store {store_code}",
            inventory=inventory,
            sales={"TOTAL": sold} if sold > 0 else {},
        )
        store.calculate_metrics()
        article.stores[store_code] = store

    article.calculate_aggregates()
    return article


def test_low_stock_boundary_classification():
    article = build_article(
        "LOW",
        [
            ("6", {"S": 1, "M": 1}, 1),
            ("8", {"S": 1, "M": 1}, 0),
            ("9", {"S": 1, "M": 1}, 0),
        ],
    )

    assert classify_article_situation(article) == ArticleSituation.LOW_STOCK


def test_medium_stock_classification_between_thresholds():
    article = build_article(
        "MEDIUM",
        [
            ("6", {"S": 2, "M": 1}, 2),
            ("8", {"S": 1, "M": 1}, 2),
            ("9", {"S": 1, "M": 1}, 1),
            ("11", {"S": 1, "M": 1}, 1),
        ],
    )

    assert classify_article_situation(article) == ArticleSituation.MEDIUM_STOCK


def test_high_stock_total_inventory_boundary_classification():
    article = build_article(
        "HIGH",
        [
            ("6", {"S": 3, "M": 3}, 4),
            ("8", {"S": 2, "M": 2}, 3),
            ("9", {"S": 2, "M": 2}, 2),
            ("11", {"S": 2, "M": 2}, 2),
        ],
    )

    assert article.total_inventory == DEFAULT_PARAMS.high_stock_total_inventory_threshold
    assert classify_article_situation(article) == ArticleSituation.HIGH_STOCK


def test_partij_stock_to_sales_boundary_classification():
    article = build_article(
        "PARTIJ",
        [
            ("6", {"S": 4, "M": 4}, 2),
            ("8", {"S": 4, "M": 4}, 2),
            ("9", {"S": 4, "M": 4}, 1),
        ],
    )

    assert article.total_inventory == DEFAULT_PARAMS.partij_total_inventory_threshold
    assert article.total_sales == 5
    assert classify_article_situation(article) == ArticleSituation.PARTIJ


def test_zero_inventory_defaults_to_low_stock():
    article = build_article(
        "ZERO",
        [
            ("6", {"S": 0, "M": 0}, 0),
            ("8", {"S": 0, "M": 0}, 0),
        ],
    )

    assert classify_article_situation(article) == ArticleSituation.LOW_STOCK


def test_generated_proposal_contains_single_situation_rule_for_existing_batch():
    db = next(get_db())

    try:
        latest_batch_id = db.query(ArtikelVoorraad.batch_id).order_by(ArtikelVoorraad.batch_id.desc()).first()
        assert latest_batch_id is not None

        sample_article = db.query(ArtikelVoorraad.volgnummer).filter(
            ArtikelVoorraad.batch_id == latest_batch_id[0]
        ).first()
        assert sample_article is not None

        proposal = generate_redistribution_proposals_for_article(
            db,
            sample_article[0],
            latest_batch_id[0],
            DEFAULT_PARAMS,
        )

        assert proposal is not None
        assert extract_situation_rule(proposal.applied_rules) is not None
        assert sum(
            1 for rule in proposal.applied_rules if rule.startswith(SITUATION_RULE_PREFIX)
        ) == 1
        assert proposal.applied_rules[0].startswith(SITUATION_RULE_PREFIX)
    finally:
        db.close()


def test_batch_generation_marks_all_proposals_with_situation_rule():
    db = next(get_db())

    try:
        latest_batch_id = db.query(ArtikelVoorraad.batch_id).order_by(ArtikelVoorraad.batch_id.desc()).first()
        assert latest_batch_id is not None

        proposals = generate_redistribution_proposals_for_batch(
            db,
            latest_batch_id[0],
            DEFAULT_PARAMS,
        )

        assert proposals
        assert all(extract_situation_rule(proposal.applied_rules) is not None for proposal in proposals)
    finally:
        db.close()

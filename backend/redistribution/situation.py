"""
Shadow-mode situatieclassificatie voor artikelen.

De classifier annoteert proposals, maar stuurt de move-generatie nog niet aan.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from .constraints import DEFAULT_PARAMS, RedistributionParams
from .domain import ArticleSituation, ArticleStock

SITUATION_RULE_PREFIX = "Situation: "


@dataclass(frozen=True)
class SituationMetrics:
    """Samenvattende metrics die de huidige artikelpositie beschrijven."""

    total_inventory: int
    total_sales: int
    active_store_count: int
    size_count: int
    avg_units_per_active_store: float
    avg_units_per_size: float
    stock_to_sales_ratio: float


def collect_article_situation_metrics(article: ArticleStock) -> SituationMetrics:
    """Bereken de aggregate metrics die voor de classifier nodig zijn."""
    active_store_count = sum(
        1
        for store in article.stores.values()
        if sum(store.inventory.values()) > 0
    )
    size_count = len(article.all_sizes)
    avg_units_per_active_store = (
        article.total_inventory / active_store_count
        if active_store_count
        else 0.0
    )
    avg_units_per_size = (
        article.total_inventory / size_count
        if size_count
        else 0.0
    )
    stock_to_sales_ratio = (
        article.total_inventory / article.total_sales
        if article.total_sales > 0
        else float(article.total_inventory)
    )

    return SituationMetrics(
        total_inventory=article.total_inventory,
        total_sales=article.total_sales,
        active_store_count=active_store_count,
        size_count=size_count,
        avg_units_per_active_store=avg_units_per_active_store,
        avg_units_per_size=avg_units_per_size,
        stock_to_sales_ratio=stock_to_sales_ratio,
    )


def classify_article_situation(
    article: ArticleStock,
    params: Optional[RedistributionParams] = None,
) -> ArticleSituation:
    """
    Classificeer een artikel in shadow mode.

    De thresholds zijn bewust eenvoudig en configureerbaar: fase 1 voegt alleen
    een stabiele annotatie toe en verandert verder niets aan move ranking,
    selectie of optimalisatie.
    """
    if params is None:
        params = DEFAULT_PARAMS

    metrics = collect_article_situation_metrics(article)

    if metrics.total_inventory == 0:
        return ArticleSituation.LOW_STOCK

    if (
        metrics.total_inventory >= params.partij_total_inventory_threshold
        and metrics.avg_units_per_active_store >= params.partij_units_per_store_threshold
        and (
            metrics.total_sales == 0
            or metrics.stock_to_sales_ratio >= params.partij_stock_to_sales_ratio_threshold
        )
    ):
        return ArticleSituation.PARTIJ

    if (
        metrics.total_inventory <= params.low_stock_total_inventory_threshold
        or metrics.avg_units_per_active_store <= params.low_stock_units_per_store_threshold
    ):
        return ArticleSituation.LOW_STOCK

    if (
        metrics.total_inventory >= params.high_stock_total_inventory_threshold
        or metrics.avg_units_per_active_store >= params.high_stock_units_per_store_threshold
        or (
            metrics.total_sales > 0
            and metrics.stock_to_sales_ratio >= params.high_stock_stock_to_sales_ratio_threshold
        )
    ):
        return ArticleSituation.HIGH_STOCK

    return ArticleSituation.MEDIUM_STOCK


def format_situation_rule(situation: ArticleSituation) -> str:
    """Converteer een situatie naar een stabiele proposal marker."""
    return f"{SITUATION_RULE_PREFIX}{situation.value}"


def extract_situation_rule(applied_rules: Optional[Iterable[str]]) -> Optional[str]:
    """Haal de situatie-marker uit een applied_rules lijst."""
    if not applied_rules:
        return None

    for rule in applied_rules:
        if isinstance(rule, str) and rule.startswith(SITUATION_RULE_PREFIX):
            return rule
    return None

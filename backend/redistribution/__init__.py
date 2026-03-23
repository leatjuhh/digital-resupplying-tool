"""
Herverdelingsalgoritme voor MC Company
Genereert slimme herverdelingsvoorstellen op basis van voorraad en verkoopcijfers
"""

from .domain import (
    ArticleStock,
    ArticleSituation,
    Move,
    Proposal,
    StoreInventory,
    SizeSequence,
    ConsolidationMetrics,
    OptimizationExplanation
)

from .constraints import (
    RedistributionParams,
    OptimizationParams,
    DEFAULT_PARAMS
)

from .algorithm import (
    generate_redistribution_proposals_for_article
)

from .situation import (
    SITUATION_RULE_PREFIX,
    classify_article_situation,
    format_situation_rule,
)

__all__ = [
    'ArticleStock',
    'ArticleSituation',
    'Move',
    'Proposal',
    'StoreInventory',
    'SizeSequence',
    'ConsolidationMetrics',
    'OptimizationExplanation',
    'RedistributionParams',
    'OptimizationParams',
    'DEFAULT_PARAMS',
    'generate_redistribution_proposals_for_article',
    'SITUATION_RULE_PREFIX',
    'classify_article_situation',
    'format_situation_rule',
]

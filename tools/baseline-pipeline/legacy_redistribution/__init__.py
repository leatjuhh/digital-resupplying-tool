"""
Herverdelingsalgoritme voor MC Company
Genereert slimme herverdelingsvoorstellen op basis van voorraad en verkoopcijfers
"""

from .domain import (
    ArticleStock,
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

from .baseline import (
    generate_baseline_proposal_from_record
)

try:
    from .algorithm import (
        generate_redistribution_proposals_for_article
    )
except ModuleNotFoundError:
    generate_redistribution_proposals_for_article = None

__all__ = [
    'ArticleStock',
    'Move',
    'Proposal',
    'StoreInventory',
    'SizeSequence',
    'ConsolidationMetrics',
    'OptimizationExplanation',
    'RedistributionParams',
    'OptimizationParams',
    'DEFAULT_PARAMS',
    'generate_baseline_proposal_from_record'
]

if generate_redistribution_proposals_for_article is not None:
    __all__.append('generate_redistribution_proposals_for_article')

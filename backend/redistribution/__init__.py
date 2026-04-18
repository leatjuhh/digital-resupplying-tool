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
)

from .constraints import (
    RedistributionParams,
    DEFAULT_PARAMS,
)

from .algorithm import (
    generate_redistribution_proposals_for_article,
)

from .situation import (
    SITUATION_RULE_PREFIX,
    classify_article_situation,
    format_situation_rule,
)

from .store_profiles import (
    StoreProfile,
    get_store_profile,
    get_all_profiles,
    set_store_profiles,
)

__all__ = [
    'ArticleStock',
    'ArticleSituation',
    'Move',
    'Proposal',
    'StoreInventory',
    'RedistributionParams',
    'DEFAULT_PARAMS',
    'generate_redistribution_proposals_for_article',
    'SITUATION_RULE_PREFIX',
    'classify_article_situation',
    'format_situation_rule',
    'StoreProfile',
    'get_store_profile',
    'get_all_profiles',
    'set_store_profiles',
]

"""
Domain models voor het herverdelingsalgoritme
Definieert de kernstructuren voor voorraad, moves, en voorstellen
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum


class SizeType(Enum):
    """Type maat reeks"""
    NUMERIC = "numeric"      # 32, 34, 36, 38, etc.
    LETTER = "letter"        # XS, S, M, L, XL, etc.
    CUSTOM = "custom"        # Onbekende/custom maat reeks


class ArticleSituation(Enum):
    """Globale voorraadpositie van een artikel in shadow mode."""
    LOW_STOCK = "LOW_STOCK"
    MEDIUM_STOCK = "MEDIUM_STOCK"
    HIGH_STOCK = "HIGH_STOCK"
    PARTIJ = "PARTIJ"


@dataclass
class StoreInventory:
    """Voorraad informatie voor één winkel"""
    store_code: str
    store_name: str
    bv_name: Optional[str] = None

    inventory: Dict[str, int] = field(default_factory=dict)   # {maat: aantal}
    sales: Dict[str, int] = field(default_factory=dict)        # {maat: verkocht}

    total_inventory: int = 0
    total_sales: int = 0
    demand_score: float = 0.0      # sales / inventory ratio
    batch_total_inventory: int = 0  # totaalvoorraad winkel over hele batch
    capacity_ratio: float = 0.0    # batch_total / max_capacity (0.0 = onbekend)

    def calculate_metrics(self, batch_total: int = 0, max_capacity: int = 0):
        """Bereken afgeleide metrics"""
        self.total_inventory = sum(self.inventory.values())
        self.total_sales = sum(self.sales.values())
        self.demand_score = (
            self.total_sales / self.total_inventory
            if self.total_inventory > 0
            else 0.0
        )
        self.batch_total_inventory = batch_total
        if max_capacity > 0 and batch_total > 0:
            self.capacity_ratio = min(1.0, batch_total / max_capacity)


@dataclass
class ArticleStock:
    """Complete voorraad informatie voor één artikel"""
    volgnummer: str
    omschrijving: str
    batch_id: int

    stores: Dict[str, StoreInventory] = field(default_factory=dict)
    all_sizes: List[str] = field(default_factory=list)
    size_type: SizeType = SizeType.CUSTOM

    total_inventory: int = 0
    total_sales: int = 0
    average_inventory_per_size: Dict[str, float] = field(default_factory=dict)

    def calculate_aggregates(self):
        """Bereken totalen en gemiddeldes"""
        self.total_inventory = sum(s.total_inventory for s in self.stores.values())
        self.total_sales = sum(s.total_sales for s in self.stores.values())

        size_totals: Dict[str, int] = {}
        size_counts: Dict[str, int] = {}

        for store in self.stores.values():
            for size, qty in store.inventory.items():
                if qty <= 0:
                    continue
                size_totals[size] = size_totals.get(size, 0) + qty
                size_counts[size] = size_counts.get(size, 0) + 1

        self.average_inventory_per_size = {
            size: size_totals[size] / size_counts[size]
            for size in size_totals
        }


@dataclass
class Move:
    """Één herverdelingsactie van winkel naar winkel"""
    volgnummer: str
    size: str
    from_store: str
    from_store_name: str
    to_store: str
    to_store_name: str
    qty: int

    score: float = 0.0
    reason: str = ""

    from_bv: Optional[str] = None
    to_bv: Optional[str] = None
    # Behouden voor API-compatibiliteit (altijd False)
    breaks_sequence: bool = False
    creates_sequence: bool = False


@dataclass
class Proposal:
    """Complete herverdelingsvoorstel voor één artikel"""
    volgnummer: str
    article_name: str
    batch_id: int

    moves: List[Move] = field(default_factory=list)

    status: str = "pending"  # pending, approved, rejected, edited
    created_at: datetime = field(default_factory=datetime.now)
    reviewed_at: Optional[datetime] = None

    reason: str = ""
    applied_rules: List[str] = field(default_factory=list)

    # Behouden voor API-compatibiliteit (altijd False/None)
    optimization_applied: bool = False
    optimization_explanation: Optional[object] = None

    total_moves: int = 0
    total_quantity: int = 0
    stores_affected: Set[str] = field(default_factory=set)

    def calculate_aggregates(self):
        """Bereken totalen"""
        self.total_moves = len(self.moves)
        self.total_quantity = sum(move.qty for move in self.moves)
        self.stores_affected = set()
        for move in self.moves:
            self.stores_affected.add(move.from_store)
            self.stores_affected.add(move.to_store)

    def to_dict(self) -> Dict:
        """Converteer naar dictionary voor database opslag"""
        return {
            'volgnummer': self.volgnummer,
            'article_name': self.article_name,
            'batch_id': self.batch_id,
            'moves': [
                {
                    'size': m.size,
                    'from_store': m.from_store,
                    'from_store_name': m.from_store_name,
                    'to_store': m.to_store,
                    'to_store_name': m.to_store_name,
                    'qty': m.qty,
                    'score': m.score,
                    'reason': m.reason,
                }
                for m in self.moves
            ],
            'status': self.status,
            'reason': self.reason,
            'applied_rules': self.applied_rules,
            'optimization_applied': self.optimization_applied,
            'total_moves': self.total_moves,
            'total_quantity': self.total_quantity,
        }

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
    bv_name: Optional[str] = None  # Voor BV constraint
    
    # Voorraad per maat
    inventory: Dict[str, int] = field(default_factory=dict)  # {maat: aantal}
    
    # Verkoopcijfers per maat
    sales: Dict[str, int] = field(default_factory=dict)  # {maat: verkocht}
    
    # Berekende metrics
    total_inventory: int = 0
    total_sales: int = 0
    demand_score: float = 0.0  # Berekend: sales / inventory ratio
    
    def calculate_metrics(self):
        """Bereken afgeleide metrics"""
        self.total_inventory = sum(self.inventory.values())
        self.total_sales = sum(self.sales.values())
        
        if self.total_inventory > 0:
            self.demand_score = self.total_sales / self.total_inventory
        else:
            self.demand_score = 0.0


@dataclass
class SizeSequence:
    """Representeert een opeenvolgende maten reeks in een winkel"""
    store_code: str
    sizes: List[str]  # Gesorteerde lijst van opeenvolgende maten
    size_type: SizeType
    width: int  # Aantal maten in de reeks
    
    def contains(self, size: str) -> bool:
        """Check of deze reeks een bepaalde maat bevat"""
        return size in self.sizes
    
    def would_break_on_removal(self, size: str) -> bool:
        """Check of verwijderen van deze maat de reeks zou breken"""
        if size not in self.sizes:
            return False
        
        # Als dit de enige maat is, of een eindmaat, breekt het niet
        if len(self.sizes) <= 1:
            return False
        
        index = self.sizes.index(size)
        # Als het een maat in het midden is, zou het de reeks breken
        return 0 < index < len(self.sizes) - 1


@dataclass
class ArticleStock:
    """Complete voorraad informatie voor één artikel"""
    volgnummer: str  # Artikelnummer
    omschrijving: str  # Artikel beschrijving
    batch_id: int  # Batch waar dit artikel uit komt
    
    # Voorraad per winkel
    stores: Dict[str, StoreInventory] = field(default_factory=dict)
    
    # Alle beschikbare maten (gesorteerd)
    all_sizes: List[str] = field(default_factory=list)
    size_type: SizeType = SizeType.CUSTOM
    
    # Maatreeksen per winkel
    size_sequences: Dict[str, List[SizeSequence]] = field(default_factory=dict)
    
    # Aggregated metrics
    total_inventory: int = 0
    total_sales: int = 0
    average_inventory_per_size: Dict[str, float] = field(default_factory=dict)
    
    def calculate_aggregates(self):
        """Bereken totalen en gemiddeldes"""
        self.total_inventory = sum(store.total_inventory for store in self.stores.values())
        self.total_sales = sum(store.total_sales for store in self.stores.values())
        
        # Bereken gemiddelde voorraad per maat
        size_totals: Dict[str, int] = {}
        size_counts: Dict[str, int] = {}
        
        for store in self.stores.values():
            for size, qty in store.inventory.items():
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
    
    # Scoring en reasoning
    score: float = 0.0
    reason: str = ""
    
    # Metadata
    from_bv: Optional[str] = None
    to_bv: Optional[str] = None
    breaks_sequence: bool = False
    creates_sequence: bool = False
    
    # Voor optimalisatie tracking
    original_move: bool = True  # False als het resultaat is van een swap
    swap_reason: Optional[str] = None


@dataclass
class ConsolidationMetrics:
    """Metrics voor move consolidatie optimalisatie"""
    
    # Voor optimalisatie (required fields first)
    total_shipments_before: int
    unique_routes_before: int
    
    # Na optimalisatie (required fields)
    total_shipments_after: int
    unique_routes_after: int
    
    # Verbetering (fields with defaults)
    destinations_per_source_before: Dict[str, int] = field(default_factory=dict)
    destinations_per_source_after: Dict[str, int] = field(default_factory=dict)
    shipments_saved: int = 0
    routes_saved: int = 0
    consolidation_improvement_pct: float = 0.0
    
    # Details (fields with defaults)
    swaps_performed: int = 0
    swaps_attempted: int = 0
    
    def calculate_improvement(self):
        """Bereken verbetering percentages"""
        self.shipments_saved = self.total_shipments_before - self.total_shipments_after
        self.routes_saved = self.unique_routes_before - self.unique_routes_after
        
        if self.total_shipments_before > 0:
            self.consolidation_improvement_pct = (
                self.shipments_saved / self.total_shipments_before * 100
            )


@dataclass
class SwapDetail:
    """Details van een uitgevoerde swap tijdens optimalisatie"""
    move_a_before: str  # "Winkel A → Winkel C: 5x maat 38"
    move_a_after: str   # "Winkel B → Winkel C: 5x maat 38"
    move_b_before: str
    move_b_after: str
    reason: str         # "Reduced Winkel A's destinations from 3 to 2"
    benefit: int        # Aantal verzendingen bespaard


@dataclass
class OptimizationExplanation:
    """Uitleg van toegepaste optimalisaties"""
    optimization_type: str = "move_consolidation"
    
    # Voor/na structuur
    destinations_before: Dict[str, List[str]] = field(default_factory=dict)  # {source: [dest1, dest2, ...]}
    destinations_after: Dict[str, List[str]] = field(default_factory=dict)
    
    # Uitgevoerde swaps
    swaps: List[SwapDetail] = field(default_factory=list)
    
    # Metrics
    metrics: Optional[ConsolidationMetrics] = None
    
    # Summary
    summary: str = ""
    
    def generate_summary(self):
        """Genereer human-readable summary"""
        if self.metrics:
            self.summary = (
                f"Optimalisatie toegepast: {self.metrics.shipments_saved} verzendingen bespaard "
                f"({self.metrics.consolidation_improvement_pct:.1f}% verbetering). "
                f"{self.metrics.swaps_performed} swaps uitgevoerd."
            )


@dataclass
class Proposal:
    """Complete herverdelingsvoorstel voor één artikel"""
    volgnummer: str
    article_name: str
    batch_id: int
    
    # Alle moves
    moves: List[Move] = field(default_factory=list)
    
    # Status tracking
    status: str = "pending"  # pending, approved, rejected, edited
    created_at: datetime = field(default_factory=datetime.now)
    reviewed_at: Optional[datetime] = None
    
    # Reasoning
    reason: str = ""
    applied_rules: List[str] = field(default_factory=list)
    
    # Optimalisatie info
    optimization_applied: bool = False
    optimization_explanation: Optional[OptimizationExplanation] = None
    
    # Aggregates
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

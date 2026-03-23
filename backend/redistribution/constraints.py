"""
Configuratie parameters voor het herverdelingsalgoritme
Bevat drempelwaarden, wegingen, en constraints
"""

from dataclasses import dataclass


@dataclass
class RedistributionParams:
    """Hoofdparameters voor herverdeling"""
    
    # ===== DREMPELWAARDEN =====
    
    # Overschot: wanneer voorraad te hoog is (multiplicator van gemiddelde)
    oversupply_threshold: float = 1.5  # 150% van gemiddelde = overschot
    
    # Tekort: wanneer voorraad te laag is (multiplicator van gemiddelde)
    undersupply_threshold: float = 0.5  # 50% van gemiddelde = tekort
    
    # Minimaal aantal stuks om te herverdelen (voorkom tiny moves)
    min_move_quantity: int = 1
    
    # Maximaal aantal stuks per move (voor logistiek)
    max_move_quantity: int = 100
    
    # ===== MAATSERIE CONSTRAINTS =====
    
    # Minimale breedte van een maatserie (3 = minimaal 3 opeenvolgende maten)
    min_sequence_width: int = 3
    
    # Penalty voor moves die series breken (0.0 - 1.0)
    sequence_break_penalty: float = 0.5
    
    # Bonus voor moves die series creëren (0.0 - 1.0)
    sequence_creation_bonus: float = 0.3
    
    # ===== SCORING WEGINGEN =====
    
    # Demand-based scoring (hoe belangrijk is verkoopcijfer)
    demand_weight: float = 0.7  # 70% van score
    
    # Maatserie behoud (hoe belangrijk is serie integriteit)
    series_weight: float = 0.2  # 20% van score
    
    # Efficiency (aantal stuks, transport kosten)
    efficiency_weight: float = 0.1  # 10% van score
    
    # ===== BV CONSTRAINT =====
    
    # Enforce BV separation (kan uitgezet worden in settings)
    enforce_bv_separation: bool = True
    
    # ===== BV CONSOLIDATIE =====
    
    # Minimaal aantal stuks per winkel bij maken van voorstel
    # Als een BV minder heeft, consolideer naar best verkopende winkel
    min_items_per_store: int = 6
    
    # Enable BV consolidation rule
    enable_bv_consolidation: bool = True
    
    # ===== DEMAND THRESHOLDS =====
    
    # High demand threshold (sales / inventory ratio)
    high_demand_threshold: float = 0.8  # 80% van voorraad verkocht = high demand
    
    # Low demand threshold
    low_demand_threshold: float = 0.2  # 20% van voorraad verkocht = low demand

    # ===== SITUATIECLASSIFICATIE (SHADOW MODE) =====

    # Artikel heeft structureel weinig voorraad over alle winkels heen
    low_stock_total_inventory_threshold: int = 6
    low_stock_units_per_store_threshold: float = 1.5

    # Artikel heeft voldoende diepte om herverdeling interessant te maken
    high_stock_total_inventory_threshold: int = 18
    high_stock_units_per_store_threshold: float = 3.0
    high_stock_stock_to_sales_ratio_threshold: float = 2.5

    # Partij-artikel: diepe voorraad met relatief lage vraag
    partij_total_inventory_threshold: int = 24
    partij_units_per_store_threshold: float = 4.0
    partij_stock_to_sales_ratio_threshold: float = 4.0
    
    # ===== OPTIMALISATIE =====
    
    # Enable post-processing optimalisatie
    enable_optimization: bool = True
    
    def validate(self) -> bool:
        """Valideer parameters"""
        if not (0 < self.oversupply_threshold):
            return False
        if not (0 < self.undersupply_threshold < 1):
            return False
        if not (0 <= self.demand_weight <= 1):
            return False
        if not (0 <= self.series_weight <= 1):
            return False
        if not (0 <= self.efficiency_weight <= 1):
            return False
        if self.low_stock_total_inventory_threshold < 0:
            return False
        if self.high_stock_total_inventory_threshold <= self.low_stock_total_inventory_threshold:
            return False
        if self.partij_total_inventory_threshold < self.high_stock_total_inventory_threshold:
            return False
        if self.low_stock_units_per_store_threshold <= 0:
            return False
        if self.high_stock_units_per_store_threshold < self.low_stock_units_per_store_threshold:
            return False
        if self.partij_units_per_store_threshold < self.high_stock_units_per_store_threshold:
            return False
        if self.high_stock_stock_to_sales_ratio_threshold <= 0:
            return False
        if self.partij_stock_to_sales_ratio_threshold < self.high_stock_stock_to_sales_ratio_threshold:
            return False

        # Check dat wegingen optellen tot ~1.0
        total_weight = self.demand_weight + self.series_weight + self.efficiency_weight
        if not (0.99 <= total_weight <= 1.01):
            return False
        
        return True


@dataclass
class OptimizationParams:
    """Parameters voor post-processing optimalisatie"""
    
    # ===== CONSOLIDATION =====
    
    # Enable move consolidation
    enable_consolidation: bool = True
    
    # Maximaal toegestane hoeveelheid verschil bij swaps (20% = 0.2)
    max_swap_quantity_diff: float = 0.2
    
    # Minimaal voordeel voor een swap (aantal verzendingen bespaard)
    min_consolidation_benefit: int = 1
    
    # ===== SCORING WEGINGEN =====
    
    # Hoe belangrijk is het reduceren van bestemmingen per bron
    consolidation_weight: float = 0.7
    
    # Hoe belangrijk is serie behoud bij swaps
    series_preservation_weight: float = 0.2
    
    # Hoe belangrijk is quantity matching bij swaps
    quantity_match_weight: float = 0.1
    
    # ===== PERFORMANCE LIMIETEN =====
    
    # Maximaal aantal swap iteraties (voorkom oneindige loops)
    max_swap_iterations: int = 10
    
    # Maximaal aantal swaps per artikel (performance limiet)
    max_swaps_per_article: int = 50
    
    # ===== DEBUGGING =====
    
    # Toon gedetailleerde swap informatie
    verbose_logging: bool = False
    
    def validate(self) -> bool:
        """Valideer parameters"""
        if not (0 < self.max_swap_quantity_diff <= 1):
            return False
        if not (0 <= self.consolidation_weight <= 1):
            return False
        if not (0 <= self.series_preservation_weight <= 1):
            return False
        if not (0 <= self.quantity_match_weight <= 1):
            return False
        
        # Check dat wegingen optellen tot ~1.0
        total_weight = (
            self.consolidation_weight +
            self.series_preservation_weight +
            self.quantity_match_weight
        )
        if not (0.99 <= total_weight <= 1.01):
            return False
        
        return True


# ===== DEFAULT CONFIGURATIE =====

DEFAULT_PARAMS = RedistributionParams(
    oversupply_threshold=1.5,
    undersupply_threshold=0.5,
    min_move_quantity=1,
    max_move_quantity=100,
    min_sequence_width=3,
    sequence_break_penalty=0.5,
    sequence_creation_bonus=0.3,
    demand_weight=0.7,
    series_weight=0.2,
    efficiency_weight=0.1,
    enforce_bv_separation=True,
    min_items_per_store=6,
    enable_bv_consolidation=True,
    high_demand_threshold=0.8,
    low_demand_threshold=0.2,
    low_stock_total_inventory_threshold=6,
    low_stock_units_per_store_threshold=1.5,
    high_stock_total_inventory_threshold=18,
    high_stock_units_per_store_threshold=3.0,
    high_stock_stock_to_sales_ratio_threshold=2.5,
    partij_total_inventory_threshold=24,
    partij_units_per_store_threshold=4.0,
    partij_stock_to_sales_ratio_threshold=4.0,
    enable_optimization=True
)

DEFAULT_OPTIMIZATION_PARAMS = OptimizationParams(
    enable_consolidation=True,
    max_swap_quantity_diff=0.2,
    min_consolidation_benefit=1,
    consolidation_weight=0.7,
    series_preservation_weight=0.2,
    quantity_match_weight=0.1,
    max_swap_iterations=10,
    max_swaps_per_article=50,
    verbose_logging=False
)


# ===== MAAT REEKS DEFINITIES =====

# Letter maten in volgorde
LETTER_SIZE_ORDER = [
    'XXXS', 'XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', 'XXXXL'
]

# Functie om custom maat reeksen toe te voegen
CUSTOM_SIZE_ORDERS = {}

def register_custom_size_order(name: str, sizes: list):
    """Registreer een custom maat reeks"""
    CUSTOM_SIZE_ORDERS[name] = sizes


def get_size_order(sizes: list) -> list:
    """
    Bepaal de correcte volgorde voor een lijst maten
    
    Args:
        sizes: Lijst van maten
        
    Returns:
        Gesorteerde lijst van maten
    """
    # Check of het numerieke maten zijn
    if all(size.isdigit() for size in sizes):
        return sorted(sizes, key=int)
    
    # Check of het letter maten zijn
    sizes_upper = [s.upper() for s in sizes]
    if all(s in LETTER_SIZE_ORDER for s in sizes_upper):
        return sorted(sizes_upper, key=lambda x: LETTER_SIZE_ORDER.index(x))
    
    # Check custom orders
    for name, order in CUSTOM_SIZE_ORDERS.items():
        if all(s in order for s in sizes):
            return sorted(sizes, key=lambda x: order.index(x))
    
    # Fallback: alfabetisch
    return sorted(sizes)

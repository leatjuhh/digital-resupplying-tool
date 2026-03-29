"""
Configuratie parameters voor het herverdelingsalgoritme
Bevat drempelwaarden en constraints
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

    # ===== BV CONSTRAINT =====

    # Enforce BV separation (kan uitgezet worden in settings)
    enforce_bv_separation: bool = True

    # ===== BV CONSOLIDATIE =====

    # Als een BV minder dan dit aantal heeft, consolideer naar best verkopende winkel
    min_items_per_store: int = 6

    # Enable BV consolidation rule
    enable_bv_consolidation: bool = True

    # ===== DEMAND THRESHOLDS =====

    high_demand_threshold: float = 0.8  # 80% van voorraad verkocht = high demand
    low_demand_threshold: float = 0.2   # 20% van voorraad verkocht = low demand

    # ===== SITUATIECLASSIFICATIE (SHADOW MODE) =====

    low_stock_total_inventory_threshold: int = 6
    low_stock_units_per_store_threshold: float = 1.5

    high_stock_total_inventory_threshold: int = 18
    high_stock_units_per_store_threshold: float = 3.0
    high_stock_stock_to_sales_ratio_threshold: float = 2.5

    partij_total_inventory_threshold: int = 24
    partij_units_per_store_threshold: float = 4.0
    partij_stock_to_sales_ratio_threshold: float = 4.0

    # ===== SCORING =====

    # Minimale score om een move te behouden
    min_move_score: float = 0.2

    def validate(self) -> bool:
        """Valideer parameters"""
        if not (0 < self.oversupply_threshold):
            return False
        if not (0 < self.undersupply_threshold < 1):
            return False
        if self.low_stock_total_inventory_threshold < 0:
            return False
        if self.high_stock_total_inventory_threshold <= self.low_stock_total_inventory_threshold:
            return False
        if self.partij_total_inventory_threshold < self.high_stock_total_inventory_threshold:
            return False
        return True


# ===== DEFAULT CONFIGURATIE =====

DEFAULT_PARAMS = RedistributionParams()


# ===== MAAT REEKS DEFINITIES =====

LETTER_SIZE_ORDER = [
    'XXXS', 'XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', 'XXXXL'
]

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
    if all(size.isdigit() for size in sizes):
        return sorted(sizes, key=int)

    sizes_upper = [s.upper() for s in sizes]
    if all(s in LETTER_SIZE_ORDER for s in sizes_upper):
        return sorted(sizes_upper, key=lambda x: LETTER_SIZE_ORDER.index(x))

    for name, order in CUSTOM_SIZE_ORDERS.items():
        if all(s in order for s in sizes):
            return sorted(sizes, key=lambda x: order.index(x))

    return sorted(sizes)

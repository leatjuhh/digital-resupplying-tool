"""
Utility functions voor backend
"""
from typing import Any, List
import re


def extract_store_code_numeric(store_id: str) -> int:
    """
    Extraheer numerieke filiaalcode uit store ID string.
    
    Args:
        store_id: Filiaalcode als string (bijv. "001", "010", "100")
        
    Returns:
        Numerieke waarde van de code, of sys.maxsize als parsing faalt
        
    Examples:
        >>> extract_store_code_numeric("001")
        1
        >>> extract_store_code_numeric("010")
        10
        >>> extract_store_code_numeric("100")
        100
        >>> extract_store_code_numeric("ABC")  # Invalid
        9223372036854775807  # sys.maxsize (komt onderaan)
    """
    import sys
    
    if not store_id:
        return sys.maxsize
    
    # Als het al een integer is, return het
    if isinstance(store_id, int):
        return store_id
    
    # Probeer direct te parsen
    store_str = str(store_id).strip()
    
    # Als het alleen cijfers zijn, parse het direct
    if store_str.isdigit():
        return int(store_str)
    
    # Probeer leading digits te extraheren (bijv. "001 - Amsterdam" -> 1)
    match = re.match(r'^(\d+)', store_str)
    if match:
        return int(match.group(1))
    
    # Als niets werkt, return maxsize (komt onderaan in sortering)
    return sys.maxsize


def sort_stores_by_code(stores: List[Any], 
                       code_key: str = 'store_id',
                       name_key: str = 'store_name') -> List[Any]:
    """
    Sorteer stores numeriek op filiaalcode (oplopend).
    Stores zonder geldige code komen onderaan.
    Bij gelijke code wordt alfabetisch op naam gesorteerd (tiebreaker).
    
    Args:
        stores: List van store dictionaries of objecten
        code_key: Key/attribuut voor store code (default: 'store_id')
        name_key: Key/attribuut voor store naam (default: 'store_name')
        
    Returns:
        Gesorteerde list van stores
        
    Examples:
        >>> stores = [
        ...     {"store_id": "010", "store_name": "Utrecht"},
        ...     {"store_id": "001", "store_name": "Amsterdam"},
        ...     {"store_id": "100", "store_name": "Groningen"},
        ... ]
        >>> sorted_stores = sort_stores_by_code(stores)
        >>> [s["store_id"] for s in sorted_stores]
        ['001', '010', '100']
    """
    def get_value(store, key):
        """Haal waarde op uit dict of object attribuut"""
        if isinstance(store, dict):
            return store.get(key, '')
        return getattr(store, key, '')
    
    def sort_key(store):
        """Sorteer key: eerst numerieke code, dan naam als tiebreaker"""
        code = get_value(store, code_key)
        name = get_value(store, name_key)
        numeric_code = extract_store_code_numeric(code)
        return (numeric_code, str(name).lower())
    
    return sorted(stores, key=sort_key)


def sort_store_ids(store_ids: List[str]) -> List[str]:
    """
    Sorteer lijst van store ID strings numeriek.
    
    Args:
        store_ids: List van store ID strings
        
    Returns:
        Numeriek gesorteerde list
        
    Examples:
        >>> sort_store_ids(["010", "001", "100", "002"])
        ['001', '002', '010', '100']
    """
    return sorted(store_ids, key=extract_store_code_numeric)

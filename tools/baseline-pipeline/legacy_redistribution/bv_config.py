"""
BV (Bedrijfsvennootschap) Configuratie
Beheert de mapping tussen winkels en BV's voor cross-BV blokkering
"""

from typing import Dict, Optional, Set
import json
import os


class BVConfig:
    """
    BV Configuratie Manager
    
    Beheert welke winkels tot welke BV behoren.
    Cross-BV herverdeling kan worden geblokkeerd indien gewenst.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialiseer BV configuratie
        
        Args:
            config_file: Pad naar configuratie bestand (optioneel)
        """
        self.config_file = config_file or "bv_mapping.json"
        self.store_to_bv: Dict[str, str] = {}
        self.bv_to_stores: Dict[str, Set[str]] = {}
        
        # Probeer configuratie te laden
        self.load_config()
    
    def load_config(self) -> bool:
        """
        Laad BV configuratie uit bestand
        
        Returns:
            True als succesvol geladen, False anders
        """
        if not os.path.exists(self.config_file):
            # Maak default configuratie
            self._create_default_config()
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.store_to_bv = data.get('store_to_bv', {})
            
            # Build reverse mapping
            self._build_reverse_mapping()
            
            return True
        except Exception as e:
            print(f"Fout bij laden BV configuratie: {e}")
            self._create_default_config()
            return False
    
    def save_config(self) -> bool:
        """
        Sla BV configuratie op naar bestand
        
        Returns:
            True als succesvol opgeslagen, False anders
        """
        try:
            data = {
                'store_to_bv': self.store_to_bv,
                'bv_names': list(self.bv_to_stores.keys())
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Fout bij opslaan BV configuratie: {e}")
            return False
    
    def _create_default_config(self):
        """Maak default BV configuratie"""
        # Default mapping (kan later worden aangepast via UI)
        self.store_to_bv = {
            # Lumitex B.V. winkels (voorbeeld)
            'AMS': 'Lumitex B.V.',
            'ROT': 'Lumitex B.V.',
            'UTR': 'Lumitex B.V.',
            'DEN': 'Lumitex B.V.',
            
            # MC Company Partners B.V. winkels (voorbeeld)
            'EIN': 'MC Company Partners B.V.',
            'GRO': 'MC Company Partners B.V.',
            'MAA': 'MC Company Partners B.V.',
            'BRE': 'MC Company Partners B.V.',
        }
        
        self._build_reverse_mapping()
        self.save_config()
    
    def _build_reverse_mapping(self):
        """Bouw reverse mapping: BV -> winkels"""
        self.bv_to_stores = {}
        
        for store, bv in self.store_to_bv.items():
            if bv not in self.bv_to_stores:
                self.bv_to_stores[bv] = set()
            self.bv_to_stores[bv].add(store)
    
    def get_bv(self, store_code: str) -> Optional[str]:
        """
        Haal BV op voor een winkel
        
        Args:
            store_code: Winkel code (bijv. 'AMS')
            
        Returns:
            BV naam of None als niet gevonden
        """
        return self.store_to_bv.get(store_code)
    
    def get_stores_in_bv(self, bv_name: str) -> Set[str]:
        """
        Haal alle winkels op in een BV
        
        Args:
            bv_name: BV naam
            
        Returns:
            Set van winkel codes
        """
        return self.bv_to_stores.get(bv_name, set())
    
    def can_redistribute(self, from_store: str, to_store: str, enforce: bool = True) -> bool:
        """
        Check of herverdeling tussen twee winkels is toegestaan
        
        Args:
            from_store: Bron winkel code
            to_store: Doel winkel code
            enforce: Of BV constraint gehandhaafd moet worden
            
        Returns:
            True als herverdeling toegestaan, False anders
        """
        # Als enforce uit staat, altijd toestaan
        if not enforce:
            return True
        
        # Haal BV's op
        from_bv = self.get_bv(from_store)
        to_bv = self.get_bv(to_store)
        
        # Als een van beide geen BV heeft, toestaan (met warning)
        if from_bv is None or to_bv is None:
            return True
        
        # Check of zelfde BV
        return from_bv == to_bv
    
    def set_bv_for_store(self, store_code: str, bv_name: str) -> bool:
        """
        Stel BV in voor een winkel
        
        Args:
            store_code: Winkel code
            bv_name: BV naam
            
        Returns:
            True als succesvol ingesteld
        """
        self.store_to_bv[store_code] = bv_name
        self._build_reverse_mapping()
        return self.save_config()
    
    def remove_store(self, store_code: str) -> bool:
        """
        Verwijder winkel uit configuratie
        
        Args:
            store_code: Winkel code
            
        Returns:
            True als succesvol verwijderd
        """
        if store_code in self.store_to_bv:
            del self.store_to_bv[store_code]
            self._build_reverse_mapping()
            return self.save_config()
        return False
    
    def get_all_bvs(self) -> list:
        """
        Haal alle BV namen op
        
        Returns:
            Lijst van BV namen
        """
        return list(self.bv_to_stores.keys())
    
    def get_all_stores(self) -> list:
        """
        Haal alle winkel codes op
        
        Returns:
            Lijst van winkel codes
        """
        return list(self.store_to_bv.keys())
    
    def import_from_database(self, db_session):
        """
        Importeer winkel data uit database en map naar BV's
        
        Args:
            db_session: SQLAlchemy database sessie
        """
        # TODO: Implementeer database import
        # Dit zou alle winkels uit de database kunnen halen
        # en automatisch aan BV's kunnen toewijzen op basis van regels
        pass
    
    def to_dict(self) -> dict:
        """
        Converteer naar dictionary voor API responses
        
        Returns:
            Dictionary representatie
        """
        return {
            'store_to_bv': self.store_to_bv,
            'bv_to_stores': {
                bv: list(stores) 
                for bv, stores in self.bv_to_stores.items()
            },
            'total_stores': len(self.store_to_bv),
            'total_bvs': len(self.bv_to_stores)
        }


# Global instance (kan worden gebruikt door algoritme)
_global_bv_config: Optional[BVConfig] = None


def get_bv_config() -> BVConfig:
    """
    Haal global BV configuratie op (singleton pattern)
    
    Returns:
        BVConfig instance
    """
    global _global_bv_config
    
    if _global_bv_config is None:
        _global_bv_config = BVConfig()
    
    return _global_bv_config


def reload_bv_config():
    """Herlaad BV configuratie (bijv. na wijzigingen via UI)"""
    global _global_bv_config
    _global_bv_config = BVConfig()


# ===== UTILITY FUNCTIONS =====

def validate_bv_move(from_store: str, to_store: str, enforce_bv: bool = True) -> tuple[bool, str]:
    """
    Valideer of een move toegestaan is volgens BV regels
    
    Args:
        from_store: Bron winkel
        to_store: Doel winkel
        enforce_bv: Of BV constraint gehandhaafd moet worden
        
    Returns:
        Tuple van (is_valid, reason)
    """
    config = get_bv_config()
    
    if not enforce_bv:
        return True, "BV constraint niet actief"
    
    from_bv = config.get_bv(from_store)
    to_bv = config.get_bv(to_store)
    
    if from_bv is None:
        return True, f"Winkel {from_store} heeft geen BV toewijzing"
    
    if to_bv is None:
        return True, f"Winkel {to_store} heeft geen BV toewijzing"
    
    if from_bv == to_bv:
        return True, f"Beide winkels in {from_bv}"
    
    return False, f"Cross-BV move niet toegestaan: {from_bv} → {to_bv}"

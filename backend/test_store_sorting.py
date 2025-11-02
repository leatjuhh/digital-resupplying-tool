"""
Tests voor store sorting utilities
"""
import pytest
from utils import extract_store_code_numeric, sort_stores_by_code, sort_store_ids


class TestExtractStoreCodeNumeric:
    """Tests voor extract_store_code_numeric functie"""
    
    def test_parse_numeric_string_codes(self):
        """Test parsing van numerieke string codes"""
        assert extract_store_code_numeric("001") == 1
        assert extract_store_code_numeric("010") == 10
        assert extract_store_code_numeric("100") == 100
        assert extract_store_code_numeric("2") == 2
        assert extract_store_code_numeric("0025") == 25
    
    def test_parse_numeric_codes(self):
        """Test directe numerieke codes"""
        assert extract_store_code_numeric(1) == 1
        assert extract_store_code_numeric(10) == 10
        assert extract_store_code_numeric(100) == 100
    
    def test_extract_leading_digits(self):
        """Test extractie van leading digits uit labels"""
        assert extract_store_code_numeric("001 - Amsterdam") == 1
        assert extract_store_code_numeric("010 Utrecht") == 10
        assert extract_store_code_numeric("100-Groningen") == 100
        assert extract_store_code_numeric("  5 Den Haag") == 5
    
    def test_invalid_codes(self):
        """Test ongeldige codes (moeten maxsize returnen)"""
        import sys
        assert extract_store_code_numeric("ABC") == sys.maxsize
        assert extract_store_code_numeric("XYZ-123") == sys.maxsize
        assert extract_store_code_numeric("") == sys.maxsize
        assert extract_store_code_numeric(None) == sys.maxsize
    
    def test_whitespace_handling(self):
        """Test whitespace handling"""
        assert extract_store_code_numeric("  001  ") == 1
        assert extract_store_code_numeric("\t10\n") == 10


class TestSortStoresByCode:
    """Tests voor sort_stores_by_code functie"""
    
    def test_sort_basic_dict_stores(self):
        """Test basis sortering van store dictionaries"""
        stores = [
            {"store_id": "010", "store_name": "Utrecht"},
            {"store_id": "001", "store_name": "Amsterdam"},
            {"store_id": "100", "store_name": "Groningen"},
            {"store_id": "002", "store_name": "Rotterdam"},
        ]
        sorted_stores = sort_stores_by_code(stores)
        
        expected_order = ["001", "002", "010", "100"]
        actual_order = [s["store_id"] for s in sorted_stores]
        
        assert actual_order == expected_order
    
    def test_sort_prevents_lexicographic_error(self):
        """Test dat het voorkomt dat 10 voor 2 komt (lexicografisch)"""
        stores = [
            {"store_id": "10", "store_name": "Utrecht"},
            {"store_id": "2", "store_name": "Rotterdam"},
            {"store_id": "1", "store_name": "Amsterdam"},
            {"store_id": "100", "store_name": "Groningen"},
        ]
        sorted_stores = sort_stores_by_code(stores)
        
        # Numeriek correct: 1, 2, 10, 100
        # (NIET lexicografisch: 1, 10, 100, 2)
        expected_order = ["1", "2", "10", "100"]
        actual_order = [s["store_id"] for s in sorted_stores]
        
        assert actual_order == expected_order
    
    def test_sort_with_leading_zeros(self):
        """Test dat leading zeros correct worden behandeld"""
        stores = [
            {"store_id": "001", "store_name": "Amsterdam"},
            {"store_id": "01", "store_name": "Rotterdam"}, 
            {"store_id": "1", "store_name": "Utrecht"},
        ]
        sorted_stores = sort_stores_by_code(stores)
        
        # Allemaal numeriek 1, dus sorteer op naam
        names = [s["store_name"] for s in sorted_stores]
        assert names == ["Amsterdam", "Rotterdam", "Utrecht"]
    
    def test_sort_invalid_codes_at_end(self):
        """Test dat stores zonder geldige code onderaan komen"""
        stores = [
            {"store_id": "002", "store_name": "Rotterdam"},
            {"store_id": "XXX", "store_name": "Invalid 1"},
            {"store_id": "001", "store_name": "Amsterdam"},
            {"store_id": "ABC", "store_name": "Invalid 2"},
        ]
        sorted_stores = sort_stores_by_code(stores)
        
        # Valid codes eerst (001, 002), dan invalid (ABC, XXX - alfabetisch op naam)
        codes = [s["store_id"] for s in sorted_stores]
        assert codes[:2] == ["001", "002"]
        assert set(codes[2:]) == {"XXX", "ABC"}
    
    def test_sort_tiebreaker_on_name(self):
        """Test dat bij gelijke code op naam wordt gesorteerd"""
        stores = [
            {"store_id": "001", "store_name": "Utrecht"},
            {"store_id": "001", "store_name": "Amsterdam"},
            {"store_id": "001", "store_name": "Rotterdam"},
        ]
        sorted_stores = sort_stores_by_code(stores)
        
        names = [s["store_name"] for s in sorted_stores]
        assert names == ["Amsterdam", "Rotterdam", "Utrecht"]
    
    def test_sort_with_custom_keys(self):
        """Test sortering met custom key names"""
        stores = [
            {"code": "010", "name": "Utrecht"},
            {"code": "001", "name": "Amsterdam"},
        ]
        sorted_stores = sort_stores_by_code(stores, code_key="code", name_key="name")
        
        assert sorted_stores[0]["code"] == "001"
        assert sorted_stores[1]["code"] == "010"
    
    def test_sort_mixed_formats(self):
        """Test sortering met gemixte code formats"""
        stores = [
            {"store_id": "100", "store_name": "Groningen"},
            {"store_id": "10", "store_name": "Utrecht"},
            {"store_id": "001", "store_name": "Amsterdam"},
            {"store_id": "2", "store_name": "Rotterdam"},
        ]
        sorted_stores = sort_stores_by_code(stores)
        
        expected_order = ["001", "2", "10", "100"]
        actual_order = [s["store_id"] for s in sorted_stores]
        
        assert actual_order == expected_order


class TestSortStoreIds:
    """Tests voor sort_store_ids functie"""
    
    def test_sort_basic_ids(self):
        """Test basis sortering van ID strings"""
        ids = ["010", "001", "100", "002"]
        sorted_ids = sort_store_ids(ids)
        
        assert sorted_ids == ["001", "002", "010", "100"]
    
    def test_sort_prevents_lexicographic(self):
        """Test correcte numerieke sortering"""
        ids = ["10", "2", "1", "100"]
        sorted_ids = sort_store_ids(ids)
        
        # Numeriek: 1, 2, 10, 100
        # NIET lexicografisch: 1, 10, 100, 2
        assert sorted_ids == ["1", "2", "10", "100"]
    
    def test_sort_mixed_lengths(self):
        """Test sortering met verschillende string lengtes"""
        ids = ["1", "01", "001", "10", "010", "100"]
        sorted_ids = sort_store_ids(ids)
        
        # Allemaal dezelfde numerieke waarde groepen
        # 1=01=001, 10=010, 100
        expected = ["1", "01", "001", "10", "010", "100"]
        assert sorted_ids == expected
    
    def test_empty_list(self):
        """Test lege lijst"""
        assert sort_store_ids([]) == []


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

"""
Eenvoudige tests voor store sorting utilities (zonder pytest)
"""
from utils import extract_store_code_numeric, sort_stores_by_code, sort_store_ids
import sys


def test_extract_store_code_numeric():
    """Test extract_store_code_numeric functie"""
    print("\n=== Test extract_store_code_numeric ===")
    
    # Test numerieke string codes
    assert extract_store_code_numeric("001") == 1, "Failed: 001 should be 1"
    assert extract_store_code_numeric("010") == 10, "Failed: 010 should be 10"
    assert extract_store_code_numeric("100") == 100, "Failed: 100 should be 100"
    print("✓ Numerieke string codes")
    
    # Test directe numerieke codes
    assert extract_store_code_numeric(1) == 1, "Failed: 1 should be 1"
    assert extract_store_code_numeric(10) == 10, "Failed: 10 should be 10"
    print("✓ Directe numerieke codes")
    
    # Test leading digits extractie
    assert extract_store_code_numeric("001 - Amsterdam") == 1, "Failed: leading digits"
    assert extract_store_code_numeric("010 Utrecht") == 10, "Failed: leading digits"
    print("✓ Leading digits extractie")
    
    # Test ongeldige codes
    assert extract_store_code_numeric("ABC") == sys.maxsize, "Failed: invalid should be maxsize"
    assert extract_store_code_numeric("") == sys.maxsize, "Failed: empty should be maxsize"
    assert extract_store_code_numeric(None) == sys.maxsize, "Failed: None should be maxsize"
    print("✓ Ongeldige codes (maxsize)")
    
    print("✅ All extract_store_code_numeric tests passed!")


def test_sort_stores_by_code():
    """Test sort_stores_by_code functie"""
    print("\n=== Test sort_stores_by_code ===")
    
    # Test basis sortering
    stores = [
        {"store_id": "010", "store_name": "Utrecht"},
        {"store_id": "001", "store_name": "Amsterdam"},
        {"store_id": "100", "store_name": "Groningen"},
        {"store_id": "002", "store_name": "Rotterdam"},
    ]
    sorted_stores = sort_stores_by_code(stores)
    expected_order = ["001", "002", "010", "100"]
    actual_order = [s["store_id"] for s in sorted_stores]
    assert actual_order == expected_order, f"Failed: expected {expected_order}, got {actual_order}"
    print("✓ Basis sortering correct")
    
    # Test numeriek vs lexicografisch
    stores2 = [
        {"store_id": "10", "store_name": "Utrecht"},
        {"store_id": "2", "store_name": "Rotterdam"},
        {"store_id": "1", "store_name": "Amsterdam"},
        {"store_id": "100", "store_name": "Groningen"},
    ]
    sorted_stores2 = sort_stores_by_code(stores2)
    expected_order2 = ["1", "2", "10", "100"]  # Numeriek, NIET ["1", "10", "100", "2"]
    actual_order2 = [s["store_id"] for s in sorted_stores2]
    assert actual_order2 == expected_order2, f"Failed: expected {expected_order2}, got {actual_order2}"
    print("✓ Voorkomt lexicografische bug (10 voor 2)")
    
    # Test ongeldige codes onderaan
    stores3 = [
        {"store_id": "002", "store_name": "Rotterdam"},
        {"store_id": "XXX", "store_name": "Invalid 1"},
        {"store_id": "001", "store_name": "Amsterdam"},
    ]
    sorted_stores3 = sort_stores_by_code(stores3)
    codes = [s["store_id"] for s in sorted_stores3]
    assert codes[:2] == ["001", "002"], f"Failed: valid codes should be first, got {codes}"
    assert codes[2] == "XXX", f"Failed: invalid code should be last, got {codes}"
    print("✓ Ongeldige codes onderaan")
    
    print("✅ All sort_stores_by_code tests passed!")


def test_sort_store_ids():
    """Test sort_store_ids functie"""
    print("\n=== Test sort_store_ids ===")
    
    # Test basis sortering
    ids = ["010", "001", "100", "002"]
    sorted_ids = sort_store_ids(ids)
    expected = ["001", "002", "010", "100"]
    assert sorted_ids == expected, f"Failed: expected {expected}, got {sorted_ids}"
    print("✓ Basis sortering correct")
    
    # Test numeriek vs lexicografisch
    ids2 = ["10", "2", "1", "100"]
    sorted_ids2 = sort_store_ids(ids2)
    expected2 = ["1", "2", "10", "100"]  # NIET ["1", "10", "100", "2"]
    assert sorted_ids2 == expected2, f"Failed: expected {expected2}, got {sorted_ids2}"
    print("✓ Numerieke sortering correct (niet lexicografisch)")
    
    # Test lege lijst
    assert sort_store_ids([]) == [], "Failed: empty list should return empty list"
    print("✓ Lege lijst")
    
    print("✅ All sort_store_ids tests passed!")


def main():
    """Run alle tests"""
    print("=" * 60)
    print("Store Sorting Utilities Tests")
    print("=" * 60)
    
    try:
        test_extract_store_code_numeric()
        test_sort_stores_by_code()
        test_sort_store_ids()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

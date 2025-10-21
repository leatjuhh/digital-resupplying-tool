"""
Test negatieve voorraad handling
Verify dat negatieve voorraad waarden correct naar 0 worden geconverteerd
"""
import sys
from pdf_extract.normalizers import normalize_voorraad_value

def test_normalize_voorraad():
    """Test de normalize_voorraad_value functie met verschillende inputs"""
    
    print("=" * 80)
    print("TEST: Negatieve Voorraad Handling")
    print("=" * 80)
    
    test_cases = [
        # (input, expected_output, description)
        ("5", 5, "Positive number"),
        ("0", 0, "Zero"),
        (".", 0, "Dot (means zero)"),
        ("-", 0, "Dash (means zero)"),
        ("", 0, "Empty string"),
        ("-2", 0, "Negative number (should convert to 0)"),
        ("-5", 0, "Negative number (should convert to 0)"),
        ("-10", 0, "Negative double digit (should convert to 0)"),
        ("10", 10, "Positive double digit"),
        ("  3  ", 3, "Number with whitespace"),
        ("1a", 1, "Number with letter"),
    ]
    
    print("\nTest Cases:")
    print("-" * 80)
    
    passed = 0
    failed = 0
    
    for input_val, expected, description in test_cases:
        result = normalize_voorraad_value(input_val)
        status = "✓" if result == expected else "✗"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} Input: {repr(input_val):15s} → Output: {result:3d} (Expected: {expected:3d}) - {description}")
    
    print("\n" + "=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = test_normalize_voorraad()
    sys.exit(0 if success else 1)

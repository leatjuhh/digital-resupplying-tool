"""
Test script for PDF extraction
Tests against the golden sample PDF
"""
import sys
from pdf_extract import parse_pdf_to_records
from pathlib import Path

def test_pdf_extraction():
    """Test PDF extraction with the sample file"""
    
    # Path to test PDF
    pdf_path = Path("../dummyinfo/Interfiliaalverdeling vooraf - 423264.pdf")
    
    if not pdf_path.exists():
        print(f"❌ Test PDF not found: {pdf_path}")
        return False
    
    print(f"📄 Testing PDF extraction: {pdf_path}")
    print("=" * 70)
    
    # Parse the PDF
    try:
        result = parse_pdf_to_records(str(pdf_path))
    except Exception as e:
        print(f"❌ Parsing failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check for errors
    if result.errors:
        print("❌ Parsing completed with errors:")
        for error in result.errors:
            print(f"   - {error}")
        return False
    
    print("✓ PDF parsed successfully\n")
    
    # Display metadata
    print("📋 METADATA")
    print("-" * 70)
    for key, value in result.meta.items():
        print(f"  {key}: {value}")
    print()
    
    # Display sizes
    print(f"📏 SIZES DETECTED: {result.sizes}")
    print()
    
    # Display totals
    if result.totals:
        print("📊 TOTALS")
        print("-" * 70)
        print(f"  Filiaal: {result.totals.get('filiaal_naam', 'N/A')}")
        voorraad = result.totals.get('voorraad_per_maat', {})
        for size, count in voorraad.items():
            if count > 0:
                print(f"    {size}: {count}")
        print(f"  Verkocht: {result.totals.get('verkocht', 0)}")
        print()
    
    # Display sample rows
    print(f"📦 DATA ROWS ({len(result.rows)} total)")
    print("-" * 70)
    for i, row in enumerate(result.rows[:5], 1):  # Show first 5
        print(f"\n  Row {i}:")
        print(f"    Code: {row.get('filiaal_code')}")
        print(f"    Naam: {row.get('filiaal_naam')}")
        voorraad = row.get('voorraad_per_maat', {})
        non_zero = {k: v for k, v in voorraad.items() if v > 0}
        if non_zero:
            print(f"    Voorraad: {non_zero}")
        print(f"    Verkocht: {row.get('verkocht', 0)}")
    
    if len(result.rows) > 5:
        print(f"\n  ... and {len(result.rows) - 5} more rows")
    
    print("\n" + "=" * 70)
    
    # Validation checks against expected data
    print("\n🔍 VALIDATION CHECKS")
    print("-" * 70)
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Volgnummer should be 423264
    checks_total += 1
    expected_volgnummer = "423264"
    actual_volgnummer = result.meta.get("Volgnummer", "")
    if actual_volgnummer == expected_volgnummer:
        print(f"✓ Volgnummer correct: {actual_volgnummer}")
        checks_passed += 1
    else:
        print(f"✗ Volgnummer mismatch: expected {expected_volgnummer}, got {actual_volgnummer}")
    
    # Check 2: Should have 8 sizes (XXS to XXXL)
    checks_total += 1
    expected_sizes = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL"]
    if result.sizes == expected_sizes:
        print(f"✓ Sizes correct: {result.sizes}")
        checks_passed += 1
    else:
        print(f"✗ Sizes mismatch: expected {expected_sizes}, got {result.sizes}")
    
    # Check 3: Should have data rows
    checks_total += 1
    if len(result.rows) >= 10:
        print(f"✓ Has sufficient data rows: {len(result.rows)}")
        checks_passed += 1
    else:
        print(f"✗ Insufficient data rows: {len(result.rows)}")
    
    # Check 4: Should have totals
    checks_total += 1
    if result.totals and result.totals.get('voorraad_per_maat'):
        print(f"✓ Totals extracted")
        checks_passed += 1
    else:
        print(f"✗ Totals missing")
    
    # Check 5: Totals should match sum (if available)
    checks_total += 1
    if result.totals and result.rows:
        # Calculate sum of all voorraad for size S
        s_sum = sum(row.get('voorraad_per_maat', {}).get('S', 0) for row in result.rows)
        s_total = result.totals.get('voorraad_per_maat', {}).get('S', 0)
        if s_sum == s_total:
            print(f"✓ Totals validation passed (S: {s_sum} == {s_total})")
            checks_passed += 1
        else:
            print(f"✗ Totals validation failed (S: sum={s_sum}, total={s_total})")
    
    # Check 6: Specific filiaal should exist
    checks_total += 1
    filiaal_names = [row.get('filiaal_naam', '') for row in result.rows]
    if 'Panningen' in filiaal_names:
        print(f"✓ Found expected filiaal: Panningen")
        checks_passed += 1
    else:
        print(f"✗ Expected filiaal not found: Panningen")
    
    print()
    print("=" * 70)
    print(f"📈 RESULTS: {checks_passed}/{checks_total} checks passed")
    print("=" * 70)
    
    if checks_passed == checks_total:
        print("\n🎉 All checks passed! PDF extraction is working correctly.")
        return True
    else:
        print(f"\n⚠️  {checks_total - checks_passed} checks failed. Review the output above.")
        return False


if __name__ == "__main__":
    success = test_pdf_extraction()
    sys.exit(0 if success else 1)

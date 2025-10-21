"""
Test 54448.pdf voor negatieve voorraad detectie
"""
from pdf_extract import parse_pdf_to_records

result = parse_pdf_to_records('../dummyinfo/54448.pdf')

print("\n" + "=" * 80)
print("TEST: 54448.pdf Negatieve Voorraad Detectie")
print("=" * 80)

print(f"\nVolgnummer: {result.meta.get('Volgnummer')}")
print(f"Omschrijving: {result.meta.get('Omschrijving')}")

print(f"\n⚠️  NEGATIEVE VOORRAAD GEDETECTEERD: {len(result.negative_voorraad_detected)} instances")

if result.negative_voorraad_detected:
    print("\nDetails:")
    for item in result.negative_voorraad_detected:
        code = item.get('filiaal_code', '')
        naam = item.get('filiaal_naam', '')
        maat = item.get('maat', '')
        raw = item.get('raw_value', '')
        print(f"  🚫 [{code:3s}] {naam:30s} Maat {maat:6s}: {raw} → omgezet naar 0")
else:
    print("\n✓ Geen negatieve voorraad gedetecteerd")

print("\n" + "=" * 80)

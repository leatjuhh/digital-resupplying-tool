"""
Vergelijk geëxtraheerde data met de visuele PDF
Toont data in een leesbare vorm voor handmatige verificatie
"""
from pdf_extract import parse_pdf_to_records

def print_extraction_comparison():
    """Toon geëxtraheerde data vs verwachte data uit PDF"""
    
    pdf_path = "../dummyinfo/Interfiliaalverdeling vooraf - 423264.pdf"
    
    print("=" * 80)
    print("VERGELIJKING: Geëxtraheerde Data vs Visuele PDF")
    print("=" * 80)
    
    # Parse PDF
    result = parse_pdf_to_records(pdf_path)
    
    # Toon metadata
    print("\n📋 METADATA UIT PDF:")
    print("-" * 80)
    print(f"Volgnummer: {result.meta.get('Volgnummer', 'NIET GEVONDEN')}")
    print(f"Omschrijving: {result.meta.get('Omschrijving', 'NIET GEVONDEN')}")
    for key, value in result.meta.items():
        if key not in ['Volgnummer', 'Omschrijving']:
            print(f"{key}: {value}")
    
    # Verwachte data uit golden sample
    print("\n📋 VERWACHTE DATA UIT GOLDEN SAMPLE:")
    print("-" * 80)
    print("Volgnummer: 423264")
    print("Omschrijving: Brisia Peacock Top")
    print("Leverancier: 70 NED")
    print("Kleur: 32 pink")
    
    # Toon sizes
    print("\n📏 SIZES:")
    print("-" * 80)
    print(f"Geëxtraheerd: {result.sizes}")
    print(f"Verwacht:     ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']")
    
    # Toon totals
    print("\n📊 TOTAAL RIJ:")
    print("-" * 80)
    if result.totals:
        print(f"Geëxtraheerd Totaal:")
        voorraad = result.totals.get('voorraad_per_maat', {})
        print(f"  XXS: {voorraad.get('XXS', '?')}")
        print(f"  XS:  {voorraad.get('XS', '?')}")
        print(f"  S:   {voorraad.get('S', '?')}")
        print(f"  M:   {voorraad.get('M', '?')}")
        print(f"  L:   {voorraad.get('L', '?')}")
        print(f"  XL:  {voorraad.get('XL', '?')}")
        print(f"  XXL: {voorraad.get('XXL', '?')}")
        print(f"  XXXL: {voorraad.get('XXXL', '?')}")
        print(f"  Verkocht: {result.totals.get('verkocht', '?')}")
    else:
        print("GEEN TOTAAL GEVONDEN")
    
    print("\nVerwacht Totaal (uit PDF):")
    print("  XXS: . (0)")
    print("  XS:  . (0)")
    print("  S:   6")
    print("  M:   12")
    print("  L:   9")
    print("  XL:  8")
    print("  XXL: 5")
    print("  XXXL: . (0)")
    print("  Verkocht: 14")
    
    # Toon alle data rows in detail
    print("\n📦 ALLE DATA RIJEN (GEËXTRAHEERD):")
    print("=" * 80)
    
    for i, row in enumerate(result.rows, 1):
        code = row.get('filiaal_code', '')
        naam = row.get('filiaal_naam', '')
        voorraad = row.get('voorraad_per_maat', {})
        verkocht = row.get('verkocht', 0)
        
        print(f"\n{i:2d}. Code: {code:3s} | Naam: {naam:20s}")
        print(f"    Voorraad: XXS={voorraad.get('XXS', 0)} XS={voorraad.get('XS', 0)} " + 
              f"S={voorraad.get('S', 0)} M={voorraad.get('M', 0)} " +
              f"L={voorraad.get('L', 0)} XL={voorraad.get('XL', 0)} " +
              f"XXL={voorraad.get('XXL', 0)} XXXL={voorraad.get('XXXL', 0)}")
        print(f"    Verkocht: {verkocht}")
    
    # Verwachte data uit golden sample
    print("\n\n📦 VERWACHTE DATA RIJEN (UIT PDF):")
    print("=" * 80)
    
    expected_rows = [
        ("Totaal", "", {"XXS": 0, "XS": 0, "S": 6, "M": 12, "L": 9, "XL": 8, "XXL": 5, "XXXL": 0}, 14),
        ("0", "Centraal M", {"XXS": 0, "XS": 0, "S": 0, "M": 0, "L": 0, "XL": 0, "XXL": 0, "XXXL": 0}, 0),
        ("2", "Lumitex", {"XXS": 0, "XS": 0, "S": 0, "M": 0, "L": 0, "XL": 0, "XXL": 0, "XXXL": 0}, 0),
        ("3", "Mag Part.", {"XXS": 0, "XS": 0, "S": 0, "M": 0, "L": 0, "XL": 0, "XXL": 0, "XXXL": 0}, 0),
        ("5", "Panningen", {"XXS": 0, "XS": 0, "S": 1, "M": 1, "L": 0, "XL": 0, "XXL": 0, "XXXL": 0}, 6),
        ("6", "Echt", {"XXS": 0, "XS": 0, "S": 0, "M": 1, "L": 1, "XL": 1, "XXL": 1, "XXXL": 0}, 1),
        ("8", "Weert", {"XXS": 0, "XS": 0, "S": 1, "M": 1, "L": 1, "XL": 0, "XXL": 1, "XXXL": 0}, 1),
        ("9", "Stein", {"XXS": 0, "XS": 0, "S": 1, "M": 2, "L": 1, "XL": 1, "XXL": 0, "XXXL": 0}, 0),
        ("11", "Brunssum", {"XXS": 0, "XS": 0, "S": 0, "M": 1, "L": 1, "XL": 1, "XXL": 1, "XXXL": 0}, 1),
        ("12", "Kerkrade", {"XXS": 0, "XS": 0, "S": 0, "M": 1, "L": 1, "XL": 2, "XXL": 1, "XXXL": 0}, 1),
        ("13", "Budel", {"XXS": 0, "XS": 0, "S": 1, "M": 2, "L": 1, "XL": 1, "XXL": 0, "XXXL": 0}, 0),
        ("14", "OL Weert", {"XXS": 0, "XS": 0, "S": 0, "M": 0, "L": 0, "XL": 0, "XXL": 0, "XXXL": 0}, 0),
        ("15", "OL Sittard", {"XXS": 0, "XS": 0, "S": 0, "M": 0, "L": 0, "XL": 0, "XXL": 0, "XXXL": 0}, 0),
        ("16", "OL Roermon", {"XXS": 0, "XS": 0, "S": 0, "M": 0, "L": 0, "XL": 0, "XXL": 0, "XXXL": 0}, 0),
        ("27", "Klachten", {"XXS": 0, "XS": 0, "S": 0, "M": 0, "L": 0, "XL": 0, "XXL": 0, "XXXL": 0}, 0),
        ("31", "Tilburg", {"XXS": 0, "XS": 0, "S": 0, "M": 1, "L": 1, "XL": 1, "XXL": 1, "XXXL": 0}, 1),
        ("35", "Etten-Leur", {"XXS": 0, "XS": 0, "S": 1, "M": 1, "L": 1, "XL": 1, "XXL": 0, "XXXL": 0}, 2),
        ("38", "Tegelen", {"XXS": 0, "XS": 0, "S": 1, "M": 1, "L": 1, "XL": 0, "XXL": 0, "XXXL": 0}, 1),
        ("39", "OL Blerick", {"XXS": 0, "XS": 0, "S": 0, "M": 0, "L": 0, "XL": 0, "XXL": 0, "XXXL": 0}, 0),
        ("99", "Verschil", {"XXS": 0, "XS": 0, "S": 0, "M": 0, "L": 0, "XL": 0, "XXL": 0, "XXXL": 0}, 0),
    ]
    
    for i, (code, naam, voorraad, verkocht) in enumerate(expected_rows, 1):
        print(f"\n{i:2d}. Code: {code:3s} | Naam: {naam:20s}")
        print(f"    Voorraad: XXS={voorraad['XXS']} XS={voorraad['XS']} " + 
              f"S={voorraad['S']} M={voorraad['M']} " +
              f"L={voorraad['L']} XL={voorraad['XL']} " +
              f"XXL={voorraad['XXL']} XXXL={voorraad['XXXL']}")
        print(f"    Verkocht: {verkocht}")
    
    # Vergelijkingssamenvatting
    print("\n\n" + "=" * 80)
    print("VERGELIJKINGS SAMENVATTING")
    print("=" * 80)
    
    print(f"\nAantal rijen:")
    print(f"  Geëxtraheerd: {len(result.rows)}")
    print(f"  Verwacht:     {len([r for r in expected_rows if r[0] not in ['Totaal', '99']])}")  # Zonder Totaal en Verschil
    
    # Check if totals match
    if result.totals:
        totals_voorraad = result.totals.get('voorraad_per_maat', {})
        expected_totals = expected_rows[0][2]  # Totaal row
        
        print(f"\nTotalen vergelijking:")
        for size in ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']:
            extracted = totals_voorraad.get(size, 0)
            expected = expected_totals[size]
            match = "✓" if extracted == expected else "✗"
            print(f"  {size:4s}: Geëxtraheerd={extracted:2d}, Verwacht={expected:2d} {match}")
        
        extracted_verkocht = result.totals.get('verkocht', 0)
        expected_verkocht = expected_rows[0][3]
        match = "✓" if extracted_verkocht == expected_verkocht else "✗"
        print(f"  Verkocht: Geëxtraheerd={extracted_verkocht:2d}, Verwacht={expected_verkocht:2d} {match}")


if __name__ == "__main__":
    print_extraction_comparison()

"""
Gedetailleerd rapport per PDF voor handmatige verificatie
"""
import os
import glob
from pdf_extract import parse_pdf_to_records

def generate_detailed_report():
    """Genereer gedetailleerd rapport per PDF"""
    
    pdf_folder = "../dummyinfo"
    pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf"))
    
    for pdf_path in sorted(pdf_files):
        filename = os.path.basename(pdf_path)
        
        print("\n" + "=" * 100)
        print(f"📄 BESTAND: {filename}")
        print("=" * 100)
        
        result = parse_pdf_to_records(pdf_path)
        
        # METADATA
        print("\n📋 METADATA:")
        print("-" * 100)
        for key, value in result.meta.items():
            print(f"  {key}: {value}")
        
        # MAATBALK
        print(f"\n📏 MAATBALK: {result.sizes}")
        
        # NEGATIEVE VOORRAAD DETECTIE
        if result.negative_voorraad_detected:
            print(f"\n⚠️  NEGATIEVE VOORRAAD GEDETECTEERD ({len(result.negative_voorraad_detected)} instances):")
            print("-" * 100)
            for item in result.negative_voorraad_detected:
                code = item.get('filiaal_code', '')
                naam = item.get('filiaal_naam', '')
                maat = item.get('maat', '')
                raw = item.get('raw_value', '')
                print(f"  🚫 [{code:3s}] {naam:30s} Maat {maat:6s}: {raw} → omgezet naar 0")
        
        # TOTAAL RIJ
        if result.totals:
            print(f"\n📊 TOTAAL RIJ:")
            print("-" * 100)
            voorraad = result.totals.get('voorraad_per_maat', {})
            verkocht = result.totals.get('verkocht', 0)
            
            # Toon per maat
            print("  Voorraad per maat:")
            for size in result.sizes:
                print(f"    {size:6s}: {voorraad.get(size, 0):3d}")
            print(f"  Verkocht: {verkocht}")
            print(f"  Totaal voorraad: {sum(voorraad.values())}")
        
        # ALLE DATA RIJEN
        print(f"\n📦 ALLE DATA RIJEN ({len(result.rows)} totaal):")
        print("=" * 100)
        
        for i, row in enumerate(result.rows, 1):
            code = row.get('filiaal_code', '')
            naam = row.get('filiaal_naam', '')
            voorraad = row.get('voorraad_per_maat', {})
            verkocht = row.get('verkocht', 0)
            
            # Alleen rijen met voorraad of verkocht tonen in detail
            has_data = any(v > 0 for v in voorraad.values()) or verkocht > 0
            
            if has_data:
                print(f"\n{i:2d}. [{code:3s}] {naam}")
                
                # Toon alleen maten met voorraad > 0
                voorraad_str = ", ".join([f"{size}={v}" for size, v in voorraad.items() if v > 0])
                if voorraad_str:
                    print(f"     Voorraad: {voorraad_str}")
                
                if verkocht > 0:
                    print(f"     Verkocht: {verkocht}")
            else:
                # Korte weergave voor lege rijen
                print(f"{i:2d}. [{code:3s}] {naam:30s} - leeg")
        
        print("\n" + "=" * 100)
        print()


if __name__ == "__main__":
    generate_detailed_report()

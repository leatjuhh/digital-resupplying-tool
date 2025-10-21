"""
Batch test script voor alle PDF's in dummyinfo folder
Test de extractie en toon resultaten per bestand
"""
import os
import glob
from pdf_extract import parse_pdf_to_records

def test_all_pdfs():
    """Test alle PDFs en toon overzicht"""
    
    pdf_folder = "../dummyinfo"
    pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf"))
    
    print("=" * 100)
    print("BATCH TEST: Alle PDFs in dummyinfo folder")
    print("=" * 100)
    print(f"\nGevonden PDFs: {len(pdf_files)}\n")
    
    results = []
    
    for pdf_path in sorted(pdf_files):
        filename = os.path.basename(pdf_path)
        print("\n" + "=" * 100)
        print(f"📄 BESTAND: {filename}")
        print("=" * 100)
        
        try:
            # Parse PDF
            result = parse_pdf_to_records(pdf_path)
            
            # Toon metadata
            print("\n📋 METADATA:")
            print("-" * 80)
            volgnummer = result.meta.get('Volgnummer', 'NIET GEVONDEN')
            omschrijving = result.meta.get('Omschrijving', 'NIET GEVONDEN')
            print(f"  Volgnummer: {volgnummer}")
            print(f"  Omschrijving: {omschrijving}")
            
            # Toon sizes
            print(f"\n📏 MAATBALK:")
            print("-" * 80)
            if result.sizes:
                print(f"  Gevonden: {result.sizes}")
                print(f"  Aantal: {len(result.sizes)}")
            else:
                print("  ⚠️  GEEN MATEN GEVONDEN")
            
            # Toon data
            print(f"\n📊 DATA:")
            print("-" * 80)
            print(f"  Aantal rijen: {len(result.rows)}")
            if result.totals:
                voorraad = result.totals.get('voorraad_per_maat', {})
                total_voorraad = sum(voorraad.values())
                print(f"  Totaal voorraad: {total_voorraad}")
                print(f"  Totaal verkocht: {result.totals.get('verkocht', 0)}")
            
            # Toon sample rijen
            if result.rows:
                print(f"\n  Sample rijen (eerste 3):")
                for i, row in enumerate(result.rows[:3], 1):
                    naam = row.get('filiaal_naam', 'N/A')
                    voorraad = row.get('voorraad_per_maat', {})
                    non_zero = {k: v for k, v in voorraad.items() if v > 0}
                    verkocht = row.get('verkocht', 0)
                    print(f"    {i}. {naam}: voorraad={non_zero}, verkocht={verkocht}")
            
            # Toon errors/warnings
            if result.errors:
                print(f"\n❌ ERRORS ({len(result.errors)}):")
                for error in result.errors[:3]:  # Max 3
                    print(f"  - {error}")
            
            if result.warnings:
                print(f"\n⚠️  WARNINGS ({len(result.warnings)}):")
                for warning in result.warnings[:3]:
                    print(f"  - {warning}")
            
            # Status
            status = "✓ SUCCESS" if not result.errors else "✗ FAILED"
            if result.errors and result.rows:
                status = "⚠️  PARTIAL SUCCESS"
            
            print(f"\n{status}")
            
            # Bewaar resultaat
            results.append({
                'filename': filename,
                'status': status,
                'volgnummer': volgnummer,
                'omschrijving': omschrijving,
                'sizes': result.sizes,
                'row_count': len(result.rows),
                'has_totals': bool(result.totals),
                'errors': len(result.errors)
            })
            
        except Exception as e:
            print(f"\n❌ EXCEPTION: {str(e)}")
            results.append({
                'filename': filename,
                'status': '✗ EXCEPTION',
                'error': str(e)
            })
    
    # Samenvatting
    print("\n\n" + "=" * 100)
    print("📈 SAMENVATTING")
    print("=" * 100)
    
    success_count = sum(1 for r in results if '✓' in r['status'])
    partial_count = sum(1 for r in results if '⚠️' in r['status'])
    failed_count = sum(1 for r in results if '✗' in r['status'])
    
    print(f"\nTotaal bestanden: {len(results)}")
    print(f"  ✓ Succesvol: {success_count}")
    print(f"  ⚠️  Gedeeltelijk: {partial_count}")
    print(f"  ✗ Mislukt: {failed_count}")
    
    print("\n" + "-" * 100)
    print(f"{'Bestand':<50} {'Status':<20} {'Maten':<15} {'Rijen':<10}")
    print("-" * 100)
    
    for r in results:
        filename = r['filename'][:47] + "..." if len(r['filename']) > 50 else r['filename']
        status = r['status']
        sizes = str(len(r.get('sizes', []))) + " maten" if r.get('sizes') else "N/A"
        rows = str(r.get('row_count', 0))
        
        print(f"{filename:<50} {status:<20} {sizes:<15} {rows:<10}")
    
    # Detecteer maatbalk variaties
    print("\n" + "=" * 100)
    print("🔍 MAATBALK ANALYSE")
    print("=" * 100)
    
    size_patterns = {}
    for r in results:
        if r.get('sizes'):
            pattern = tuple(r['sizes'])
            if pattern not in size_patterns:
                size_patterns[pattern] = []
            size_patterns[pattern].append(r['filename'])
    
    print(f"\nGevonden {len(size_patterns)} verschillende maatbalk variaties:\n")
    for i, (pattern, files) in enumerate(size_patterns.items(), 1):
        print(f"{i}. {list(pattern)}")
        print(f"   Bestanden: {', '.join(files)}")
        print()


if __name__ == "__main__":
    test_all_pdfs()

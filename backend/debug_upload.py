"""
Debug script voor PDF upload issues
Helpt bij het diagnosticeren van PDF extractie problemen
"""
import sys
from pdf_extract import parse_pdf_to_records
import json

def debug_pdf_extraction(pdf_path: str):
    """
    Debug PDF extractie en toon gedetailleerde output
    
    Args:
        pdf_path: Path naar de PDF file
    """
    print(f"\n{'='*60}")
    print(f"DEBUGGING PDF EXTRACTION")
    print(f"{'='*60}")
    print(f"File: {pdf_path}\n")
    
    # Parse PDF
    result = parse_pdf_to_records(pdf_path)
    
    # Toon metadata
    print(f"\n{'='*60}")
    print("METADATA")
    print(f"{'='*60}")
    if result.meta:
        for key, value in result.meta.items():
            print(f"{key}: {value}")
    else:
        print("⚠️  Geen metadata gevonden")
    
    # Toon maten
    print(f"\n{'='*60}")
    print("MATEN (SIZES)")
    print(f"{'='*60}")
    if result.sizes:
        print(f"Gevonden maten: {', '.join(result.sizes)}")
    else:
        print("⚠️  Geen maten gevonden")
    
    # Toon aantal rijen
    print(f"\n{'='*60}")
    print("DATA RIJEN")
    print(f"{'='*60}")
    print(f"Aantal rijen: {len(result.rows)}")
    
    if result.rows:
        print("\nEerste 3 rijen:")
        for i, row in enumerate(result.rows[:3], 1):
            print(f"\n  Rij {i}:")
            print(f"    Filiaal Code: {row.get('filiaal_code', 'N/A')}")
            print(f"    Filiaal Naam: {row.get('filiaal_naam', 'N/A')}")
            print(f"    Verkocht: {row.get('verkocht', 0)}")
            voorraad = row.get('voorraad_per_maat', {})
            if voorraad:
                print(f"    Voorraad: {voorraad}")
            else:
                print(f"    Voorraad: Geen voorraad data")
    
    # Toon totalen
    print(f"\n{'='*60}")
    print("TOTALEN")
    print(f"{'='*60}")
    if result.totals:
        print(f"Totaal rij gevonden:")
        print(f"  Filiaal: {result.totals.get('filiaal_naam', 'N/A')}")
        print(f"  Verkocht: {result.totals.get('verkocht', 0)}")
        voorraad = result.totals.get('voorraad_per_maat', {})
        if voorraad:
            print(f"  Voorraad: {voorraad}")
    else:
        print("Geen totaal rij gevonden")
    
    # Toon verschillen
    if result.difference:
        print(f"\n{'='*60}")
        print("VERSCHILLEN")
        print(f"{'='*60}")
        print(f"Verschil rij gevonden:")
        print(f"  Filiaal: {result.difference.get('filiaal_naam', 'N/A')}")
        print(f"  Verkocht: {result.difference.get('verkocht', 0)}")
        voorraad = result.difference.get('voorraad_per_maat', {})
        if voorraad:
            print(f"  Voorraad: {voorraad}")
    
    # Toon negatieve voorraad waarschuwingen
    if result.negative_voorraad_detected:
        print(f"\n{'='*60}")
        print("⚠️  NEGATIEVE VOORRAAD GEDETECTEERD")
        print(f"{'='*60}")
        for neg in result.negative_voorraad_detected[:5]:
            print(f"  {neg}")
    
    # Toon fouten
    print(f"\n{'='*60}")
    print("FOUTEN EN WAARSCHUWINGEN")
    print(f"{'='*60}")
    
    if result.errors:
        print(f"\n❌ FOUTEN ({len(result.errors)}):")
        for i, error in enumerate(result.errors, 1):
            print(f"  {i}. {error}")
    else:
        print("✅ Geen fouten")
    
    if result.warnings:
        print(f"\n⚠️  WAARSCHUWINGEN ({len(result.warnings)}):")
        for i, warning in enumerate(result.warnings, 1):
            print(f"  {i}. {warning}")
    else:
        print("✅ Geen waarschuwingen")
    
    # Samenvatting
    print(f"\n{'='*60}")
    print("SAMENVATTING")
    print(f"{'='*60}")
    
    is_valid = (
        result.meta and 
        result.sizes and 
        result.rows and 
        not result.errors
    )
    
    if is_valid:
        print("✅ PDF extractie succesvol")
        print(f"   - {len(result.rows)} winkelfilialen")
        print(f"   - {len(result.sizes)} maten")
        print(f"   - Volgnummer: {result.meta.get('Volgnummer', 'N/A')}")
        print(f"   - Omschrijving: {result.meta.get('Omschrijving', 'N/A')}")
    else:
        print("❌ PDF extractie MISLUKT")
        
        if not result.meta:
            print("   - Geen metadata gevonden (Volgnummer, Omschrijving, etc.)")
        if not result.sizes:
            print("   - Geen maten gedetecteerd (bijv. 34, 36, S, M, L)")
        if not result.rows:
            print("   - Geen data rijen gevonden (winkelfilialen)")
        if result.errors:
            print(f"   - {len(result.errors)} fout(en) gevonden (zie boven)")
    
    print(f"\n{'='*60}\n")
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_upload.py <path_to_pdf>")
        print("\nExample:")
        print("  python debug_upload.py backend/uploads/pdf_batches/batch_1/voorraad.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    try:
        result = debug_pdf_extraction(pdf_path)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR:")
        print(f"   {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)

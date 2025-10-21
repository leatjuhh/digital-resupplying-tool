"""
PDF Parser voor voorraad documenten
Gebaseerd op pdfplumber (beproefd in oud project)
"""
import pdfplumber
import re
from typing import Dict, List, Optional


def parse_voorraad_pdf(pdf_path: str) -> Dict:
    """
    Parse een voorraad PDF en extracteer artikelnummers
    
    Args:
        pdf_path: Pad naar het PDF bestand
        
    Returns:
        Dictionary met parsed data:
        {
            "artikelnummers": ["423264", "423265", ...],
            "raw_text": "...",
            "page_count": 3
        }
    """
    try:
        # Open PDF met pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            all_lines = []
            
            # Extraheer tekst per pagina
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_lines.extend(text.split("\n"))
            
            # Filter de regels (verwijder headers en footers)
            # Aanname: eerste 10 regels = header, laatste regel = totaal
            filtered_lines = all_lines[10:-1] if len(all_lines) > 11 else all_lines
            
            # Extracteer artikelnummers (5-6 cijfers aan begin van regel)
            artikelnummers = []
            for line in filtered_lines:
                # Pak eerste element (vóór eerste spatie)
                parts = line.split()
                if parts:
                    first_part = parts[0]
                    # Check of het een geldig artikelnummer is (5-6 cijfers)
                    if re.match(r'^\d{5,6}$', first_part):
                        artikelnummers.append(first_part)
            
            return {
                "success": True,
                "artikelnummers": artikelnummers,
                "raw_text": "\n".join(all_lines[:100]),  # Eerste 100 regels voor debugging
                "page_count": len(pdf.pages),
                "total_lines": len(all_lines),
                "extracted_count": len(artikelnummers)
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "artikelnummers": []
        }


def parse_interfiliaal_pdf(pdf_path: str) -> Dict:
    """
    Parse een interfiliaal verdeling PDF
    Meer geavanceerde parsing voor volledige voorraad data
    
    TODO: Implementeer volledige parsing met winkels, maten, aantallen
    Voor nu: basis extractie
    """
    result = parse_voorraad_pdf(pdf_path)
    
    # In toekomst: parse ook winkel namen, maten, aantallen
    # Voor nu: return basis artikelnummers
    
    return result


# Utility functies
def validate_pdf(pdf_path: str) -> bool:
    """Check of PDF geldig is en kan worden geopend"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return len(pdf.pages) > 0
    except:
        return False

"""
Text normalization and correction utilities
Handles common extraction issues and standardizes data
"""
import re
from typing import Optional, Dict, List
from .extract_settings import FILIAAL_NAME_MAPPINGS


def normalize_filiaal_name(raw_name: str) -> str:
    """
    Normalize filiaal names, handling common abbreviations and splitting
    
    Args:
        raw_name: Raw extracted filiaal name
        
    Returns:
        Normalized filiaal name
    """
    if not raw_name or not raw_name.strip():
        return raw_name
    
    # Remove extra whitespace
    name = ' '.join(raw_name.split())
    
    # Check for direct mappings
    if name in FILIAAL_NAME_MAPPINGS:
        return FILIAAL_NAME_MAPPINGS[name]
    
    # Handle split names (e.g., "OL Weert" -> "Outlet Weert")
    for abbrev, full in FILIAAL_NAME_MAPPINGS.items():
        if name.startswith(abbrev + ' '):
            # Replace abbreviation with full name
            name = name.replace(abbrev + ' ', full + ' ', 1)
            break
    
    return name


def normalize_size(raw_size: str) -> str:
    """
    Normalize size labels
    
    Args:
        raw_size: Raw size string
        
    Returns:
        Normalized size
    """
    if not raw_size:
        return raw_size
    
    # Remove whitespace
    size = raw_size.strip()
    
    # Uppercase for letter sizes
    if re.match(r'^[XxSsLlMm]+$', size):
        size = size.upper()
    
    return size


def normalize_voorraad_value(raw_value: str, track_negative: bool = False) -> tuple[int, bool]:
    """
    Convert voorraad values to integers
    Handles ".", empty strings, and various formats
    
    BUSINESS RULE: Negative voorraad values are converted to 0
    This aligns with manual redistribution practice where negative 
    inventory cannot be redistributed.
    
    Args:
        raw_value: Raw value from PDF
        track_negative: If True, return tuple (value, is_negative)
        
    Returns:
        If track_negative=False: Integer voorraad value (0 if empty/invalid/negative)
        If track_negative=True: Tuple of (value, was_negative_flag)
    """
    if not raw_value or not isinstance(raw_value, str):
        return (0, False) if track_negative else 0
    
    # Remove whitespace
    value = raw_value.strip()
    
    # Handle empty or "." (which means 0)
    if not value or value == '.' or value == '-':
        return (0, False) if track_negative else 0
    
    was_negative = False
    
    # Try to parse as integer (including negative values)
    try:
        parsed_value = int(value)
        
        # BUSINESS RULE: Convert negative voorraad to 0
        # Negative inventory cannot be redistributed
        if parsed_value < 0:
            was_negative = True
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"[NEGATIVE_VOORRAAD] Detected negative voorraad value '{raw_value}', converting to 0")
            return (0, True) if track_negative else 0
        
        return (parsed_value, False) if track_negative else parsed_value
    except ValueError:
        # Try removing non-numeric characters (but preserve minus sign)
        cleaned = re.sub(r'[^\d\-]', '', value)
        if cleaned:
            try:
                parsed_value = int(cleaned)
                
                # BUSINESS RULE: Convert negative voorraad to 0
                if parsed_value < 0:
                    was_negative = True
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"[NEGATIVE_VOORRAAD] Detected negative voorraad value '{raw_value}', converting to 0")
                    return (0, True) if track_negative else 0
                
                return (parsed_value, False) if track_negative else parsed_value
            except ValueError:
                pass
    
    return (0, False) if track_negative else 0


def normalize_verkocht_value(raw_value: str) -> int:
    """
    Convert verkocht (sold) values to integers
    Same logic as voorraad values
    
    Args:
        raw_value: Raw value from PDF
        
    Returns:
        Integer verkocht value
    """
    return normalize_voorraad_value(raw_value)


def clean_cell_text(text: str) -> str:
    """
    Clean cell text from tables
    Removes extra whitespace, newlines, etc.
    
    Args:
        text: Raw cell text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Replace newlines with spaces
    text = text.replace('\n', ' ')
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def parse_metadata_line(line: str) -> Optional[tuple[str, str]]:
    """
    Parse a metadata line (key : value format)
    
    Args:
        line: Raw line from PDF
        
    Returns:
        Tuple of (key, value) or None if not a valid metadata line
    """
    if ':' not in line:
        return None
    
    parts = line.split(':', 1)
    if len(parts) != 2:
        return None
    
    key = parts[0].strip()
    value = parts[1].strip()
    
    return (key, value)


def extract_article_number(text: str) -> Optional[str]:
    """
    Extract article number from text
    Looks for 5-6 digit numbers
    
    Args:
        text: Text to search
        
    Returns:
        Article number or None
    """
    match = re.search(r'\b\d{5,6}\b', text)
    if match:
        return match.group(0)
    return None


def combine_split_filiaal(cells: List[str], start_idx: int) -> tuple[str, int]:
    """
    Combine filiaal names that were split across cells
    Example: ["OL", "Weert"] -> "OL Weert"
    
    Args:
        cells: List of cell values
        start_idx: Starting index in cells
        
    Returns:
        Tuple of (combined_name, next_index)
    """
    if start_idx >= len(cells):
        return ("", start_idx)
    
    # Start with the first cell
    name_parts = [cells[start_idx]]
    next_idx = start_idx + 1
    
    # Check if next cell(s) might be part of the name
    # This happens when a filiaal name was split (e.g., "OL" "Weert")
    # We look ahead up to 2 cells
    while next_idx < len(cells) and next_idx < start_idx + 3:
        next_cell = cells[next_idx].strip()
        
        # If next cell looks like a size or number, stop
        if re.match(r'^[.\d]+$', next_cell) or re.match(r'^X{0,3}[SML]$', next_cell):
            break
        
        # If it's a word, it might be part of the name
        if next_cell and not next_cell.isdigit():
            name_parts.append(next_cell)
            next_idx += 1
        else:
            break
    
    combined = ' '.join(name_parts)
    return (combined, next_idx)


def is_totals_row(filiaal_name: str) -> bool:
    """
    Check if a row is the totals row
    
    Args:
        filiaal_name: Filiaal name to check
        
    Returns:
        True if this is a totals row
    """
    name_lower = filiaal_name.lower().strip()
    return name_lower in ['totaal', 'total', 'totals']


def is_verschil_row(filiaal_name: str) -> bool:
    """
    Check if a row is the verschil (difference) row
    
    Args:
        filiaal_name: Filiaal name to check
        
    Returns:
        True if this is a verschil row
    """
    name_lower = filiaal_name.lower().strip()
    return name_lower in ['verschil', 'difference']


def validate_filiaal_code(code: str) -> bool:
    """
    Validate that a filiaal code looks correct
    Should be 1-3 digits
    
    Args:
        code: Code to validate
        
    Returns:
        True if valid
    """
    if not code:
        return False
    return bool(re.match(r'^\d{1,3}$', code))


def normalize_metadata_value(key: str, value: str) -> str:
    """
    Normalize metadata values based on their key
    
    Args:
        key: Metadata key
        value: Raw value
        
    Returns:
        Normalized value
    """
    # Clean whitespace
    value = value.strip()
    
    # Specific normalizations based on key
    if key.lower() in ['volgnummer', 'artikelnummer']:
        # Extract only the first number (before any space or next field)
        # e.g., "423264 Leverancier" -> "423264"
        match = re.match(r'^(\d+)', value)
        if match:
            value = match.group(1)
        else:
            # Fallback: keep only digits
            value = re.sub(r'[^\d]', '', value)
    
    elif key.lower() == 'omschrijving':
        # Remove trailing text like "Laatste leverdatum:"
        value = re.sub(r'\s*Laatste\s+leverdatum:?\s*$', '', value)
    
    elif key.lower() == 'leverancier':
        # Format: "70 NED" - keep both parts
        value = value.strip()
    
    elif key.lower() == 'kleur':
        # Format: "32 pink" - keep both parts
        value = value.strip()
    
    return value

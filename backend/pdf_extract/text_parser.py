"""
Text-based PDF parser
For PDFs where table extraction doesn't work well
"""
import re
from typing import List, Dict, Tuple, Optional
from .normalizers import (
    normalize_filiaal_name,
    normalize_size,
    normalize_voorraad_value,
    normalize_verkocht_value,
    is_totals_row,
    is_verschil_row,
)


def parse_from_text_lines(text: str) -> Tuple[List[str], List[Dict], Dict, Dict, List[Dict]]:
    """
    Parse voorraad data from plain text lines
    
    Args:
        text: Raw text from PDF
        
    Returns:
        Tuple of (sizes, rows, totals, difference, negative_voorraad_detected)
    """
    lines = text.split('\n')
    negative_voorraad_detected = []
    
    # Find the size header line (contains sizes like XXS/XS/S/M/L or 34/36/38/40)
    size_line_idx = None
    for idx, line in enumerate(lines):
        # Check for letter sizes pattern
        if re.search(r'\bXXS\b.*\bXS\b.*\bS\b.*\bM\b.*\bL\b', line):
            size_line_idx = idx
            break
        # Check for numeric sizes pattern (at least 4 two-digit numbers in sequence)
        if re.search(r'\b\d{2}\b.*\b\d{2}\b.*\b\d{2}\b.*\b\d{2}\b', line):
            # Make sure it's the right line (should contain "maat" or appear after "Filiaal")
            if 'maat' in line.lower() or (idx > 0 and 'filiaal' in lines[idx-1].lower()):
                size_line_idx = idx
                break
    
    if size_line_idx is None:
        return [], [], {}, {}
    
    # Extract sizes from the size line
    size_line = lines[size_line_idx]
    sizes = extract_sizes_from_line(size_line)
    
    # Parse data rows (everything after size line)
    rows = []
    totals = {}
    difference = {}
    
    for line_idx in range(size_line_idx + 1, len(lines)):
        line = lines[line_idx].strip()
        
        if not line:
            continue
        
        # Check if line starts with "Totaal" - special handling needed
        # because it appears before other data rows
        if line.lower().startswith('totaal'):
            # Parse totaal line directly
            parsed = parse_data_line(line, sizes)
            if parsed:
                totals = parsed
            continue
        
        # Parse the row
        parsed = parse_data_line(line, sizes)
        
        if not parsed:
            continue
        
        filiaal_naam = parsed['filiaal_naam']
        
        # Skip rows without a valid name
        if not filiaal_naam or not filiaal_naam.strip():
            continue
        
        # Collect negative voorraad info if present
        if 'negative_voorraad' in parsed:
            negative_voorraad_detected.extend(parsed['negative_voorraad'])
            # Remove from parsed dict as it's tracked separately
            del parsed['negative_voorraad']
        
        # Check if verschil
        if is_verschil_row(filiaal_naam):
            difference = parsed
        else:
            rows.append(parsed)
    
    return sizes, rows, totals, difference, negative_voorraad_detected


def extract_sizes_from_line(line: str) -> List[str]:
    """
    Extract size labels from header line
    
    Args:
        line: Header line containing sizes
        
    Returns:
        List of size labels
    """
    sizes = []
    
    # Check for numeric sizes first (34, 36, 38, 40, 42, 44, 46, 48, 50, 52, etc.)
    numeric_sizes = re.findall(r'\b(\d{2})\b', line)
    if numeric_sizes and len(numeric_sizes) >= 3:
        # Looks like numeric sizes - filter to common clothing sizes
        valid_numeric = [s for s in numeric_sizes if 30 <= int(s) <= 60]
        if len(valid_numeric) >= 3:
            return valid_numeric
    
    # Check for letter-based sizes
    size_patterns = [
        r'\bXXXL\b',
        r'\bXXL\b',
        r'\bXL\b',
        r'\bXXS\b',
        r'\bXS\b',
        r'\bS\b',
        r'\bM\b',
        r'\bL\b',
    ]
    
    for pattern in size_patterns:
        if re.search(pattern, line):
            size = pattern.replace(r'\b', '').strip()
            if size not in sizes:
                sizes.append(size)
    
    # Sort letter sizes in standard order
    if sizes and not sizes[0].isdigit():
        size_order = ['XXXS', 'XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
        sizes = sorted(sizes, key=lambda x: size_order.index(x) if x in size_order else 999)
    
    return sizes


def parse_data_line(line: str, sizes: List[str]) -> Optional[Dict]:
    """
    Parse a single data line
    Format: "CODE NAME VALUE VALUE VALUE ... VERKOCHT"
    
    Args:
        line: Line to parse
        sizes: List of expected sizes
        
    Returns:
        Parsed dict or None
    """
    # Split line into parts
    parts = line.split()
    
    if len(parts) < 3:
        return None
    
    # First part is filiaal code (may be empty or numeric)
    filiaal_code = parts[0] if parts[0].isdigit() else ""
    
    # Find where the name ends and values begin
    # Values are typically "." or numbers
    name_parts = []
    value_start_idx = 1
    
    for idx in range(1, len(parts)):
        part = parts[idx]
        # If it's a dot or number, this is where values start
        if part == '.' or part.replace('.', '').isdigit():
            value_start_idx = idx
            break
        else:
            name_parts.append(part)
    
    filiaal_naam = ' '.join(name_parts)
    filiaal_naam = normalize_filiaal_name(filiaal_naam)
    
    # Extract values for each size
    value_parts = parts[value_start_idx:]
    
    # The number of sizes determines how many values to extract
    # Plus one more for verkocht at the end
    expected_count = len(sizes) + 1
    
    # If we don't have enough parts, pad with dots
    while len(value_parts) < expected_count:
        value_parts.append('.')
    
    # Map sizes to values
    voorraad_per_maat = {}
    negative_voorraad_info = []
    
    for i, size in enumerate(sizes):
        if i < len(value_parts):
            value = value_parts[i]
            # Check for negative voorraad
            normalized, was_negative = normalize_voorraad_value(value, track_negative=True)
            voorraad_per_maat[size] = normalized
            
            # Track negative voorraad detection
            if was_negative:
                negative_voorraad_info.append({
                    'filiaal_code': filiaal_code if filiaal_code else "",
                    'filiaal_naam': filiaal_naam,
                    'maat': size,
                    'raw_value': value,
                    'normalized_value': 0
                })
        else:
            voorraad_per_maat[size] = 0
    
    # Last value (or close to last) should be verkocht
    # Sometimes there's a trailing "." so we need to handle that
    # Also handle cases like "1 4." which should be "14"
    verkocht = 0
    if len(value_parts) >= len(sizes):
        # Try to combine last numeric values (e.g., "1 4" -> "14")
        verkocht_parts = []
        for idx in range(len(sizes), len(value_parts)):
            val = value_parts[idx].rstrip('.')
            if val and val != '.' and val.isdigit():
                verkocht_parts.append(val)
        
        if verkocht_parts:
            # Combine into single number
            verkocht_str = ''.join(verkocht_parts)
            verkocht = normalize_verkocht_value(verkocht_str)
    
    result = {
        'filiaal_code': filiaal_code,
        'filiaal_naam': filiaal_naam,
        'voorraad_per_maat': voorraad_per_maat,
        'verkocht': verkocht
    }
    
    # Add negative voorraad info if any detected
    if negative_voorraad_info:
        result['negative_voorraad'] = negative_voorraad_info
    
    return result

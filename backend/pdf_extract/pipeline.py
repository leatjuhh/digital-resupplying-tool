"""
Main PDF extraction pipeline
Converts voorraad PDF reports to structured data
"""
import pdfplumber
import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from .extract_settings import (
    TABLE_SETTINGS,
    TABLE_SETTINGS_TEXT_FALLBACK,
    HEADER_KEYWORDS,
    KNOWN_SIZE_PATTERNS,
)
from .normalizers import (
    normalize_filiaal_name,
    normalize_size,
    normalize_voorraad_value,
    normalize_verkocht_value,
    clean_cell_text,
    parse_metadata_line,
    combine_split_filiaal,
    is_totals_row,
    is_verschil_row,
    validate_filiaal_code,
    normalize_metadata_value,
)
from .text_parser import parse_from_text_lines

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ParsedDoc:
    """Structure for parsed PDF document"""
    meta: Dict[str, str] = field(default_factory=dict)
    sizes: List[str] = field(default_factory=list)
    rows: List[Dict[str, Any]] = field(default_factory=list)
    totals: Dict[str, Any] = field(default_factory=dict)
    difference: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    negative_voorraad_detected: List[Dict[str, Any]] = field(default_factory=list)  # Track negative inventory


def parse_pdf_to_records(pdf_path: str) -> ParsedDoc:
    """
    Main entry point: Parse PDF voorraad report to structured records
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        ParsedDoc with all extracted data
    """
    logger.info(f"[PARSE_START] Starting parse of: {pdf_path}")
    result = ParsedDoc()
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"[PDF_OPEN] Opened PDF with {len(pdf.pages)} pages")
            
            # Phase 1: Extract metadata from first page
            if pdf.pages:
                result.meta = extract_metadata(pdf.pages[0])
                logger.info(f"[HEADER_PARSE] Extracted metadata: {result.meta}")
            
            # Phase 2: Extract table data from all pages
            all_table_rows = []
            for page_num, page in enumerate(pdf.pages, 1):
                logger.info(f"[PAGE_PARSE] Processing page {page_num}")
                page_rows = extract_table_from_page(page, page_num)
                all_table_rows.extend(page_rows)
            
            logger.info(f"[TABLE_PARSE] Extracted {len(all_table_rows)} total rows")
            
            # Phase 3: Parse and structure the rows
            if all_table_rows:
                result.sizes, result.rows, result.totals, result.difference = \
                    parse_table_rows(all_table_rows)
                logger.info(f"[ROW_PARSE] Parsed {len(result.rows)} data rows, sizes: {result.sizes}")
                
                # If table parsing didn't work well, try text-based parsing
                if not result.sizes or len(result.rows) < 5:
                    logger.info("[TEXT_FALLBACK] Table parsing insufficient, trying text-based parser")
                    text = pdf.pages[0].extract_text()
                    result.sizes, result.rows, result.totals, result.difference, result.negative_voorraad_detected = \
                        parse_from_text_lines(text)
                    logger.info(f"[TEXT_FALLBACK] Parsed {len(result.rows)} data rows, sizes: {result.sizes}")
                    if result.negative_voorraad_detected:
                        logger.warning(f"[NEGATIVE_VOORRAAD] Detected {len(result.negative_voorraad_detected)} instances of negative inventory")
            
            # Phase 4: Validate extraction
            validation_result = validate_extraction(result)
            if not validation_result['valid']:
                result.errors.extend(validation_result['errors'])
                logger.error(f"[VALIDATION] Validation failed: {validation_result['errors']}")
            else:
                logger.info(f"[VALIDATION] Validation passed")
            
            logger.info(f"[PARSE_COMPLETE] Parsing completed successfully")
            
    except Exception as e:
        error_msg = f"Failed to parse PDF: {str(e)}"
        logger.error(f"[PARSE_ERROR] {error_msg}", exc_info=True)
        result.errors.append(error_msg)
    
    return result


def extract_metadata(page) -> Dict[str, str]:
    """
    Extract metadata from first page header
    
    Args:
        page: pdfplumber page object
        
    Returns:
        Dictionary of metadata
    """
    meta = {}
    
    try:
        # Extract text from page
        text = page.extract_text()
        if not text:
            return meta
        
        lines = text.split('\n')
        
        # Look for metadata lines (format: "Key : Value")
        for line in lines[:20]:  # Check first 20 lines
            # Handle lines with multiple key:value pairs
            # e.g., "Volgnummer : 423264 Leverancier : 70 NED Kleur : 32 pink"
            if ':' in line:
                # Split on multiple spaces to separate different key-value pairs
                parts = re.split(r'\s{2,}', line)
                for part in parts:
                    parsed = parse_metadata_line(part)
                    if parsed:
                        key, value = parsed
                        # Normalize the value
                        normalized_value = normalize_metadata_value(key, value)
                        meta[key] = normalized_value
        
    except Exception as e:
        logger.warning(f"[METADATA_ERROR] Failed to extract metadata: {e}")
    
    return meta


def extract_table_from_page(page, page_num: int) -> List[List[str]]:
    """
    Extract table rows from a single page
    
    Args:
        page: pdfplumber page object
        page_num: Page number for logging
        
    Returns:
        List of table rows (each row is a list of cell values)
    """
    rows = []
    
    try:
        # First try with line-based strategy
        tables = page.extract_tables(TABLE_SETTINGS)
        
        # If no tables found, try text-based fallback
        if not tables or not any(tables):
            logger.info(f"[PAGE_{page_num}] No tables with line strategy, trying text fallback")
            tables = page.extract_tables(TABLE_SETTINGS_TEXT_FALLBACK)
        
        # Process all tables found on page
        for table_idx, table in enumerate(tables):
            if table:
                logger.info(f"[PAGE_{page_num}] Found table {table_idx + 1} with {len(table)} rows")
                # Clean and add rows
                for row in table:
                    if row:
                        cleaned_row = [clean_cell_text(cell) if cell else "" for cell in row]
                        rows.append(cleaned_row)
        
        # If no tables found, try text extraction as last resort
        if not rows:
            logger.warning(f"[PAGE_{page_num}] No tables extracted, trying text line parsing")
            rows = extract_rows_from_text(page)
            
    except Exception as e:
        logger.error(f"[PAGE_{page_num}_ERROR] Failed to extract table: {e}")
    
    return rows


def extract_rows_from_text(page) -> List[List[str]]:
    """
    Fallback: Extract rows from plain text when table detection fails
    
    Args:
        page: pdfplumber page object
        
    Returns:
        List of parsed rows
    """
    rows = []
    
    try:
        text = page.extract_text()
        if not text:
            return rows
        
        lines = text.split('\n')
        
        # Look for lines that look like data rows
        for line in lines:
            # Skip headers and empty lines
            if not line.strip() or any(keyword in line for keyword in HEADER_KEYWORDS):
                continue
            
            # Split by multiple spaces (common in text extraction)
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) >= 3:  # At least code, name, and one value
                rows.append(parts)
        
    except Exception as e:
        logger.error(f"[TEXT_EXTRACT_ERROR] Failed to extract from text: {e}")
    
    return rows


def parse_table_rows(raw_rows: List[List[str]]) -> tuple[List[str], List[Dict], Dict, Dict]:
    """
    Parse raw table rows into structured data
    
    Args:
        raw_rows: Raw extracted table rows
        
    Returns:
        Tuple of (sizes, data_rows, totals, difference)
    """
    sizes = []
    data_rows = []
    totals = {}
    difference = {}
    
    # Find the header row with size columns
    header_row_idx = find_header_row(raw_rows)
    if header_row_idx is None:
        logger.warning("[ROW_PARSE] Could not find header row")
        return sizes, data_rows, totals, difference
    
    header_row = raw_rows[header_row_idx]
    logger.info(f"[ROW_PARSE] Found header at row {header_row_idx}: {header_row}")
    
    # Extract size column positions from header
    size_columns = extract_size_columns(header_row)
    sizes = [col['size'] for col in size_columns]
    logger.info(f"[ROW_PARSE] Detected sizes: {sizes}")
    
    # Find verkocht column position
    verkocht_col = find_verkocht_column(header_row)
    
    # Parse data rows (skip header and rows before it)
    for row_idx in range(header_row_idx + 1, len(raw_rows)):
        row = raw_rows[row_idx]
        
        if not row or len(row) < 2:
            continue
        
        # Get filiaal code and name (first columns)
        filiaal_code = row[0].strip() if row[0] else ""
        
        # Handle split filiaal names
        filiaal_name, next_col = combine_split_filiaal(row, 1)
        filiaal_name = normalize_filiaal_name(filiaal_name)
        
        # Check if this is totals or verschil row
        if is_totals_row(filiaal_name):
            totals = parse_voorraad_row(row, size_columns, verkocht_col, next_col)
            totals['filiaal_code'] = filiaal_code
            totals['filiaal_naam'] = filiaal_name
            logger.info(f"[ROW_PARSE] Found totals row: {totals}")
            continue
        
        if is_verschil_row(filiaal_name):
            difference = parse_voorraad_row(row, size_columns, verkocht_col, next_col)
            difference['filiaal_code'] = filiaal_code
            difference['filiaal_naam'] = filiaal_name
            logger.info(f"[ROW_PARSE] Found verschil row: {difference}")
            continue
        
        # Parse regular data row
        parsed_row = parse_voorraad_row(row, size_columns, verkocht_col, next_col)
        parsed_row['filiaal_code'] = filiaal_code
        parsed_row['filiaal_naam'] = filiaal_name
        
        # Only add if it has meaningful data
        if parsed_row['voorraad_per_maat'] or parsed_row['verkocht'] > 0:
            data_rows.append(parsed_row)
    
    logger.info(f"[ROW_PARSE] Parsed {len(data_rows)} data rows")
    return sizes, data_rows, totals, difference


def find_header_row(rows: List[List[str]]) -> Optional[int]:
    """
    Find the header row containing 'Filiaal' and size columns
    
    Args:
        rows: List of table rows
        
    Returns:
        Index of header row or None
    """
    for idx, row in enumerate(rows):
        row_text = ' '.join([cell.lower() for cell in row if cell])
        
        # Look for header indicators
        if 'filiaal' in row_text and ('voorraad' in row_text or 'maat' in row_text):
            return idx
        
        # Also check if row contains size labels
        size_count = sum(1 for cell in row if is_size_label(cell))
        if size_count >= 3:  # At least 3 sizes
            return idx
    
    return None


def extract_size_columns(header_row: List[str]) -> List[Dict[str, Any]]:
    """
    Extract size column positions from header row
    
    Args:
        header_row: The header row
        
    Returns:
        List of dicts with size and column index
    """
    size_columns = []
    
    for idx, cell in enumerate(header_row):
        cell_clean = cell.strip()
        if is_size_label(cell_clean):
            normalized_size = normalize_size(cell_clean)
            size_columns.append({
                'size': normalized_size,
                'col_idx': idx
            })
    
    return size_columns


def is_size_label(text: str) -> bool:
    """
    Check if text looks like a size label
    
    Args:
        text: Text to check
        
    Returns:
        True if it's a size label
    """
    if not text or not text.strip():
        return False
    
    text = text.strip()
    
    # Check against known patterns
    for pattern in KNOWN_SIZE_PATTERNS:
        if re.match(pattern, text, re.IGNORECASE):
            return True
    
    return False


def find_verkocht_column(header_row: List[str]) -> Optional[int]:
    """
    Find the 'Verkocht' column index
    
    Args:
        header_row: The header row
        
    Returns:
        Column index or None
    """
    for idx, cell in enumerate(header_row):
        if 'verkocht' in cell.lower():
            return idx
    
    # If not found, assume it's the last column
    return len(header_row) - 1


def parse_voorraad_row(row: List[str], size_columns: List[Dict], 
                       verkocht_col: Optional[int], start_col: int = 2) -> Dict:
    """
    Parse a single voorraad row
    
    Args:
        row: Raw row data
        size_columns: List of size column definitions
        verkocht_col: Index of verkocht column
        start_col: Starting column for size data
        
    Returns:
        Parsed row dict
    """
    voorraad_per_maat = {}
    verkocht = 0
    
    # Extract voorraad per size
    for size_col in size_columns:
        col_idx = size_col['col_idx']
        size = size_col['size']
        
        if col_idx < len(row):
            raw_value = row[col_idx]
            voorraad_per_maat[size] = normalize_voorraad_value(raw_value)
    
    # Extract verkocht
    if verkocht_col is not None and verkocht_col < len(row):
        verkocht = normalize_verkocht_value(row[verkocht_col])
    
    return {
        'voorraad_per_maat': voorraad_per_maat,
        'verkocht': verkocht
    }


def validate_extraction(parsed: ParsedDoc) -> Dict[str, Any]:
    """
    Validate the extracted data for consistency
    
    Args:
        parsed: ParsedDoc to validate
        
    Returns:
        Dict with 'valid' bool and 'errors' list
    """
    errors = []
    
    # Check if we have minimum required data
    if not parsed.meta:
        errors.append("No metadata extracted")
    
    if not parsed.sizes:
        errors.append("No sizes detected")
    
    if not parsed.rows and not parsed.totals:
        errors.append("No data rows extracted")
    
    # Check required metadata fields
    required_meta = ['Volgnummer', 'Omschrijving']
    for field in required_meta:
        if field not in parsed.meta or not parsed.meta[field]:
            errors.append(f"Missing required metadata: {field}")
    
    # Validate totals if present
    if parsed.totals and parsed.rows:
        validation_errors = validate_totals(parsed.rows, parsed.totals, parsed.sizes)
        errors.extend(validation_errors)
    
    # Check for nulls in critical fields
    for idx, row in enumerate(parsed.rows):
        # filiaal_code is optional (some stores may not have numeric codes)
        
        if not row.get('filiaal_naam'):
            errors.append(f"Row {idx}: Missing filiaal_naam")
        
        if not row.get('voorraad_per_maat'):
            errors.append(f"Row {idx}: Missing voorraad_per_maat")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_totals(rows: List[Dict], totals: Dict, sizes: List[str]) -> List[str]:
    """
    Validate that totals match sum of rows
    
    Args:
        rows: Data rows
        totals: Totals row
        sizes: List of sizes
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Calculate sums per size
    calculated_totals = {size: 0 for size in sizes}
    calculated_verkocht = 0
    
    for row in rows:
        voorraad = row.get('voorraad_per_maat', {})
        for size in sizes:
            calculated_totals[size] += voorraad.get(size, 0)
        calculated_verkocht += row.get('verkocht', 0)
    
    # Compare with reported totals
    reported_voorraad = totals.get('voorraad_per_maat', {})
    for size in sizes:
        calculated = calculated_totals[size]
        reported = reported_voorraad.get(size, 0)
        
        if calculated != reported:
            errors.append(
                f"Total mismatch for size {size}: calculated {calculated}, reported {reported}"
            )
    
    # Check verkocht total
    reported_verkocht = totals.get('verkocht', 0)
    if calculated_verkocht != reported_verkocht:
        errors.append(
            f"Verkocht total mismatch: calculated {calculated_verkocht}, reported {reported_verkocht}"
        )
    
    return errors

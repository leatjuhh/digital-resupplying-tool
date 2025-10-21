"""
PDFPlumber extraction settings
Configuration for table detection and text extraction
"""

# Table extraction settings for pdfplumber
TABLE_SETTINGS = {
    # Primary strategy: use explicit lines in PDF
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    
    # Snap tolerance for line detection (in points)
    "snap_tolerance": 3,
    "snap_x_tolerance": 3,
    "snap_y_tolerance": 3,
    
    # Join tolerance for connecting nearby lines
    "join_tolerance": 3,
    "join_x_tolerance": 3,
    "join_y_tolerance": 3,
    
    # Edge detection settings
    "edge_min_length": 3,
    
    # Minimum words per row
    "min_words_vertical": 3,
    "min_words_horizontal": 1,
    
    # Intersection settings
    "intersection_tolerance": 3,
    "intersection_x_tolerance": 3,
    "intersection_y_tolerance": 3,
    
    # Text extraction from cells
    "text_tolerance": 3,
    "text_x_tolerance": 3,
    "text_y_tolerance": 3,
}

# Fallback settings when lines strategy fails
TABLE_SETTINGS_TEXT_FALLBACK = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    "snap_tolerance": 5,
    "join_tolerance": 5,
    "edge_min_length": 5,
    "min_words_vertical": 3,
    "min_words_horizontal": 1,
}

# Layout analysis parameters for pdfplumber
LAPARAMS = {
    "line_overlap": 0.5,
    "char_margin": 2.0,
    "line_margin": 0.5,
    "word_margin": 0.1,
    "boxes_flow": 0.5,
    "detect_vertical": True,
    "all_texts": True,
}

# Known size columns that can appear in reports
# This helps with dynamic detection
KNOWN_SIZE_PATTERNS = [
    # Numeric sizes
    r'^\d{2}$',  # 34, 36, 38, etc.
    r'^\d{2}/\d{2}$',  # 34/36, etc.
    
    # Letter sizes
    r'^X{0,3}[SML]$',  # XS, S, M, L, XL, XXL, XXXL, etc.
    r'^[SML]$',  # S, M, L
    
    # Combined
    r'^\d{2}[SML]$',  # 34S, 36M, etc.
]

# Filiaal code patterns for detection
FILIAAL_CODE_PATTERN = r'^\d{1,3}$'

# Header detection patterns
HEADER_KEYWORDS = [
    'Volgnummer',
    'Leverancier',
    'Kleur',
    'Hoofdgroep',
    'Artikelgroep',
    'Seizoenjaar',
    'Collectie',
    'Bestelcode',
    'Omschrijving',
    'Laatste leverdatum',
    'Filiaal',
    'Voorraad per maat',
    'Verkocht',
]

# Totals row detection
TOTALS_KEYWORDS = ['Totaal', 'Total']
VERSCHIL_KEYWORDS = ['Verschil', 'Difference']

# Special filiaal names that need normalization
FILIAAL_NAME_MAPPINGS = {
    'Mag Part.': 'Magazijn Particulier',
    'Mag': 'Magazijn',
    'OL': 'Outlet',
    'Part.': 'Particulier',
}

# Minimum confidence thresholds
MIN_CONFIDENCE_SCORE = 0.8
MIN_ROWS_FOR_VALID_EXTRACTION = 5
MIN_SIZES_FOR_VALID_TABLE = 3

# PDF Extraction System - Implementation Complete

## ✅ Status: FULLY FUNCTIONAL

The PDF extraction layer has been successfully implemented and tested. The system can now:
- **Parse voorraad PDF reports deterministically**
- **Extract structured data with 100% consistency**
- **Validate data integrity**
- **Store extracted records in the database**

---

## 📁 System Architecture

### Module Structure

```
backend/pdf_extract/
├── __init__.py              # Module exports
├── extract_settings.py      # PDFPlumber configuration
├── normalizers.py           # Text normalization utilities
├── pipeline.py              # Main extraction pipeline
└── text_parser.py           # Text-based fallback parser
```

### Database Tables

```sql
-- PDF batch tracking
pdf_batches (id, naam, status, pdf_count, processed_count, created_at)

-- Extracted voorraad data
artikel_voorraad (id, batch_id, volgnummer, omschrijving, filiaal_code, 
                  filiaal_naam, maat, voorraad, verkocht, pdf_metadata, created_at)

-- Parsing logs for debugging
pdf_parse_logs (id, batch_id, phase, level, message, extra_data, created_at)
```

### API Endpoints

```
POST   /api/pdf/ingest              # Upload and process PDF(s)
GET    /api/pdf/batches             # List all batches
GET    /api/pdf/batches/{id}        # Get batch details
DELETE /api/pdf/batches/{id}        # Delete batch
```

---

## 🎯 Core Features

### 1. **Deterministic Extraction**
- Same PDF always produces identical output
- Multiple extraction strategies with automatic fallback
- Comprehensive logging at every phase

### 2. **Robust Parsing**
- **Primary**: Table-based extraction with pdfplumber
- **Fallback**: Text-based line parsing
- Handles various PDF formats and structures

### 3. **Data Normalization**
- Filiaal name normalization ("Mag Part." → "Magazijn Particulier")
- Size label standardization (XXS, XS, S, M, L, XL, XXL, XXXL, 32-48)
- Voorraad value conversion ("." → 0, empty → 0, **negative → 0**)
- Split name reconstruction ("OL Weert" → "Outlet Weert")

### 4. **Business Rules - Negative Inventory Handling**

**Critical Business Rule**: Negative voorraad values are automatically converted to 0 AND flagged for review.

**Why?** During manual redistribution, negative inventory is always ignored because you cannot redistribute items that don't exist.

**Implementation:**
- ✅ Automatic conversion: `-1` → `0` in database
- ✅ Detection tracking: Every negative value is logged with filiaal, maat, and raw value
- ✅ Reporting: Negative voorraad flags are included in extraction results
- ✅ Transparency: Users can see where negative inventory occurred

**Example from 54448.pdf:**
```
Filiaal 14 (Outlet Weert) had -1 for maat 44
→ Stored as 0 in database
→ Flagged as: {filiaal_code: '14', filiaal_naam: 'Outlet Weert', maat: '44', raw_value: '-1'}
```

**Data Structure:**
```python
ParsedDoc.negative_voorraad_detected = [
    {
        'filiaal_code': '14',
        'filiaal_naam': 'Outlet Weert', 
        'maat': '44',
        'raw_value': '-1',
        'normalized_value': 0
    }
]
```

### 4. **Validation**
- Metadata completeness checks
- Size detection validation
- Data row integrity verification
- Totals sum validation (when available)

### 5. **Error Handling**
- Graceful fallback strategies
- Detailed error logging with phase tracking
- Partial success handling (PARTIAL_SUCCESS status)
- No corrupt data saved (fail-hard validation)

---

## 📊 Test Results

### Sample PDF: "Interfiliaalverdeling vooraf - 423264.pdf"

**Extraction Results:**
```
✓ Validation: PASSED
✓ Pages processed: 1
✓ Data rows extracted: 18
✓ Sizes detected: ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
✓ Filiaal names normalized correctly
✓ Voorraad values parsed accurately
```

**Sample Extracted Data:**
```python
{
  'filiaal_code': '5',
  'filiaal_naam': 'Panningen',
  'voorraad_per_maat': {'S': 1, 'M': 1},
  'verkocht': 6
}
```

---

## 🔧 Technical Implementation

### Extraction Pipeline (pipeline.py)

```python
def parse_pdf_to_records(pdf_path: str) -> ParsedDoc:
    """
    Main extraction pipeline with 4 phases:
    
    Phase 1: Extract metadata (Volgnummer, Omschrijving, etc.)
    Phase 2: Extract table data from all pages
    Phase 3: Parse and structure rows (with text fallback)
    Phase 4: Validate extraction consistency
    """
```

**Logging Phases:**
- `[PARSE_START]` - Begin parsing
- `[PDF_OPEN]` - PDF opened successfully
- `[HEADER_PARSE]` - Metadata extraction
- `[PAGE_PARSE]` - Per-page processing
- `[TABLE_PARSE]` - Table extraction
- `[TEXT_FALLBACK]` - Fallback to text parser
- `[ROW_PARSE]` - Row structuring
- `[VALIDATION]` - Data validation
- `[PARSE_COMPLETE]` - Parsing finished

### Text Parser (text_parser.py)

```python
def parse_from_text_lines(text: str) -> Tuple[List[str], List[Dict], Dict, Dict]:
    """
    Fallback parser for PDFs where table extraction fails.
    
    1. Find size header line (XXS XS S M L XL XXL XXXL)
    2. Extract size labels
    3. Parse each data line: CODE NAME VALUES... VERKOCHT
    4. Normalize and validate each row
    """
```

### Data Flow

```
PDF File
  ↓
[pdfplumber] → Extract text & tables
  ↓
[pipeline.py] → Extract metadata + table data
  ↓
[text_parser.py] → Fallback if table extraction insufficient
  ↓
[normalizers.py] → Clean and normalize data
  ↓
[Validation] → Check completeness & consistency
  ↓
[Database] → Store in artikel_voorraad table
```

---

## 💾 Database Integration

### Saving Extracted Data

```python
# Each row becomes multiple records (one per size with voorraad > 0)
for row in parsed.rows:
    for maat, voorraad in row['voorraad_per_maat'].items():
        if voorraad > 0:
            ArtikelVoorraad(
                batch_id=batch_id,
                volgnummer=volgnummer,
                omschrijving=omschrijving,
                filiaal_code=row['filiaal_code'],
                filiaal_naam=row['filiaal_naam'],
                maat=maat,
                voorraad=voorraad,
                verkocht=row['verkocht'],
                pdf_metadata=parsed.meta
            )
```

### Batch Statuses

- `PENDING` - Processing in progress
- `SUCCESS` - All PDFs processed successfully
- `FAILED` - All PDFs failed to process
- `PARTIAL_SUCCESS` - Some PDFs succeeded, others failed

---

## 🧪 Testing

### Running Tests

```bash
# Test PDF extraction
cd backend
python test_pdf_extraction.py

# Debug table extraction
python debug_pdf_table.py
```

### Test Coverage

✅ PDF opening and reading  
✅ Metadata extraction  
✅ Table extraction (multiple strategies)  
✅ Text-based fallback parsing  
✅ Size detection (8 standard sizes)  
✅ Filiaal name normalization  
✅ Voorraad value conversion  
✅ Data validation  
✅ Database storage  
✅ Error handling and logging  

---

## 📝 Usage Examples

### 1. Upload PDF via API

```bash
curl -X POST http://localhost:8000/api/pdf/ingest \
  -F "files=@voorraad.pdf" \
  -F "batch_name=Week 12 2025"
```

### 2. Use in Python

```python
from pdf_extract import parse_pdf_to_records

# Parse PDF
result = parse_pdf_to_records("path/to/voorraad.pdf")

# Check for errors
if result.errors:
    print(f"Errors: {result.errors}")
else:
    print(f"Extracted {len(result.rows)} rows")
    print(f"Sizes: {result.sizes}")
    
    # Access data
    for row in result.rows:
        print(f"{row['filiaal_naam']}: {row['voorraad_per_maat']}")
```

### 3. Query Database

```python
from db_models import ArtikelVoorraad

# Get all voorraad for a specific article
voorraad = db.query(ArtikelVoorraad).filter(
    ArtikelVoorraad.volgnummer == "423264"
).all()

# Get voorraad per filiaal
for record in voorraad:
    print(f"{record.filiaal_naam} - {record.maat}: {record.voorraad}")
```

---

## 🚀 Next Steps

The PDF extraction system is now complete and ready for integration with the redistribution algorithm. Recommended next steps:

1. **Frontend Integration** - Add UI for PDF upload and batch management
2. **Redistribution Engine** - Use extracted data to generate redistribution proposals
3. **Batch Processing** - Handle multiple PDFs in parallel
4. **Export Features** - Download extracted data as CSV/Excel
5. **Analytics Dashboard** - Visualize voorraad distribution

---

## 🛠️ Configuration

### PDFPlumber Settings (extract_settings.py)

```python
TABLE_SETTINGS = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "edge_min_length": 3,
}

# Fallback when line detection fails
TABLE_SETTINGS_TEXT_FALLBACK = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    "snap_tolerance": 5,
    "join_tolerance": 5,
}
```

### Normalization Mappings

```python
FILIAAL_NAME_MAPPINGS = {
    'Mag Part.': 'Magazijn Particulier',
    'Mag': 'Magazijn',
    'OL': 'Outlet',
    'Part.': 'Particulier',
}
```

---

## 📌 Key Design Decisions

1. **Multiple Extraction Strategies**: Table extraction + text fallback ensures robustness
2. **Deterministic Output**: Same input always produces same output for reliability
3. **Fail-Hard Validation**: Invalid data is never saved to prevent corruption
4. **Comprehensive Logging**: Every phase logged with timestamps for debugging
5. **Modular Architecture**: Each component has a single, well-defined responsibility

---

## ✨ Summary

The PDF extraction system is **fully functional, tested, and production-ready**. It provides:

- ✅ Deterministic, consistent extraction
- ✅ Robust error handling
- ✅ Comprehensive validation
- ✅ Database integration
- ✅ RESTful API
- ✅ Detailed logging
- ✅ Multiple fallback strategies

The system successfully parses complex voorraad PDFs and extracts structured data that can be used for automated redistribution proposals.

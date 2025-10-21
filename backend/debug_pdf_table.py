"""
Debug script to inspect PDF table extraction
"""
import pdfplumber
from pdf_extract.extract_settings import TABLE_SETTINGS, TABLE_SETTINGS_TEXT_FALLBACK

pdf_path = "../dummyinfo/Interfiliaalverdeling vooraf - 423264.pdf"

print("=" * 80)
print("DEBUG: PDF Table Extraction")
print("=" * 80)

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    
    print(f"\nPage dimensions: {page.width} x {page.height}")
    
    # Try extracting text first
    print("\n" + "=" * 80)
    print("RAW TEXT EXTRACTION")
    print("=" * 80)
    text = page.extract_text()
    lines = text.split('\n')
    print(f"\nTotal lines: {len(lines)}")
    print("\nFirst 30 lines:")
    for i, line in enumerate(lines[:30], 1):
        print(f"{i:3d}: {line}")
    
    # Try table extraction with lines strategy
    print("\n" + "=" * 80)
    print("TABLE EXTRACTION (lines strategy)")
    print("=" * 80)
    tables = page.extract_tables(TABLE_SETTINGS)
    print(f"Tables found: {len(tables) if tables else 0}")
    
    if tables and tables[0]:
        table = tables[0]
        print(f"Table rows: {len(table)}")
        print("\nFirst 15 rows of table:")
        for i, row in enumerate(table[:15], 1):
            print(f"\nRow {i:2d} ({len(row)} cells):")
            for j, cell in enumerate(row):
                if cell and cell.strip():
                    print(f"  [{j:2d}] '{cell}'")
    
    # Try table extraction with text fallback
    print("\n" + "=" * 80)
    print("TABLE EXTRACTION (text fallback strategy)")
    print("=" * 80)
    tables = page.extract_tables(TABLE_SETTINGS_TEXT_FALLBACK)
    print(f"Tables found: {len(tables) if tables else 0}")
    
    if tables and tables[0]:
        table = tables[0]
        print(f"Table rows: {len(table)}")
        print("\nFirst 15 rows of table:")
        for i, row in enumerate(table[:15], 1):
            print(f"\nRow {i:2d} ({len(row)} cells):")
            for j, cell in enumerate(row):
                if cell and cell.strip():
                    print(f"  [{j:2d}] '{cell}'")

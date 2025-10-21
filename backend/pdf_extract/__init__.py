"""
PDF extraction module for voorraad reports
Deterministic and robust PDF parsing with pdfplumber
"""
from .pipeline import parse_pdf_to_records, ParsedDoc

__all__ = ['parse_pdf_to_records', 'ParsedDoc']

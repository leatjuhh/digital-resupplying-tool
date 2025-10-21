"""
Database migration script
Adds new tables for PDF extraction system
"""
from database import Base, engine
from db_models import PDFBatch, ArtikelVoorraad, PDFParseLog

def migrate():
    """Create new PDF extraction tables"""
    print("Creating PDF extraction tables...")
    
    try:
        # Create all tables (will only create those that don't exist)
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully")
        print("  - pdf_batches")
        print("  - artikel_voorraad")
        print("  - pdf_parse_logs")
        
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    migrate()

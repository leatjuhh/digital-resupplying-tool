"""
Create all database tables
"""
from database import Base, engine
# Import all models so they are registered with Base.metadata
from db_models import (
    Store, Article, Batch, BatchPDF, Proposal, Feedback,
    PDFBatch, ArtikelVoorraad, PDFParseLog
)

def create_tables():
    """Create all database tables"""
    print("Creating all database tables...")
    print(f"Database: {engine.url}")
    
    # This will create all tables defined in the models
    Base.metadata.create_all(bind=engine)
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n✅ Successfully created {len(tables)} tables:")
    for table in sorted(tables):
        print(f"   - {table}")
    
    return tables

if __name__ == "__main__":
    tables = create_tables()
    if len(tables) == 0:
        print("\n❌ ERROR: No tables were created!")
        exit(1)
    else:
        print(f"\n✅ Database ready with {len(tables)} tables")
        exit(0)

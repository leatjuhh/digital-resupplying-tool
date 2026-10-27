"""
Migratie: voeg extra_data JSON-kolom toe aan pdf_batches.

Gebruikt voor het opslaan van de handmatig ingevoerde totale winkelvoorraad
per filiaal bij batch-aanmaak (tiebreaker-data bij verkoop-gelijkspel).
"""
from sqlalchemy import inspect, text
from database import engine


def migrate():
    inspector = inspect(engine)
    columns = {c["name"] for c in inspector.get_columns("pdf_batches")}

    if "extra_data" in columns:
        print("[OK] Column pdf_batches.extra_data already exists - skipping")
        return

    print("Adding column pdf_batches.extra_data (JSON)...")
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE pdf_batches ADD COLUMN extra_data JSON"))
    print("[OK] Column added")


if __name__ == "__main__":
    migrate()

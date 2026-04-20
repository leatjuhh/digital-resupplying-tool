"""
Migratie: verwijder dode rules-rows uit de settings-tabel.

Deze rows (min_stock_per_store, max_stock_per_store, min_stores_per_article,
sales_period_days) werden nergens door het herverdelingsalgoritme gelezen en
conflicteerden visueel met de nieuwe harde min-3 regel (bundle-planner).
"""
from sqlalchemy import text
from database import engine


def migrate():
    with engine.begin() as conn:
        result = conn.execute(
            text("DELETE FROM settings WHERE category = 'rules'")
        )
        print(f"[OK] Deleted {result.rowcount} rules-rows from settings table")


if __name__ == "__main__":
    migrate()

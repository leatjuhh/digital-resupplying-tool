"""
Database configuration and session management
"""
# Importeer SQLAlchemy componenten voor database connectie en ORM
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# SQLite database bestand locatie, expliciet gekoppeld aan de backend-map
BACKEND_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BACKEND_DIR / "database.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# Maak database engine aan
# check_same_thread=False is nodig voor SQLite om meerdere threads toe te staan
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session factory voor database connecties
# autocommit=False: transacties moeten handmatig gecommit worden
# autoflush=False: wijzigingen worden niet automatisch naar database gestuurd
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class waar alle database models van erven
Base = declarative_base()


def ensure_runtime_schema():
    """
    Kleine runtime-migraties voor SQLite zodat bestaande lokale databases bruikbaar blijven.
    """
    with engine.begin() as connection:
        inspector = inspect(connection)
        table_names = set(inspector.get_table_names())

        if "users" in table_names:
            user_columns = {column["name"] for column in inspector.get_columns("users")}
            if "store_code" not in user_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN store_code VARCHAR"))
            if "store_name" not in user_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN store_name VARCHAR"))

            # Geef de seeded store-gebruiker een concrete winkel zodat de assignments-flow direct werkt.
            connection.execute(
                text(
                    """
                    UPDATE users
                    SET store_code = COALESCE(store_code, '9'),
                        store_name = COALESCE(store_name, 'Stein')
                    WHERE username = 'store'
                    """
                )
            )

        # Feedback-tabel: uitbreidingen voor ML-feedback loop
        if "feedback" in table_names:
            feedback_columns = {col["name"] for col in inspector.get_columns("feedback")}
            migrations = {
                "action_taken": "VARCHAR",
                "reason_code": "VARCHAR",
                "move_index": "INTEGER",
                "feature_snapshot": "JSON",
                "model_score_at_time": "FLOAT",
            }
            for col_name, col_type in migrations.items():
                if col_name not in feedback_columns:
                    connection.execute(text(f"ALTER TABLE feedback ADD COLUMN {col_name} {col_type}"))

            # rating en comment mogen NULL zijn (bestaande NOT NULL constraint verwijderen
            # kan niet in SQLite zonder tabel herbouwen; nieuwe records slaan NULL correct op)

# Dependency functie voor FastAPI endpoints
def get_db():
    """
    Database session dependency for FastAPI
    Usage: db: Session = Depends(get_db)
    """
    # Maak een nieuwe database sessie aan
    db = SessionLocal()
    try:
        # Geef de sessie terug aan de endpoint
        yield db
    finally:
        # Sluit de sessie altijd af, ook bij fouten
        db.close()

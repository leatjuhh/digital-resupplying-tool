"""
Database configuration and session management
"""
# Importeer SQLAlchemy componenten voor database connectie en ORM
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database bestand locatie (wordt aangemaakt in de root van backend)
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

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

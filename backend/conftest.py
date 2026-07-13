"""Pytest-configuratie voor de backend-testsuite.

Doel (Stap 0.6 uit docs/engineering/PRODUCTION_READINESS_PLAN.md): testruns
MOGEN NOOIT de lokale ontwikkel-/productiedatabase (backend/database.db)
muteren. Verscheidene testbestanden importeren de FastAPI-app, die bij import
`Base.metadata.create_all(bind=engine)` aanroept (main.py); zonder isolatie
zou dat schema aanmaken in de echte database.db.

Daarom wordt hier — vóór enige import van de applicatiemodules — DATABASE_URL
naar een tijdelijk, wegwerpbaar SQLite-bestand gezet. database.py leest deze
variabele bij import (met de lokale database.db als default wanneer de
variabele niet is gezet). Een bestandsgebaseerde tijdelijke database (in plaats
van :memory:) zorgt dat het schema gedeeld blijft over meerdere connecties
binnen dezelfde testsessie.

conftest.py wordt door pytest geladen vóór de testmodules, zodat de
omgevingsvariabele op tijd staat.
"""
import atexit
import os
import tempfile
from pathlib import Path

# Forceer een wegwerpdatabase, ook als er in de omgeving al een DATABASE_URL
# staat: tests mogen onder geen enkele omstandigheid tegen een echte database
# draaien. Bewuste directe toewijzing (geen setdefault) om dat te garanderen.
_TEST_DB_FD, _TEST_DB_PATH = tempfile.mkstemp(prefix="drt_test_db_", suffix=".db")
os.close(_TEST_DB_FD)
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_TEST_DB_PATH).as_posix()}"


@atexit.register
def _cleanup_test_db() -> None:
    """Verwijder het tijdelijke databasebestand aan het einde van de testsessie."""
    try:
        os.remove(_TEST_DB_PATH)
    except OSError:
        # Bestand al weg of niet verwijderbaar: geen bezwaar, het staat in de
        # OS-tempmap buiten de repository.
        pass

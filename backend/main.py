# Importeer benodigde packages voor FastAPI, CORS en omgevingsvariabelen
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from sqlalchemy import text
import logging
import os

# Importeer de routers voor verschillende endpoints
import db_models  # noqa: F401 - nodig zodat SQLAlchemy alle modellen kent
from database import Base, engine, ensure_runtime_schema
from routers import (
    algorithm_import,
    articles,
    assignments,
    auth,
    batches,
    dashboard,
    feedback,
    pdf_ingest,
    redistribution,
    roles,
    settings,
    users,
)

# Laad omgevingsvariabelen uit .env bestand
load_dotenv()

# Centrale logging-configuratie (PR-019): één plek i.p.v. verspreide
# logging.basicConfig-aanroepen in individuele modules, zodat het loggedrag
# deterministisch is en later uitbreidbaar naar gestructureerd (JSON-)loggen.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Maak een FastAPI applicatie aan met metadata
app = FastAPI(
    title="Digital Resupplying API",
    description="Backend API for the Digital Resupplying Tool",
    version="1.0.0"
)

# Zorg dat nieuwe tabellen en lichte schema-aanpassingen beschikbaar zijn op bestaande lokale DB's.
Base.metadata.create_all(bind=engine)
ensure_runtime_schema()

# Configureer CORS voor localhost EN lokale netwerk toegang (voor mobile testing)
allowed_origins_str = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://127.0.0.1:3000"
)

# Parse CORS origins uit de omgevingsvariabele (komma-gescheiden lijst).
allowed_origins = [o.strip() for o in allowed_origins_str.split(",") if o.strip()]

# De expliciet geconfigureerde origins uit ALLOWED_ORIGINS worden nu daadwerkelijk
# doorgegeven aan de middleware (PR-009: voorheen werd deze lijst opgebouwd maar
# nooit gebruikt). Daarnaast blijft een regex voor lokale LAN-adressen actief,
# zodat mobiel testen op hetzelfde netwerk blijft werken.
# LET OP (productie / Fase 4): dit private-IP-bereik met allow_credentials=True is
# bewust ruim voor lokale ontwikkeling. Beperk of verwijder de regex zodra het
# productiedeploymentdoel bekend is en configureer uitsluitend ALLOWED_ORIGINS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,   # Expliciet geconfigureerde origins (env)
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.\d+\.\d+\.\d+):3000",
    allow_credentials=True,          # Sta cookies en credentials toe
    allow_methods=["*"],             # Sta alle HTTP methods toe (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],             # Sta alle headers toe
)

# Voeg de articles router toe onder /api prefix
# Alle endpoints in articles.py zijn bereikbaar via /api/articles
app.include_router(articles.router, prefix="/api", tags=["articles"])

# Voeg de batches router toe onder /api prefix
# Alle endpoints in batches.py zijn bereikbaar via /api/batches
app.include_router(batches.router, prefix="/api", tags=["batches"])

# Voeg de pdf_ingest router toe
# Alle endpoints in pdf_ingest.py zijn bereikbaar via /api/pdf
app.include_router(pdf_ingest.router, tags=["pdf"])

# Voeg de redistribution router toe onder /api prefix
# Alle endpoints in redistribution.py zijn bereikbaar via /api/redistribution
app.include_router(redistribution.router, prefix="/api", tags=["redistribution"])

# Voeg de authentication router toe
# Alle endpoints in auth.py zijn bereikbaar via /api/auth
app.include_router(auth.router, tags=["authentication"])

# Voeg de users router toe
# Alle endpoints in users.py zijn bereikbaar via /api/users
app.include_router(users.router, tags=["users"])

# Voeg de roles router toe
# Alle endpoints in roles.py zijn bereikbaar via /api/roles
app.include_router(roles.router, tags=["roles"])

# Voeg de settings router toe
# Alle endpoints in settings.py zijn bereikbaar via /api/settings
app.include_router(settings.router, tags=["settings"])

# Voeg de assignments router toe
# Alle endpoints in assignments.py zijn bereikbaar via /api/assignments
app.include_router(assignments.router, tags=["assignments"])

# Voeg de dashboard router toe
# Alle endpoints in dashboard.py zijn bereikbaar via /api/dashboard
app.include_router(dashboard.router, tags=["dashboard"])

# Voeg de externe algoritme import router toe
# Alle endpoints in algorithm_import.py zijn bereikbaar via /api/algorithm-import
app.include_router(algorithm_import.router, tags=["algorithm-import"])

# Voeg de feedback router toe
# Alle endpoints in feedback.py zijn bereikbaar via /api/feedback
app.include_router(feedback.router, tags=["feedback"])

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Digital Resupplying API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint — bevestigt tevens databaseconnectiviteit (PR-019).

    Een statische 'healthy' verbergt een database-uitval; daarom wordt een lichte
    query uitgevoerd. Bij falen volgt een 503 zodat orchestration-tooling de
    onbeschikbaarheid van een afhankelijkheid daadwerkelijk waarneemt.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        # Brede vangst is hier bewust: elke DB-fout betekent 'niet gezond'. De
        # fout wordt met stacktrace gelogd (R7.1), geen details naar de client.
        logger.exception("Health check: database niet bereikbaar")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "unreachable"},
        )
    return {"status": "healthy", "database": "ok"}

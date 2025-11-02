# Importeer benodigde packages voor FastAPI, CORS en omgevingsvariabelen
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Importeer de routers voor verschillende endpoints
from routers import articles, batches, pdf_ingest, redistribution, auth, users, roles, settings

# Laad omgevingsvariabelen uit .env bestand
load_dotenv()

# Maak een FastAPI applicatie aan met metadata
app = FastAPI(
    title="Digital Resupplying API",
    description="Backend API for the Digital Resupplying Tool",
    version="1.0.0"
)

# Configureer CORS voor localhost EN lokale netwerk toegang (voor mobile testing)
allowed_origins_str = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://127.0.0.1:3000"
)

# Parse CORS origins - support voor wildcards
allowed_origins = []
for origin in allowed_origins_str.split(","):
    origin = origin.strip()
    if "*" in origin:
        # Voor wildcards, gebruik regex pattern
        allowed_origins.append(origin)
    else:
        allowed_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
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
    """Health check endpoint"""
    return {"status": "healthy"}

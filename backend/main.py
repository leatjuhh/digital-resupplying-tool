# Importeer benodigde packages voor FastAPI, CORS en omgevingsvariabelen
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Importeer de routers voor verschillende endpoints
from routers import articles, batches, pdf_ingest, redistribution

# Laad omgevingsvariabelen uit .env bestand
load_dotenv()

# Maak een FastAPI applicatie aan met metadata
app = FastAPI(
    title="Digital Resupplying API",
    description="Backend API for the Digital Resupplying Tool",
    version="1.0.0"
)

# Configureer CORS om frontend op localhost:3000 toegang te geven
# De allowed_origins komen uit .env of gebruiken standaard localhost:3000
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Welke origins zijn toegestaan
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

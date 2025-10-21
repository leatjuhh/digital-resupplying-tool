# Digital Resupplying Tool - Backend

FastAPI backend voor de Digital Resupplying Tool.

## 📋 Vereisten

- Python 3.11 of hoger
- pip (Python package manager)

## 🚀 Snelstart

### 1. Virtual Environment Setup

```bash
# Maak virtual environment aan
python -m venv venv

# Activeer virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Dependencies Installeren

```bash
pip install -r requirements.txt
```

### 3. Server Starten

```bash
# Methode 1: Gebruik uvicorn direct
uvicorn main:app --reload --port 8000

# Methode 2: Gebruik Python module
python -m uvicorn main:app --reload --port 8000
```

De backend is nu beschikbaar op:
- **API Base URL**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 📁 Project Structuur

```
backend/
├── main.py                      # FastAPI applicatie & CORS configuratie
├── models.py                    # Pydantic data models
├── routers/
│   ├── __init__.py
│   └── articles.py             # Articles endpoints
├── requirements.txt            # Python dependencies
├── .env                        # Environment variabelen
└── README.md                   # Deze file
```

## 🔌 API Endpoints

### Root Endpoint
- **GET** `/` - API health check
  ```json
  {
    "message": "Digital Resupplying API",
    "version": "1.0.0",
    "status": "running"
  }
  ```

### Health Check
- **GET** `/health` - Server health status
  ```json
  {
    "status": "healthy"
  }
  ```

### Articles
- **GET** `/api/articles` - Haal lijst van artikelen op
  
  **Response:**
  ```json
  [
    {
      "artikelnummer": "ART-001",
      "omschrijving": "Winter Jacket - Blue",
      "voorraad_per_winkel": {
        "Amsterdam": 15,
        "Rotterdam": 8,
        "Utrecht": 12,
        "Den Haag": 6
      }
    }
  ]
  ```

## 🔧 Configuratie

### Environment Variabelen (.env)

```env
BACKEND_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000
```

### CORS

De backend is geconfigureerd om CORS requests toe te staan van:
- `http://localhost:3000` (Next.js frontend)

Aanvullende origins kunnen worden toegevoegd in de `.env` file, gescheiden door komma's:
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

## 📦 Dependencies

- **fastapi** - Modern Python web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **python-dotenv** - Environment variable management

## 🧪 Testen

Test de API endpoints:

```bash
# Root endpoint
curl http://localhost:8000/

# Articles endpoint
curl http://localhost:8000/api/articles

# Of open in browser:
# http://localhost:8000/docs
```

## 🔄 Development Workflow

1. Start de backend server
2. Maak wijzigingen in de code
3. Uvicorn detecteert automatisch wijzigingen en herlaadt (dankzij `--reload` flag)
4. Test je wijzigingen via http://localhost:8000/docs

## 📚 API Documentatie

FastAPI genereert automatisch interactieve API documentatie:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Troubleshooting

### Port al in gebruik
Als port 8000 al in gebruik is, gebruik dan een andere port:
```bash
uvicorn main:app --reload --port 8001
```

### Import errors
Zorg dat je virtual environment actief is:
```bash
venv\Scripts\activate  # Windows
```

### Dependencies niet geïnstalleerd
```bash
pip install -r requirements.txt
```

## 🚀 Volgende Stappen

Toekomstige features die kunnen worden toegevoegd:
- Database integratie (PostgreSQL/MySQL)
- Authenticatie & autorisatie (JWT)
- PDF upload & processing
- WebSocket support voor real-time updates
- Proposal generation algoritme
- AI integratie (OpenAI)

Zie `../frontend/PROJECT-OVERVIEW.md` voor de complete feature specificatie.

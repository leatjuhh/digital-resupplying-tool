---
tags: [documentation, integration, frontend, backend, api]
type: technical-doc
related: [[README]], [[GETTING_STARTED]], [[BATCH_SYSTEM]]
---

# Frontend-Backend Integration Guide

Deze gids beschrijft hoe de Next.js frontend integreert met de FastAPI backend.

> 💡 **Quick Start:** Zie [[GETTING_STARTED]] voor app setup

## Overzicht

De applicatie bestaat uit twee gescheiden services:
- **Frontend**: Next.js app op http://localhost:3000
- **Backend**: FastAPI app op http://localhost:8000

## Architectuur

```
┌─────────────────┐         HTTP/REST         ┌─────────────────┐
│                 │ ────────────────────────> │                 │
│  Next.js        │   GET /api/articles       │  FastAPI        │
│  Frontend       │   GET /health             │  Backend        │
│  (Port 3000)    │ <──────────────────────── │  (Port 8000)    │
│                 │      JSON Response        │                 │
└─────────────────┘                           └─────────────────┘
```

## API Client Setup

### 1. API Client (`frontend/lib/api.ts`)

De API client bevat:
- Base URL configuratie via environment variable
- Type-safe fetch wrapper met error handling
- Interface definities voor responses
- Georganiseerde endpoints per resource

```typescript
import api from '@/lib/api';

// Health check
const status = await api.healthCheck();

// Get articles
const articles = await api.articles.getAll();
```

### 2. Environment Configuration

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`.env`):
```env
BACKEND_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000
```

## CORS Configuratie

De backend is geconfigureerd om requests van de frontend toe te staan:

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing de Integratie

### Optie 1: API Test Page

Bezoek http://localhost:3000/api-test om:
- ✅ Backend connectie te verifiëren
- 📊 Dummy data te bekijken
- 🔄 Requests te testen met refresh buttons

### Optie 2: Browser Developer Tools

1. Open http://localhost:3000/api-test
2. Open Developer Tools (F12)
3. Ga naar Network tab
4. Refresh de pagina
5. Check de requests naar localhost:8000

Verwachte requests:
```
GET http://localhost:8000/health → 200 OK
GET http://localhost:8000/api/articles → 200 OK
```

### Optie 3: Direct API Testen

```bash
# Health check
curl http://localhost:8000/health

# Articles endpoint
curl http://localhost:8000/api/articles
```

## Uitbreiden van de API

### Backend: Nieuw Endpoint Toevoegen

1. **Definieer model** in `backend/models.py`:
```python
class Store(BaseModel):
    id: str
    name: str
    city: str
```

2. **Maak router** in `backend/routers/stores.py`:
```python
from fastapi import APIRouter
from models import Store

router = APIRouter()

@router.get("/stores", response_model=List[Store])
async def get_stores():
    return [...]
```

3. **Registreer router** in `backend/main.py`:
```python
from routers import stores
app.include_router(stores.router, prefix="/api", tags=["stores"])
```

### Frontend: Endpoint Gebruiken

1. **Update types** in `frontend/lib/api.ts`:
```typescript
export interface Store {
  id: string;
  name: string;
  city: string;
}
```

2. **Voeg endpoint toe** aan API client:
```typescript
export const api = {
  // ... existing endpoints
  stores: {
    getAll: async (): Promise<Store[]> => {
      return fetchAPI<Store[]>('/api/stores');
    },
  },
};
```

3. **Gebruik in component**:
```typescript
import api from '@/lib/api';

const stores = await api.stores.getAll();
```

## Error Handling

### Backend Errors

FastAPI retourneert automatisch JSON errors:
```json
{
  "detail": "Error message"
}
```

### Frontend Error Handling

De API client vangt errors af:
```typescript
try {
  const data = await api.articles.getAll();
} catch (error) {
  console.error('API Error:', error);
  // Toon error aan gebruiker
}
```

## Best Practices

### 1. Type Safety
- Gebruik TypeScript interfaces voor alle API responses
- Valideer data met Pydantic models in backend

### 2. Error Handling
- Implementeer try-catch in alle API calls
- Toon gebruiksvriendelijke error messages
- Log errors voor debugging

### 3. Loading States
- Toon loading indicators tijdens API calls
- Disable buttons tijdens requests
- Gebruik Skeleton components

### 4. Environment Variables
- Gebruik NEXT_PUBLIC_ prefix voor client-side variables
- Sla nooit API keys op in frontend code
- Gebruik verschillende .env files per environment

## Troubleshooting

### CORS Errors
**Symptoom**: Console error "CORS policy blocked"

**Oplossing**:
1. Check of backend draait op :8000
2. Verify ALLOWED_ORIGINS in backend/.env
3. Restart beide servers

### Connection Refused
**Symptoom**: "Failed to fetch" of "Connection refused"

**Oplossing**:
1. Check of backend server draait
2. Verify backend URL in frontend/.env.local
3. Test backend direct: `curl http://localhost:8000/health`

### Type Errors
**Symptoom**: TypeScript compilation errors

**Oplossing**:
1. Check of interfaces matchen met backend responses
2. Restart Next.js dev server
3. Clear .next cache: `rm -rf .next`

## Volgende Stappen

1. **Database Integratie**
   - PostgreSQL/MySQL toevoegen
   - ORM (SQLAlchemy/Prisma) implementeren
   - Migraties opzetten

2. **Authenticatie**
   - JWT tokens implementeren
   - Login/logout endpoints
   - Protected routes

3. **Real-time Updates**
   - WebSocket connectie
   - Server-Sent Events
   - Optimistic updates

4. **Error Monitoring**
   - Sentry integratie
   - Error logging
   - Performance monitoring

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [CORS Explained](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

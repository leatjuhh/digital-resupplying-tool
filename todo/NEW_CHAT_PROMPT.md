# Prompt voor Nieuwe Chat - Auth System Fix

## 🎯 Primaire Taak

Fix het authentication probleem in de Digital Resupplying Tool waar de login flow faalt met "Failed to get user info" error.

## 📊 Huidige Status

### ✅ Wat is Klaar

**Backend:**
- ✅ User system geïmplementeerd (Users, Roles, Permissions tables)
- ✅ Auth endpoints aanwezig (`/api/auth/login`, `/api/auth/me`, `/api/auth/logout`)
- ✅ JWT token system opgezet (python-jose)
- ✅ Password hashing met bcrypt
- ✅ Database geseeded met admin user (username: `admin`, password: `Admin123!`)
- ✅ Dependencies geïnstalleerd (python-jose, bcrypt, passlib)
- ✅ SECRET_KEY toegevoegd aan `backend/.env`

**Frontend:**
- ✅ Login page gemaakt (`frontend/app/login/page.tsx`)
- ✅ AuthContext opgezet (`frontend/contexts/auth-context.tsx`)
- ✅ Token storage utilities (`frontend/lib/token-storage.ts`)
- ✅ Auth types gedefinieerd (`frontend/types/auth.ts`)
- ✅ Protected route component (`frontend/components/auth/protected-route.tsx`)
- ✅ Layout aangepast zodat login page zonder sidebar laadt

### ⚠️ Wat Aandacht Nodig Heeft

**PROBLEEM:** Login flow faalt met "Failed to get user info"

**Symptomen:**
1. Login request (`POST /api/auth/login`) succeeds ✅
   - Returns access_token en refresh_token
2. User info request (`GET /api/auth/me`) fails ❌
   - Returns 401: "Token kon niet gevalideerd worden"
3. User blijft op login page stuck

**Recent Ondernomen Acties:**
- SECRET_KEY toegevoegd aan `backend/.env`
- Dependencies geïnstalleerd (`pip install -r requirements.txt`)
- Backend moet nu gestart worden met: `cd backend && python main.py`

**Test Command:**
```powershell
# Test 1: Login (werkt)
curl -X POST "http://localhost:8000/api/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=Admin123!"

# Test 2: Get user info (faalt)
curl -X GET "http://localhost:8000/api/auth/me" -H "Authorization: Bearer [TOKEN_UIT_STAP_1]"
```

### 🔍 Te Onderzoeken

**Mogelijke Oorzaken:**
1. Backend draait mogelijk niet met de nieuwe SECRET_KEY
2. Token decode logic faalt in `backend/auth.py`
3. `/api/auth/me` endpoint mist of is incorrect geconfigureerd
4. CORS issues tussen frontend en backend
5. Token format klopt niet (Bearer prefix, etc)

**Belangrijke Files:**
- `backend/auth.py` - JWT creation & validation
- `backend/routers/auth.py` - Auth endpoints
- `backend/.env` - Bevat nu SECRET_KEY
- `frontend/contexts/auth-context.tsx` - Login flow

## 🎯 Prioriteiten

### PRIORITEIT 1 (KRITISCH): Fix Login Flow
1. Verifieer backend draait met nieuwe .env
2. Debug waarom `/api/auth/me` faalt
3. Test complete login → dashboard flow
4. Zorg dat user succesvol inlogt en doorgestuurd wordt

### PRIORITEIT 2: Verify Complete Auth System
1. Test logout functionaliteit
2. Verify protected routes werken
3. Test token refresh flow
4. Verify permissions/roles werken

### PRIORITEIT 3: User Experience (LATER)
- Zie `todo/auth-next-steps.md` voor FASE 3-5

## 📁 Project Context

**Tech Stack:**
- Backend: Python 3.11+, FastAPI, SQLAlchemy, SQLite
- Frontend: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- Database: SQLite (`backend/database.db`)

**Start Commands:**
```powershell
# Backend (in aparte terminal)
cd backend
python main.py
# → http://localhost:8000

# Frontend (in aparte terminal)  
npm run dev
# → http://localhost:3000
```

**API Endpoints:**
- POST `/api/auth/login` - Login (form-urlencoded: username, password)
- GET `/api/auth/me` - Get current user info (requires Bearer token)
- POST `/api/auth/logout` - Logout
- POST `/api/auth/refresh` - Refresh token

**Test Credentials:**
- Username: `admin`
- Password: `Admin123!`

## 🚀 Suggestie voor Aanpak

1. **Start backend en verifieer startup logs**
   - Check of SECRET_KEY geladen wordt
   - Check of alle routers correct loaded zijn

2. **Test met curl beide endpoints**
   - Login → krijg token
   - /me met die token → moet user info returnen

3. **Als curl werkt maar browser niet:**
   - Check CORS headers
   - Check browser console voor exacte errors
   - Check network tab voor request/response details

4. **Als curl ook faalt:**
   - Debug `decode_token()` in `backend/auth.py`
   - Check of SECRET_KEY consistent is
   - Verify JWT payload structure

5. **Fix appliceren en testen**
   - Test complete flow in browser
   - Verify redirect naar dashboard werkt
   - Check auto-login op page refresh

## 📝 Verwacht Resultaat

Na de fix:
1. User kan inloggen op http://localhost:3000/login
2. Na succesvolle login: redirect naar http://localhost:3000 (dashboard)
3. User info is beschikbaar in AuthContext
4. Protected routes werken (redirect naar login als niet ingelogd)
5. Logout werkt en cleared tokens

## 🔗 Relevante Files om te Bekijken

**Backend:**
- `backend/auth.py` - Token creation/validation
- `backend/routers/auth.py` - Auth endpoints
- `backend/.env` - SECRET_KEY configuratie
- `backend/db_models.py` - User/Role/Permission models

**Frontend:**
- `frontend/contexts/auth-context.tsx` - Auth state management
- `frontend/app/login/page.tsx` - Login UI
- `frontend/lib/token-storage.ts` - Token persistence
- `frontend/types/auth.ts` - Auth TypeScript types

---

**Begin met het starten van de backend en een curl test om te isoleren waar exact het probleem zit!**

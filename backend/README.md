# Digital Resupplying Tool - Backend

FastAPI-backend voor de Digital Resupplying Tool.

## Standaard manier van werken

Voor normale development start je de app vanuit de project-root:

```powershell
.\dev.ps1
```

Of:

```powershell
npm run dev
```

Dat start backend en frontend samen via de centrale launcher.

## Alleen backend starten

Als je alleen de backend wilt draaien voor diagnose of API-werk:

```powershell
npm run dev:backend
```

De backend draait dan op:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Setup

Eerste keer of na een schone omgeving:

```powershell
npm run setup:backend
```

Dat maakt de virtual environment aan, installeert dependencies en initialiseert de database als die ontbreekt.

## Handmatig backend starten

Alleen nodig als je buiten de projectlaunchers werkt:

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## Health check

```text
http://127.0.0.1:8000/health
```

Verwachte response:

```json
{"status":"healthy"}
```

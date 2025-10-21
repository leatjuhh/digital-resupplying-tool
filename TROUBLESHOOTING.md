---
tags: [documentation, troubleshooting, help, debugging]
type: reference
related: [[README]], [[GETTING_STARTED]], [[DATABASE]], [[BATCH_SYSTEM]]
---

# Troubleshooting Guide

> 💡 **Quick Start:** Zie [[GETTING_STARTED]] voor basis setup

## ✅ Problemen Opgelost

Ik heb de volgende fixes toegepast:
1. ✅ Verwijderd: `frontend/app/api-test/page.tsx` (veroorzaakte TypeScript errors)
2. ✅ Verwijderd: `frontend/lib/api.ts` (veroorzaakte 76 TypeScript errors)
3. ✅ Verwijderd: `frontend/.env.local` (niet meer nodig)

**Status**: Frontend is teruggezet naar de originele werkende staat (voor de backend integratie)

## 🔧 Hoe de Terminal Weer Te Gebruiken

### Probleem: Terminal accepteert geen input
**Oorzaak**: Er draait waarschijnlijk een development server (frontend of backend)

**Oplossing**:
1. Klik in de terminal window
2. Druk op `Ctrl + C` om het draaiende proces te stoppen
3. Wacht tot je de command prompt weer ziet: `PS C:\...>`
4. Nu kun je weer commando's invoeren

### Als Ctrl+C niet werkt:
1. Klik op het 🗑️ (prullenbak) icoon rechtsboven in de terminal
2. Of: Open een nieuwe terminal met het `+` icoon
3. Of: Klik Terminal → New Terminal in het menu

## 🚀 Frontend Opnieuw Starten

### Stap 1: Stop huidige processen
Als er iets draait in de terminal:
```bash
# Druk Ctrl + C
```

### Stap 2: Navigeer naar frontend directory
```bash
cd frontend
```

### Stap 3: Start de frontend
```bash
npm run dev
```

### Stap 4: Wacht op Success Bericht
Je zou moeten zien:
```
✓ Ready in Xs
○ Local: http://localhost:3000
```

### Stap 5: Open Browser
Ga naar: http://localhost:3000

## 🔍 Controleer of Errors Weg Zijn

### In Cursor/VS Code:
1. Kijk naar het "Problems" tab (naast Terminal)
2. De 63 errors zouden nu weg moeten zijn
3. Als er nog errors zijn, laat het me weten

### Als frontend nog niet start:
```bash
# Stop alles (Ctrl+C), dan:
cd frontend
rm -rf .next
npm run dev
```

## 🌐 Backend Draaien (Optioneel)

Als je ook de backend wilt testen:

### Terminal 1 - Backend:
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

## ❓ Veelvoorkomende Problemen

### "Port 3000 already in use"
**Oplossing**: Er draait al een frontend server
```bash
# Stop de oude server of gebruik andere port:
npm run dev -- -p 3001
```

### "Module not found" errors
**Oplossing**: Dependencies opnieuw installeren
```bash
cd frontend
npm install
npm run dev
```

### TypeScript errors blijven
**Oplossing**: Cache clearen
```bash
cd frontend
rm -rf .next
rm -rf node_modules/.cache
npm run dev
```

## 📊 Status Checklist

- [ ] Terminal accepteert weer input (Ctrl+C werkt)
- [ ] Frontend start zonder errors
- [ ] Browser toont de applicatie op http://localhost:3000
- [ ] Problems tab heeft 0 errors
- [ ] (Optioneel) Backend draait op http://localhost:8000

## 🆘 Als Niets Werkt

1. Sluit Cursor/VS Code volledig af
2. Heropen het project
3. Open een frisse terminal
4. Probeer frontend opnieuw te starten

## 📞 Hulp Nodig?

Laat me weten:
- Hoeveel errors staan er nog in Problems tab?
- Wat is de laatste error message in de terminal?
- Kan je nu wel weer typen in de terminal?

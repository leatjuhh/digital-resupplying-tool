# Frontend-Backend Integratie - Test Guide

## ✅ Wat is er Gebouwd

1. **API Client** (`frontend/lib/api.ts`)
   - Simpele, geteste implementatie
   - Health check functie
   - getArticles functie
   
2. **Test Pagina** (`frontend/app/test/page.tsx`)
   - Live backend status indicator
   - Automatisch data ophalen
   - Ververs knop
   - Error handling
   - Mooie UI met alle artikel details

## 🧪 Test Stappen

### Stap 1: Backend Starten

Open een terminal en run:

```powershell
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Je zou moeten zien:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Check:** Backend API docs: http://localhost:8000/docs

---

### Stap 2: Frontend Starten

Open een **NIEUWE terminal** (laat backend draaien!) en run:

```powershell
cd frontend
npm run dev
```

**Je zou moeten zien:**
```
✓ Ready in 2.5s
○ Local:   http://localhost:3000
```

✅ **Check:** Frontend: http://localhost:3000

---

### Stap 3: Test Pagina Openen

Ga naar: **http://localhost:3000/test**

**Wat je zou moeten zien:**

✅ **Backend Status:** Groene stip + "Verbonden"
✅ **Artikelen lijst:** 5 artikelen met voorraad per winkel
✅ **Details:** SKU, naam, voorraad per winkel, totalen

**Elk artikel toont:**
- Artikelnummer (bijv. ART-001)
- Omschrijving (bijv. "Winter Jacket - Blue")
- Voorraad per winkel (Amsterdam, Rotterdam, Utrecht, Den Haag)
- Totaal aantal stuks

---

## 🔍 Verificatie Checklist

Controleer de volgende punten:

### Backend Status
- [ ] Groene stip naast "Verbonden"
- [ ] URL toont http://localhost:8000

### Artikelen Data
- [ ] 5 artikelen zichtbaar
- [ ] Elk artikel heeft een naam
- [ ] Elk artikel heeft een SKU
- [ ] Voorraad per winkel is zichtbaar
- [ ] Totaal aantal is correct

### Interactiviteit
- [ ] "Ververs" knop werkt
- [ ] Klikken op ververs laadt data opnieuw
- [ ] Tijdens laden toont het "Laden..."

### Browser Console (F12)
- [ ] Geen errors in de console
- [ ] Je ziet fetch requests naar localhost:8000

---

## ❌ Troubleshooting

### "Niet verbonden" (Rode stip)

**Probleem:** Backend draait niet of CORS issues

**Oplossing:**
1. Check of backend draait: http://localhost:8000/docs
2. Check terminal - zie je de uvicorn server?
3. Herstart beide servers

### "Kon artikelen niet laden"

**Probleem:** API request faalt

**Oplossing:**
1. Open browser console (F12)
2. Zoek naar de error message
3. Check of je CORS errors ziet
4. Verify backend endpoint: http://localhost:8000/api/articles

### TypeScript Errors

**Probleem:** Errors in Problems tab

**Oplossing:**
1. Kijk naar de errors
2. Meestal auto-fixed bij save
3. Herstart VSCode/Cursor als het blijft

### Frontend compile errors

**Probleem:** npm run dev faalt

**Oplossing:**
```powershell
cd frontend
rm -rf .next
npm run dev
```

---

## 🎉 Success Criteria

Je hebt **succesvol geïntegreerd** als:

✅ Backend Status is groen
✅ 5 artikelen worden getoond
✅ Data komt van http://localhost:8000/api/articles
✅ Geen errors in browser console
✅ Ververs knop werkt

---

## 📸 Expected Result

Je zou dit moeten zien:

```
Backend Integratie Test
━━━━━━━━━━━━━━━━━━━━━

Backend Status
🟢 Verbonden  http://localhost:8000

Artikelen van Backend                [Ververs]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Winter Jacket - Blue
SKU: ART-001

Voorraad per winkel:
Amsterdam: 15 stuks    Rotterdam: 8 stuks
Utrecht: 12 stuks      Den Haag: 6 stuks
Totaal: 41 stuks

[+ 4 meer artikelen...]
```

---

## 🚀 Volgende Stappen

Nu de integratie werkt, kun je:

1. **Database toevoegen** - Echte data opslag
2. **Meer endpoints** - CRUD operaties
3. **Authenticatie** - User login
4. **PDF Upload** - Core functionaliteit

Laat me weten wat je wilt bouwen! 🎯

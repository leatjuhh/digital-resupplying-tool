---
title: Mobile & Network Access
category: getting-started
tags: [mobile, ios, android, network, setup]
last_updated: 2025-11-02
related:
  - quick-start.md
  - troubleshooting.md
---

# Mobile & Network Access

Deze handleiding legt uit hoe je de Digital Resupplying Tool toegankelijk maakt vanaf je iOS/Android apparaat op hetzelfde netwerk.

## Inhoudsopgave
- [Quick Start](#quick-start)
- [Wat is er veranderd?](#wat-is-er-veranderd)
- [Handmatige Setup](#handmatige-setup)
- [Troubleshooting](#troubleshooting)
- [Terug naar Localhost](#terug-naar-localhost)

---

## Quick Start

### Automatische Setup (Aanbevolen)

1. **Run het setup script:**
   ```powershell
   .\setup-mobile.ps1
   ```

2. **Start de development servers:**
   ```powershell
   .\dev.ps1
   ```

3. **Open op je iOS/Android apparaat:**
   - Het script toont je lokale IP (bijv. `192.168.1.100`)
   - Ga naar: `http://[JE-IP]:3000`

**Voorbeeld:**
```
http://192.168.1.100:3000
```

---

## Wat is er veranderd?

### Backend Changes

1. **Host Binding** - Backend luistert nu op `0.0.0.0` (alle network interfaces):
   ```python
   # backend/.env
   BACKEND_HOST=0.0.0.0
   ```

2. **CORS Configuration** - Toegang vanaf lokale netwerk IP's toegestaan:
   ```python
   # Staat toe: localhost, 127.0.0.1, 192.168.x.x, 10.x.x.x, 172.x.x.x
   allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.\d+\.\d+\.\d+):3000"
   ```

### Frontend Changes

1. **Environment Variable** - API URL is nu configureerbaar:
   ```typescript
   // frontend/lib/api-client.ts
   const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
   ```

2. **Configuration File** - Nieuwe `.env.local` file:
   ```bash
   # frontend/.env.local
   NEXT_PUBLIC_API_URL=http://192.168.1.100:8000
   ```

---

## Handmatige Setup

Als je het setup script niet wilt gebruiken:

### Stap 1: Zoek je Local IP Address

**Windows:**
```powershell
ipconfig
```
Zoek naar "IPv4 Address" onder je actieve network adapter (WiFi of Ethernet).

**Alternatief:**
```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like '*Wi-Fi*'}
```

### Stap 2: Update Frontend Config

Edit `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://[JE-LOCAL-IP]:8000
```

**Voorbeeld:**
```bash
NEXT_PUBLIC_API_URL=http://192.168.1.100:8000
```

### Stap 3: Start Servers

De backend is al geconfigureerd om op alle interfaces te luisteren:
```powershell
.\dev.ps1
```

### Stap 4: Test op Mobile

Open op je mobile device:
```
http://[JE-LOCAL-IP]:3000
```

---

## Troubleshooting

### Kan App Niet Bereiken

**Probleem:** iOS/Android kan de app niet laden.

**Oplossingen:**

1. **Check netwerk:**
   - Zorg dat je mobile device op **hetzelfde WiFi netwerk** zit als je PC
   - Geen gastennetwerk gebruiken

2. **Check firewall:**
   ```powershell
   # Windows Firewall rule toevoegen voor poorten 3000 en 8000
   New-NetFirewallRule -DisplayName "Digital Resupplying - Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
   New-NetFirewallRule -DisplayName "Digital Resupplying - Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

3. **Verify servers draaien:**
   - Check of beide servers gestart zijn
   - Test op PC eerst: `http://localhost:3000`

4. **Check IP address:**
   - Run `ipconfig` opnieuw om je huidige IP te bevestigen
   - IP adressen kunnen veranderen (vooral bij DHCP)

### CORS Errors in Browser

**Probleem:** "CORS policy: No 'Access-Control-Allow-Origin' header"

**Oplossing:**
- Backend moet herstart worden na CORS wijzigingen
- Check dat je het correcte IP format gebruikt (geen https://)

### API Calls Falen

**Probleem:** Network errors of timeouts

**Diagnose:**
1. Test backend direct vanuit iOS Safari:
   ```
   http://[JE-IP]:8000/health
   ```
   Verwacht resultaat: `{"status":"healthy"}`

2. Check backend logs voor inkomende requests

3. Verify `.env.local` bevat het juiste IP

### Authentication Issues

**Probleem:** Kan niet inloggen vanaf mobile

**Check:**
- Tokens worden correct opgeslagen in localStorage
- API URL in frontend is correct ingesteld
- Backend health endpoint is bereikbaar

---

## Terug naar Localhost

Om terug te schakelen naar lokale development (alleen PC):

### Optie 1: Edit .env.local

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Optie 2: Verwijder .env.local

```powershell
Remove-Item frontend/.env.local
```
Frontend valt terug op default `localhost:8000`.

### Herstart Frontend

```powershell
# Stop huidige servers (Ctrl+C)
# Start opnieuw
.\dev.ps1
```

---

## Network Security Notes

### Development Mode

⚠️ **Deze configuratie is ALLEEN voor development/testing!**

**Waarom:**
- Backend luistert op alle interfaces (0.0.0.0)
- CORS staat alle lokale netwerk origins toe
- Geen HTTPS/SSL encryption
- Secret keys zijn voor development

### Production Deployment

Voor productie gebruik:
- Specifieke IP whitelisting in plaats van wildcards
- HTTPS/SSL certificates
- Sterke secret keys
- Firewall configuratie
- Reverse proxy (nginx/Apache)

---

## Tips & Best Practices

### Stabiel IP Address

Om je IP address stabiel te houden:

1. **Static IP in Router:**
   - Log in op je router
   - Configureer DHCP reservation voor je PC's MAC address

2. **Static IP op PC:**
   - Control Panel → Network Connections
   - Right-click adapter → Properties
   - IPv4 → Use following IP address

### Development Workflow

**Aanbevolen workflow:**

1. Develop lokaal op PC met localhost
2. Voor mobile testing:
   - Run `.\setup-mobile.ps1`
   - Test op mobile
3. Switch terug naar localhost voor verder development

### Quick Network Check Script

Maak `check-network.ps1`:
```powershell
$ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "*Wi-Fi*").IPAddress
Write-Host "Local IP: $ip"
Write-Host "Frontend URL: http://${ip}:3000"
Write-Host "Backend URL: http://${ip}:8000"
```

---

## Veelgestelde Vragen

**Q: Moet ik elke keer setup-mobile.ps1 runnen?**
A: Alleen als je IP address verandert. Als je een static IP gebruikt, één keer is genoeg.

**Q: Werkt dit ook met Android?**
A: Ja! Dezelfde setup werkt voor iOS, Android, en andere devices op het netwerk.

**Q: Kan ik tegelijk vanaf PC en mobile testen?**
A: Ja, meerdere clients kunnen tegelijk verbinden met de development servers.

**Q: Waarom zie ik "localhost refused to connect" op mobile?**
A: Je gebruikt waarschijnlijk nog de localhost URL. Mobile devices kennen geen "localhost" - gebruik het IP address.

**Q: Mijn IP verandert vaak, is er een makkelijkere manier?**
A: Gebruik een static IP in je router settings, of run het setup script elke keer voordat je gaat testen.

---

## Samenvatting

**Voor Mobile Access:**
```powershell
# 1. Setup
.\setup-mobile.ps1

# 2. Start
.\dev.ps1

# 3. Browse op mobile
http://[JE-IP]:3000
```

**Terug naar Localhost:**
```bash
# Edit frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Voor meer hulp, zie [Troubleshooting Guide](troubleshooting.md).

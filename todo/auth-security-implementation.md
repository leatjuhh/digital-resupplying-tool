# Authentication & Security Implementatie Plan

## Overzicht
Volledige implementatie van authentication systeem met rol-gebaseerd toegangsbeheer voor Digital Resupplying Tool.

## Security Strategie

### Fase 1: Intern Netwerk (HUIDIGE FASE)
**Deployment:** Lumitex intern netwerk  
**Status:** ✅ SAFE voor productie

#### Implementatie Details
- **Volledig functioneel login systeem** met JWT tokens
- **Password hashing** met bcrypt (cost factor 12)
- **Session management** met "Remember Me" functie
- **Role-based access control** (RBAC)
- **HTTP toegestaan** binnen intern netwerk
- **CORS** ingesteld voor localhost development

#### Security Maatregelen (Intern Netwerk)
✅ Password hashing (bcrypt)  
✅ JWT tokens met expiration  
✅ Role-based permissions  
✅ Input validatie  
✅ SQL injection bescherming (SQLAlchemy ORM)  
✅ XSS bescherming (React)  
⚠️ HTTP (geen HTTPS nodig binnen intern netwerk)  
⚠️ Basic rate limiting  

### Fase 2: Online Hosting (TOEKOMSTIG)
**Deployment:** Publiek internet / Cloud  
**Status:** ⏳ VEREIST AANVULLENDE SECURITY

#### Extra Vereisten voor Online Deployment

##### 🔒 KRITIEK (Verplicht voor online)
1. **HTTPS/SSL Certificaat**
   - Let's Encrypt certificaat
   - Alle HTTP verkeer redirecten naar HTTPS
   - HSTS headers instellen
   - Bestand: `backend/main.py` - SSL middleware toevoegen

2. **Environment Variables Security**
   - `.env` bestand NOOIT committen
   - Secrets management systeem (AWS Secrets Manager / Azure Key Vault)
   - Database credentials rotatie
   - API keys encryption at rest

3. **Database Security**
   - Migratie van SQLite naar PostgreSQL
   - Database in private subnet
   - SSL/TLS voor database connecties
   - Regular automated backups
   - Bestand: `backend/database.py` - PostgreSQL configuratie

4. **Rate Limiting & DDoS Bescherming**
   - Rate limiting per IP en per user
   - Cloudflare of AWS WAF
   - Login attempt throttling (max 5 per 15 min)
   - Bestand: `backend/middleware/rate_limit.py` - Implementeren

5. **Security Headers**
   - Content-Security-Policy
   - X-Frame-Options: DENY
   - X-Content-Type-Options: nosniff
   - Referrer-Policy
   - Bestand: `backend/middleware/security_headers.py` - Implementeren

##### 🛡️ BELANGRIJK (Sterk aanbevolen)
6. **Audit Logging**
   - Alle security events loggen
   - Login attempts (success/failure)
   - Permission changes
   - User modifications
   - Settings wijzigingen
   - Bestand: `backend/db_models.py` - AuditLog model toevoegen

7. **Two-Factor Authentication (2FA)**
   - TOTP (Time-based One-Time Password)
   - QR code generation voor authenticator apps
   - Backup codes
   - Bestanden: `backend/routers/auth.py`, `backend/models/user.py`

8. **Session Security**
   - Secure cookie flags (HttpOnly, Secure, SameSite)
   - Session invalidation bij password change
   - Concurrent session limits
   - Bestand: `backend/auth.py` - Session management

9. **Regular Security Updates**
   - Dependency scanning (Dependabot)
   - CVE monitoring
   - Regular `pip audit` runs
   - Update policy voor dependencies

##### 📊 NUTTIG (Nice to have)
10. **Monitoring & Alerting**
    - Failed login monitoring
    - Unusual activity detection
    - Performance monitoring
    - Error tracking (Sentry)

11. **Backup & Disaster Recovery**
    - Automated daily backups
    - Backup verification
    - Disaster recovery plan
    - Recovery time objective (RTO)

12. **Penetration Testing**
    - Annual security audits
    - Vulnerability scanning
    - OWASP Top 10 compliance

## Huidige Implementatie Specificaties

### Password Policy
**Sterke security volgens OWASP guidelines:**
```python
- Minimale lengte: 12 karakters
- Maximale lengte: 128 karakters
- Vereisten:
  * Minimaal 1 hoofdletter
  * Minimaal 1 kleine letter
  * Minimaal 1 cijfer
  * Minimaal 1 speciaal karakter (!@#$%^&*(),.?":{}|<>)
- Verboden:
  * Veelvoorkomende passwords (top 10000 lijst)
  * Sequenties (123456, abcdef)
  * Herhalingen (aaaaaa)
  * Gebruikersnaam in password
```

### JWT Token Management
```python
- Access Token Expiration: 15 minuten
- Refresh Token Expiration: 7 dagen (Remember Me: OFF)
- Refresh Token Expiration: 30 dagen (Remember Me: ON)
- Algorithm: HS256
- Token bevat: user_id, role, permissions, exp, iat
```

### Remember Me Functie
```python
- Checkbox in login form
- Gebruikt langere refresh token (30 dagen)
- Stored in secure HttpOnly cookie
- Auto-refresh bij expiratie access token
```

### Role System
**3 Default Rollen:**
1. **Admin** - Volledige toegang
2. **User** - Hoofdkantoor medewerker
3. **Store** - Winkel medewerker

**UI voor Role Management:**
- Nieuwe rollen aanmaken
- Permissions per rol configureren
- Default rollen niet verwijderbaar
- Minimaal 1 admin account verplicht

### Permissions Systeem
**Categorieën:**
- `proposals` - Voorstellen beheer
- `assignments` - Opdrachten beheer  
- `users` - Gebruikersbeheer
- `settings` - Instellingen beheer
- `roles` - Rollenbeheer
- `uploads` - PDF uploads
- `batches` - Batch beheer

**Specifieke Permissions:**
```
view_dashboard
view_proposals
create_proposals
approve_proposals
reject_proposals
edit_proposals
delete_proposals
view_assignments
manage_assignments
view_users
manage_users
view_settings
manage_general_settings
manage_rules_settings
manage_api_settings
manage_roles
manage_permissions
upload_pdfs
view_batches
manage_batches
```

## Implementatie Checklist

### Backend
- [ ] Database models (User, Role, Permission, RolePermission, Settings)
- [ ] Password hashing utilities (bcrypt)
- [ ] JWT token generation/validation
- [ ] Auth middleware (get_current_user, require_permission)
- [ ] Auth router (login, logout, refresh, me)
- [ ] Users router (CRUD operations)
- [ ] Roles router (CRUD + permissions)
- [ ] Settings router (general, rules, api)
- [ ] Seed data (users, roles, permissions)
- [ ] Password validation
- [ ] Remember me functionality

### Frontend
- [ ] Auth context (login, logout, user state)
- [ ] Login page
- [ ] Protected route wrapper
- [ ] Permission checks in UI
- [ ] API client updates
- [ ] Token refresh logic
- [ ] Remember me checkbox
- [ ] Settings API integration
- [ ] User management UI updates
- [ ] Role management UI

### Testing
- [ ] Login flow
- [ ] JWT token validation
- [ ] Permission checks
- [ ] Remember me functionaliteit
- [ ] Password policy validation
- [ ] Role-based access
- [ ] Settings CRUD
- [ ] User CRUD

## Migration Path naar Online

### Stap 1: Pre-Launch Checklist
```
[ ] HTTPS/SSL certificaat geïnstalleerd
[ ] Environment variables in secret manager
[ ] PostgreSQL database opgezet
[ ] Database migrations getest
[ ] Rate limiting geïmplementeerd
[ ] Security headers geconfigureerd
[ ] Audit logging actief
[ ] Backups geconfigureerd
[ ] Monitoring ingesteld
```

### Stap 2: Launch
```
[ ] Security audit uitgevoerd
[ ] Penetration test completed
[ ] Load testing
[ ] Disaster recovery plan gedocumenteerd
[ ] Incident response plan
[ ] User training
```

### Stap 3: Post-Launch
```
[ ] Regular security updates
[ ] Log monitoring
[ ] Performance monitoring
[ ] User feedback
[ ] 2FA roll-out (optioneel)
```

## Files Affected

### Nieuw
- `backend/auth.py` - Authentication utilities
- `backend/middleware/rate_limit.py` - Rate limiting (online fase)
- `backend/middleware/security_headers.py` - Security headers (online fase)
- `backend/routers/auth.py` - Auth endpoints
- `backend/routers/users.py` - User management
- `backend/routers/roles.py` - Role management
- `backend/routers/settings.py` - Settings management
- `frontend/contexts/auth-context.tsx` - Auth state management
- `frontend/app/login/page.tsx` - Login page
- `frontend/components/auth/protected-route.tsx` - Route protection
- `todo/online-deployment-security.md` - Detailed online checklist (toekomstig)

### Aangepast
- `backend/db_models.py` - Nieuwe models
- `backend/main.py` - Auth router toevoegen
- `backend/seed_database.py` - Users en roles seeden
- `backend/requirements.txt` - Auth dependencies
- `frontend/lib/api.ts` - Auth API calls
- `frontend/app/settings/page.tsx` - Echte API calls
- `frontend/components/settings/*.tsx` - API integratie

## Security Contact

Voor security vragen of concerns tijdens online deployment:
- OWASP Resources: https://owasp.org/
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- JWT Best Practices: https://tools.ietf.org/html/rfc8725

## Status

**Huidige Fase:** ✅ Intern Netwerk Implementatie  
**Volgende Fase:** ⏳ Online Deployment (toekomstig)

**Laatste Update:** 31 oktober 2025  
**Versie:** 1.0

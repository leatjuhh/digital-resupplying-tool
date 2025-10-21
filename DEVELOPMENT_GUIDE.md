# Development Guide - Digital Resupplying Tool

Deze gids helpt ontwikkelaars om effectief bij te dragen aan het project met consistente workflows en code conventies.

## 📋 Inhoudsopgave

- [Development Workflow](#-development-workflow)
- [Git Workflow](#-git-workflow)
- [Code Conventies](#-code-conventies)
- [Testing](#-testing)
- [Dependencies Beheren](#-dependencies-beheren)
- [Database Migraties](#-database-migraties)
- [Documentatie Updates](#-documentatie-updates)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Development Workflow

### Dagelijkse Development Setup

**1. Pull laatste wijzigingen**
```powershell
git pull origin main
```

**2. Start Development Servers**

**Optie A: PowerShell script (aanbevolen)**
```powershell
.\start-dev.ps1
```

**Optie B: Manueel (twee terminals)**
```powershell
# Terminal 1 - Backend
cd backend
.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**3. Toegang tot applicatie**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Test Page: http://localhost:3000/test

**4. Development cyclus**
- Maak wijzigingen in code
- Test lokaal (zie [Testing](#-testing))
- Commit regelmatig met duidelijke messages
- Push naar GitHub

---

## 🌿 Git Workflow

### Branch Strategie

**Klein team - eenvoudig houden:**
- **main branch:** Stabiele, werkende code
- Directe commits op main voor kleine wijzigingen
- Feature branches voor grotere features

### Feature Branches (Optioneel - voor grote features)

**Branch aanmaken:**
```bash
git checkout -b feature/beschrijving
# of
git checkout -b fix/beschrijving
```

**Voorbeelden:**
- `feature/ai-suggestions`
- `feature/proposal-approval`
- `fix/pdf-parsing-bug`
- `docs/api-documentation`

**Na voltooiing:**
```bash
git checkout main
git merge feature/beschrijving
git push origin main
git branch -d feature/beschrijving
```

### Commit Conventies

**Format:** `type: beschrijving`

**Types:**
- `feat:` Nieuwe feature
- `fix:` Bug fix
- `docs:` Documentatie wijzigingen
- `style:` Code formatting (geen functionaliteit wijziging)
- `refactor:` Code refactoring
- `test:` Test toevoegingen/wijzigingen
- `chore:` Build/dependency updates

**Voorbeelden:**
```bash
git commit -m "feat: add batch PDF upload system"
git commit -m "fix: resolve artikelnummer parsing issue"
git commit -m "docs: update README with new features"
git commit -m "refactor: improve PDF parser performance"
git commit -m "test: add unit tests for PDF extraction"
```

### Standaard Workflow

**1. Maak wijzigingen**
```bash
# Bekijk status
git status

# Bekijk wijzigingen
git diff
```

**2. Stage en commit**
```bash
# Stage specifieke bestanden
git add backend/main.py frontend/app/page.tsx

# Of stage alles
git add .

# Commit met bericht
git commit -m "feat: add new feature"
```

**3. Push naar GitHub**
```bash
git push origin main
```

**4. Check GitHub**
- Verifieer dat commit zichtbaar is
- Controleer dat CI/CD (indien geconfigureerd) slaagt

---

## 📝 Code Conventies

### Python (Backend)

**Style Guide:** PEP8

**Type Hints:** Verplicht voor alle functies
```python
def parse_pdf(file_path: str, extract_tables: bool = True) -> list[dict]:
    """
    Parse PDF en extract artikelnummers.
    
    Args:
        file_path: Pad naar PDF bestand
        extract_tables: Of tabellen geëxtraheerd moeten worden
        
    Returns:
        List met geëxtraheerde artikelen
    """
    pass
```

**Naming Conventions:**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

**Docstrings:**
```python
def complex_function(param: str) -> dict:
    """
    Korte beschrijving van functie.
    
    Langere uitleg indien nodig voor complexe logica.
    
    Args:
        param: Beschrijving van parameter
        
    Returns:
        Beschrijving van return waarde
        
    Raises:
        ValueError: Wanneer param invalid is
    """
    pass
```

**Imports:**
```python
# Standaard library
import os
from typing import Optional

# Third-party
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local
from .models import Article
from .database import get_db
```

### TypeScript/React (Frontend)

**Formatting:** Prettier (automatisch in Cursor/VSCode)

**Component Structure:**
```typescript
'use client';

import React from 'react';
import { ComponentProps } from '@/types';

interface Props {
  title: string;
  items: Item[];
  onSelect?: (id: string) => void;
}

export function MyComponent({ title, items, onSelect }: Props) {
  // Component logic
  
  return (
    <div>
      {/* JSX */}
    </div>
  );
}
```

**Naming Conventions:**
- Components: `PascalCase`
- Functions/variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Types/Interfaces: `PascalCase`

**File Naming:**
- Components: `my-component.tsx`
- Utilities: `utils.ts`
- Types: `types.ts`
- API calls: `api.ts`

---

## 🧪 Testing

### Backend Tests

**Run alle tests:**
```powershell
cd backend
.venv\Scripts\python.exe -m pytest
```

**Specifieke test files:**
```powershell
.venv\Scripts\python.exe test_batch_api.py
.venv\Scripts\python.exe test_pdf_extraction.py
```

**Test schrijven:**
```python
# test_feature.py
import pytest
from main import app

def test_endpoint():
    """Test beschrijving."""
    # Arrange
    data = {"key": "value"}
    
    # Act
    response = client.post("/api/endpoint", json=data)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["result"] == "expected"
```

### Frontend Tests

**Build check (detecteert TypeScript errors):**
```powershell
cd frontend
npm run build
```

**Linting:**
```powershell
npm run lint
```

### Manual Testing Checklist

- [ ] Backend API werkt (http://localhost:8000/docs)
- [ ] Frontend laadt correct (http://localhost:3000)
- [ ] Batch upload functionaliteit
- [ ] PDF parsing werkt correct
- [ ] Database operaties succesvol
- [ ] Geen console errors in browser
- [ ] Responsive design werkt

---

## 📦 Dependencies Beheren

### Backend Dependencies

**Nieuwe package installeren:**
```powershell
cd backend
.venv\Scripts\pip.exe install <package-name>
.venv\Scripts\pip.exe freeze > requirements.txt
git add requirements.txt
git commit -m "deps: add <package-name>"
```

**Dependencies updaten:**
```powershell
.venv\Scripts\pip.exe install --upgrade <package-name>
.venv\Scripts\pip.exe freeze > requirements.txt
```

**Alle dependencies installeren:**
```powershell
.venv\Scripts\pip.exe install -r requirements.txt
```

### Frontend Dependencies

**Nieuwe package installeren:**
```powershell
cd frontend
npm install <package-name>
git add package.json package-lock.json
git commit -m "deps: add <package-name>"
```

**Dependencies updaten:**
```powershell
npm update <package-name>
```

**Alle dependencies installeren:**
```powershell
npm install
```

---

## 🗄️ Database Migraties

### Schema Wijzigingen

**1. Update models:**
```python
# backend/db_models.py
class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True)
    # Nieuwe kolom toevoegen:
    new_field = Column(String, nullable=True)
```

**2. Maak migratie script:**
```python
# backend/migrate_add_field.py
from database import engine, SessionLocal
from sqlalchemy import text

def migrate():
    """Add new_field to articles table."""
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE articles 
            ADD COLUMN new_field TEXT
        """))
        conn.commit()

if __name__ == "__main__":
    migrate()
    print("Migration completed")
```

**3. Run migratie:**
```powershell
cd backend
.venv\Scripts\python.exe migrate_add_field.py
```

**4. Test migratie:**
```powershell
.venv\Scripts\python.exe test_migration.py
```

**5. Commit:**
```bash
git add backend/db_models.py backend/migrate_add_field.py
git commit -m "feat: add new_field to articles table"
```

### Database Reset (Development)

**⚠️ Verwijdert alle data!**
```powershell
cd backend
Remove-Item database.db
.venv\Scripts\python.exe seed_database.py
```

---

## 📝 Documentatie Updates

### Bij Nieuwe Features

**Update documentatie in deze volgorde:**

1. **README.md** - Project status sectie
2. **CHANGELOG.md** - Voeg feature toe onder juiste versie
3. **Specifieke .md bestanden** - BATCH_SYSTEM.md, DATABASE.md, etc.
4. **Code comments** - Docstrings en inline comments

**Commit message:**
```bash
git commit -m "docs: update documentation for <feature>"
```

### Documentatie Structuur

```
project/
├── README.md              # Project overview & quick start
├── CHANGELOG.md           # Version history
├── DEVELOPMENT_GUIDE.md   # Dit bestand
├── GETTING_STARTED.md     # Nieuwe developer setup
├── BATCH_SYSTEM.md        # Batch feature documentatie
├── DATABASE.md            # Database schema & queries
├── INTEGRATION.md         # Frontend-backend integratie
└── TROUBLESHOOTING.md     # Veelvoorkomende problemen
```

---

## 🚨 Troubleshooting

Zie **[[TROUBLESHOOTING.md]]** voor uitgebreide troubleshooting.

### Quick Fixes

**Port al in gebruik:**
```powershell
# Check actieve processen
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill proces (gebruik PID van netstat)
taskkill /PID <PID> /F
```

**Database errors:**
```powershell
cd backend
Remove-Item database.db
.venv\Scripts\python.exe seed_database.py
```

**Dependency issues:**
```powershell
# Backend
cd backend
Remove-Item -Recurse -Force .venv
python -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt

# Frontend
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
```

**Git conflicts:**
```bash
# Bekijk conflict
git status

# Reset naar laatste commit (⚠️ verliest lokale wijzigingen)
git reset --hard HEAD

# Of resolve manueel en commit
git add .
git commit -m "fix: resolve merge conflict"
```

---

## 🎯 Best Practices

### Development

1. **Test lokaal** voor elke commit
2. **Commit vaak** met kleine, logische wijzigingen
3. **Pull regelmatig** om sync te blijven met team
4. **Documenteer** complexe logica in code comments
5. **Review eigen code** voor het pushen

### Code Quality

1. **Type hints** in Python
2. **TypeScript strict mode** in frontend
3. **Error handling** overal waar nodig
4. **Logging** voor debugging (niet print statements)
5. **DRY principe** - Don't Repeat Yourself

### Git

1. **Duidelijke commit messages**
2. **Kleine commits** (één logische wijziging per commit)
3. **Feature branches** voor grote features
4. **Pull voor push** om conflicts te voorkomen
5. **Review changes** met `git diff` voor commit

---

## 📞 Hulp Nodig?

- **Documentatie:** Zie andere .md bestanden in project root
- **API Docs:** http://localhost:8000/docs
- **Issues:** Check bestaande issues op GitHub
- **Team:** Neem contact op met development team

---

**Laatst bijgewerkt:** 2025-10-21  
**Versie:** 1.0

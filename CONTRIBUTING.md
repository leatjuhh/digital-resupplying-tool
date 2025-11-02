# Contributing to Digital Resupplying Tool

Bedankt voor je interesse om bij te dragen aan het Digital Resupplying Tool project! 🎉

Dit document bevat richtlijnen voor het bijdragen aan het project, zodat we een consistente en hoogwaardige codebase kunnen behouden.

---

## 📋 Inhoudsopgave

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Conventions](#code-conventions)
- [Commit Guidelines](#commit-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

### Onze Belofte

Wij streven naar een open en welkom omgeving voor iedereen, ongeacht:
- Ervaring level
- Geslacht, genderidentiteit en -expressie
- Seksuele oriëntatie
- Handicap
- Persoonlijke verschijning
- Etniciteit, nationaliteit of religie

### Verwacht Gedrag

- Gebruik welkomend en inclusief taalgebruik
- Respecteer verschillende standpunten en ervaringen
- Accepteer constructieve kritiek gracieus
- Focus op wat het beste is voor de community
- Toon empathie naar andere community leden

### Onacceptabel Gedrag

- Trollen, beledigende/denigrerende opmerkingen
- Publieke of private intimidatie
- Publiceren van privé-informatie zonder toestemming
- Andere gedrag dat redelijkerwijs als ongepast beschouwd kan worden

### Handhaving

Gevallen van onacceptabel gedrag kunnen gerapporteerd worden via GitHub Issues. Alle klachten worden beoordeeld en onderzocht.

---

## Getting Started

### Vereisten

Zorg dat je het volgende geïnstalleerd hebt:

- **Python 3.11+** - Backend development
- **Node.js 18+** - Frontend development  
- **Git** - Version control
- **VSCode/Cursor** - Aanbevolen editors

### Development Setup

1. **Clone de repository:**
```bash
git clone https://github.com/your-org/digital-resupplying-tool.git
cd digital-resupplying-tool
```

2. **Installeer dependencies:**
```bash
npm run setup
```

3. **Start development servers:**
```bash
npm run dev
```

Zie [Quick Start Guide](docs/getting-started/quick-start.md) voor gedetailleerde installatie-instructies.

---

## Development Workflow

### Standard Workflow

1. **Pull laatste wijzigingen:**
```bash
git pull origin main
```

2. **Maak wijzigingen in je code**

3. **Test lokaal:**
```bash
# Backend tests
cd backend
.venv\Scripts\python.exe -m pytest

# Frontend build check
cd frontend
npm run build
```

4. **Commit met duidelijke message:**
```bash
git add .
git commit -m "feat: add new feature"
```

5. **Push naar GitHub:**
```bash
git push origin main
```

### Branch Strategie

**Voor kleine wijzigingen:**
- Direct commit op `main` branch is OK

**Voor grote features:**
- Maak een feature branch:
```bash
git checkout -b feature/beschrijving
```

- Na voltooiing, merge naar main:
```bash
git checkout main
git merge feature/beschrijving
git push origin main
git branch -d feature/beschrijving
```

**Branch naming conventies:**
- `feature/` - Nieuwe features
- `fix/` - Bug fixes
- `docs/` - Documentatie wijzigingen
- `refactor/` - Code refactoring

---

## Code Conventions

### Python (Backend)

**Style Guide:** PEP8

**Type Hints verplicht:**
```python
def parse_pdf(file_path: str, extract_tables: bool = True) -> list[dict]:
    """
    Parse PDF en extract artikelnummers.
    
    Args:
        file_path: Pad naar PDF bestand
        extract_tables: Of tabellen geëxtraheerd moeten worden
        
    Returns:
        List met geëxtraheerde artikelen
        
    Raises:
        ValueError: Wanneer file_path ongeldig is
    """
    pass
```

**Naming Conventions:**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

**Import Order:**
```python
# 1. Standaard library
import os
from typing import Optional

# 2. Third-party
from fastapi import FastAPI
from pydantic import BaseModel

# 3. Local imports
from .models import Article
from .database import get_db
```

### TypeScript/React (Frontend)

**Formatting:** Prettier (automatisch in editors)

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
- Files: `kebab-case.tsx`

---

## Commit Guidelines

### Commit Message Format

```
type: subject

body (optioneel)

footer (optioneel)
```

### Types

- `feat:` - Nieuwe feature
- `fix:` - Bug fix
- `docs:` - Documentatie wijzigingen
- `style:` - Code formatting (geen functionaliteit wijziging)
- `refactor:` - Code refactoring
- `test:` - Test toevoegingen/wijzigingen
- `chore:` - Build/dependency updates

### Voorbeelden

```bash
feat: add batch PDF upload system

fix: resolve artikelnummer parsing issue in PDF parser

docs: update README with new batch system features

refactor: improve PDF parser performance by 50%

test: add unit tests for PDF extraction module
```

### Best Practices

✅ **DO:**
- Beschrijvende subject lines (max 72 karakters)
- Present tense gebruiken ("add" niet "added")
- Begin met lowercase na type:
- Elke commit moet een logische wijziging bevatten

❌ **DON'T:**
- Vage messages ("fix stuff", "updates")
- Meerdere ongerelateerde wijzigingen in één commit
- Commit messages zonder type prefix

---

## Testing

### Backend Tests

```bash
cd backend
.venv\Scripts\python.exe -m pytest
```

**Test schrijven:**
```python
def test_pdf_extraction():
    """Test PDF artikelnummer extractie."""
    # Arrange
    pdf_path = "test.pdf"
    
    # Act
    result = extract_articles(pdf_path)
    
    # Assert
    assert len(result) > 0
    assert result[0].article_number.isdigit()
```

### Frontend Tests

```bash
cd frontend
npm run build    # Type check
npm run lint     # Lint check
```

### Manual Testing Checklist

Voor elke wijziging:
- [ ] Backend API werkt (http://localhost:8000/docs)
- [ ] Frontend laadt correct
- [ ] Geen console errors
- [ ] Responsive design werkt
- [ ] Feature werkt zoals verwacht

---

## Documentation

### Wanneer Documentatie Bijwerken

**ALTIJD update documentatie wanneer je:**
- Nieuwe features toevoegt
- API endpoints wijzigt
- Configuration opties toevoegt/wijzigt
- Bug fixes die gebruikers beïnvloeden

### Documentatie Regels

⚠️ **BELANGRIJK:** Volg de [Documentation Guidelines](docs/DOCUMENTATION_GUIDELINES.md) voor het toevoegen van nieuwe documentatie!

**Checklist voor nieuwe documentatie:**
- [ ] Bepaal juiste categorie (getting-started/guides/technical/sessions)
- [ ] Gebruik lowercase-with-dashes.md naming
- [ ] Voeg YAML frontmatter toe
- [ ] Update README.md met link
- [ ] Gebruik relatieve links

**Verboden:**
- ❌ Nieuwe .md bestanden in root directory
- ❌ UPPERCASE bestandsnamen (behalve README, CHANGELOG, CONTRIBUTING, LICENSE)
- ❌ Wiki-style [[links]]

### Waar Documentatie Toevoegen

```
docs/
├── getting-started/    # Voor nieuwe gebruikers
├── guides/            # Feature guides & tutorials
├── technical/         # Technische/architectuur docs
└── sessions/          # Development session logs (YYYY-MM-DD.md)
```

Zie [Documentation Guidelines](docs/DOCUMENTATION_GUIDELINES.md) voor complete instructies.

---

## Pull Request Process

### Voor Grote Features

1. **Maak feature branch:**
```bash
git checkout -b feature/mijn-feature
```

2. **Ontwikkel en test:**
- Schrijf code
- Schrijf tests
- Update documentatie
- Test lokaal

3. **Commit regelmatig:**
```bash
git add .
git commit -m "feat: implement part of feature"
```

4. **Push naar GitHub:**
```bash
git push origin feature/mijn-feature
```

5. **Open Pull Request:**
- Ga naar GitHub repository
- Klik "New Pull Request"
- Selecteer feature branch
- Schrijf duidelijke beschrijving
- Link naar relevante issues

6. **Review proces:**
- Wacht op code review
- Adresseer feedback
- Merge wanneer goedgekeurd

### PR Template

```markdown
## Beschrijving
[Wat doet deze PR?]

## Type wijziging
- [ ] Bug fix
- [ ] Nieuwe feature
- [ ] Breaking change
- [ ] Documentatie update

## Checklist
- [ ] Code volgt project conventies
- [ ] Tests toegevoegd/geüpdatet
- [ ] Documentatie geüpdatet
- [ ] Geen console errors
- [ ] Lokaal getest

## Screenshots (indien van toepassing)
[Voeg screenshots toe]
```

---

## Dependencies Beheren

### Backend (Python)

**Nieuwe dependency toevoegen:**
```bash
cd backend
.venv\Scripts\pip.exe install <package>
.venv\Scripts\pip.exe freeze > requirements.txt
git add requirements.txt
git commit -m "deps: add <package>"
```

### Frontend (Node)

**Nieuwe dependency toevoegen:**
```bash
cd frontend
npm install <package>
git add package.json package-lock.json
git commit -m "deps: add <package>"
```

---

## Database Wijzigingen

### Schema Updates

**1. Update model:**
```python
# backend/db_models.py
class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True)
    new_field = Column(String, nullable=True)  # Nieuw!
```

**2. Maak migratie script:**
```python
# backend/migrate_add_field.py
from database import engine
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
```bash
cd backend
.venv\Scripts\python.exe migrate_add_field.py
```

**4. Test:**
```bash
.venv\Scripts\python.exe check_db.py
```

**5. Commit:**
```bash
git add backend/db_models.py backend/migrate_add_field.py
git commit -m "feat: add new_field to articles table"
```

---

## Project Structuur

```
digital-resupplying-tool/
├── README.md                  # Project overview
├── CHANGELOG.md               # Version history
├── CONTRIBUTING.md            # Dit bestand
├── LICENSE                    # MIT License
│
├── docs/                      # Documentatie
│   ├── DOCUMENTATION_GUIDELINES.md
│   ├── getting-started/
│   ├── guides/
│   ├── technical/
│   └── sessions/
│
├── backend/                   # Python FastAPI backend
│   ├── main.py               # FastAPI app
│   ├── database.py           # Database setup
│   ├── db_models.py          # SQLAlchemy models
│   ├── models.py             # Pydantic models
│   ├── routers/              # API endpoints
│   ├── redistribution/       # Redistribution algorithm
│   └── pdf_extract/          # PDF parsing
│
├── frontend/                  # Next.js frontend
│   ├── app/                  # Next.js pages
│   ├── components/           # React components
│   ├── lib/                  # Utilities
│   └── public/               # Static assets
│
├── todo/                      # Todo items
├── archive/                   # Archived docs
└── dummyinfo/                # Test data
```

---

## Hulp Nodig?

### Resources

- **Documentatie:** Zie [docs/](docs/) folder
- **API Docs:** http://localhost:8000/docs
- **GitHub Issues:**  Maak een issue voor vragen/bugs
- **Quick Start:** [docs/getting-started/quick-start.md](docs/getting-started/quick-start.md)

### Contact

Voor vragen over bijdragen:
1. Check bestaande GitHub Issues
2. Maak een nieuwe Issue met label "question"
3. Neem contact op met het development team

---

## Licentie

Door bij te dragen aan dit project, ga je akkoord dat je bijdragen gelicenseerd worden onder de MIT License.

---

**Bedankt voor je bijdrage! 🚀**

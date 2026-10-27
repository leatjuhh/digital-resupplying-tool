# 📚 Documentation Guidelines

**Versie:** 1.2  
**Laatst bijgewerkt:** 13 juli 2026

> ⚠️ **BELANGRIJK**: Dit document bevat strikte regels voor het toevoegen en beheren van documentatie. Volg deze regels om wildgroei te voorkomen!

---

## 🎯 Doel

Dit document zorgt ervoor dat:
- Documentatie georganiseerd blijft
- Geen wildgroei ontstaat in de root folder
- Nieuwe documentatie op de juiste plek komt
- Het project professioneel en navigeerbaar blijft

---

## 📁 Documentatie Structuur

```
project-root/
├── README.md                    # ✅ Project overview & entry point
├── CHANGELOG.md                 # ✅ Versiegeschiedenis
├── CONTRIBUTING.md              # ✅ Contributing guidelines
├── AGENTS.md                    # ✅ Agent context & prompt-ingang
├── CLAUDE.md                    # ✅ Claude Code-adapter (importeert de standaard)
├── CHATGPT_PROJECT_INSTRUCTIONS.md  # ✅ Zelfstandige ChatGPT-projectinstructies
├── LICENSE                      # ✅ License file
│
├── docs/                        # 📁 ALLE overige documentatie gaat hier
│   ├── DOCUMENTATION_GUIDELINES.md  # Dit document
│   ├── getting-started/         # Voor nieuwe gebruikers
│   ├── guides/                  # User & developer guides
│   ├── technical/               # Technische documentatie
│   ├── engineering/             # Engineeringstandaard, audits, verbeterplannen
│   ├── references/              # Externe bronbestanden, alleen-lezen
│   └── sessions/                # Development session logs
│
├── todo/                        # ✅ Todo items en planning
└── archive/                     # ✅ Oude/verouderde documentatie
```

---

## ✅ REGEL 1: Maximaal 7 MD Bestanden in Root

**Root level mag ALLEEN bevatten:**

1. `README.md` - Project overview en entry point
2. `CHANGELOG.md` - Versiegeschiedenis
3. `CONTRIBUTING.md` - Contributing guidelines
4. `AGENTS.md` - Korte agent-instructies en context-ingang voor toekomstige prompts
5. `CLAUDE.md` - Claude Code-adapter (importeert de canonieke engineeringstandaard)
6. `CHATGPT_PROJECT_INSTRUCTIONS.md` - Zelfstandige, kopieerbare ChatGPT-projectinstructies
7. `LICENSE` - License file

> **Conflictoplossing:** `.clinerules` vermeldde eerder "maximaal 4" (zonder `AGENTS.md`). Dit document is voortaan dé bron voor deze whitelist en `.clinerules` volgt. Reden voor de uitbreiding naar 7: AI-adapterbestanden (`AGENTS.md`, `CLAUDE.md`, `CHATGPT_PROJECT_INSTRUCTIONS.md`) moeten in de root staan omdat hun respectievelijke tools (Claude Code, ChatGPT-projecten, overige agents) ze daar automatisch verwachten.

**❌ VERBODEN in root:**
- Feature documentatie
- Technical reports
- Getting started guides
- Session logs
- Analyses
- Overige guides

**✅ Deze gaan naar `docs/` folder!**

---

## ✅ REGEL 2: Gebruik de Juiste Subfolder

### `docs/getting-started/`
**Voor:** Documentatie voor nieuwe gebruikers en eerste stappen

**Voorbeelden:**
- `quick-start.md` - Snelle start gids
- `installation.md` - Installatie instructies
- `troubleshooting.md` - Veelvoorkomende problemen

**Template naam:** `lowercase-with-dashes.md`

---

### `docs/guides/`
**Voor:** User en developer guides voor specifieke features

**Voorbeelden:**
- `cursor-workflow.md` - Cursor AI workflow
- `batch-system.md` - Batch upload systeem
- `database.md` - Database management
- `integration.md` - Frontend-backend integratie

**Template naam:** `lowercase-with-dashes.md`

---

### `docs/technical/`
**Voor:** Technische documentatie, architectuur, analyses

**Voorbeelden:**
- `pdf-extraction-system.md` - PDF parsing technisch
- `gui-overview.md` - GUI architectuur
- `api-reference.md` - API specificaties
- `performance-analysis.md` - Performance rapporten

**Template naam:** `lowercase-with-dashes.md`

---

### `docs/sessions/`
**Voor:** Development session logs (dag logs)

**Template naam:** `YYYY-MM-DD.md`

**Voorbeelden:**
- `2025-10-31.md`
- `2025-11-15.md`

**Format:**
```markdown
# Development Session - [Datum]

## Wat is er gedaan
- Feature X geïmplementeerd
- Bug Y opgelost

## Problemen
- Issue Z gevonden

## Volgende stappen
- [ ] Todo item 1
```

---

### `docs/engineering/`
**Voor:** Engineeringstandaard, production-readiness audits en gefaseerde verbeterplannen

**Voorbeelden:**
- `PRODUCTION_ENGINEERING_STANDARD.md` - Canonieke projectstandaard (P10-vertaling)
- `PRODUCTION_READINESS_AUDIT.md` - Bevindingen met bewijs (pad:regel)
- `PRODUCTION_READINESS_PLAN.md` - Gefaseerd verbeterplan
- `AI_SESSION_HANDOFF.md` - Sjabloon voor sessie-overdracht

**Template naam:** `UPPERCASE_WITH_UNDERSCORES.md` (afwijkend van REGEL 4 hieronder — deze documenten zijn normatief en volgen hun eigen vaste naamgeving, gelijk aan `README.md`/`CHANGELOG.md`)

**Belangrijk:** wijzig deze documenten alleen via het wijzigingsbeheerproces dat de standaard zelf beschrijft (zie hoofdstuk 16 van `PRODUCTION_ENGINEERING_STANDARD.md`), niet ad hoc.

---

### `docs/references/`
**Voor:** Externe bronbestanden waarop projectstandaarden zijn gebaseerd

**Voorbeelden:**
- `P10.pdf` - "The Power of Ten" (Holzmann/NASA-JPL), bron van de engineeringstandaard

**Belangrijk:** alleen-lezen. De inhoud van bestanden in deze map wordt nooit gewijzigd; een nieuwe bron wordt als apart bestand toegevoegd, nooit een bestaande overschreven.

---

## ✅ REGEL 3: Documentatie Template

**Gebruik altijd deze header:**

```markdown
---
title: [Document Titel]
category: [getting-started|guides|technical|sessions]
tags: [tag1, tag2, tag3]
last_updated: YYYY-MM-DD
related:
  - path/to/related/doc.md
  - path/to/another/doc.md
---

# [Document Titel]

[Korte beschrijving wat dit document behandelt]

## Inhoudsopgave
- [Sectie 1](#sectie-1)
- [Sectie 2](#sectie-2)

---

[Document inhoud]
```

---

## ✅ REGEL 4: Bestandsnaming Conventies

### Standaard Format
**Gebruik:** `lowercase-with-dashes.md`

**✅ Goed:**
- `quick-start.md`
- `batch-system.md`
- `pdf-extraction-system.md`
- `contributing-guidelines.md`

**❌ Fout:**
- `QuickStart.md` (geen PascalCase)
- `quick_start.md` (geen underscores)
- `QUICK-START.md` (niet volledig uppercase)
- `quickstart.md` (gebruik dashes voor leesbaarheid)

### Uitzonderingen in Root
**Alleen deze mogen UPPERCASE zijn:**
- `README.md` (GitHub conventie)
- `CHANGELOG.md` (Standaard conventie)
- `CONTRIBUTING.md` (GitHub conventie)
- `AGENTS.md` (AI-adapter; ontbrak eerder in deze lijst terwijl REGEL 1 het al toestond — hersteld voor interne consistentie)
- `CLAUDE.md` (AI-adapter; Claude Code-conventie)
- `CHATGPT_PROJECT_INSTRUCTIONS.md` (AI-adapter)
- `LICENSE` (GitHub conventie)

---

## ✅ REGEL 5: Links Updaten

**Gebruik relatieve links:**

```markdown
// ✅ Goed
[Quick Start](docs/getting-started/quick-start.md)
[Database Guide](docs/guides/database.md)

// ❌ Fout
[Quick Start](QUICK_START.md)  // Niet meer in root!
[[QUICK_START]]                // Wiki-style werkt niet in GitHub
```

**In README.md:**
```markdown
## 📖 Documentation

- **Getting Started**
  - [Quick Start](docs/getting-started/quick-start.md)
  - [Installation](docs/getting-started/installation.md)
  - [Troubleshooting](docs/getting-started/troubleshooting.md)

- **Guides**
  - [Cursor Workflow](docs/guides/cursor-workflow.md)
  - [Batch System](docs/guides/batch-system.md)
  - [Database](docs/guides/database.md)
```

---

## ✅ REGEL 6: Wanneer Nieuwe Documentatie Toevoegen

**1. Bepaal de categorie:**
- Is het voor beginners? → `getting-started/`
- Is het een guide/tutorial? → `guides/`
- Is het technisch/architectuur? → `technical/`
- Is het een session log? → `sessions/`

**2. Kies de juiste naam:**
- Gebruik lowercase-with-dashes.md
- Beschrijvend maar kort
- Max 3-4 woorden

**3. Gebruik de template:**
- Kopieer de header template (Regel 3)
- Vul metadata in
- Link naar gerelateerde docs

**4. Update README.md:**
- Voeg link toe in juiste sectie
- Zorg voor consistente formatting

**5. Commit met duidelijke message:**
```bash
git add docs/[category]/[filename].md
git commit -m "docs: add [onderwerp] documentation"
```

---

## ✅ REGEL 7: VOOR JE EEN NIEUW .MD BESTAND MAAKT

**Checklist:**

- [ ] Is er al een bestaand document waar dit bij hoort?
- [ ] Kan dit informatie toegevoegd worden aan een bestaand document?
- [ ] Is dit echt nodig als apart document?
- [ ] Heb ik de juiste categorie gekozen?
- [ ] Gebruikt de bestandsnaam het juiste format?
- [ ] Heb ik de template header gebruikt?
- [ ] Moet README.md geüpdatet worden?

**Als er twijfel is:** Vraag eerst, voeg later toe!

---

## ⚠️ Wat Te Doen Bij Wildgroei

Als je merkt dat er te veel bestanden in één folder komen:

**1. Stop en analyseer:**
- Zijn er subcategorieën mogelijk?
- Kunnen documenten samengevoegd worden?
- Zijn er verouderde documenten die naar archive/ kunnen?

**2. Bespreek met team:**
- Voordat je grote wijzigingen maakt
- Update deze guidelines indien nodig

**3. Maak een plan:**
- Documenteer de reorganisatie
- Update alle links tegelijk
- Test dat alles nog werkt

---

## 🔄 Periodic Maintenance

**Elk kwartaal:**
- [ ] Review alle documenten
- [ ] Archiveer verouderde docs
- [ ] Update outdated informatie
- [ ] Check of links nog werken
- [ ] Merge overlappende documenten

**Bij elke release:**
- [ ] Update CHANGELOG.md
- [ ] Update README.md indien nodig
- [ ] Check technische docs voor accuracy

---

## 📞 Vragen?

**Voor grote documentatie wijzigingen:**
1. Maak een TODO item in `todo/`
2. Bespreek met team
3. Update deze guidelines indien nodig

**Bij twijfel over categorie:**
- Getting started = "Hoe start ik?"
- Guides = "Hoe gebruik

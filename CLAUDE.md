@docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md

# CLAUDE.md

Dit bestand is een Claude Code-adapter op de canonieke projectstandaard hierboven (import-regel). Lees daarna ook `AGENTS.md` — dat bevat de operationele werkinstructies (leesvolgorde, documenthiërarchie, niet-onderhandelbare beslisregels, projectcommando's) die voor elke agent gelden, inclusief Claude.

## Conflictregel

Bij tegenspraak tussen dit bestand en `docs/engineering/PRODUCTION_ENGINEERING_STANDARD.md` is de canonieke standaard leidend. Dit bestand definieert geen eigen afwijkende regels — het is uitsluitend een Claude-specifieke adapter.

## Claude-specifiek: omgeving

- De primaire ontwikkelomgeving is **Windows/PowerShell** (`dev.ps1`, `.venv\Scripts\python.exe`, zie `.clinerules`).
- In een remote Linux-sessie (zoals deze) zijn de `.ps1`-scripts niet bruikbaar. Gebruik dan directe commando's (bijv. `uvicorn main:app --reload`, `npm run dev` / `npm run build`) en zet zelf een Python-venv op (`python -m venv .venv && .venv/bin/pip install -r backend/requirements.txt`) in plaats van het Windows-pad te simuleren.
- Wijzig nooit `backend/database.db` of de seed/reset/migrate-scripts (`seed_database.py`, `reset_database.py`, `migrate_*.py`) zonder expliciete opdracht van de gebruiker — dit zijn acties met risico op verlies van (test)data.

## Rapportage

Vul bij sessie-einde of overdracht `docs/engineering/AI_SESSION_HANDOFF.md` in (zie dat bestand voor secties en waar het ingevulde exemplaar hoort).

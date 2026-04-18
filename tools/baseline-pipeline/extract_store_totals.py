"""extract_store_totals.py — Schrijf store_totals.tsv voor een specifieke week.

Draait volledig lokaal; er wordt geen data gedeeld met een externe service of LLM.

Gebruik:
    python extract_store_totals.py --year 2026 --week 16
    python extract_store_totals.py          # interactieve prompts

Het script:
  1. Zoekt Print_nummers.xlsx in de weekmap en scant het werkblad automatisch
     op filiaalcodes + totaalwaarden (ongeacht de exacte cellocatie).
  2. Schrijft het resultaat als store_totals.tsv naar dezelfde weekmap.
  3. Als er al een store_totals.* aanwezig is, wordt een waarschuwing getoond
     en vraagt het script om bevestiging voor overschrijving.

Toekomstige uitbreiding (PDF-bron):
  - Vervang of vul _load_from_source() aan met pdfplumber-logica die de
    benodigde stuks-kolom uit de bronpagina extraheert. Voeg de bronpdf-pad
    toe als argument. De financiële PDF wordt nooit buiten dit script gedeeld.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SOURCE_ROOT = Path(r"Z:\Herverdeellijsten")


def _week_dir(year: int, week: int) -> Path:
    return SOURCE_ROOT / f"Jaar {year}" / f"Week {week}"


def _load_from_print_nummers(week_dir: Path) -> dict[str, int]:
    """Laad store_totals via de automatische cel-scan in week_sources.py."""
    # Voeg de projectroot toe aan het pad zodat week_sources importeerbaar is
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from week_sources import _scan_store_totals_from_workbook, PRINT_NUMMERS_WORKBOOK

    wb_path = week_dir / PRINT_NUMMERS_WORKBOOK
    if not wb_path.exists():
        print(f"[FOUT] Print_nummers.xlsx niet gevonden: {wb_path}")
        return {}

    totals = _scan_store_totals_from_workbook(wb_path)
    if not totals:
        print(f"[WAARSCHUWING] Geen filiaalcodes gevonden in {wb_path}")
    return totals


def _write_store_totals(week_dir: Path, totals: dict[str, int]) -> Path:
    from pipeline_config import ACTIVE_STORES

    out_path = week_dir / "store_totals.tsv"

    # Schrijf in volgorde van filiaalcode
    lines = ["filiaalcode\ttotaal"]
    for code in sorted(totals, key=lambda c: int(c)):
        name = ACTIVE_STORES.get(code, code)
        lines.append(f"{code}\t{totals[code]}\t# {name}")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Schrijf store_totals.tsv voor een week")
    parser.add_argument("--year", type=int)
    parser.add_argument("--week", type=int)
    parser.add_argument("--force", action="store_true", help="Overschrijf bestaande store_totals zonder te vragen")
    args = parser.parse_args()

    year = args.year or int(input("Jaar [2026]: ").strip() or "2026")
    week = args.week or int(input("Weeknummer: ").strip())

    week_dir = _week_dir(year, week)
    if not week_dir.exists():
        print(f"[FOUT] Weekmap niet gevonden: {week_dir}")
        sys.exit(1)

    # Waarschuwen als er al een store_totals bestand is
    existing = [f for f in week_dir.iterdir() if f.stem == "store_totals"]
    if existing and not args.force:
        print(f"[WAARSCHUWING] Bestaand bestand gevonden: {existing[0]}")
        antwoord = input("Overschrijven? [j/N]: ").strip().lower()
        if antwoord not in ("j", "ja", "y", "yes"):
            print("Afgebroken.")
            sys.exit(0)

    print(f"Scanning {week_dir / 'Print_nummers.xlsx'} ...")
    totals = _load_from_print_nummers(week_dir)

    if not totals:
        print("[FOUT] Geen store_totals gevonden. Controleer Print_nummers.xlsx.")
        sys.exit(1)

    out_path = _write_store_totals(week_dir, totals)
    print(f"\nStore totals geschreven naar: {out_path}")
    print(f"{'Filiaal':>12}  {'Totaal':>7}")
    print("-" * 22)
    from pipeline_config import ACTIVE_STORES
    for code in sorted(totals, key=lambda c: int(c)):
        name = ACTIVE_STORES.get(code, code)
        print(f"{name:>12}  {totals[code]:>7}")


if __name__ == "__main__":
    main()

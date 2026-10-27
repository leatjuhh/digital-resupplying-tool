"""Week-inventarisatie van manuele herverdeeldata.

Scant Z:\\Herverdeellijsten en schrijft één CSV-regel per week naar
backend/algorithm_data/inventory/week_inventory.csv.

Modi
----
--fast (standaard)
    Bestandscontroles en Excel/PDF-kruischeck; snel genoeg voor alle jaren.
--full
    Bovenstaand + PDF-parsing, ongeldige filiaalcodes en donorvoorraad-check.
    Kan bij veel weken meerdere minuten duren.

Wisselweken (zie "Domeinkennis Manuele Herverdeling" in current-state.md)
-------------------------------------------------------------------------
--bv-merge-year / --bv-merge-week   Eerste week na BV-samenvoeging.
--kriskras-year / --kriskras-week   Eerste week met kriskrasverdeling.
Als niet opgegeven: period="unknown" voor alle weken.

Gebruik
-------
    cd tools\\baseline-pipeline
    ..\\..\\backend\\venv\\Scripts\\python.exe inventory_weeks.py
    ..\\..\\backend\\venv\\Scripts\\python.exe inventory_weeks.py --full
    ..\\..\\backend\\venv\\Scripts\\python.exe inventory_weeks.py --year 2026 --week 12
    ..\\..\\backend\\venv\\Scripts\\python.exe inventory_weeks.py --bv-merge-year 2024 --bv-merge-week 1

Uitvoer
-------
CSV met één regel per gevonden weekmap.  Kolommen: zie WeekRecord hieronder.
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Voeg tools/ en backend/ toe aan sys.path zodat pipeline-modules en pdf_extract
# importeerbaar zijn, ongeacht vanuit welke cwd het script wordt gestart.
_TOOLS_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _TOOLS_DIR.parents[1] / "backend"
for _p in (_TOOLS_DIR, _BACKEND_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from openpyxl import load_workbook  # noqa: E402  (na sys.path-setup)

from pipeline_config import ACTIVE_STORES, EXCLUDED_STORES  # noqa: E402

# ──────────────────────────────────────────────────────────────────
# Constanten
# ──────────────────────────────────────────────────────────────────

DEFAULT_SOURCE_ROOT = Path(r"Z:\Herverdeellijsten")
DEFAULT_OUTPUT = (
    _TOOLS_DIR.parents[1]
    / "backend"
    / "algorithm_data"
    / "inventory"
    / "week_inventory.csv"
)

# Naam van bekende PDF-submappen (case-insensitief vergeleken).
# Volgorde is prioriteit: eerste match wint.
_PDF_DIR_NAMES_PRIORITY = [
    "interfiliaallijsten",
    "print pdf",
    "pdf_print",
    "print_pdf",
    "pdf print",
    "digiherver",
    "digi herver",
    "pdf",
    "pdf_originelen",
    "digiherverdocu",
    "pdf herverderlen naar manuel",
]

# Excel-bestandsnamen om naar te zoeken, in volgorde van voorkeur.
_EXCEL_CANDIDATES = [
    "Ingevoerd.xlsx",
    "Ingevoerd - bewerkt.xlsx",
    "Ingevoerde nrs.xlsx",
    "Ingevoerde nummers.xlsx",
    "Ingevoerde.xlsx",
    "Ingevoerd - kopie.xlsx",
    "Ingevoerd - kopie - bewerkt.xlsx",
    "Ingevoerd v2.xlsx",
    "Ingevoerd nieuwste.xlsx",
    "Ingevoerd klaar.xlsx",
    "Ingevoerd DEZE GEBRUIKEN.xlsx",
    "Totaal ingevoerd.xlsx",
]

_ACTIVE_STORE_CODES: frozenset[str] = frozenset(ACTIVE_STORES.keys())
_EXCLUDED_STORE_CODES: frozenset[str] = frozenset(EXCLUDED_STORES)
_ALL_KNOWN_CODES: frozenset[str] = _ACTIVE_STORE_CODES | _EXCLUDED_STORE_CODES

# CSV-kolomvolgorde (exact de veldnamen van WeekRecord)
_CSV_COLUMNS = [
    "year",
    "week",
    "week_dir_name",
    "excel_found",
    "excel_filename",
    "excel_article_count",
    "pdf_submap_found",
    "pdf_submap_name",
    "pdf_count",
    "loose_pdfs_at_root",
    "missing_pdfs_count",
    "extra_pdfs_count",
    "period",
    "parse_failure_count",
    "invalid_store_moves",
    "donor_violation_count",
    "non_numeric_qty_count",
    "cooldown_article_count",
    "quality_label",
    "flags",
    "notes",
]

# ──────────────────────────────────────────────────────────────────
# Data-structuur
# ──────────────────────────────────────────────────────────────────


@dataclass
class WeekRecord:
    year: int
    week: int
    week_dir_name: str
    excel_found: bool = False
    excel_filename: str = ""
    excel_article_count: int = 0
    pdf_submap_found: bool = False
    pdf_submap_name: str = ""
    pdf_count: int = 0
    loose_pdfs_at_root: int = 0
    missing_pdfs_count: int = 0
    extra_pdfs_count: int = 0
    period: str = "unknown"
    # Volledig-modus (−1 = niet gemeten)
    parse_failure_count: int = -1
    invalid_store_moves: int = -1
    donor_violation_count: int = -1
    non_numeric_qty_count: int = -1
    # Ingevuld na cross-week-pass
    cooldown_article_count: int = -1
    quality_label: str = "onbruikbaar"
    flags: str = ""
    notes: str = ""


# ──────────────────────────────────────────────────────────────────
# Hulpfuncties: mapstructuur
# ──────────────────────────────────────────────────────────────────


def _year_from_dir(name: str) -> int | None:
    """Parst "Jaar YYYY" → YYYY; None als het formaat niet klopt."""
    parts = name.strip().split()
    if len(parts) == 2 and parts[0].lower() == "jaar" and parts[1].isdigit():
        return int(parts[1])
    return None


def _week_from_dir(name: str) -> int | None:
    """Parst "Week N" (hoofd-/kleine letters, extra tokens ok) → N; None anders."""
    parts = name.strip().split()
    if len(parts) >= 2 and parts[0].lower() == "week" and parts[1].isdigit():
        return int(parts[1])
    return None


def _find_excel(week_dir: Path) -> Path | None:
    """Zoekt de beste Ingevoerd-Excel in de weekmap.

    Geeft voorkeur aan de standaardnaam. Valt terug op een case-insensitieve
    scan voor overige "Ingevoerd*"-bestanden. Slaat Excel lock-bestanden (~$) over.
    """
    for name in _EXCEL_CANDIDATES:
        candidate = week_dir / name
        if candidate.exists():
            return candidate
    # Case-insensitieve fallback (werkt ook op Windows)
    try:
        for f in week_dir.iterdir():
            if (
                f.suffix.lower() == ".xlsx"
                and "ingevoerd" in f.name.lower()
                and not f.name.startswith("~$")
            ):
                return f
    except PermissionError:
        pass
    return None


def _resolve_pdf_dir_extended(week_dir: Path) -> tuple[Path | None, str]:
    """Zoekt de PDF-submap met case-insensitieve matching op alle bekende namen.

    Retourneert (pad, naam_zoals_gevonden) of (None, "") als niet gevonden.
    De volgorde in _PDF_DIR_NAMES_PRIORITY is bepalend: de eerste match wint.
    """
    try:
        subdirs = {d.name.lower(): d for d in week_dir.iterdir() if d.is_dir()}
    except PermissionError:
        return None, ""
    for candidate in _PDF_DIR_NAMES_PRIORITY:
        if candidate in subdirs:
            d = subdirs[candidate]
            return d, d.name
    return None, ""


def _count_loose_pdfs(week_dir: Path) -> int:
    """Telt *.pdf-bestanden direct in de weekmap (niet in submappen)."""
    try:
        return sum(
            1
            for f in week_dir.iterdir()
            if f.is_file() and f.suffix.lower() == ".pdf"
        )
    except PermissionError:
        return 0


def _count_pdfs_in_dir(pdf_dir: Path) -> int:
    """Telt alle *.pdf-bestanden in pdf_dir (recursief)."""
    return sum(1 for _ in pdf_dir.rglob("*.pdf"))


# ──────────────────────────────────────────────────────────────────
# Hulpfuncties: Excel
# ──────────────────────────────────────────────────────────────────


def _excel_article_ids(excel_path: Path) -> list[str]:
    """Leest unieke artikelnummers uit kolom A van het eerste tabblad."""
    wb = load_workbook(excel_path, data_only=True, read_only=True)
    try:
        ws = wb[wb.sheetnames[0]]
        seen: set[str] = set()
        for row in ws.iter_rows(min_row=2, min_col=1, max_col=1, values_only=True):
            val = row[0]
            if val is None:
                continue
            art_id = str(val).strip()
            if art_id:
                seen.add(art_id)
        return sorted(seen)
    finally:
        wb.close()


def _pdf_article_ids(pdf_dir: Path) -> list[str]:
    """Geeft de stammen (bestandsnaam zonder extensie) van alle PDF's in pdf_dir."""
    return sorted({p.stem for p in pdf_dir.rglob("*.pdf")})


def _crosscheck(
    excel_path: Path, pdf_dir: Path
) -> tuple[list[str], list[str]]:
    """Retourneert (excel_zonder_pdf, pdf_zonder_excel)."""
    excel_ids = set(_excel_article_ids(excel_path))
    pdf_ids = set(_pdf_article_ids(pdf_dir))
    missing = sorted(excel_ids - pdf_ids)
    extra = sorted(pdf_ids - excel_ids)
    return missing, extra


# ──────────────────────────────────────────────────────────────────
# Hulpfuncties: periode
# ──────────────────────────────────────────────────────────────────


def _label_period(
    year: int,
    week: int,
    bv_merge: tuple[int, int] | None,
    kriskras: tuple[int, int] | None,
) -> str:
    """Geeft de periode-label op basis van de wisselweken."""
    yw = (year, week)
    if kriskras and yw >= kriskras:
        return "na_kriskras"
    if bv_merge and yw >= bv_merge:
        return "na_bv_samenvoeging"
    if bv_merge and yw < bv_merge:
        return "voor_bv_samenvoeging"
    return "unknown"


# ──────────────────────────────────────────────────────────────────
# Hulpfuncties: kwaliteitsoordeel
# ──────────────────────────────────────────────────────────────────


def _compute_quality(rec: WeekRecord) -> tuple[str, list[str]]:
    """Berekent quality_label en flags op basis van de velden van rec.

    Regels
    ------
    compleet  : Excel + PDF-submap aanwezig, 0 missing PDFs,
                parse_failures == 0 (indien gemeten), donor_violations == 0 (indien gemeten).
    bruikbaar : Excel of PDF-submap heeft kleine problemen maar is bruikbaar.
    onbruikbaar: Geen Excel, of geen PDF's (submap én los), of veel missing PDFs.
    """
    flags: list[str] = []

    if not rec.excel_found:
        flags.append("excel_missing")
    if not rec.pdf_submap_found and rec.loose_pdfs_at_root == 0:
        flags.append("pdf_missing")
    elif not rec.pdf_submap_found and rec.loose_pdfs_at_root > 0:
        flags.append("loose_pdfs_only")

    if rec.excel_found and rec.excel_filename:
        n = rec.excel_filename.lower()
        if "bewerkt" in n or "kopie" in n:
            flags.append("only_bewerkt_excel")

    if rec.missing_pdfs_count > 0:
        ratio = rec.missing_pdfs_count / max(rec.excel_article_count, 1)
        flags.append("many_missing_pdfs" if ratio >= 0.3 else "some_missing_pdfs")

    if rec.extra_pdfs_count > 0:
        flags.append("extra_pdfs")

    if rec.parse_failure_count > 0:
        flags.append("parse_failures")
    if rec.donor_violation_count > 0:
        flags.append("donor_violations")
    if rec.invalid_store_moves > 0:
        flags.append("invalid_stores")
    if rec.non_numeric_qty_count > 0:
        flags.append("non_numeric_qty")

    # Kwaliteitslabel
    hard_broken = "excel_missing" in flags and "pdf_missing" in flags
    if hard_broken:
        return "onbruikbaar", flags

    blocking = {"excel_missing", "pdf_missing", "many_missing_pdfs"}
    if blocking & set(flags):
        return "bruikbaar", flags

    soft_issues = {
        "some_missing_pdfs",
        "parse_failures",
        "donor_violations",
        "invalid_stores",
        "non_numeric_qty",
        "only_bewerkt_excel",
        "loose_pdfs_only",
    }
    if soft_issues & set(flags):
        return "bruikbaar", flags

    return "compleet", flags


# ──────────────────────────────────────────────────────────────────
# Fast-modus scan (bestandscontroles + kruischeck)
# ──────────────────────────────────────────────────────────────────


def scan_week_fast(
    week_dir: Path,
    year: int,
    week: int,
    bv_merge: tuple[int, int] | None,
    kriskras: tuple[int, int] | None,
) -> WeekRecord:
    """Scant één week in fast-modus: alleen bestandscontroles."""
    rec = WeekRecord(year=year, week=week, week_dir_name=week_dir.name)
    notes: list[str] = []

    # ── Excel ──────────────────────────────────────────────────────
    excel_path = _find_excel(week_dir)
    if excel_path:
        rec.excel_found = True
        rec.excel_filename = excel_path.name
        try:
            ids = _excel_article_ids(excel_path)
            rec.excel_article_count = len(ids)
        except Exception as exc:  # noqa: BLE001
            notes.append(f"excel_leesfout:{exc!r}")
    else:
        # Meld als er wél xlsx-bestanden zijn (maar geen Ingevoerd-variant)
        try:
            other = [
                f.name
                for f in week_dir.iterdir()
                if f.suffix.lower() == ".xlsx" and not f.name.startswith("~$")
            ]
        except PermissionError:
            other = []
        if other:
            notes.append(f"geen_ingevoerd_maar_xlsx:{','.join(other[:5])}")

    # ── PDF-submap ─────────────────────────────────────────────────
    pdf_dir, pdf_dir_name = _resolve_pdf_dir_extended(week_dir)
    if pdf_dir:
        rec.pdf_submap_found = True
        rec.pdf_submap_name = pdf_dir_name
        rec.pdf_count = _count_pdfs_in_dir(pdf_dir)
    else:
        # Rapporteer submappen die we niet herkennen als PDF-map
        try:
            unknown = [
                d.name
                for d in week_dir.iterdir()
                if d.is_dir() and d.name.lower() not in _PDF_DIR_NAMES_PRIORITY
                and d.name.lower() not in {"winkels", "logs", "winkels new", "winkels new 2",
                                            "voor winkels", "nieuwe map", "ingevoerd",
                                            "winkels outlet", "relevante_rapportages",
                                            "extra retour winter basics", "extra rt opdracht"}
            ]
        except PermissionError:
            unknown = []
        if unknown:
            notes.append(f"onbekende_submappen:{','.join(unknown[:5])}")

    rec.loose_pdfs_at_root = _count_loose_pdfs(week_dir)

    # ── Kruischeck Excel ↔ PDF ─────────────────────────────────────
    if rec.excel_found and rec.pdf_submap_found and excel_path is not None:
        try:
            missing, extra = _crosscheck(excel_path, pdf_dir)  # type: ignore[arg-type]
            rec.missing_pdfs_count = len(missing)
            rec.extra_pdfs_count = len(extra)
        except Exception as exc:  # noqa: BLE001
            notes.append(f"kruischeck_fout:{exc!r}")

    # ── Periode ───────────────────────────────────────────────────
    rec.period = _label_period(year, week, bv_merge, kriskras)

    # ── Kwaliteitsoordeel ─────────────────────────────────────────
    label, flags = _compute_quality(rec)
    rec.quality_label = label
    rec.flags = ",".join(flags)
    rec.notes = "; ".join(notes)
    return rec


# ──────────────────────────────────────────────────────────────────
# Full-modus uitbreiding (PDF-parsing + donorcheck)
# ──────────────────────────────────────────────────────────────────


def _enrich_with_full_scan(rec: WeekRecord, week_dir: Path) -> None:
    """Vult parse_failure_count, donor_violation_count etc. in via PDF-parsing.

    Mutaties worden in-place in rec aangebracht.
    Roept week_pipeline.load_moves_from_excel en parse_pdf_snapshot aan.
    """
    from week_pipeline import load_moves_from_excel, parse_pdf_snapshot  # noqa: PLC0415

    if not rec.excel_found or not rec.pdf_submap_found:
        return

    excel_path = _find_excel(week_dir)
    pdf_dir, _ = _resolve_pdf_dir_extended(week_dir)
    if excel_path is None or pdf_dir is None:
        return

    # Capture stdout om niet-numerieke waarschuwingen te tellen
    captured = io.StringIO()
    orig_stdout = sys.stdout
    sys.stdout = captured
    try:
        try:
            moves, article_ids = load_moves_from_excel(excel_path)
        except Exception:  # noqa: BLE001
            return
    finally:
        sys.stdout = orig_stdout

    warning_lines = captured.getvalue().splitlines()
    rec.non_numeric_qty_count = sum(
        1 for line in warning_lines if "WAARSCHUWING" in line
    )

    # Bouw PDF-lookup
    pdf_by_article: dict[str, Path] = {
        p.stem: p for p in pdf_dir.rglob("*.pdf")
    }

    parse_failures = 0
    donor_violations = 0
    invalid_store_moves = 0

    moves_by_article: dict[str, list[dict[str, Any]]] = {}
    for move in moves:
        moves_by_article.setdefault(move["article_id"], []).append(move)

    for article_id in article_ids:
        pdf_path = pdf_by_article.get(article_id)
        if pdf_path is None:
            continue
        try:
            snapshot = parse_pdf_snapshot(pdf_path, store_totals={})
        except Exception:  # noqa: BLE001
            parse_failures += 1
            continue

        if snapshot.get("errors"):
            parse_failures += 1

        stock_by_store_size: dict[str, dict[str, int]] = {
            store: {
                k: int(v)
                for k, v in store_data.items()
                if k not in {"sold", "store_name", "store_size_class",
                              "store_sales_rank", "store_total_stock_week"}
            }
            for store, store_data in snapshot.get("stores", {}).items()
        }

        for move in moves_by_article.get(article_id, []):
            from_store = str(move["from_store"]).strip()
            to_store = str(move["to_store"]).strip()

            # Ongeldige filiaalcodes
            if from_store not in _ALL_KNOWN_CODES or to_store not in _ALL_KNOWN_CODES:
                invalid_store_moves += 1

            # Donorvoorraad-check
            donor = stock_by_store_size.get(from_store, {})
            size = str(move["size"]).upper()
            donor_stock = donor.get(size, 0)
            qty = int(move.get("qty", 0))
            if donor_stock < qty:
                donor_violations += 1

    rec.parse_failure_count = parse_failures
    rec.donor_violation_count = donor_violations
    rec.invalid_store_moves = invalid_store_moves

    # Herbereken kwaliteitsoordeel na full-scan
    label, flags = _compute_quality(rec)
    rec.quality_label = label
    rec.flags = ",".join(flags)


# ──────────────────────────────────────────────────────────────────
# Cooldown-berekening (cross-week)
# ──────────────────────────────────────────────────────────────────


def _compute_cooldown(records: list[WeekRecord], week_dir_by_key: dict[tuple[int, int], Path]) -> None:
    """Vult cooldown_article_count in voor elke week.

    Telt voor week N het aantal artikelnummers dat ook in week N−1 voorkwam.
    "Week N−1" is de direct voorgaande week op kalenderweek (zelfde jaar) of
    week 52/53 van het vorige jaar.  Als week N−1 niet in de data zit: 0.
    Werkt alleen als de Excel leesbaar was; anders blijft het −1.
    """
    # Bouw {(year, week): set(article_ids)}
    articles_by_week: dict[tuple[int, int], set[str]] = {}
    for rec in records:
        if not rec.excel_found:
            continue
        week_dir = week_dir_by_key.get((rec.year, rec.week))
        if week_dir is None:
            continue
        excel_path = _find_excel(week_dir)
        if excel_path is None:
            continue
        try:
            ids = _excel_article_ids(excel_path)
            articles_by_week[(rec.year, rec.week)] = set(ids)
        except Exception:  # noqa: BLE001
            pass

    for rec in records:
        key = (rec.year, rec.week)
        current = articles_by_week.get(key)
        if current is None:
            continue

        # Vorige kalenderweek (week 1 → week 52 van vorig jaar)
        if rec.week > 1:
            prev_key = (rec.year, rec.week - 1)
        else:
            prev_key = (rec.year - 1, 52)

        prev = articles_by_week.get(prev_key, set())
        rec.cooldown_article_count = len(current & prev)


# ──────────────────────────────────────────────────────────────────
# Hoofd-scan
# ──────────────────────────────────────────────────────────────────


def _iter_week_dirs(
    source_root: Path,
    year_filter: int | None,
    week_filter: int | None,
) -> list[tuple[int, int, Path]]:
    """Retourneert gesorteerde lijst van (year, week, week_dir)-tuples."""
    result: list[tuple[int, int, Path]] = []
    jaar_mappen = sorted(source_root.iterdir(), key=lambda d: d.name)
    for jaar_map in jaar_mappen:
        if not jaar_map.is_dir():
            continue
        year = _year_from_dir(jaar_map.name)
        if year is None:
            continue
        if year_filter is not None and year != year_filter:
            continue
        week_mappen = sorted(jaar_map.iterdir(), key=lambda d: d.name)
        for week_map in week_mappen:
            if not week_map.is_dir():
                continue
            week = _week_from_dir(week_map.name)
            if week is None:
                continue
            if week_filter is not None and week != week_filter:
                continue
            result.append((year, week, week_map))
    return result


def run_scan(
    source_root: Path,
    output_path: Path,
    full_mode: bool,
    bv_merge: tuple[int, int] | None,
    kriskras: tuple[int, int] | None,
    year_filter: int | None,
    week_filter: int | None,
    verbose: bool,
) -> list[WeekRecord]:
    """Hoofd-scanfunctie.  Schrijft CSV en retourneert de records."""
    week_dirs = _iter_week_dirs(source_root, year_filter, week_filter)
    if not week_dirs:
        print(f"Geen weekmappen gevonden in {source_root}", file=sys.stderr)
        return []

    records: list[WeekRecord] = []
    week_dir_by_key: dict[tuple[int, int], Path] = {}

    total = len(week_dirs)
    for i, (year, week, week_dir) in enumerate(week_dirs, start=1):
        if verbose:
            print(f"[{i}/{total}] {year} week {week} … ", end="", flush=True)
        rec = scan_week_fast(week_dir, year, week, bv_merge, kriskras)
        if full_mode:
            _enrich_with_full_scan(rec, week_dir)
        records.append(rec)
        week_dir_by_key[(year, week)] = week_dir
        if verbose:
            print(rec.quality_label)

    print(f"\nCooldown berekenen voor {len(records)} weken … ", end="", flush=True)
    _compute_cooldown(records, week_dir_by_key)
    print("klaar.")

    # Herbereken kwaliteitsoordeel na cooldown (cooldown_article_count is nu ingevuld)
    # Cooldown is een meting, geen hard blokkerende vlag, dus label verandert niet.

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_COLUMNS)
        writer.writeheader()
        for rec in records:
            row = asdict(rec)
            writer.writerow({k: row[k] for k in _CSV_COLUMNS})

    print(f"CSV geschreven naar: {output_path}")
    return records


# ──────────────────────────────────────────────────────────────────
# Samenvatting
# ──────────────────────────────────────────────────────────────────


def print_summary(records: list[WeekRecord]) -> None:
    """Rapporteert aantallen per label en bijzondere weken."""
    from collections import Counter

    label_counts = Counter(r.quality_label for r in records)
    print("\n=== Samenvatting ===")
    print(f"Totaal weken gescand : {len(records)}")
    print(f"  compleet           : {label_counts['compleet']}")
    print(f"  bruikbaar          : {label_counts['bruikbaar']}")
    print(f"  onbruikbaar        : {label_counts['onbruikbaar']}")

    print("\n── PDF-submap varianten ──")
    submap_counts = Counter(r.pdf_submap_name for r in records if r.pdf_submap_found)
    for name, cnt in submap_counts.most_common():
        print(f"  {cnt:3}x  {name!r}")
    no_submap = sum(1 for r in records if not r.pdf_submap_found)
    print(f"  {no_submap:3}x  (geen submap; {sum(1 for r in records if not r.pdf_submap_found and r.loose_pdfs_at_root > 0)}x met losse PDFs)")

    print("\n── Periodes ──")
    period_counts = Counter(r.period for r in records)
    for period, cnt in period_counts.most_common():
        print(f"  {cnt:3}x  {period}")

    flagged = [r for r in records if r.flags]
    if flagged:
        print(f"\n── Weken met kwaliteitsvlag ({len(flagged)}) ──")
        for rec in flagged:
            print(f"  {rec.year} week {rec.week:2}: {rec.flags}")
            if rec.notes:
                print(f"             notes: {rec.notes}")

    cooldown_total = sum(r.cooldown_article_count for r in records if r.cooldown_article_count > 0)
    weeks_with_cooldown = sum(1 for r in records if r.cooldown_article_count > 0)
    print("\n── Cooldown ──")
    print(f"  Weken met ≥1 herhaald artikel: {weeks_with_cooldown}")
    print(f"  Totaal herhaalde artikel-week combinaties: {cooldown_total}")


# ──────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--fast", action="store_true", default=True,
                      help="Alleen bestandscontroles (standaard).")
    mode.add_argument("--full", action="store_true", default=False,
                      help="Inclusief PDF-parsing en donorvoorraad-check (traag).")
    p.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT,
                   help="Root van Z:\\Herverdeellijsten.")
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                   help="Pad voor de uitvoer-CSV.")
    p.add_argument("--year", type=int, default=None,
                   help="Scan alleen dit jaar.")
    p.add_argument("--week", type=int, default=None,
                   help="Samen met --year: scan alleen deze week.")
    p.add_argument("--bv-merge-year", type=int, default=None)
    p.add_argument("--bv-merge-week", type=int, default=None)
    p.add_argument("--kriskras-year", type=int, default=None)
    p.add_argument("--kriskras-week", type=int, default=None)
    p.add_argument("--quiet", action="store_true",
                   help="Geen per-week voortgang.")
    return p


def main() -> None:
    args = _build_parser().parse_args()

    bv_merge: tuple[int, int] | None = None
    if args.bv_merge_year is not None and args.bv_merge_week is not None:
        bv_merge = (args.bv_merge_year, args.bv_merge_week)
    elif (args.bv_merge_year is None) != (args.bv_merge_week is None):
        _build_parser().error("Geef zowel --bv-merge-year als --bv-merge-week op.")

    kriskras: tuple[int, int] | None = None
    if args.kriskras_year is not None and args.kriskras_week is not None:
        kriskras = (args.kriskras_year, args.kriskras_week)
    elif (args.kriskras_year is None) != (args.kriskras_week is None):
        _build_parser().error("Geef zowel --kriskras-year als --kriskras-week op.")

    if args.week is not None and args.year is None:
        _build_parser().error("--week vereist ook --year.")

    full_mode = args.full

    records = run_scan(
        source_root=args.source_root,
        output_path=args.output,
        full_mode=full_mode,
        bv_merge=bv_merge,
        kriskras=kriskras,
        year_filter=args.year,
        week_filter=args.week,
        verbose=not args.quiet,
    )
    print_summary(records)


if __name__ == "__main__":
    main()

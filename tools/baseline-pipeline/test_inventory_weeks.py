"""Unit-tests voor inventory_weeks.py.

Werkt uitsluitend met kunstmatige weekmappen via pytest's tmp_path-fixture.
Geen echte data uit Z: of het algoritme wordt aangeraakt.
"""
from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

import inventory_weeks as iw


# ──────────────────────────────────────────────────────────────────
# Hulpfuncties om testmappen aan te maken
# ──────────────────────────────────────────────────────────────────


def _make_excel(path: Path, article_ids: list[str | int]) -> None:
    """Schrijft een minimaal Ingevoerd.xlsx met artikelnummers in kolom A."""
    wb = Workbook()
    ws = wb.active
    ws.append(["Artikelnummer", "Van", "Naar", "S", "M", "L"])
    for art in article_ids:
        ws.append([art, "6", "8", 1, 0, 0])
    wb.save(path)


def _make_pdf(path: Path) -> None:
    """Maakt een leeg placeholder-bestand aan met .pdf-extensie."""
    path.write_bytes(b"%PDF-1.4 placeholder")


def _make_week(
    root: Path,
    year: int,
    week: int,
    *,
    excel_name: str | None = "Ingevoerd.xlsx",
    article_ids: list[str] | None = None,
    pdf_submap: str | None = "print pdf",
    pdf_ids: list[str] | None = None,
    loose_pdfs: int = 0,
) -> Path:
    """Bouwt een kunstmatige weekmap en retourneert het pad ervan."""
    week_dir = root / f"Jaar {year}" / f"Week {week}"
    week_dir.mkdir(parents=True, exist_ok=True)

    if excel_name and article_ids is not None:
        _make_excel(week_dir / excel_name, article_ids)

    if pdf_submap and pdf_ids is not None:
        pdf_dir = week_dir / pdf_submap
        pdf_dir.mkdir(exist_ok=True)
        for pid in pdf_ids:
            _make_pdf(pdf_dir / f"{pid}.pdf")

    for i in range(loose_pdfs):
        _make_pdf(week_dir / f"los_{i}.pdf")

    return week_dir


# ──────────────────────────────────────────────────────────────────
# Tests: hulpfuncties op mapstructuur
# ──────────────────────────────────────────────────────────────────


class TestYearWeekParsing:
    def test_year_valid(self) -> None:
        assert iw._year_from_dir("Jaar 2026") == 2026

    def test_year_invalid(self) -> None:
        assert iw._year_from_dir("Herverdelingsalgoritme") is None
        assert iw._year_from_dir("Jaar abc") is None

    def test_week_valid(self) -> None:
        assert iw._week_from_dir("Week 12") == 12
        assert iw._week_from_dir("week 3") == 3

    def test_week_with_suffix(self) -> None:
        # "Week 42 Fout" moet week 42 opleveren
        assert iw._week_from_dir("Week 42 Fout") == 42

    def test_week_lowercase(self) -> None:
        assert iw._week_from_dir("week 36") == 36

    def test_week_invalid(self) -> None:
        assert iw._week_from_dir("Macro") is None
        assert iw._week_from_dir("Week") is None


class TestFindExcel:
    def test_finds_standard_name(self, tmp_path: Path) -> None:
        _make_excel(tmp_path / "Ingevoerd.xlsx", ["100", "200"])
        result = iw._find_excel(tmp_path)
        assert result is not None
        assert result.name == "Ingevoerd.xlsx"

    def test_falls_back_to_bewerkt(self, tmp_path: Path) -> None:
        _make_excel(tmp_path / "Ingevoerd - bewerkt.xlsx", ["100"])
        result = iw._find_excel(tmp_path)
        assert result is not None
        assert result.name == "Ingevoerd - bewerkt.xlsx"

    def test_prefers_standard_over_bewerkt(self, tmp_path: Path) -> None:
        _make_excel(tmp_path / "Ingevoerd.xlsx", ["100"])
        _make_excel(tmp_path / "Ingevoerd - bewerkt.xlsx", ["200"])
        result = iw._find_excel(tmp_path)
        assert result is not None
        assert result.name == "Ingevoerd.xlsx"

    def test_skips_lock_files(self, tmp_path: Path) -> None:
        # Excel lock-bestand (~$...) moet worden overgeslagen
        (tmp_path / "~$Ingevoerd.xlsx").write_bytes(b"lock")
        result = iw._find_excel(tmp_path)
        assert result is None

    def test_returns_none_when_nothing(self, tmp_path: Path) -> None:
        assert iw._find_excel(tmp_path) is None


class TestResolvePdfDir:
    def test_finds_print_pdf(self, tmp_path: Path) -> None:
        (tmp_path / "print pdf").mkdir()
        pdf_dir, name = iw._resolve_pdf_dir_extended(tmp_path)
        assert pdf_dir is not None
        assert name == "print pdf"

    def test_finds_pdf_print(self, tmp_path: Path) -> None:
        (tmp_path / "pdf_print").mkdir()
        pdf_dir, name = iw._resolve_pdf_dir_extended(tmp_path)
        assert pdf_dir is not None
        assert name == "pdf_print"

    def test_finds_interfiliaallijsten(self, tmp_path: Path) -> None:
        (tmp_path / "Interfiliaallijsten").mkdir()
        pdf_dir, name = iw._resolve_pdf_dir_extended(tmp_path)
        assert pdf_dir is not None
        assert name == "Interfiliaallijsten"

    def test_priority_interfiliaallijsten_over_print_pdf(self, tmp_path: Path) -> None:
        # Interfiliaallijsten heeft hogere prioriteit
        (tmp_path / "Interfiliaallijsten").mkdir()
        (tmp_path / "print pdf").mkdir()
        _, name = iw._resolve_pdf_dir_extended(tmp_path)
        assert name == "Interfiliaallijsten"

    def test_returns_none_when_no_match(self, tmp_path: Path) -> None:
        (tmp_path / "Winkels").mkdir()
        pdf_dir, name = iw._resolve_pdf_dir_extended(tmp_path)
        assert pdf_dir is None
        assert name == ""

    def test_case_insensitive(self, tmp_path: Path) -> None:
        # Mapnaam "PRINT PDF" (hoofdletters) moet ook matchen
        (tmp_path / "PRINT PDF").mkdir()
        pdf_dir, name = iw._resolve_pdf_dir_extended(tmp_path)
        assert pdf_dir is not None


# ──────────────────────────────────────────────────────────────────
# Tests: periode-labeling
# ──────────────────────────────────────────────────────────────────


class TestLabelPeriod:
    def test_unknown_when_no_config(self) -> None:
        assert iw._label_period(2026, 12, None, None) == "unknown"

    def test_voor_bv_samenvoeging(self) -> None:
        result = iw._label_period(2023, 5, (2024, 1), None)
        assert result == "voor_bv_samenvoeging"

    def test_na_bv_samenvoeging(self) -> None:
        result = iw._label_period(2024, 10, (2024, 1), None)
        assert result == "na_bv_samenvoeging"

    def test_na_kriskras_overruled_bv(self) -> None:
        result = iw._label_period(2025, 20, (2024, 1), (2025, 10))
        assert result == "na_kriskras"

    def test_exact_boundary(self) -> None:
        assert iw._label_period(2024, 1, (2024, 1), None) == "na_bv_samenvoeging"
        assert iw._label_period(2023, 52, (2024, 1), None) == "voor_bv_samenvoeging"


# ──────────────────────────────────────────────────────────────────
# Tests: kwaliteitsoordeel
# ──────────────────────────────────────────────────────────────────


class TestComputeQuality:
    def _make_rec(self, **kwargs: object) -> iw.WeekRecord:
        rec = iw.WeekRecord(year=2026, week=1, week_dir_name="Week 1")
        for k, v in kwargs.items():
            setattr(rec, k, v)
        return rec

    def test_compleet(self) -> None:
        rec = self._make_rec(
            excel_found=True, excel_filename="Ingevoerd.xlsx",
            pdf_submap_found=True, pdf_submap_name="print pdf",
            missing_pdfs_count=0, extra_pdfs_count=0,
            parse_failure_count=0, donor_violation_count=0,
        )
        label, flags = iw._compute_quality(rec)
        assert label == "compleet"
        assert not flags

    def test_onbruikbaar_geen_excel_en_pdf(self) -> None:
        rec = self._make_rec(excel_found=False, pdf_submap_found=False,
                             loose_pdfs_at_root=0)
        label, flags = iw._compute_quality(rec)
        assert label == "onbruikbaar"
        assert "excel_missing" in flags
        assert "pdf_missing" in flags

    def test_bruikbaar_bij_enkele_missing_pdfs(self) -> None:
        rec = self._make_rec(
            excel_found=True, excel_filename="Ingevoerd.xlsx",
            excel_article_count=91,
            pdf_submap_found=True, pdf_submap_name="print pdf",
            missing_pdfs_count=8,  # 8/91 ≈ 9% < 30%
        )
        label, flags = iw._compute_quality(rec)
        assert label == "bruikbaar"
        assert "some_missing_pdfs" in flags

    def test_bruikbaar_bij_veel_missing_pdfs(self) -> None:
        rec = self._make_rec(
            excel_found=True, excel_filename="Ingevoerd.xlsx",
            excel_article_count=10,
            pdf_submap_found=True, pdf_submap_name="print pdf",
            missing_pdfs_count=4,  # 40% ≥ 30%
        )
        label, flags = iw._compute_quality(rec)
        assert label == "bruikbaar"
        assert "many_missing_pdfs" in flags

    def test_bewerkt_excel_geeft_bruikbaar(self) -> None:
        rec = self._make_rec(
            excel_found=True, excel_filename="Ingevoerd - bewerkt.xlsx",
            pdf_submap_found=True, pdf_submap_name="print pdf",
        )
        label, flags = iw._compute_quality(rec)
        assert label == "bruikbaar"
        assert "only_bewerkt_excel" in flags

    def test_parse_failures_geeft_bruikbaar(self) -> None:
        rec = self._make_rec(
            excel_found=True, excel_filename="Ingevoerd.xlsx",
            pdf_submap_found=True, pdf_submap_name="print pdf",
            parse_failure_count=2,
        )
        label, flags = iw._compute_quality(rec)
        assert label == "bruikbaar"
        assert "parse_failures" in flags


# ──────────────────────────────────────────────────────────────────
# Tests: scan_week_fast (integratief met nep-weekmap)
# ──────────────────────────────────────────────────────────────────


class TestScanWeekFast:
    def test_compleet_week(self, tmp_path: Path) -> None:
        arts = ["100", "200", "300"]
        week_dir = _make_week(tmp_path, 2026, 12, article_ids=arts, pdf_ids=arts)
        rec = iw.scan_week_fast(week_dir, 2026, 12, None, None)
        assert rec.excel_found
        assert rec.pdf_submap_found
        assert rec.excel_article_count == 3
        assert rec.missing_pdfs_count == 0
        assert rec.extra_pdfs_count == 0
        assert rec.quality_label == "compleet"

    def test_missing_pdfs_detected(self, tmp_path: Path) -> None:
        arts = ["100", "200", "300"]
        week_dir = _make_week(tmp_path, 2026, 13, article_ids=arts,
                              pdf_ids=["100", "200"])  # 300 ontbreekt
        rec = iw.scan_week_fast(week_dir, 2026, 13, None, None)
        assert rec.missing_pdfs_count == 1
        assert rec.quality_label == "bruikbaar"

    def test_extra_pdfs_detected(self, tmp_path: Path) -> None:
        arts = ["100"]
        week_dir = _make_week(tmp_path, 2026, 14, article_ids=arts,
                              pdf_ids=["100", "200", "300"])  # 2 extra
        rec = iw.scan_week_fast(week_dir, 2026, 14, None, None)
        assert rec.extra_pdfs_count == 2

    def test_no_excel(self, tmp_path: Path) -> None:
        week_dir = _make_week(tmp_path, 2026, 15, excel_name=None,
                              article_ids=None, pdf_ids=["100"])
        rec = iw.scan_week_fast(week_dir, 2026, 15, None, None)
        assert not rec.excel_found
        assert rec.quality_label in ("onbruikbaar", "bruikbaar")

    def test_no_pdf_submap_but_loose(self, tmp_path: Path) -> None:
        arts = ["100"]
        week_dir = _make_week(tmp_path, 2026, 16, article_ids=arts,
                              pdf_submap=None, pdf_ids=None, loose_pdfs=3)
        rec = iw.scan_week_fast(week_dir, 2026, 16, None, None)
        assert not rec.pdf_submap_found
        assert rec.loose_pdfs_at_root == 3
        assert "loose_pdfs_only" in rec.flags

    def test_period_label_applied(self, tmp_path: Path) -> None:
        arts = ["100"]
        week_dir = _make_week(tmp_path, 2025, 5, article_ids=arts, pdf_ids=arts)
        rec = iw.scan_week_fast(week_dir, 2025, 5, (2026, 1), (2026, 10))
        assert rec.period == "voor_bv_samenvoeging"

    def test_alternative_pdf_submap_variant(self, tmp_path: Path) -> None:
        # digiherver moet ook herkend worden
        arts = ["100", "200"]
        week_dir = _make_week(tmp_path, 2024, 20, article_ids=arts,
                              pdf_submap="digiherver", pdf_ids=arts)
        rec = iw.scan_week_fast(week_dir, 2024, 20, None, None)
        assert rec.pdf_submap_found
        assert rec.pdf_submap_name == "digiherver"
        assert rec.quality_label == "compleet"


# ──────────────────────────────────────────────────────────────────
# Tests: run_scan (schrijft CSV)
# ──────────────────────────────────────────────────────────────────


class TestRunScan:
    def test_csv_written(self, tmp_path: Path) -> None:
        arts = ["100", "200"]
        _make_week(tmp_path / "source", 2026, 12, article_ids=arts, pdf_ids=arts)
        output = tmp_path / "out" / "inventory.csv"
        records = iw.run_scan(
            source_root=tmp_path / "source",
            output_path=output,
            full_mode=False,
            bv_merge=None,
            kriskras=None,
            year_filter=None,
            week_filter=None,
            verbose=False,
        )
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "year" in content  # header aanwezig
        assert "2026" in content
        assert len(records) == 1

    def test_filters_by_year_and_week(self, tmp_path: Path) -> None:
        src = tmp_path / "source"
        _make_week(src, 2026, 12, article_ids=["1"], pdf_ids=["1"])
        _make_week(src, 2026, 13, article_ids=["2"], pdf_ids=["2"])
        _make_week(src, 2025, 12, article_ids=["3"], pdf_ids=["3"])
        output = tmp_path / "out.csv"
        records = iw.run_scan(
            source_root=src,
            output_path=output,
            full_mode=False,
            bv_merge=None,
            kriskras=None,
            year_filter=2026,
            week_filter=12,
            verbose=False,
        )
        assert len(records) == 1
        assert records[0].year == 2026
        assert records[0].week == 12

    def test_source_not_written(self, tmp_path: Path) -> None:
        """De bronmap mag nooit aangeraakt worden."""
        src = tmp_path / "source"
        arts = ["100"]
        week_dir = _make_week(src, 2026, 12, article_ids=arts, pdf_ids=arts)
        files_before = {f: f.stat().st_mtime for f in week_dir.rglob("*")}
        output = tmp_path / "out.csv"
        iw.run_scan(
            source_root=src,
            output_path=output,
            full_mode=False,
            bv_merge=None,
            kriskras=None,
            year_filter=None,
            week_filter=None,
            verbose=False,
        )
        files_after = {f: f.stat().st_mtime for f in week_dir.rglob("*")}
        assert files_before == files_after, "Bronbestanden zijn gewijzigd!"


# ──────────────────────────────────────────────────────────────────
# Tests: cooldown-berekening
# ──────────────────────────────────────────────────────────────────


class TestCooldown:
    def test_cooldown_detected(self, tmp_path: Path) -> None:
        src = tmp_path / "source"
        # Week 11: artikel 100
        _make_week(src, 2026, 11, article_ids=["100"], pdf_ids=["100"])
        # Week 12: artikel 100 opnieuw + 200
        _make_week(src, 2026, 12, article_ids=["100", "200"],
                   pdf_ids=["100", "200"])
        output = tmp_path / "out.csv"
        records = iw.run_scan(
            source_root=src,
            output_path=output,
            full_mode=False,
            bv_merge=None,
            kriskras=None,
            year_filter=None,
            week_filter=None,
            verbose=False,
        )
        rec_12 = next(r for r in records if r.week == 12)
        # Artikel 100 zat ook in week 11 → cooldown_article_count = 1
        assert rec_12.cooldown_article_count == 1

    def test_no_cooldown_when_different_articles(self, tmp_path: Path) -> None:
        src = tmp_path / "source"
        _make_week(src, 2026, 11, article_ids=["100"], pdf_ids=["100"])
        _make_week(src, 2026, 12, article_ids=["200"], pdf_ids=["200"])
        output = tmp_path / "out.csv"
        records = iw.run_scan(
            source_root=src,
            output_path=output,
            full_mode=False,
            bv_merge=None,
            kriskras=None,
            year_filter=None,
            week_filter=None,
            verbose=False,
        )
        rec_12 = next(r for r in records if r.week == 12)
        assert rec_12.cooldown_article_count == 0

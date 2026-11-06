"""Regressietests voor de filiaalwissel van 5 november 2026.

Dekt de acceptatiecriteria uit het migratieplan: nieuwe reguliere winkels
14/15 (Tilburg/Tegelen) en nieuwe outlets 42-45/98 worden correct behandeld,
en een eventuele herberekening van een batch van vóór de wissel gebruikt nog
de toen geldige configuratie (geen stille datacorruptie bij 14/15-hergebruik).
"""
from datetime import date

from .store_config import (
    MIGRATION_DATE,
    is_redistribution_candidate,
)
from .store_profiles import get_store_profile

PRE_MIGRATION_DATE = date(2026, 10, 1)
POST_MIGRATION_DATE = date(2026, 11, 10)


def test_regular_stores_are_redistribution_candidates_post_migration():
    for code in ["6", "8", "9", "11", "12", "13", "14", "15"]:
        assert is_redistribution_candidate(code, as_of=POST_MIGRATION_DATE), code


def test_new_outlets_and_klachten_excluded_post_migration():
    for code in ["39", "42", "43", "44", "45", "98"]:
        assert not is_redistribution_candidate(code, as_of=POST_MIGRATION_DATE), code


def test_old_outlet_codes_14_15_excluded_pre_migration():
    # Vóór de wissel waren 14/15 Outlet Weert/Sittard — niet herverdeelbaar.
    assert not is_redistribution_candidate("14", as_of=PRE_MIGRATION_DATE)
    assert not is_redistribution_candidate("15", as_of=PRE_MIGRATION_DATE)


def test_old_regular_codes_31_38_are_candidates_pre_migration():
    # Vóór de wissel waren 31/38 Tilburg/Tegelen regulier — wél herverdeelbaar.
    assert is_redistribution_candidate("31", as_of=PRE_MIGRATION_DATE)
    assert is_redistribution_candidate("38", as_of=PRE_MIGRATION_DATE)


def test_default_as_of_uses_current_set():
    # Geen as_of meegegeven -> vandaag -> na MIGRATION_DATE -> nieuwe set.
    assert date.today() >= MIGRATION_DATE
    assert is_redistribution_candidate("14")
    assert not is_redistribution_candidate("42")


def test_store_profile_14_15_post_migration():
    profile_14 = get_store_profile("14", as_of=POST_MIGRATION_DATE)
    profile_15 = get_store_profile("15", as_of=POST_MIGRATION_DATE)
    assert profile_14 is not None and profile_14.max_capacity == 400
    assert profile_15 is not None and profile_15.max_capacity == 220


def test_store_profile_31_38_pre_migration():
    profile_31 = get_store_profile("31", as_of=PRE_MIGRATION_DATE)
    profile_38 = get_store_profile("38", as_of=PRE_MIGRATION_DATE)
    assert profile_31 is not None and profile_31.max_capacity == 400
    assert profile_38 is not None and profile_38.max_capacity == 220


def test_store_profile_14_missing_pre_migration():
    # Pre-migratie bestond "14" nog niet als reguliere winkel.
    assert get_store_profile("14", as_of=PRE_MIGRATION_DATE) is None

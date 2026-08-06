"""Compenserende controle voor R5.4 (PR-006): de niet-negativiteits-
CheckConstraints op ArtikelVoorraad.

Bouwt een verse in-memory SQLite-DB via create_all (waar de constraints vanaf
tabel-aanmaak gelden) en verifieert dat negatieve voorraad/verkocht op
databaseniveau geweigerd worden en geldige rijen worden geaccepteerd.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from db_models import Base, ArtikelVoorraad


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def _row(**overrides):
    data = dict(
        batch_id=1,
        volgnummer="1",
        omschrijving="Testartikel",
        filiaal_code="6",
        filiaal_naam="Store6",
        maat="M",
        voorraad=0,
        verkocht=0,
    )
    data.update(overrides)
    return ArtikelVoorraad(**data)


def test_negative_voorraad_rejected():
    session = _session()
    session.add(_row(voorraad=-1))
    with pytest.raises(IntegrityError):
        session.commit()


def test_negative_verkocht_rejected():
    session = _session()
    session.add(_row(verkocht=-5))
    with pytest.raises(IntegrityError):
        session.commit()


def test_nonnegative_row_accepted():
    session = _session()
    session.add(_row(voorraad=3, verkocht=0))
    session.commit()  # mag niet falen
    assert session.query(ArtikelVoorraad).count() == 1

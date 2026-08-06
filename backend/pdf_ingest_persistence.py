"""Persistence-laag voor de PDF-ingest-flow (Fase 3.1, audit-bevinding PR-022).

Bevat uitsluitend het wegschrijven van geparste voorraad en gegenereerde
proposals naar de database — geen HTTP-kennis en geen domeinregels. De
domeinorkestratie staat in `pdf_ingest_service.py`, de HTTP-laag in
`routers/pdf_ingest.py`.

Deze module is een 1-op-1-extractie van gedrag dat voorheen in
`routers/pdf_ingest.py` leefde; het externe API-contract verandert niet.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from db_models import ArtikelVoorraad, PDFParseLog, Proposal

logger = logging.getLogger(__name__)


def save_parsed_records(db: Session, batch_id: int, parsed, filename: str) -> int:
    """Schrijf de geparste voorraadrijen (één record per maat) naar de database.

    Args:
        db: Database-sessie.
        batch_id: Batch-ID waaronder de records vallen.
        parsed: ParsedDoc-object uit de PDF-extractie.
        filename: Oorspronkelijke bestandsnaam (voor de logregel).

    Returns:
        Het aantal weggeschreven ArtikelVoorraad-records.
    """
    count = 0

    # Metadata
    volgnummer = parsed.meta.get("Volgnummer", "")
    omschrijving = parsed.meta.get("Omschrijving", "")

    # Sla elke rij op als losse records (één per maat)
    for row in parsed.rows:
        filiaal_code = row.get("filiaal_code", "")
        filiaal_naam = row.get("filiaal_naam", "")
        voorraad_per_maat = row.get("voorraad_per_maat", {})
        verkocht = row.get("verkocht", 0)

        # `verkocht` is een filiaaltotaal, geen maat-waarde: bewaar het alleen in
        # het EERSTE record per filiaal om dubbeltelling te voorkomen.
        first_record_for_filiaal = True

        for maat, voorraad in voorraad_per_maat.items():
            if voorraad > 0 or (verkocht > 0 and first_record_for_filiaal):
                record = ArtikelVoorraad(
                    batch_id=batch_id,
                    volgnummer=volgnummer,
                    omschrijving=omschrijving,
                    filiaal_code=filiaal_code,
                    filiaal_naam=filiaal_naam,
                    maat=maat,
                    voorraad=voorraad,
                    verkocht=verkocht if first_record_for_filiaal else 0,
                    pdf_metadata=parsed.meta,
                )
                db.add(record)
                count += 1
                first_record_for_filiaal = False

    db.commit()

    log_entry = PDFParseLog(
        batch_id=batch_id,
        phase="DATABASE_SAVE",
        level="INFO",
        message=f"Saved {count} records from {filename}",
        extra_data={
            "filename": filename,
            "volgnummer": volgnummer,
            "record_count": count,
        },
    )
    db.add(log_entry)
    db.commit()

    return count


def save_generated_proposals(
    db: Session, batch_id: int, proposal_rows: List[Dict[str, Any]]
) -> int:
    """Schrijf voorbereide proposal-dicts weg als Proposal-rijen.

    De structuur en domeinverrijking van `proposal_rows` wordt door de
    domeinlaag (`pdf_ingest_service.build_proposal_rows`) opgebouwd; deze functie
    doet uitsluitend de persistentie plus een afsluitende logregel.

    Args:
        db: Database-sessie.
        batch_id: Batch-ID waaronder de proposals vallen.
        proposal_rows: Lijst van dicts met de Proposal-kolomwaarden.

    Returns:
        Het aantal weggeschreven Proposal-rijen.
    """
    saved_count = 0
    for row in proposal_rows:
        db_proposal = Proposal(
            pdf_batch_id=batch_id,
            artikelnummer=row["artikelnummer"],
            article_name=row["article_name"],
            moves=row["moves"],
            total_moves=row["total_moves"],
            total_quantity=row["total_quantity"],
            status="pending",
            reason=row["reason"],
            applied_rules=row["applied_rules"],
            optimization_applied=row["optimization_applied"],
            stores_affected=row["stores_affected"],
        )
        db.add(db_proposal)
        saved_count += 1

    db.commit()

    log_entry = PDFParseLog(
        batch_id=batch_id,
        phase="PROPOSAL_GENERATION",
        level="INFO",
        message=f"Generated {saved_count} redistribution proposals",
        extra_data={"proposals_count": saved_count},
    )
    db.add(log_entry)
    db.commit()

    return saved_count

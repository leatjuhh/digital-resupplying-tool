"""Domeinlaag voor de PDF-ingest-flow (Fase 3.1, audit-bevinding PR-022).

Bevat de bedrijfslogica van ingest en proposal-generatie, losgekoppeld van de
HTTP-laag (`routers/pdf_ingest.py`) en de persistentielaag
(`pdf_ingest_persistence.py`). Deze module kent geen FastAPI/HTTP-details.

De functies hier zijn een gedragsbehoudende extractie van code die voorheen in
`routers/pdf_ingest.py` leefde; het externe API-contract verandert niet.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Tuple

from sqlalchemy.orm import Session

from db_models import ArtikelVoorraad, PDFBatch, PDFParseLog, Proposal
from pdf_extract import parse_pdf_to_records
from redistribution.algorithm import generate_redistribution_proposals_for_batch
from redistribution.constraints import DEFAULT_PARAMS
from algorithm_import.config import get_algorithm_assist_mode
from algorithm_import.service import enrich_moves_with_model_scores
from utils import save_upload_within_limit
from pdf_ingest_persistence import save_parsed_records, save_generated_proposals

logger = logging.getLogger(__name__)

OPTIMAL_DISTRIBUTION_RULE = "Optimal Distribution Analysis"


def is_optimal_distribution_proposal(proposal: Proposal) -> bool:
    """Markeer expliciet wanneer het algoritme geen moves nodig vond."""
    if proposal.moves:
        return False

    applied_rules = proposal.applied_rules or []
    reason = (proposal.reason or "").lower()

    return (
        OPTIMAL_DISTRIBUTION_RULE in applied_rules
        or "optimaal verdeeld" in reason
    )


def collect_store_inventory(
    voorraad_records: List[ArtikelVoorraad],
) -> Tuple[dict, List[str]]:
    """Groepeer voorraad per winkel.

    `verkocht` komt uit de PDF als totaal per filiaal, niet per maat. Daarom
    bewaren we hier expliciet `sold_total` per winkel in plaats van verkoop
    kunstmatig aan een maat te koppelen.
    """
    stores_inventory: Dict[str, dict] = {}
    all_sizes = set()

    for record in voorraad_records:
        store_key = record.filiaal_code
        if store_key not in stores_inventory:
            stores_inventory[store_key] = {
                "store_id": record.filiaal_code,
                "store_name": record.filiaal_naam,
                "sizes": {},
                "sold_total": 0,
            }

        stores_inventory[store_key]["sizes"][record.maat] = record.voorraad
        stores_inventory[store_key]["sold_total"] = max(
            stores_inventory[store_key]["sold_total"],
            record.verkocht,
        )
        all_sizes.add(record.maat)

    return stores_inventory, list(all_sizes)


def apply_moves_to_inventory(
    stores_inventory: Dict[str, dict], moves: List[dict]
) -> Dict[str, dict]:
    """Pas moves toe op de huidige voorraad om de "proposed" situatie te krijgen.

    Defensieve toegang op de (JSON) moves: een onvolledige/legacy move wordt
    overgeslagen i.p.v. een ongevangen KeyError te veroorzaken (R7.3).
    """
    proposed_inventory: Dict[str, dict] = {}
    for store_id, data in stores_inventory.items():
        proposed_inventory[store_id] = dict(data["sizes"])  # kopie van huidige

    for move in moves:
        from_store = move.get("from_store")
        to_store = move.get("to_store")
        size = move.get("size")
        qty = move.get("qty", 0) or 0
        if from_store is None or to_store is None or size is None:
            continue

        # Verwijder van bron
        if from_store in proposed_inventory and size in proposed_inventory[from_store]:
            proposed_inventory[from_store][size] = max(
                0, proposed_inventory[from_store][size] - qty
            )

        # Voeg toe aan bestemming
        if to_store in proposed_inventory:
            if size not in proposed_inventory[to_store]:
                proposed_inventory[to_store][size] = 0
            proposed_inventory[to_store][size] += qty

    return proposed_inventory


def build_proposal_rows(
    proposals, assist_mode: str, use_model_scoring: bool
) -> List[Dict[str, Any]]:
    """Zet algoritme-proposals om naar persistentie-klare dict-rijen.

    Serialiseert de moves, verrijkt ze bij `shadow`/`rank_assist` met
    model-scores en hersorteert bij `rank_assist` op combined_score. Geeft
    dicts terug die `pdf_ingest_persistence.save_generated_proposals` wegschrijft.
    """
    rows: List[Dict[str, Any]] = []
    for proposal in proposals:
        raw_moves = [
            {
                "size": move.size,
                "from_store": move.from_store,
                "from_store_name": move.from_store_name,
                "to_store": move.to_store,
                "to_store_name": move.to_store_name,
                "qty": move.qty,
                "score": round(move.score, 2),
                "reason": move.reason,
                "from_bv": move.from_bv,
                "to_bv": move.to_bv,
                "model_score": None,
                "feature_snapshot": None,
            }
            for move in proposal.moves
        ]

        applied_rules = list(proposal.applied_rules)

        # Shadow/rank_assist: verrijk moves met model-score + feature_snapshot
        if use_model_scoring and raw_moves:
            try:
                raw_moves, model_meta = enrich_moves_with_model_scores(
                    proposal.volgnummer, raw_moves
                )
                if model_meta.get("model_score_applied"):
                    applied_rules.append({
                        "model_version": model_meta.get("model_version"),
                        "assist_mode": assist_mode,
                        "source_week": model_meta.get("week"),
                        "source_year": model_meta.get("year"),
                    })
            except Exception as exc:
                logger.warning(
                    f"[MODEL_SCORING] Skipped voor {proposal.volgnummer}: {exc}"
                )
                applied_rules.append("fallback:rule_only")

        # Bij rank_assist: hersorteer op combined_score (0.4 demand + 0.6 model)
        if assist_mode == "rank_assist" and raw_moves:
            def combined_score(m: dict) -> float:
                demand = float(m.get("score") or 0.0)
                model = float(m.get("model_score") or demand)
                return 0.4 * demand + 0.6 * model
            raw_moves = sorted(raw_moves, key=combined_score, reverse=True)

        rows.append({
            "artikelnummer": proposal.volgnummer,
            "article_name": proposal.article_name,
            "moves": raw_moves,
            "total_moves": proposal.total_moves,
            "total_quantity": proposal.total_quantity,
            "reason": proposal.reason,
            "applied_rules": applied_rules,
            "optimization_applied": str(proposal.optimization_applied).lower(),
            "stores_affected": list(proposal.stores_affected),
        })

    return rows


def generate_and_save_proposals(db: Session, batch_id: int) -> int:
    """Genereer herverdelingsvoorstellen voor een batch en sla ze op.

    Returns:
        Het aantal aangemaakte proposals (0 wanneer het algoritme niets voorstelt).
    """
    proposals = generate_redistribution_proposals_for_batch(db, batch_id, DEFAULT_PARAMS)

    if not proposals:
        return 0

    assist_mode = get_algorithm_assist_mode()
    use_model_scoring = assist_mode in {"shadow", "rank_assist"}

    rows = build_proposal_rows(proposals, assist_mode, use_model_scoring)
    return save_generated_proposals(db, batch_id, rows)


def run_batch_ingest(
    db: Session,
    files: List[Any],
    safe_filenames: List[str],
    batch_name: str,
    extra_data: Any,
    upload_dir: str,
) -> Dict[str, Any]:
    """Verwerk een batch geüploade PDF's: opslaan, parsen, persisteren, voorstellen.

    De bestandsnamen zijn vooraf door de HTTP-laag gevalideerd (`safe_filenames`
    correspondeert 1-op-1 met `files`). Geeft de payload terug die de router als
    JSON teruggeeft; het externe contract is ongewijzigd t.o.v. de vorige inline
    implementatie.
    """
    batch = PDFBatch(
        naam=batch_name,
        status="PENDING",
        pdf_count=len(files),
        processed_count=0,
        extra_data=extra_data,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    batch_id = batch.id
    logger.info(f"[BATCH_CREATE] Created batch {batch_id}: {batch_name}")

    batch_dir = os.path.join(upload_dir, f"batch_{batch_id}")
    os.makedirs(batch_dir, exist_ok=True)

    results: List[Dict[str, Any]] = []
    success_count = 0
    failed_count = 0

    for file, safe_name in zip(files, safe_filenames):
        logger.info(f"[FILE_PROCESS] Processing {file.filename}")

        try:
            # Sla het bestand op met een genormaliseerde, veilige naam en een harde
            # groottelimiet; parse het en persisteer de records.
            file_path = os.path.join(batch_dir, safe_name)
            save_upload_within_limit(file, file_path)

            parsed = parse_pdf_to_records(file_path)

            if parsed.errors:
                for error in parsed.errors:
                    log_entry = PDFParseLog(
                        batch_id=batch_id,
                        phase="VALIDATION",
                        level="ERROR",
                        message=error,
                        extra_data={"filename": file.filename},
                    )
                    db.add(log_entry)

                # Commit de validatie-logs meteen, zodat ze niet verloren gaan als
                # een later bestand in deze batch een sessie-rollback veroorzaakt.
                # Defensief: een mislukte log-commit mag de batch niet meeslepen.
                try:
                    db.commit()
                except Exception:
                    db.rollback()
                    logger.exception("[VALIDATION] Kon validatielog niet wegschrijven")

                failed_count += 1
                results.append({
                    "filename": file.filename,
                    "status": "FAILED",
                    "errors": parsed.errors,
                    "artikel_count": 0,
                })
                continue

            artikel_count = save_parsed_records(db, batch_id, parsed, file.filename)

            success_count += 1
            results.append({
                "filename": file.filename,
                "status": "SUCCESS",
                "artikel_count": artikel_count,
                "volgnummer": parsed.meta.get("Volgnummer"),
                "omschrijving": parsed.meta.get("Omschrijving"),
            })

            logger.info(f"[FILE_SUCCESS] {file.filename}: {artikel_count} records saved")

        except Exception as e:
            # Bewuste brede vangst op de buitenste per-bestand-laag (R7.1-uitzondering):
            # één corrupt bestand mag de rest van de batch niet meeslepen. De fout
            # wordt met stacktrace gelogd en als per-bestand FAILED gerapporteerd.
            #
            # Herstel eerst de sessie: als de fout een mislukte commit was (bv. een
            # UniqueConstraint-schending bij een dubbel bestand), staat de sessie in
            # een pending-rollback-staat en zou elke verdere db-actie — inclusief de
            # foutlog en de batch-afronding hieronder — óók falen. rollback() gooit
            # alleen de niet-gecommitte records van DIT bestand weg (all-or-nothing
            # per bestand); reeds gecommitte bestanden blijven behouden.
            db.rollback()

            logger.error(f"[FILE_ERROR] Error processing {file.filename}: {e}", exc_info=True)

            log_entry = PDFParseLog(
                batch_id=batch_id,
                phase="PROCESSING",
                level="ERROR",
                message=f"Failed to process file: {str(e)}",
                extra_data={"filename": file.filename},
            )
            db.add(log_entry)
            # Commit de foutlog meteen (net als in de validatie-tak), zodat een
            # rollback bij een later falend bestand deze diagnostiek niet wist.
            # Defensief: faalt zelfs deze log-commit (bv. DB locked/vol), dan mag
            # dat de batch-afronding niet meeslepen — val terug op de app-log.
            try:
                db.commit()
            except Exception:
                db.rollback()
                logger.exception("[FILE_ERROR] Kon foutlog niet wegschrijven")

            failed_count += 1
            results.append({
                "filename": file.filename,
                "status": "FAILED",
                "errors": [str(e)],
                "artikel_count": 0,
            })

    batch.processed_count = success_count

    if failed_count == 0:
        batch.status = "SUCCESS"
    elif success_count == 0:
        batch.status = "FAILED"
    else:
        batch.status = "PARTIAL_SUCCESS"

    db.commit()

    logger.info(
        f"[INGEST_COMPLETE] Batch {batch_id}: {success_count} success, {failed_count} failed"
    )

    proposals_count = 0
    if success_count > 0:
        try:
            logger.info(f"[PROPOSALS_START] Generating proposals for batch {batch_id}")
            proposals_count = generate_and_save_proposals(db, batch_id)
            logger.info(
                f"[PROPOSALS_SUCCESS] Generated {proposals_count} proposals for batch {batch_id}"
            )
        except Exception as e:
            # Proposal-generatie mag een succesvolle ingest niet laten falen: log
            # de fout, maar geef de batch alsnog terug (R7.1-uitzondering).
            logger.error(f"[PROPOSALS_ERROR] Failed to generate proposals: {e}", exc_info=True)
            log_entry = PDFParseLog(
                batch_id=batch_id,
                phase="PROPOSAL_GENERATION",
                level="ERROR",
                message=f"Failed to generate proposals: {str(e)}",
                extra_data={},
            )
            db.add(log_entry)
            db.commit()

    return {
        "batch_id": batch_id,
        "batch_name": batch_name,
        "status": batch.status,
        "total_files": len(files),
        "success_count": success_count,
        "failed_count": failed_count,
        "proposals_generated": proposals_count,
        "results": results,
    }

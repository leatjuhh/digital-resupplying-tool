"""
Test script to manually generate proposals for a batch
"""
from database import SessionLocal
from redistribution.algorithm import generate_redistribution_proposals_for_batch
from redistribution.constraints import DEFAULT_PARAMS
from db_models import Proposal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_generate_proposals(batch_id: int):
    """Generate proposals for a specific batch"""
    db = SessionLocal()
    
    try:
        logger.info(f"Generating proposals for batch {batch_id}...")
        
        # Generate proposals
        proposals = generate_redistribution_proposals_for_batch(db, batch_id, DEFAULT_PARAMS)
        
        logger.info(f"Generated {len(proposals)} proposals")
        
        if not proposals:
            logger.warning("No proposals generated! Checking data...")
            
            # Check voorraad data
            from db_models import ArtikelVoorraad
            voorraad_count = db.query(ArtikelVoorraad).filter(
                ArtikelVoorraad.batch_id == batch_id
            ).count()
            logger.info(f"Voorraad records in batch: {voorraad_count}")
            
            # Show some sample data
            sample = db.query(ArtikelVoorraad).filter(
                ArtikelVoorraad.batch_id == batch_id
            ).limit(5).all()
            
            logger.info("Sample voorraad data:")
            for record in sample:
                logger.info(f"  {record.volgnummer} - {record.omschrijving} - {record.filiaal_naam} - Maat {record.maat}: {record.voorraad}")
        
        else:
            # Save proposals
            logger.info("Saving proposals to database...")
            saved_count = 0
            for proposal in proposals:
                db_proposal = Proposal(
                    pdf_batch_id=batch_id,
                    artikelnummer=proposal.volgnummer,
                    article_name=proposal.article_name,
                    moves=[
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
                            "to_bv": move.to_bv
                        }
                        for move in proposal.moves
                    ],
                    total_moves=proposal.total_moves,
                    total_quantity=proposal.total_quantity,
                    status='pending',
                    reason=proposal.reason,
                    applied_rules=proposal.applied_rules,
                    optimization_applied=str(proposal.optimization_applied).lower(),
                    stores_affected=list(proposal.stores_affected)
                )
                db.add(db_proposal)
                saved_count += 1
            
            db.commit()
            logger.info(f"Saved {saved_count} proposals to database")
        
    except Exception as e:
        logger.error(f"Error generating proposals: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    batch_id = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    test_generate_proposals(batch_id)

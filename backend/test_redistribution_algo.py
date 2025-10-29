"""
Test script voor het herverdelingsalgoritme
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import get_db
from redistribution.algorithm import (
    generate_redistribution_proposals_for_article,
    generate_redistribution_proposals_for_batch
)
from redistribution.constraints import DEFAULT_PARAMS
from db_models import ArtikelVoorraad, Batch
import os
from dotenv import load_dotenv

load_dotenv()

def test_algorithm():
    """Test het herverdelingsalgoritme"""
    print("=== Test Herverdelingsalgoritme ===\n")
    
    # Maak database connectie
    db = next(get_db())
    
    try:
        # Haal de meest recente batch op
        latest_batch = db.query(Batch).order_by(Batch.created_at.desc()).first()
        
        if not latest_batch:
            print("Geen batches gevonden in de database")
            return
        
        print(f"Test met Batch ID: {latest_batch.id}")
        print(f"Batch naam: {latest_batch.name}")
        print(f"Aangemaakt op: {latest_batch.created_at}")
        print()
        
        # Haal een artikel uit deze batch
        sample_article = db.query(ArtikelVoorraad).filter(
            ArtikelVoorraad.batch_id == latest_batch.id
        ).first()
        
        if not sample_article:
            print("Geen artikelen gevonden in deze batch")
            return
        
        print(f"Test artikel: {sample_article.volgnummer}")
        print(f"Omschrijving: {sample_article.omschrijving}")
        print()
        
        # Test 1: Genereer voorstel voor één artikel
        print("--- Test 1: Genereer voorstel voor één artikel ---")
        proposal = generate_redistribution_proposals_for_article(
            db, 
            sample_article.volgnummer, 
            latest_batch.id,
            DEFAULT_PARAMS
        )
        
        if proposal:
            print(f"✓ Voorstel gegenereerd!")
            print(f"  - Aantal moves: {proposal.total_moves}")
            print(f"  - Totale hoeveelheid: {proposal.total_quantity}")
            print(f"  - Winkels betrokken: {len(proposal.stores_affected)}")
            print(f"  - Status: {proposal.status}")
            print(f"  - Reden: {proposal.reason}")
            print(f"  - Toegepaste regels: {', '.join(proposal.applied_rules)}")
            
            if proposal.moves:
                print(f"\n  Eerste 3 moves:")
                for i, move in enumerate(proposal.moves[:3], 1):
                    print(f"    {i}. {move.from_store} → {move.to_store}: {move.qty}x maat {move.size}")
                    print(f"       Score: {move.score:.2f}, Reden: {move.reason}")
        else:
            print("✗ Geen voorstel gegenereerd (mogelijk geen herverdeling nodig)")
        
        print()
        
        # Test 2: Genereer voorstellen voor hele batch (eerste 5 artikelen)
        print("--- Test 2: Genereer voorstellen voor batch (eerste 5 artikelen) ---")
        
        # Haal eerste 5 artikelnummers op
        article_numbers = db.query(ArtikelVoorraad.volgnummer).filter(
            ArtikelVoorraad.batch_id == latest_batch.id
        ).distinct().limit(5).all()
        
        article_numbers = [a[0] for a in article_numbers]
        print(f"Artikelen om te verwerken: {', '.join(article_numbers)}")
        print()
        
        proposals = []
        for volgnummer in article_numbers:
            prop = generate_redistribution_proposals_for_article(
                db, volgnummer, latest_batch.id, DEFAULT_PARAMS
            )
            if prop:
                proposals.append(prop)
        
        print(f"✓ {len(proposals)} voorstellen gegenereerd van {len(article_numbers)} artikelen")
        
        if proposals:
            total_moves = sum(p.total_moves for p in proposals)
            total_qty = sum(p.total_quantity for p in proposals)
            print(f"  - Totaal aantal moves: {total_moves}")
            print(f"  - Totale hoeveelheid: {total_qty}")
            
            print(f"\n  Samenvatting per artikel:")
            for prop in proposals:
                print(f"    - {prop.volgnummer}: {prop.total_moves} moves, {prop.total_quantity} items")
        
        print("\n=== Test Succesvol Afgerond ===")
        
    except Exception as e:
        print(f"\n✗ Error opgetreden: {type(e).__name__}")
        print(f"  Bericht: {str(e)}")
        import traceback
        print(f"\n  Traceback:")
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_algorithm()

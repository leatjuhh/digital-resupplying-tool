"""
Check detailed proposal info
"""
from database import SessionLocal
from db_models import Proposal
import json

db = SessionLocal()

print("=== CHECKING PROPOSAL 3 ===\n")
p = db.query(Proposal).filter(Proposal.id == 3).first()

if p:
    print(f"Artikelnummer: {p.artikelnummer}")
    print(f"Article Name: {p.article_name}")
    print(f"Status: {p.status}")
    print(f"Batch ID: {p.pdf_batch_id}")
    print(f"Total Moves: {p.total_moves}")
    print(f"Total Quantity: {p.total_quantity}")
    print(f"\nMoves (JSON):")
    if p.moves:
        print(json.dumps(p.moves, indent=2))
    else:
        print("  EMPTY or NULL")
    print(f"\nApplied Rules: {p.applied_rules}")
    print(f"Reason: {p.reason}")
    print(f"Optimization Applied: {p.optimization_applied}")
    print(f"Stores Affected: {p.stores_affected}")
else:
    print("Proposal 3 not found!")

db.close()

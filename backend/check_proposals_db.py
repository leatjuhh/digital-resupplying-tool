"""
Check database voor proposals en batches
"""
from database import SessionLocal
from db_models import Proposal, PDFBatch, ArtikelVoorraad

db = SessionLocal()

print("=== PDF BATCHES ===")
batches = db.query(PDFBatch).all()
print(f"Total batches: {len(batches)}\n")
for b in batches:
    print(f"Batch {b.id}: {b.naam}")
    print(f"  Status: {b.status}")
    print(f"  PDFs: {b.processed_count}/{b.pdf_count}")
    print(f"  Created: {b.created_at}")
    print()

print("\n=== PROPOSALS ===")
proposals = db.query(Proposal).all()
print(f"Total proposals: {len(proposals)}\n")

if proposals:
    for p in proposals[:10]:
        print(f"Proposal {p.id}: {p.artikelnummer}")
        print(f"  Article: {p.article_name}")
        print(f"  Status: {p.status}")
        print(f"  Batch: {p.pdf_batch_id}")
        print(f"  Moves: {p.total_moves}")
        print(f"  Quantity: {p.total_quantity}")
        print()
else:
    print("❌ NO PROPOSALS FOUND IN DATABASE!")
    
print("\n=== ARTIKEL VOORRAAD ===")
voorraad_count = db.query(ArtikelVoorraad).count()
print(f"Total voorraad records: {voorraad_count}")

if voorraad_count > 0:
    sample = db.query(ArtikelVoorraad).first()
    print(f"\nSample record:")
    print(f"  Volgnummer: {sample.volgnummer}")
    print(f"  Omschrijving: {sample.omschrijving}")
    print(f"  Batch: {sample.batch_id}")
    print(f"  Filiaal: {sample.filiaal_code} - {sample.filiaal_naam}")
    print(f"  Maat: {sample.maat}")
    print(f"  Voorraad: {sample.voorraad}")

db.close()

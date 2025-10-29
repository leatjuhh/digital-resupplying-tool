"""
Seed script voor herverdelingsalgoritme test data
Maakt realistische voorraad data aan per artikel/maat/winkel
"""

from database import SessionLocal
from db_models import Batch, ArtikelVoorraad
from datetime import datetime
import random


def create_test_batch(db):
    """Maak een test batch aan"""
    batch = Batch(
        name=f"Test Herverdeling - {datetime.now().strftime('%d %b %Y')}",
        status="completed",
        pdf_count=4,
        processed_count=4,
        created_at=datetime.now()
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def generate_realistic_inventory():
    """
    Genereer realistische voorraad verdeling
    Sommige winkels hebben teveel, andere te weinig
    """
    # Basis voorraad tussen 0-20 per winkel per maat
    base = random.randint(0, 20)
    variation = random.randint(-10, 10)
    return max(0, base + variation)


def generate_realistic_sales(inventory):
    """
    Genereer verkoopcijfers gebaseerd op voorraad
    Hoge voorraad = mogelijk meer verkocht
    """
    if inventory == 0:
        return 0
    # Verkocht is 10-80% van huidige voorraad
    sales_ratio = random.uniform(0.1, 0.8)
    return int(inventory * sales_ratio)


def seed_redistribution_data(db, batch_id):
    """Vul database met test data voor herverdeling"""
    
    # Test artikelen met verschillende maat types
    test_articles = [
        {
            'volgnummer': '54321',
            'omschrijving': 'Spijkerbroek Slim Fit Blauw',
            'sizes': ['28', '30', '32', '34', '36', '38', '40']  # Numeric sizes
        },
        {
            'volgnummer': '54448',
            'omschrijving': 'T-Shirt Basic Wit',
            'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL']  # Letter sizes
        },
        {
            'volgnummer': '12345',
            'omschrijving': 'Sneakers Running Zwart',
            'sizes': ['39', '40', '41', '42', '43', '44', '45']  # Shoe sizes
        },
        {
            'volgnummer': '67890',
            'omschrijving': 'Winterjas Lang Model',
            'sizes': ['S', 'M', 'L', 'XL']  # Limited sizes
        },
    ]
    
    # Test winkels met codes en namen
    test_stores = [
        ('001', 'Amsterdam Centrum'),
        ('002', 'Rotterdam Zuid'),
        ('003', 'Utrecht CS'),
        ('004', 'Den Haag Spui'),
        ('005', 'Eindhoven Centrum'),
        ('006', 'Groningen Grote Markt'),
        ('007', 'Maastricht Stationsstraat'),
        ('008', 'Arnhem Centraal'),
    ]
    
    records_created = 0
    
    for article in test_articles:
        print(f"\nSeeding artikel: {article['volgnummer']} - {article['omschrijving']}")
        
        for store_code, store_name in test_stores:
            for size in article['sizes']:
                # Genereer realistische cijfers
                voorraad = generate_realistic_inventory()
                verkocht = generate_realistic_sales(voorraad)
                
                # Maak voorraad record aan
                record = ArtikelVoorraad(
                    volgnummer=article['volgnummer'],
                    omschrijving=article['omschrijving'],
                    maat=size,
                    filiaal_code=store_code,
                    filiaal_naam=store_name,
                    voorraad=voorraad,
                    verkocht=verkocht,
                    batch_id=batch_id
                )
                
                db.add(record)
                records_created += 1
        
        print(f"  ✓ {len(test_stores) * len(article['sizes'])} records aangemaakt")
    
    db.commit()
    print(f"\n✓ Totaal {records_created} voorraad records aangemaakt")
    return records_created


def main():
    """Main seeding functie"""
    print("\n🌱 Seeding herverdelingsalgoritme test data...\n")
    
    db = SessionLocal()
    
    try:
        # Stap 1: Maak test batch
        print("Stap 1: Batch aanmaken...")
        batch = create_test_batch(db)
        print(f"✓ Batch aangemaakt: ID={batch.id}, Naam='{batch.name}'")
        
        # Stap 2: Vul met voorraad data
        print(f"\nStap 2: Voorraad data aanmaken...")
        records = seed_redistribution_data(db, batch.id)
        
        print(f"\n✅ Seeding succesvol!\n")
        print(f"Batch ID: {batch.id}")
        print(f"Records: {records}")
        print(f"\nJe kunt nu testen met:")
        print(f"  python test_redistribution_algo.py")
        
    except Exception as e:
        print(f"\n❌ Error tijdens seeding: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

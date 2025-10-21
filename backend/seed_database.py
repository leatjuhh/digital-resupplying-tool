"""
Database seeding script
Run this to initialize the database with test data
"""
# Importeer database componenten en models
from database import engine, SessionLocal, Base
from db_models import Store, Article


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    # Maak alle tabellen aan op basis van de Base metadata (Store en Article)
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")


def seed_stores(db):
    """Add default stores"""
    # Lijst met standaard winkels om toe te voegen
    stores = [
        Store(name="Amsterdam", city="Amsterdam", code="AMS"),
        Store(name="Rotterdam", city="Rotterdam", code="RTM"),
        Store(name="Utrecht", city="Utrecht", code="UTR"),
        Store(name="Den Haag", city="Den Haag", code="DHG"),
    ]
    
    # Loop door alle winkels en voeg ze toe indien ze nog niet bestaan
    for store in stores:
        # Controleer of winkel al bestaat op basis van code
        existing = db.query(Store).filter(Store.code == store.code).first()
        if not existing:
            # Voeg nieuwe winkel toe
            db.add(store)
            print(f"✓ Added store: {store.name}")
        else:
            # Winkel bestaat al, skip
            print(f"- Store already exists: {store.name}")
    
    # Sla alle wijzigingen op in de database
    db.commit()


def seed_articles(db):
    """Add default articles"""
    # Lijst met test artikelen inclusief voorraad per winkel
    articles = [
        Article(
            artikelnummer="ART-001",
            omschrijving="Winter Jacket - Blue",
            voorraad_per_winkel={
                "Amsterdam": 15,
                "Rotterdam": 8,
                "Utrecht": 12,
                "Den Haag": 6
            }
        ),
        Article(
            artikelnummer="ART-002",
            omschrijving="Summer T-Shirt - White",
            voorraad_per_winkel={
                "Amsterdam": 25,
                "Rotterdam": 18,
                "Utrecht": 20,
                "Den Haag": 15
            }
        ),
        Article(
            artikelnummer="ART-003",
            omschrijving="Denim Jeans - Black",
            voorraad_per_winkel={
                "Amsterdam": 10,
                "Rotterdam": 12,
                "Utrecht": 8,
                "Den Haag": 14
            }
        ),
        Article(
            artikelnummer="ART-004",
            omschrijving="Sneakers - Red",
            voorraad_per_winkel={
                "Amsterdam": 7,
                "Rotterdam": 5,
                "Utrecht": 9,
                "Den Haag": 11
            }
        ),
        Article(
            artikelnummer="ART-005",
            omschrijving="Baseball Cap - Green",
            voorraad_per_winkel={
                "Amsterdam": 20,
                "Rotterdam": 16,
                "Utrecht": 18,
                "Den Haag": 22
            }
        ),
    ]
    
    # Loop door alle artikelen en voeg ze toe indien ze nog niet bestaan
    for article in articles:
        # Controleer of artikel al bestaat op basis van artikelnummer
        existing = db.query(Article).filter(
            Article.artikelnummer == article.artikelnummer
        ).first()
        if not existing:
            # Voeg nieuw artikel toe
            db.add(article)
            print(f"✓ Added article: {article.artikelnummer} - {article.omschrijving}")
        else:
            # Artikel bestaat al, skip
            print(f"- Article already exists: {article.artikelnummer}")
    
    # Sla alle wijzigingen op in de database
    db.commit()


def main():
    """Main seeding function"""
    print("\n🌱 Starting database seeding...\n")
    
    # Stap 1: Maak database tabellen aan
    create_tables()
    
    # Stap 2: Open een database sessie
    db = SessionLocal()
    
    try:
        # Stap 3: Voeg standaard winkels toe
        print("\nSeeding stores...")
        seed_stores(db)
        
        # Stap 4: Voeg test artikelen toe
        print("\nSeeding articles...")
        seed_articles(db)
        
        # Succes bericht
        print("\n✅ Database seeding completed!\n")
        print("Database file: database.db")
        print("You can now start the API server.\n")
        
    except Exception as e:
        # Bij fouten: rollback alle wijzigingen
        print(f"\n❌ Error during seeding: {e}\n")
        db.rollback()
    finally:
        # Sluit altijd de database sessie
        db.close()


# Start het seeding proces als dit script direct wordt uitgevoerd
if __name__ == "__main__":
    main()

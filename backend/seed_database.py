"""
Database seeding script
Run this to initialize the database with test data
"""
# Importeer database componenten en models
from database import engine, SessionLocal, Base
from db_models import Store, Article, User, Role, Permission, Settings
from auth import get_password_hash


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


def seed_permissions(db):
    """Add default permissions"""
    print("\nSeeding permissions...")
    
    permissions_data = [
        # Dashboard
        ("view_dashboard", "Dashboard Bekijken", "Toegang tot dashboard", "dashboard"),
        
        # Proposals
        ("view_proposals", "Voorstellen Bekijken", "Voorstellen bekijken", "proposals"),
        ("create_proposals", "Voorstellen Aanmaken", "Nieuwe voorstellen aanmaken", "proposals"),
        ("approve_proposals", "Voorstellen Goedkeuren", "Voorstellen goedkeuren", "proposals"),
        ("reject_proposals", "Voorstellen Afkeuren", "Voorstellen afkeuren", "proposals"),
        ("edit_proposals", "Voorstellen Bewerken", "Voorstellen aanpassen", "proposals"),
        ("delete_proposals", "Voorstellen Verwijderen", "Voorstellen verwijderen", "proposals"),
        
        # Assignments
        ("view_assignments", "Opdrachten Bekijken", "Opdrachten bekijken", "assignments"),
        ("manage_assignments", "Opdrachten Beheren", "Opdrachten aanmaken en aanpassen", "assignments"),
        
        # Users
        ("view_users", "Gebruikers Bekijken", "Gebruikers bekijken", "users"),
        ("manage_users", "Gebruikers Beheren", "Gebruikers aanmaken, bewerken en verwijderen", "users"),
        
        # Settings
        ("view_settings", "Instellingen Bekijken", "Instellingen bekijken", "settings"),
        ("manage_general_settings", "Algemene Instellingen Beheren", "Algemene instellingen aanpassen", "settings"),
        ("manage_rules_settings", "Regel Instellingen Beheren", "Herverdelingsregels aanpassen", "settings"),
        ("manage_api_settings", "API Instellingen Beheren", "API instellingen aanpassen", "settings"),
        
        # Roles
        ("manage_roles", "Rollen Beheren", "Rollen en permissies beheren", "roles"),
        ("manage_permissions", "Permissies Beheren", "Permissies toewijzen", "roles"),
        
        # Uploads & Batches
        ("upload_pdfs", "PDFs Uploaden", "PDF bestanden uploaden", "uploads"),
        ("view_batches", "Batches Bekijken", "Upload batches bekijken", "batches"),
        ("manage_batches", "Batches Beheren", "Batches beheren", "batches"),
    ]
    
    for name, display_name, description, category in permissions_data:
        existing = db.query(Permission).filter(Permission.name == name).first()
        if not existing:
            perm = Permission(
                name=name,
                display_name=display_name,
                description=description,
                category=category
            )
            db.add(perm)
            print(f"✓ Added permission: {display_name}")
        else:
            print(f"- Permission already exists: {display_name}")
    
    db.commit()


def seed_roles(db):
    """Add default roles with permissions"""
    print("\nSeeding roles...")
    
    # Haal alle permissions op
    all_permissions = db.query(Permission).all()
    perm_dict = {p.name: p for p in all_permissions}
    
    # Admin role - alle permissions
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(
            name="admin",
            display_name="Administrator",
            description="Volledige toegang tot alle functies",
            is_system_role=True
        )
        admin_role.permissions = all_permissions
        db.add(admin_role)
        print(f"✓ Added role: Administrator (met alle {len(all_permissions)} permissions)")
    else:
        print("- Role already exists: Administrator")
    
    # User role - hoofdkantoor medewerker
    user_role = db.query(Role).filter(Role.name == "user").first()
    if not user_role:
        user_permissions = [
            perm_dict.get(p) for p in [
                "view_dashboard",
                "view_proposals",
                "approve_proposals",
                "reject_proposals",
                "edit_proposals",
                "view_assignments",
                "view_settings",
                "manage_rules_settings",
                "upload_pdfs",
                "view_batches"
            ] if perm_dict.get(p)
        ]
        
        user_role = Role(
            name="user",
            display_name="Gebruiker",
            description="Hoofdkantoor medewerker met toegang tot voorstellen en regels",
            is_system_role=True
        )
        user_role.permissions = user_permissions
        db.add(user_role)
        print(f"✓ Added role: Gebruiker (met {len(user_permissions)} permissions)")
    else:
        print("- Role already exists: Gebruiker")
    
    # Store role - winkel medewerker
    store_role = db.query(Role).filter(Role.name == "store").first()
    if not store_role:
        store_permissions = [
            perm_dict.get(p) for p in [
                "view_dashboard",
                "view_assignments",
                "view_proposals"
            ] if perm_dict.get(p)
        ]
        
        store_role = Role(
            name="store",
            display_name="Winkel",
            description="Winkel medewerker met beperkte toegang",
            is_system_role=True
        )
        store_role.permissions = store_permissions
        db.add(store_role)
        print(f"✓ Added role: Winkel (met {len(store_permissions)} permissions)")
    else:
        print("- Role already exists: Winkel")
    
    db.commit()


def seed_users(db):
    """Add default users"""
    print("\nSeeding users...")
    
    # Haal roles op
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    user_role = db.query(Role).filter(Role.name == "user").first()
    store_role = db.query(Role).filter(Role.name == "store").first()
    
    users_data = [
        ("admin", "admin@lumitex.nl", "Admin User", "Admin123!", admin_role.id, None, None),
        ("user", "user@lumitex.nl", "Test User", "User123!", user_role.id, None, None),
        ("store", "store@lumitex.nl", "Store User", "Store123!", store_role.id, "9", "Stein"),
    ]
    
    for username, email, full_name, password, role_id, store_code, store_name in users_data:
        existing = db.query(User).filter(User.username == username).first()
        if not existing:
            hashed_password = get_password_hash(password)
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=hashed_password,
                role_id=role_id,
                is_active=True,
                store_code=store_code,
                store_name=store_name,
            )
            db.add(user)
            print(f"✓ Added user: {username} ({email}) - Password: {password}")
        else:
            print(f"- User already exists: {username}")
    
    db.commit()


def seed_settings(db):
    """Add default settings"""
    print("\nSeeding settings...")
    
    settings_data = [
        # General settings
        ("app_name", "Digital Resupplying", "general", "Applicatie naam"),
        ("language", "nl", "general", "Taal"),
        ("timezone", "Europe/Amsterdam", "general", "Tijdzone"),
        ("email_notifications", True, "general", "E-mail notificaties"),
        
        # Rules settings
        ("min_stock_per_store", 2, "rules", "Minimum voorraad per winkel"),
        ("max_stock_per_store", 10, "rules", "Maximum voorraad per winkel"),
        ("min_stores_per_article", 3, "rules", "Minimum aantal winkels per artikel"),
        ("sales_period_days", 30, "rules", "Verkoopcijfers periode (dagen)"),
    ]
    
    for key, value, category, description in settings_data:
        existing = db.query(Settings).filter(Settings.key == key).first()
        if not existing:
            setting = Settings(
                key=key,
                value=value,
                category=category,
                description=description
            )
            db.add(setting)
            print(f"✓ Added setting: {key} = {value}")
        else:
            print(f"- Setting already exists: {key}")
    
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
        # Stap 3: Seed permissions (moet eerst)
        seed_permissions(db)
        
        # Stap 4: Seed roles (met permissions)
        seed_roles(db)
        
        # Stap 5: Seed users (met roles)
        seed_users(db)
        
        # Stap 6: Seed settings
        seed_settings(db)
        
        # Stap 7: Voeg standaard winkels toe
        print("\nSeeding stores...")
        seed_stores(db)
        
        # Stap 8: Voeg test artikelen toe
        print("\nSeeding articles...")
        seed_articles(db)
        
        # Succes bericht
        print("\n✅ Database seeding completed!\n")
        print("Database file: database.db")
        print("\n🔐 Default Users Created:")
        print("  Admin:  username='admin', password='Admin123!'")
        print("  User:   username='user', password='User123!'")
        print("  Store:  username='store', password='Store123!'")
        print("\nYou can now start the API server.\n")
        
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

"""
Reset database script
Creates a fresh database with correct schema including pdf_batch_id column
"""
import os
import shutil
from datetime import datetime
from database import Base, engine

def reset_database():
    """
    Reset the database - creates backup and recreates with correct schema
    """
    db_path = "database.db"
    
    print("="*60)
    print("DATABASE RESET SCRIPT")
    print("="*60)
    
    # Step 1: Backup existing database
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"database.db.backup_{timestamp}"
        
        print(f"\n[1/3] Creating backup...")
        try:
            shutil.copy2(db_path, backup_path)
            print(f"✓ Backup created: {backup_path}")
        except Exception as e:
            print(f"✗ Error creating backup: {e}")
            return False
        
        # Step 2: Remove old database
        print(f"\n[2/3] Removing old database...")
        try:
            os.remove(db_path)
            print(f"✓ Old database removed")
        except Exception as e:
            print(f"✗ Error removing database: {e}")
            return False
    else:
        print(f"\n[1/3] No existing database found - creating new one")
    
    # Step 3: Create new database with correct schema
    print(f"\n[3/3] Creating new database with correct schema...")
    try:
        Base.metadata.create_all(bind=engine)
        print(f"✓ New database created successfully!")
        
        # List all tables
        print("\n📋 Created tables:")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        for table in sorted(tables):
            columns = inspector.get_columns(table)
            print(f"  - {table} ({len(columns)} columns)")
            
            # Show Proposal table structure
            if table == 'proposals':
                print("    Key columns:")
                for col in columns:
                    if col['name'] in ['id', 'batch_id', 'pdf_batch_id', 'artikelnummer', 'status']:
                        nullable = "NULL" if col.get('nullable', True) else "NOT NULL"
                        print(f"      • {col['name']}: {col['type']} ({nullable})")
        
        print("\n" + "="*60)
        print("✅ DATABASE RESET COMPLETE!")
        print("="*60)
        print("\n💡 Next steps:")
        print("  1. Restart the backend server")
        print("  2. Upload new PDFs via the frontend")
        print("  3. Test the application")
        print("\n")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = reset_database()
    exit(0 if success else 1)

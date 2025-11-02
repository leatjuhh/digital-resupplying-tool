"""
Check if authentication system is ready
"""
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from db_models import User, Role, Permission

# Create engine
engine = create_engine('sqlite:///database.db')
inspector = inspect(engine)

# Check tables
tables = inspector.get_table_names()
print("=== DATABASE TABLES ===")
print(f"Present: {', '.join(tables)}")
print()

# Check if auth tables exist
auth_tables = ['users', 'roles', 'permissions', 'role_permissions']
missing_tables = [t for t in auth_tables if t not in tables]

if missing_tables:
    print(f"❌ MISSING TABLES: {', '.join(missing_tables)}")
    print("Run: python seed_database.py")
    exit(1)

# Check data
session = Session(engine)

try:
    user_count = session.query(User).count()
    role_count = session.query(Role).count()
    perm_count = session.query(Permission).count()
    
    print("=== DATA COUNT ===")
    print(f"Users: {user_count}")
    print(f"Roles: {role_count}")
    print(f"Permissions: {perm_count}")
    print()
    
    if user_count == 0 or role_count == 0:
        print("❌ NO DATA FOUND")
        print("Run: python seed_database.py")
        exit(1)
    
    # List users
    print("=== TEST USERS ===")
    users = session.query(User).all()
    for user in users:
        role = session.query(Role).filter(Role.id == user.role_id).first()
        role_name = role.name if role else "NO ROLE"
        status = "✅ ACTIVE" if user.is_active else "❌ INACTIVE"
        print(f"  {status} {user.username} (Role: {role_name})")
    print()
    
    # List roles
    print("=== ROLES ===")
    roles = session.query(Role).all()
    for role in roles:
        perm_count = len(role.permissions)
        print(f"  - {role.name}: {role.display_name} ({perm_count} permissions)")
    print()
    
    print("✅ AUTHENTICATION SYSTEM READY!")
    print()
    print("Test Credentials:")
    print("  Admin: username='admin', password from seed script")
    print("  User: username='user', password from seed script")
    print("  Store: username='store', password from seed script")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("Database structure may be incomplete")
    print("Run: python seed_database.py")
    exit(1)
finally:
    session.close()

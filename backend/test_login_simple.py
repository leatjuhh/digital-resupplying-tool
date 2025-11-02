"""
Simple test of login flow without requests library
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from auth import authenticate_user, create_access_token, decode_token
import db_models

db = SessionLocal()

print("=== SIMPLE AUTH TEST ===\n")

# Test 1: Authentication
print("1. Testing authentication...")
user = authenticate_user(db, "admin", "Admin123!")

if user:
    print(f"   ✅ User authenticated: {user.username}")
    
    # Test 2: Token creation
    print("\n2. Creating access token...")
    
    # Get role and permissions
    role = db.query(db_models.Role).filter(
        db_models.Role.id == user.role_id
    ).first()
    
    if role:
        permissions = [perm.name for perm in role.permissions]
        
        token_data = {
            "sub": user.id,
            "username": user.username,
            "role": role.name,
            "permissions": permissions
        }
        
        access_token = create_access_token(data=token_data)
        print(f"   ✅ Token created: {access_token[:50]}...")
        
        # Test 3: Token validation
        print("\n3. Validating token...")
        try:
            payload = decode_token(access_token)
            print(f"   ✅ Token valid!")
            print(f"   User ID: {payload.get('sub')}")
            print(f"   Username: {payload.get('username')}")
            print(f"   Role: {payload.get('role')}")
            print(f"   Permissions: {len(payload.get('permissions', []))} permissions")
        except Exception as e:
            print(f"   ❌ Token validation failed: {e}")
    else:
        print("   ❌ User has no role")
else:
    print("   ❌ Authentication failed")

db.close()
print("\n=== TEST COMPLETE ===")

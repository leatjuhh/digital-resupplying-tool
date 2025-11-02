"""
Check which SECRET_KEY the backend is using
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("  SECRET_KEY VERIFICATION")
print("=" * 60)

# Load .env
load_dotenv()

# Get SECRET_KEY
secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")

print(f"\n✅ .env file loaded")
print(f"🔑 SECRET_KEY from env: {secret_key}")
print(f"📏 Length: {len(secret_key)} characters")

if secret_key == "your-secret-key-change-this-in-production":
    print("\n⚠️  WARNING: Using default/fallback SECRET_KEY!")
    print("   The .env file may not be loaded properly.")
elif "supersecretkey12345" in secret_key:
    print("\n✅ Using custom SECRET_KEY from .env file")
else:
    print("\n❓ Using unknown SECRET_KEY")

print("\n" + "=" * 60)

# Also test JWT encoding/decoding
from jose import jwt
from datetime import datetime, timedelta

print("\n  TESTING JWT ENCODE/DECODE")
print("=" * 60)

try:
    # Create a test token
    test_payload = {
        "sub": 1,
        "username": "test",
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    
    token = jwt.encode(test_payload, secret_key, algorithm="HS256")
    print(f"\n✅ Token created successfully")
    print(f"🎫 Token (first 50 chars): {token[:50]}...")
    
    # Try to decode it
    decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
    print(f"\n✅ Token decoded successfully")
    print(f"👤 Decoded payload: {decoded}")
    
    print("\n✅ JWT encode/decode is working correctly!")
    
except Exception as e:
    print(f"\n❌ JWT encode/decode FAILED: {str(e)}")

print("\n" + "=" * 60)

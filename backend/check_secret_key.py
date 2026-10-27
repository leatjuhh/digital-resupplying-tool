"""Diagnose: controleer of de backend een bruikbare SECRET_KEY heeft.

Dit script toont NOOIT de sleutelwaarde zelf (PR-002 / hoofdstuk 8 van de
engineeringstandaard: geen secrets naar stdout/logs). Het rapporteert alleen
aanwezigheid en lengte, en test dat JWT encode/decode werkt met de actieve
sleutel.
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("  SECRET_KEY VERIFICATION")
print("=" * 60)

# Load .env
load_dotenv()

# Get SECRET_KEY (geen fallback: consistent met auth.py's fail-fast beleid)
secret_key = os.getenv("SECRET_KEY")

if not secret_key:
    print("\n❌ SECRET_KEY is niet gezet.")
    print("   Zet SECRET_KEY in de omgeving of in backend/.env (zie .env.example).")
    print("   De backend start bewust NIET zonder deze variabele.")
    print("\n" + "=" * 60)
    raise SystemExit(1)

print("\n✅ .env geladen; SECRET_KEY aanwezig")
print(f"📏 Lengte: {len(secret_key)} tekens")
if len(secret_key) < 32:
    print("⚠️  WAARSCHUWING: SECRET_KEY is kort (< 32 tekens); gebruik een lange, willekeurige waarde.")

print("\n" + "=" * 60)

# Test JWT encoding/decoding zonder de sleutel of payload-inhoud te tonen
from jose import jwt
from datetime import datetime, timedelta

print("\n  TESTING JWT ENCODE/DECODE")
print("=" * 60)

try:
    test_payload = {
        "sub": 1,
        "username": "test",
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    token = jwt.encode(test_payload, secret_key, algorithm="HS256")
    jwt.decode(token, secret_key, algorithms=["HS256"])
    print("\n✅ JWT encode/decode werkt correct met de actieve SECRET_KEY")
except Exception as e:
    print(f"\n❌ JWT encode/decode MISLUKT: {type(e).__name__}")

print("\n" + "=" * 60)

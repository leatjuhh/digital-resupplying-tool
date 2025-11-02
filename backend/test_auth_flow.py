"""
Test the complete authentication flow
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=== AUTH FLOW TEST ===\n")

# Step 1: Try to login
print("1. Testing login endpoint...")
login_data = {
    "username": "admin",
    "password": "Admin123!"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        tokens = response.json()
        print(f"   ✅ Login successful!")
        print(f"   Access token: {tokens['access_token'][:50]}...")
        print(f"   Refresh token: {tokens['refresh_token'][:50]}...")
        
        # Step 2: Try to get user info
        print("\n2. Testing /me endpoint with access token...")
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        print(f"   Status: {me_response.status_code}")
        
        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"   ✅ User info retrieved successfully!")
            print(f"   User: {user_data['username']}")
            print(f"   Role: {user_data['role_name']}")
            print(f"   Permissions: {len(user_data['permissions'])} permissions")
        else:
            print(f"   ❌ Failed to get user info")
            print(f"   Response: {me_response.text}")
    else:
        print(f"   ❌ Login failed")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n=== TEST COMPLETE ===")

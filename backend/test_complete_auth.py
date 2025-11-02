"""
Complete authentication flow test
Tests login -> get user info -> token validation
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_complete_auth_flow():
    """Test the complete authentication flow"""
    print_section("COMPLETE AUTH FLOW TEST")
    
    # Test credentials
    username = "admin"
    password = "Admin123!"
    
    print(f"🔐 Testing login with username: {username}")
    print(f"🔗 URL: {BASE_URL}/api/auth/login\n")
    
    # Step 1: Login
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"📊 Login Response Status: {response.status_code}")
        
        if response.status_code == 200:
            tokens = response.json()
            print("✅ Login SUCCESSFUL!")
            print(f"\n🎫 Token Type: {tokens.get('token_type')}")
            print(f"🔑 Access Token (first 50 chars): {tokens.get('access_token', '')[:50]}...")
            print(f"🔄 Refresh Token (first 50 chars): {tokens.get('refresh_token', '')[:50]}...")
            
            access_token = tokens.get('access_token')
            
            # Step 2: Get user info
            print_section("TESTING /api/auth/me ENDPOINT")
            print(f"🔗 URL: {BASE_URL}/api/auth/me")
            print(f"🔑 Using access token: {access_token[:50]}...\n")
            
            me_response = requests.get(
                f"{BASE_URL}/api/auth/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"📊 /me Response Status: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_info = me_response.json()
                print("✅ Get User Info SUCCESSFUL!")
                print(f"\n👤 User Info:")
                print(f"   - ID: {user_info.get('id')}")
                print(f"   - Username: {user_info.get('username')}")
                print(f"   - Email: {user_info.get('email')}")
                print(f"   - Full Name: {user_info.get('full_name')}")
                print(f"   - Role: {user_info.get('role_name')} ({user_info.get('role_display_name')})")
                print(f"   - Is Active: {user_info.get('is_active')}")
                print(f"   - Permissions: {user_info.get('permissions')}")
                
                print_section("✨ COMPLETE AUTH FLOW: SUCCESS ✨")
                return True
            else:
                print(f"❌ Get User Info FAILED!")
                print(f"Response: {me_response.text}")
                
                print_section("DIAGNOSIS")
                print("The login worked, but /me endpoint failed.")
                print("This suggests a token validation issue.")
                print("\nPossible causes:")
                print("1. Backend was restarted with different SECRET_KEY")
                print("2. Token encoding/decoding mismatch")
                print("3. Authorization header format issue")
                
                return False
        else:
            print(f"❌ Login FAILED!")
            print(f"Response: {response.text}")
            
            print_section("DIAGNOSIS")
            print("Login endpoint returned error.")
            print("\nPossible causes:")
            print("1. Wrong credentials (check seed_database.py)")
            print("2. Backend not running")
            print("3. Database not initialized")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR!")
        print(f"\nCouldn't connect to {BASE_URL}")
        print("\n⚠️  Make sure the backend is running:")
        print("   cd backend")
        print("   python main.py")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"\n🚀 Starting Complete Auth Flow Test")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_complete_auth_flow()
    
    if success:
        print("\n🎉 All tests passed! Auth system is working correctly.")
        print("\n💡 Next steps:")
        print("   - Try logging in via the frontend at http://localhost:3000/login")
        print("   - Use credentials: admin / Admin123!")
    else:
        print("\n❌ Tests failed. See diagnosis above for next steps.")
    
    print()

# test_complete.py
from mongodb_connection import MongoDBConnection

print("🧪 Testing Complete MongoDB Setup...")
print("=" * 60)

db = MongoDBConnection()

if db.connected:
    print("✅ MongoDB Connection: SUCCESS")
    
    # Test registration
    print("\n🔐 Testing Registration...")
    result = db.register_user(
        username="testuser123",
        email="test123@example.com",
        password="SecurePass123!",
        full_name="Test User"
    )
    
    if result['success']:
        print(f"✅ Registration: {result['message']}")
        user_id = result['user_id']
        
        # Test login
        print("\n🔐 Testing Login...")
        login_result = db.login_user("testuser123", "SecurePass123!")
        
        if login_result['success']:
            print(f"✅ Login: {login_result['message']}")
            print(f"   User ID: {login_result['user']['user_id']}")
            print(f"   Username: {login_result['user']['username']}")
            
            # Clean up
            print("\n🧹 Cleaning up...")
            db.delete_user_account(user_id)
            print("✅ Test complete and cleaned up!")
        else:
            print(f"❌ Login failed: {login_result['message']}")
    else:
        print(f"❌ Registration failed: {result['message']}")
else:
    print("❌ MongoDB Connection: FAILED")

db.disconnect()
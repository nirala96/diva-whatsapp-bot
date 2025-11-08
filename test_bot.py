"""
Test script for Diva Daulti AI Chatbot
Run this after starting the server to test the chatbot functionality
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Status: {response.status_code}")
        print(f"📋 Response: {json.dumps(response.json(), indent=2)}")
        print()
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        return False

def test_chat(user, message):
    """Test the chat webhook endpoint"""
    print(f"💬 Testing Chat: '{message}'")
    print(f"👤 User: {user}")
    try:
        response = requests.post(
            f"{BASE_URL}/webhook",
            json={"user": user, "message": message}
        )
        print(f"✅ Status: {response.status_code}")
        result = response.json()
        print(f"🤖 AI Reply: {result['reply']}")
        print()
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        return False

def run_all_tests():
    """Run all test cases"""
    print("=" * 60)
    print("🌟 Diva Daulti AI Chatbot - Test Suite")
    print("=" * 60)
    print()
    
    # Test 1: Health Check
    if not test_health_check():
        print("⚠️  Server might not be running. Start it with: ./start.sh")
        return
    
    # Test 2: Sample conversations
    test_cases = [
        {
            "user": "+919876543210",
            "message": "Hi! Do you have silk sarees?"
        },
        {
            "user": "+919876543210",
            "message": "What colors are available in lehengas?"
        },
        {
            "user": "+919123456789",
            "message": "I need an outfit for my sister's wedding. Can you help?"
        },
        {
            "user": "+919123456789",
            "message": "What's the price range for your wedding collection?"
        }
    ]
    
    print("🧪 Running Sample Conversations...")
    print("-" * 60)
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}/{len(test_cases)}")
        print("-" * 60)
        test_chat(test_case["user"], test_case["message"])
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print()
    print("💡 Tips:")
    print("   - Check Google Sheets to see logged conversations")
    print("   - Visit http://localhost:8000/docs for interactive API testing")
    print("   - Use the /test-chat endpoint for testing without logging")

if __name__ == "__main__":
    run_all_tests()

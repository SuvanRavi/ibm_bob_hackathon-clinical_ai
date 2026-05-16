"""
Quick test script to verify the symptom analyzer API is working
"""

import requests
import json

# Test 1: Check if Flask is running
print("=" * 60)
print("Testing Symptom Analyzer API")
print("=" * 60)

try:
    # Test status endpoint
    print("\n1. Testing status endpoint...")
    response = requests.get('http://127.0.0.1:5000/api/symptom-analyzer/status')
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    
    if response.json().get('available'):
        print("   ✅ Model is loaded and ready!")
    else:
        print("   ⚠️  Model not loaded yet (will load on first image upload)")
    
except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to Flask server")
    print("   Make sure Flask is running: python app.py")
    exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 2: Check other endpoints
print("\n2. Testing other Flask endpoints...")
try:
    response = requests.get('http://127.0.0.1:5000/')
    print(f"   Root endpoint (/) - Status: {response.status_code}")
    print(f"   ✅ Flask is serving content")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("API Test Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. If status shows 'available: false', the model will load on first use")
print("2. Go to http://localhost:5173/symptom-analyzer")
print("3. Upload an image to trigger model loading")
print("4. Check Flask terminal for loading messages")

# Made with Bob

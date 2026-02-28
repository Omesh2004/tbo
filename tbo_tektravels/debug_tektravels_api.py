#!/usr/bin/env python3
"""Debug script to capture raw TekTravels Flight API response"""
import requests
import json
import logging

logging.basicConfig(level=logging.DEBUG)

# TekTravels Flight API Config
BASE_URL = "https://api.tektravels.com"
USER_ID = "Hackathon"
PASSWORD = "Hackathon@123"

headers = {
    'Content-Type': 'application/json'
}

# Test 1: Try basic FlightSearch endpoint
print("=" * 80)
print("TEST 1: FlightSearch Endpoint")
print("=" * 80)

search_payload = {
    'UserId': USER_ID,
    'Password': PASSWORD,
    "Origin": "MAD",
    "Destination": "ATH",
    "DepartureDate": "2026-03-15",
    "ReturnDate": "2026-03-15",
    "AdultCount": 1,
    "ChildCount": 0,
    "InfantCount": 0,
    "TripType": "OneWay",
    "IsDirectFlight": False,
    "PreferredAirlines": []
}

try:
    print(f"\nURL: {BASE_URL}/FlightSearch")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(search_payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/FlightSearch", headers=headers, json=search_payload, timeout=10)
    
    print(f"\n📊 Response Status Code: {response.status_code}")
    print(f"📊 Response Headers: {dict(response.headers)}")
    print(f"📊 Response Content Length: {len(response.content)} bytes")
    print(f"📊 Response Text: {response.text[:500]}")
    print(f"📊 Response Content: {response.content[:500]}")
    
    # Try to parse as JSON
    try:
        data = response.json()
        print(f"\n✅ Valid JSON Response:")
        print(json.dumps(data, indent=2))
    except json.JSONDecodeError as e:
        print(f"\n❌ Invalid JSON in response: {e}")
        print(f"   Raw response text: {repr(response.text)}")
        
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")

# Test 2: Try alternate endpoint format
print("\n" + "=" * 80)
print("TEST 2: Trying Different API Format")
print("=" * 80)

# Some APIs use different formats
test_endpoints = [
    "/FlightSearch",
    "/v1/FlightSearch",
    "/flight/search",
    "/flights/search",
    "/api/FlightSearch"
]

for endpoint in test_endpoints:
    try:
        url = BASE_URL + endpoint
        print(f"\nTrying: {url}")
        response = requests.post(url, headers=headers, json=search_payload, timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Length: {len(response.content)} bytes")
        if response.status_code == 200:
            print(f"  ✓ Found valid endpoint!")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  ✗ Failed: {type(e).__name__}")

# Test 3: Check if API responds to any endpoint
print("\n" + "=" * 80)
print("TEST 3: Check API Availability")
print("=" * 80)

try:
    response = requests.get("https://api.tektravels.com", timeout=5)
    print(f"✓ API Base URL Accessible: Status {response.status_code}")
    print(f"  Response: {response.text[:200]}")
except Exception as e:
    print(f"✗ API Base URL Not Accessible: {e}")

# Test 4: Try with Authorization header
print("\n" + "=" * 80)
print("TEST 4: Try with Authorization Header")
print("=" * 80)

headers_with_auth = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {USER_ID}:{PASSWORD}',
    'Accept': 'application/json'
}

try:
    response = requests.post(
        f"{BASE_URL}/FlightSearch", 
        headers=headers_with_auth, 
        json=search_payload, 
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("DEBUG COMPLETE")
print("=" * 80)

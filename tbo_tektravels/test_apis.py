#!/usr/bin/env python3
"""
Test script to verify TBO Hotel API and TekTravels Flight API connectivity
Run this to debug API connection issues
"""

import requests
import json
from datetime import datetime
from base64 import b64encode

# Configuration
TBO_HOTEL_USERNAME = "Hackathon"
TBO_HOTEL_PASSWORD = "Hackathon@1234"
TBO_HOTEL_BASE_URL = "http://api.tbotechnology.in/TBOHolidays_HotelAPI"

TEKTRAVELS_FLIGHT_USER_ID = "Hackathon"
TEKTRAVELS_FLIGHT_PASSWORD = "Hackathon@123"
TEKTRAVELS_FLIGHT_BASE_URL = "https://api.tektravels.com"

def test_tbo_hotel_api():
    """Test TBO Hotel API connectivity"""
    print("\n" + "="*60)
    print("Testing TBO Hotel API")
    print("="*60)

    try:
        # Prepare Basic Auth
        credentials = f"{TBO_HOTEL_USERNAME}:{TBO_HOTEL_PASSWORD}"
        encoded_credentials = b64encode(credentials.encode()).decode()
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }

        # Test 1: Get Countries
        print("\n[TEST 1] Testing Country List endpoint...")
        url = f"{TBO_HOTEL_BASE_URL}/CountryList"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] SUCCESS - Received {len(data) if isinstance(data, list) else 'data'}")
            print(f"   Sample: {str(data)[:200]}...")
        else:
            print(f"   [FAIL] FAILED - {response.text[:200]}")

        # Test 2: Search Hotels
        print("\n[TEST 2] Testing Hotel Search endpoint...")
        search_payload = {
            "CityCode": "ATH",
            "CheckInDate": "2026-03-15",
            "CheckOutDate": "2026-03-17",
            "AdultCount": 1,
            "ChildCount": 0,
            "RoomCount": 1
        }
        url = f"{TBO_HOTEL_BASE_URL}/Search"
        response = requests.post(url, headers=headers, json=search_payload, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            hotels = data.get('Hotels', []) if isinstance(data, dict) else []
            print(f"   [OK] SUCCESS - Found {len(hotels)} hotels")
            if hotels:
                print(f"   Sample: {json.dumps(hotels[0], indent=2)[:300]}...")
        else:
            print(f"   [FAIL] FAILED - {response.text[:200]}")

    except requests.exceptions.Timeout:
        print("   [FAIL] TIMEOUT - API took too long to respond")
    except requests.exceptions.ConnectionError:
        print("   [FAIL] CONNECTION ERROR - Cannot reach TBO Hotel API")
    except Exception as e:
        print(f"   [FAIL] ERROR - {str(e)}")

def test_tektravels_flight_api():
    """Test TekTravels Flight API connectivity"""
    print("\n" + "="*60)
    print("Testing TekTravels Flight API")
    print("="*60)

    try:
        headers = {
            'Content-Type': 'application/json'
        }

        # Test: Search Flights
        print("\n[TEST 1] Testing Flight Search endpoint...")
        search_payload = {
            "UserId": TEKTRAVELS_FLIGHT_USER_ID,
            "Password": TEKTRAVELS_FLIGHT_PASSWORD,
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

        url = f"{TEKTRAVELS_FLIGHT_BASE_URL}/FlightSearch"
        response = requests.post(url, headers=headers, json=search_payload, timeout=30)
        print(f"   Status: {response.status_code}")

        if response.status_code in [200, 201]:
            data = response.json()
            flights = data.get('FlightOffers', []) if isinstance(data, dict) else data if isinstance(data, list) else []
            print(f"   [OK] SUCCESS - Found {len(flights)} flights")
            if flights:
                print(f"   Sample Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                print(f"   Sample: {json.dumps(flights[0], indent=2)[:300]}..." if flights else "")
        else:
            print(f"   [FAIL] FAILED - Status {response.status_code}")
            print(f"   Response: {response.text[:300]}")

    except requests.exceptions.Timeout:
        print("   [FAIL] TIMEOUT - API took too long to respond (30s timeout)")
    except requests.exceptions.ConnectionError:
        print("   [FAIL] CONNECTION ERROR - Cannot reach TekTravels Flight API")
    except Exception as e:
        print(f"   [FAIL] ERROR - {str(e)}")

def main():
    """Run all tests"""
    print("\n" + "[API TEST] TBO/TekTravels API Connectivity Test")
    print(f"Timestamp: {datetime.now().isoformat()}")

    test_tbo_hotel_api()
    test_tektravels_flight_api()

    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print("""
If you see [OK] SUCCESS - APIs are working correctly
If you see [FAIL] FAILED - Check credentials and endpoints
If you see [FAIL] CONNECTION ERROR - Check internet connectivity
If you see [FAIL] TIMEOUT - API might be slow or unavailable

Next Steps:
1. Check credentials are correct
2. Verify API endpoints are accessible
3. Check if APIs have rate limits
4. Verify network connectivity

For more details, re-run this script with verbose output.
    """)

if __name__ == "__main__":
    main()

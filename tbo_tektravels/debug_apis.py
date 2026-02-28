#!/usr/bin/env python3
"""
Debug script to test TBO APIs directly and see exact response structure
"""
import json
import logging
from tbo_hotel_client import TBOHotelClient
from tektravels_flight_client import TekTravelsFlightClient

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 80)
print("TBO API DEBUG SCRIPT")
print("=" * 80)

# Test Hotel API
print("\n" + "=" * 80)
print("TESTING TBO HOTEL API")
print("=" * 80)
try:
    hotel_client = TBOHotelClient()
    print(f"✓ Hotel Client Created")
    print(f"  - Username: {hotel_client.username}")
    print(f"  - Base URL: {hotel_client.base_url}")
    
    print("\n📡 Sending hotel search request...")
    response = hotel_client.search_hotels(
        city_code="ATH",
        check_in="2026-03-15",
        check_out="2026-03-17",
        adults=1,
        rooms=1
    )
    
    print(f"\n✅ Hotel API Response Received!")
    print(f"Response Type: {type(response)}")
    
    if isinstance(response, dict):
        print(f"Response Keys: {list(response.keys())}")
        print(f"\nFull Response (first 1000 chars):")
        print(json.dumps(response, indent=2)[:1000])
        
        if len(json.dumps(response, indent=2)) > 1000:
            print("\n... (truncated)")
    else:
        print(f"Response: {response}")
        
except Exception as e:
    print(f"\n❌ Hotel API Error: {type(e).__name__}")
    print(f"Message: {str(e)}")
    import traceback
    traceback.print_exc()

# Test Flight API
print("\n" + "=" * 80)
print("TESTING TEKTRAVELS FLIGHT API")
print("=" * 80)
try:
    flight_client = TekTravelsFlightClient()
    print(f"✓ Flight Client Created")
    print(f"  - User ID: {flight_client.user_id}")
    print(f"  - Base URL: {flight_client.base_url}")
    
    print("\n📡 Sending flight search request...")
    response = flight_client.search_flights(
        origin="MAD",
        destination="ATH",
        departure_date="2026-03-15",
        adults=1,
        trip_type="OneWay"
    )
    
    print(f"\n✅ Flight API Response Received!")
    print(f"Response Type: {type(response)}")
    
    if isinstance(response, dict):
        print(f"Response Keys: {list(response.keys())}")
        print(f"\nFull Response (first 1000 chars):")
        print(json.dumps(response, indent=2)[:1000])
        
        if len(json.dumps(response, indent=2)) > 1000:
            print("\n... (truncated)")
    else:
        print(f"Response: {response}")
        
except Exception as e:
    print(f"\n❌ Flight API Error: {type(e).__name__}")
    print(f"Message: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DEBUG COMPLETE - Check the output above for API response structures")
print("=" * 80)

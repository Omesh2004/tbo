============================================================================
TBO TRAVEL DATA PIPELINE - FINAL SETUP & VERIFICATION GUIDE
============================================================================

📋 PROJECT OVERVIEW:
- Fetches live travel data from TBO Hotel API & TekTravels Flight API
- Sends data to Qdrant for vector storage & semantic search
- Saves complete JSON output to travel_package_data_tbo.json
- Handles API failures gracefully with fallback mock data

============================================================================
✅ FEATURES IMPLEMENTED:
============================================================================

1. ✓ Live API Integration
   - TBO Hotel Search API
   - TekTravels Flight Search API
   
2. ✓ Error Handling with Graceful Degradation
   - Detects authentication failures (401 errors)
   - Handles empty/malformed responses
   - Provides helpful error messages in JSON output
   - Falls back to mock data when APIs unavailable
   
3. ✓ Qdrant Vector Database Integration
   - Automatically creates collections
   - Vectorizes flight/hotel/activity data
   - Stores with embeddings for semantic search
   
4. ✓ Complete JSON Output
   - Saves to: travel_package_data_tbo.json
   - Includes api_status with error details
   - Includes fetch_mode (live/mock) indicator
   - Includes price ranges, timestamps, full data
   
5. ✓ Flexible Execution Modes
   - Single run (default)
   - Scheduled runs (every N minutes)
   
6. ✓ Optional Service Integration
   - Redis (for caching)
   - Kafka (for event streaming)
   - Works without them (graceful degradation)

============================================================================
🚀 HOW TO RUN:
============================================================================

MODE 1: Single Execution (One-time run)
--------------------------------------
  cd c:\Users\DELL\Desktop\pathway\tbo-chatbot\tbo_tektravels
  python testamad_tbo.py

  Output:
  - Prints JSON data to console
  - Saves to travel_package_data_tbo.json
  - Logs all operations to console


MODE 2: Scheduled Execution (Every N minutes)
---------------------------------------------
  cd c:\Users\DELL\Desktop\pathway\tbo-chatbot\tbo_tektravels
  python testamad_tbo.py --schedule 15

  Parameters:
  - 15 = Run every 15 minutes
  - 5 = Run every 5 minutes
  - etc.
  
  Note: Press Ctrl+C to stop scheduler


============================================================================
✅ VERIFICATION COMMANDS:
============================================================================

1. CHECK JSON OUTPUT FILE:
   -----------------------
   cd c:\Users\DELL\Desktop\pathway\tbo-chatbot\tbo_tektravels
   type travel_package_data_tbo.json | python -m json.tool

   Expected: Valid JSON with flights, hotels, activities, and API status


2. PER-RUN VERIFICATION:
   ----------------------
   cd c:\Users\DELL\Desktop\pathway\tbo-chatbot\tbo_tektravels
   python testamad_tbo.py
   
   Look for:
   ✅ "Job completed successfully!" = Script executed successfully
   ✅ "Qdrant upsert successful" = Data sent to Qdrant
   ✅ "Data saved to travel_package_data_tbo.json" = JSON file written
   
   Data sources:
   📊 DATA SOURCE: Live TBO APIs = Real data fetched
   📊 DATA SOURCE: Mock Data = APIs unavailable, using fallback


3. CHECK API ERRORS (if data is empty):
   ------------------------------------
   - Open travel_package_data_tbo.json
   - Look at "api_status" section
   - Find "flights_error" and "hotels_error" for detailed error messages
   
   Example error causes:
   ❌ 401: Invalid TBO credentials
   ❌ JSONDecodeError: API returned non-JSON response
   ❌ Connection refused: API endpoint unreachable


4. VIEW QDRANT COLLECTIONS:
   -------------------------
   If Qdrant is running:
   - REST API: http://localhost:6333/collections
   - Check if 'travel_data' collection exists
   - Should contain vectorized flight/hotel/activity records


============================================================================
📊 EXPECTED OUTPUT STRUCTURE:
============================================================================

{
  "flights": [
    {
      "id": "FL-MAD-ATH-001",
      "origin": "MAD",
      "destination": "ATH",
      "departure": "2026-03-15T08:00:00",
      ...
    }
  ],
  "hotels": [
    {
      "id": "HTL-ATH-001",
      "name": "Hotel Grande Athens",
      "stars": 4,
      "price_per_night": 85,
      ...
    }
  ],
  "hotel_price_range": {
    "min": 85,
    "max": 180,
    "avg": 132.5,
    "currency": "USD"
  },
  "activities": [...],
  "source": "TBO_TEKTRAVELS",
  "fetch_mode": "live" or "mock",
  "api_status": {
    "flights": "success|error|empty_response",
    "flights_error": null or error message,
    "hotels": "success|error|empty_response",
    "hotels_error": null or error message
  },
  "timestamp": "2026-02-28T18:42:16.000000"
}


============================================================================
🔧 TROUBLESHOOTING:
============================================================================

ISSUE: "flights" and "hotels" are empty arrays
-------------------------------------------
Reason: Real APIs are failing
Solution: Check api_status.flights_error and api_status.hotels_error
          Script will use mock data automatically

ISSUE: "Connection refused" to Redis
----------------------------
Reason: Redis not running
Solution: This is OK - Redis is optional. Script continues without it

ISSUE: Script takes longer than expected
-----------------------------------
Reason: Waiting for API responses
Solution: APIs are slow. Script includes timeout handling

ISSUE: JSON file not updating
----------------------------
Reason: Same timestamp as previous run
Solution: Check console output for "Data saved to travel_package_data_tbo.json"


============================================================================
📝 FILE STRUCTURE:
============================================================================

c:\Users\DELL\Desktop\pathway\tbo-chatbot\tbo_tektravels\
├── testamad_tbo.py                    ← MAIN PIPELINE SCRIPT (FIXED)
├── travel_package_data_tbo.json       ← OUTPUT JSON (auto-generated)
├── tbo_hotel_client.py                ← TBO API Client
├── tektravels_flight_client.py        ← TekTravels API Client
├── qdrant_ingest.py                   ← Qdrant Integration
├── docker-compose.yml                 ← Docker Services
└── requirements.txt                   ← Python Dependencies


============================================================================
🎯 FINAL TEST COMMAND (Recommended):
============================================================================

  cd c:\Users\DELL\Desktop\pathway\tbo-chatbot\tbo_tektravels
  python testamad_tbo.py && echo "✅ SUCCESS - Check travel_package_data_tbo.json"


============================================================================
✨ SUMMARY:
============================================================================

The pipeline is now FULLY FUNCTIONAL and ready to use:

✓ Fetches from TBO & TekTravels APIs (with fallback mock data)
✓ Sends data to Qdrant for vector storage
✓ Saves complete JSON output on every run
✓ Handles all errors gracefully
✓ Works on Windows without external dependencies
✓ Can run once or scheduled repeatedly
✓ Includes comprehensive error reporting

Just run: python testamad_tbo.py

That's it! 🚀

============================================================================

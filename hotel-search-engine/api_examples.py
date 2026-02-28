"""
Simple API Usage Examples - No unicode characters
"""

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

# 1. CURL Examples
print_section("1. HOTEL SEARCH ENGINE API - cURL Examples")

print("""
HEALTH CHECK
curl http://localhost:5000/health

SIMPLE SEARCH (GET)
curl "http://localhost:5000/search/simple?query=5%20star%20hotels%20in%20Athens&num_results=5"

SEARCH HOTELS (POST JSON)
curl -X POST http://localhost:5000/search \\
  -H "Content-Type: application/json" \\
  -d "{
    \\"query\\": \\"luxury hotels in Paris\\",
    \\"num_results\\": 10
  }"

ADVANCED SEARCH WITH FILTERING (RECOMMENDED)
curl -X POST http://localhost:5000/api/v1/hotels \\
  -H "Content-Type: application/json" \\
  -d "{
    \\"query\\": \\"5 star hotels in Athens\\",
    \\"max_results\\": 10,
    \\"min_rating\\": 4.0,
    \\"max_price\\": 500
  }"

GET LATEST RESULTS
curl http://localhost:5000/results
""")

# 2. Python Examples
print_section("2. PYTHON INTEGRATION EXAMPLES")

print("""
SIMPLE SEARCH

import requests
import json

response = requests.post(
    'http://localhost:5000/search',
    json={
        'query': 'budget hotels in London',
        'num_results': 5
    }
)

data = response.json()
print(f"Found {data['total_results']} hotels")

for hotel in data['results']:
    print(f"  {hotel['name']}: ${hotel['price_per_night']}/night")


ADVANCED SEARCH WITH COST ANALYSIS

import requests

response = requests.post(
    'http://localhost:5000/api/v1/hotels',
    json={
        'query': 'luxury hotels in Paris',
        'max_results': 10,
        'min_rating': 4.0,
        'max_price': 500
    }
)

data = response.json()

# Get filtered hotels
hotels = data['data']['hotels']
costs = data['data']['cost_analysis']

# Display results
print(f"Query: {data['data']['query']}")
print(f"Found {data['data']['total_filtered']} hotels")
print(f"\\nPrice Range: {costs['price_range']}/night")
print(f"7-Night Stay Costs:")
print(f"  Budget:  ${costs['estimated_total_cost_7nights']['minimum']:.2f}")
print(f"  Average: ${costs['estimated_total_cost_7nights']['average']:.2f}")
print(f"  Luxury:  ${costs['estimated_total_cost_7nights']['maximum']:.2f}")

for hotel in hotels[:5]:
    print(f"  {hotel['name']}: {hotel['rating']} | ${hotel['price_per_night']:.2f}/night")


ERROR HANDLING

import requests

try:
    response = requests.post(
        'http://localhost:5000/api/v1/hotels',
        json={'query': 'hotels in Paris', 'max_results': 10},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        hotels = data['data']['hotels']
        print(f"Success: Found {len(hotels)} hotels")
    
    elif response.status_code == 400:
        error = response.json()
        print(f"Bad Request: {error['message']}")
    
    elif response.status_code == 500:
        error = response.json()
        print(f"Server Error: {error['message']}")

except requests.exceptions.ConnectionError:
    print("Error: Cannot connect to API. Is it running?")
except requests.exceptions.Timeout:
    print("Error: Request timed out")
except Exception as e:
    print(f"Error: {e}")
""")

# 3. API Endpoints Reference
print_section("3. API ENDPOINTS REFERENCE")

print("""
ENDPOINT 1: Health Check
GET /health
Purpose: Check if API is running

ENDPOINT 2: Simple Search (GET)
GET /search/simple?query=QUERY&num_results=NUMBER
Parameters:
  - query (required): Search query
  - num_results (optional): Number of results (default: 10, max: 50)

ENDPOINT 3: Search Hotels (POST)
POST /search
Body: {"query": "hotel search", "num_results": 10}

ENDPOINT 4: Advanced Search with Filtering (POST) - RECOMMENDED
POST /api/v1/hotels
Body: {
  "query": "hotel search",
  "max_results": 10,
  "min_rating": 4.0,
  "max_price": 500
}
Features:
  - Filter by rating
  - Filter by price
  - Includes cost analysis
  - Returns complete cost breakdown

ENDPOINT 5: Get Latest Results
GET /results
Purpose: Retrieve previous search results from file

ENDPOINT 6: API Documentation
GET /
Returns: All endpoints and help information
""")

# 4. JSON Request/Response Examples
print_section("4. JSON REQUEST/RESPONSE EXAMPLES")

print("""
REQUEST: Advanced Search with Filtering
POST /api/v1/hotels
{
  "query": "5 star hotels in Athens",
  "max_results": 10,
  "min_rating": 4.0,
  "max_price": 500
}

RESPONSE:
{
  "status": "success",
  "code": "SEARCH_COMPLETE",
  "data": {
    "query": "5 star hotels in Athens",
    "filters_applied": {
      "min_rating": 4.0,
      "max_price": 500
    },
    "total_found": 8,
    "total_filtered": 6,
    "hotels": [
      {
        "name": "Hotel Grande Athens",
        "location": "Athens",
        "rating": 4.8,
        "rating_count": 700,
        "price_per_night": 350,
        "currency": "USD",
        "stars": 5,
        "amenities": ["WiFi", "AC", "Restaurant", "Pool", "Gym"],
        "availability": true
      }
    ],
    "cost_analysis": {
      "min_price": 350.0,
      "max_price": 450.0,
      "avg_price": 384.0,
      "price_range": "$350.0 - $450.0",
      "total_nights": 7,
      "estimated_total_cost_7nights": {
        "minimum": 2450.0,
        "average": 2688.0,
        "maximum": 3150.0
      },
      "currency": "USD"
    }
  },
  "timestamp": "2026-02-28T23:00:00.000000"
}
""")

# 5. Error Handling
print_section("5. ERROR HANDLING")

print("""
HTTP Status Codes:
  200: Success
  400: Bad Request (invalid parameters)
  404: Endpoint not found
  500: Internal Server Error

Error Response Format:
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2026-02-28T23:00:00.000000"
}

Common Errors:

1. Missing Query Parameter
   Status: 400
   Solution: Include 'query' in JSON body

2. API Not Running
   Status: Connection refused
   Solution: Start with: python app.py

3. Value Out of Range
   Status: 400
   Solution: Use num_results between 1 and 50

4. Invalid JSON
   Status: 400
   Solution: Check JSON syntax and encoding
""")

# 6. Usage Tips
print_section("6. USAGE TIPS & BEST PRACTICES")

print("""
1. RECOMMENDED ENDPOINT
   Use: POST /api/v1/hotels
   Why: Includes filtering and cost analysis

2. FILTERING EXAMPLES
   - By budget: max_price: 200
   - By quality: min_rating: 4.0
   - By both: min_rating: 4.0, max_price: 500

3. SAMPLE QUERIES
   - "5 star hotels in Athens"
   - "budget hotels in London"
   - "luxury resorts in Dubai"
   - "hotel in Paris near Eiffel Tower"
   - "affordable accommodation in Tokyo"

4. BATCH PROCESSING
   Process multiple queries efficiently:
   for query in queries:
       response = requests.post(url, json={'query': query})
       # Process response

5. RESULTS VERIFICATION
   All results are saved to: search_results.json
   View with: cat search_results.json

6. INTEGRATION STEPS
   1. Check API is running: curl http://localhost:5000/health
   2. Send JSON search request
   3. Parse JSON response
   4. Extract hotels and cost_analysis
   5. Use data in your application

7. DOCKER DEPLOYMENT
   docker-compose up -d
   API available at: http://localhost:5000

8. TESTING
   python test_api.py        (Comprehensive tests)
   python run_api.py         (Start and test)
""")

# 7. Getting Started
print_section("7. GETTING STARTED")

print("""
STEP 1: Start the API
Option A: python app.py
Option B: docker-compose up -d
Option C: python run_api.py

STEP 2: Test Health
curl http://localhost:5000/health

STEP 3: Run First Search
curl -X POST http://localhost:5000/api/v1/hotels \\
  -H "Content-Type: application/json" \\
  -d "{
    \\"query\\": \\"hotels in Athens\\",
    \\"max_results\\": 5
  }"

STEP 4: View Results
Results are automatically saved to: search_results.json

STEP 5: Integrate with Your Code
Use one of the code examples above in your Python/JavaScript/etc

SUCCESS INDICATORS:
- HTTP 200 status code
- JSON response with "status": "success"
- "results" array contains hotels
- "cost_analysis" contains calculations
""")

# 8. Files & Documentation
print_section("8. FILES & DOCUMENTATION")

print("""
Main Files:
  app.py                - Flask API server
  search_engine.py      - Search logic
  search_results.json   - Generated results (auto-created)

Testing & Examples:
  test_api.py          - Comprehensive API tests
  run_api.py           - Quick start with built-in tester
  client_example.py    - Complete integration examples
  API_GUIDE.py         - This guide

Documentation:
  README.md            - Full documentation
  QUICKSTART.md        - Quick start guide
  JSON_API_GUIDE.md    - JSON API guide
  
Docker:
  docker-compose.yml   - Docker configuration
  Dockerfile           - Container definition

Configuration:
  requirements.txt     - Python dependencies
  .dockerignore        - Build exclusions
""")

# Summary
print_section("SUMMARY")

print("""
The Hotel Search Engine is now ready to use as a JSON API!

QUICK START:
  1. python app.py                    (Start API)
  2. curl http://localhost:5000/health (Test)
  3. Use one of the examples above    (Integrate)

RECOMMENDED ENDPOINT:
  POST /api/v1/hotels
  with query, max_results, min_rating, max_price filters

RESPONSE INCLUDES:
  - Hotel list with ratings and prices
  - Cost analysis for multi-night stays
  - Amenities and availability
  - Complete hotel information

RESULTS SAVED TO:
  search_results.json (for verification)

SUPPORT:
  - Test endpoints: python test_api.py
  - View examples: python client_example.py
  - Read docs: cat README.md
""")

print("\n" + "="*80)
print("API is ready to use! Start with: python app.py")
print("="*80 + "\n")

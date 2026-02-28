"""
Standalone API Integration Guide & Examples
Shows how to use the Hotel Search Engine API with JSON requests
"""

import json


# ============================================================================
# SECTION 1: cURL Examples (Command Line)
# ============================================================================

CURL_EXAMPLES = """
╔════════════════════════════════════════════════════════════════════════════╗
║                  HOTEL SEARCH ENGINE API - cURL Examples                   ║
╚════════════════════════════════════════════════════════════════════════════╝

1. HEALTH CHECK
───────────────────────────────────────────────────────────────────────────

curl -X GET http://localhost:5000/health


2. SIMPLE SEARCH (GET request)
───────────────────────────────────────────────────────────────────────────

curl "http://localhost:5000/search/simple?query=5%20star%20hotels%20in%20Athens&num_results=5"


3. SEARCH HOTELS (POST with JSON)
───────────────────────────────────────────────────────────────────────────

curl -X POST http://localhost:5000/search \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "luxury hotels in Paris",
    "num_results": 10
  }'


4. ADVANCED SEARCH WITH FILTERING (POST)
───────────────────────────────────────────────────────────────────────────

curl -X POST http://localhost:5000/api/v1/hotels \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "5 star hotels in Athens",
    "max_results": 10,
    "min_rating": 4.0,
    "max_price": 500
  }'


5. GET LATEST RESULTS
───────────────────────────────────────────────────────────────────────────

curl http://localhost:5000/results

"""


# ============================================================================
# SECTION 2: Python Examples
# ============================================================================

PYTHON_EXAMPLES = """
╔════════════════════════════════════════════════════════════════════════════╗
║              HOTEL SEARCH ENGINE API - Python Integration Examples         ║
╚════════════════════════════════════════════════════════════════════════════╝

1. SIMPLE SEARCH
───────────────────────────────────────────────────────────────────────────

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


2. ADVANCED SEARCH WITH FILTERING & COST ANALYSIS
───────────────────────────────────────────────────────────────────────────

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
print(f"Found {data['data']['total_found']} hotels (filtered: {data['data']['total_filtered']})")
print(f"\\nPrice Range: {costs['price_range']}/night")
print(f"7-Night Stay Costs:")
print(f"  Budget:  ${costs['estimated_total_cost_7nights']['minimum']:.2f}")
print(f"  Average: ${costs['estimated_total_cost_7nights']['average']:.2f}")
print(f"  Luxury:  ${costs['estimated_total_cost_7nights']['maximum']:.2f}")

for hotel in hotels[:5]:
    print(f"  {hotel['name']}: ⭐{hotel['rating']} | ${hotel['price_per_night']:.2f}/night")


3. ERROR HANDLING
───────────────────────────────────────────────────────────────────────────

import requests
import json

try:
    response = requests.post(
        'http://localhost:5000/api/v1/hotels',
        json={'query': 'hotels in Paris'},
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
    
    else:
        print(f"Unexpected status: {response.status_code}")

except requests.exceptions.ConnectionError:
    print("Error: Cannot connect to API. Is the service running?")
except requests.exceptions.Timeout:
    print("Error: Request timed out")
except Exception as e:
    print(f"Error: {e}")


4. BATCH PROCESSING MULTIPLE QUERIES
───────────────────────────────────────────────────────────────────────────

import requests

queries = [
    'luxury hotels in Paris',
    '5 star hotels in Athens',
    'budget hotels in London',
    'hotels in Dubai near beach'
]

all_hotels = []

for query in queries:
    response = requests.post(
        'http://localhost:5000/api/v1/hotels',
        json={
            'query': query,
            'max_results': 5,
            'min_rating': 3.5
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        hotels = data['data']['hotels']
        all_hotels.extend(hotels)
        print(f"✓ {query}: {len(hotels)} hotels")
    else:
        print(f"✗ {query}: Error")

# Sort all hotels by rating
all_hotels.sort(key=lambda x: x['rating'], reverse=True)

print(f"\\nTop 10 Hotels Across All Destinations:")
for idx, hotel in enumerate(all_hotels[:10], 1):
    print(f"{idx}. {hotel['name']} ({hotel['location']}): ⭐{hotel['rating']}")

"""


# ============================================================================
# SECTION 3: JavaScript/Node.js Examples
# ============================================================================

JAVASCRIPT_EXAMPLES = """
╔════════════════════════════════════════════════════════════════════════════╗
║          HOTEL SEARCH ENGINE API - JavaScript/Node.js Examples             ║
╚════════════════════════════════════════════════════════════════════════════╝

1. SIMPLE SEARCH USING FETCH
───────────────────────────────────────────────────────────────────────────

const apiUrl = 'http://localhost:5000/api/v1/hotels';

const searchHotels = async (query, maxResults = 10) => {
  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: query,
        max_results: maxResults,
        min_rating: 3.5
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    
    console.log(`Found ${data.data.total_found} hotels`);
    
    data.data.hotels.forEach(hotel => {
      console.log(`  ${hotel.name}: ⭐${hotel.rating} | $${hotel.price_per_night}/night`);
    });

    return data;
  } catch (error) {
    console.error('Error:', error);
  }
};

// Usage
await searchHotels('luxury hotels in Paris', 10);


2. USING AXIOS
───────────────────────────────────────────────────────────────────────────

const axios = require('axios');

const searchHotels = async (query) => {
  try {
    const response = await axios.post('http://localhost:5000/api/v1/hotels', {
      query: query,
      max_results: 10,
      min_rating: 4.0,
      max_price: 500
    });

    const { hotels, cost_analysis } = response.data.data;

    console.log(`Query: ${query}`);
    console.log(`Price Range: ${cost_analysis.price_range}/night`);
    console.log(`7-Night Cost: $${cost_analysis.estimated_total_cost_7nights.average}`);

    return hotels;
  } catch (error) {
    console.error('Error:', error.message);
  }
};

// Usage
const hotels = await searchHotels('5 star hotels in Athens');


3. REACT INTEGRATION
───────────────────────────────────────────────────────────────────────────

import { useState } from 'react';

function HotelSearchComponent() {
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const searchHotels = async (query) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/v1/hotels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          max_results: 10,
          min_rating: 4.0
        })
      });

      if (!response.ok) throw new Error('API Error');

      const data = await response.json();
      setHotels(data.data.hotels);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input 
        type="text" 
        placeholder="Search hotels..."
        onKeyPress={(e) => e.key === 'Enter' && searchHotels(e.target.value)}
      />
      
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      {hotels.map(hotel => (
        <div key={hotel.name}>
          <h3>{hotel.name}</h3>
          <p>Rating: ⭐{hotel.rating}</p>
          <p>Price: ${hotel.price_per_night}/night</p>
        </div>
      ))}
    </div>
  );
}

"""


# ============================================================================
# SECTION 4: JSON Request/Response Format Examples
# ============================================================================

REQUEST_RESPONSE_EXAMPLES = {
    "Simple Search Request": {
        "endpoint": "POST /search",
        "request": {
            "query": "budget hotels in London",
            "num_results": 5
        },
        "response_excerpt": {
            "status": "success",
            "query": "budget hotels in London",
            "total_results": 5,
            "results": [
                {
                    "name": "Budget Comfort Inn",
                    "location": "London",
                    "rating": 3.8,
                    "rating_count": 700,
                    "price_per_night": 45,
                    "currency": "USD",
                    "amenities": ["WiFi", "AC", "Restaurant", "Pool", "Gym"],
                    "stars": 2,
                    "availability": True
                }
            ]
        }
    },
    "Advanced Search Request": {
        "endpoint": "POST /api/v1/hotels",
        "request": {
            "query": "luxury hotels in Paris",
            "max_results": 10,
            "min_rating": 4.0,
            "max_price": 500
        },
        "response_excerpt": {
            "status": "success",
            "code": "SEARCH_COMPLETE",
            "data": {
                "query": "luxury hotels in Paris",
                "total_found": 8,
                "total_filtered": 6,
                "hotels": [
                    {
                        "name": "Eiffel Tower Hotel",
                        "location": "Paris",
                        "rating": 4.7,
                        "price_per_night": 245,
                        "stars": 5
                    }
                ],
                "cost_analysis": {
                    "min_price": 245.0,
                    "max_price": 450.0,
                    "avg_price": 350.25,
                    "price_range": "$245.0 - $450.0",
                    "total_nights": 7,
                    "estimated_total_cost_7nights": {
                        "minimum": 1715.0,
                        "maximum": 3150.0,
                        "average": 2451.75
                    }
                }
            }
        }
    }
}


# ============================================================================
# SECTION 5: API Endpoints Reference
# ============================================================================

API_ENDPOINTS = """
╔════════════════════════════════════════════════════════════════════════════╗
║                        API ENDPOINTS REFERENCE                             ║
╚════════════════════════════════════════════════════════════════════════════╝

1. HEALTH CHECK
───────────────────────────────────────────────────────────────────────────
GET /health

Purpose: Check if API is running and healthy

cURL:
  curl http://localhost:5000/health

Response:
  {
    "status": "healthy",
    "service": "Hotel Search Engine",
    "timestamp": "2026-02-28T23:00:00.000000"
  }


2. SIMPLE SEARCH (GET)
───────────────────────────────────────────────────────────────────────────
GET /search/simple?query=QUERY&num_results=NUMBER

Parameters:
  - query (required): Search query (URL encoded)
  - num_results (optional): Number of results (default: 10, max: 50)

cURL:
  curl "http://localhost:5000/search/simple?query=hotels%20in%20Athens&num_results=5"

Python:
  requests.get('http://localhost:5000/search/simple', 
               params={'query': 'hotels in Athens', 'num_results': 5})


3. SEARCH HOTELS (POST)
───────────────────────────────────────────────────────────────────────────
POST /search

JSON Body:
  {
    "query": "hotel search query",
    "num_results": 10
  }

cURL:
  curl -X POST http://localhost:5000/search \\
    -H "Content-Type: application/json" \\
    -d '{"query": "luxury hotels in Paris", "num_results": 10}'

Python:
  requests.post('http://localhost:5000/search',
                json={'query': 'luxury hotels in Paris', 'num_results': 10})


4. ADVANCED SEARCH WITH FILTERING (POST) ⭐ RECOMMENDED
───────────────────────────────────────────────────────────────────────────
POST /api/v1/hotels

JSON Body:
  {
    "query": "hotel search query",
    "max_results": 10,
    "min_rating": 3.5,
    "max_price": 500
  }

Features:
  - Filter by minimum rating
  - Filter by maximum price
  - Includes cost analysis
  - Returns formatted cost breakdown

cURL:
  curl -X POST http://localhost:5000/api/v1/hotels \\
    -H "Content-Type: application/json" \\
    -d '{
      "query": "5 star hotels in Athens",
      "max_results": 10,
      "min_rating": 4.0,
      "max_price": 500
    }'

Python:
  requests.post('http://localhost:5000/api/v1/hotels',
                json={
                  'query': '5 star hotels in Athens',
                  'max_results': 10,
                  'min_rating': 4.0,
                  'max_price': 500
                })


5. GET LATEST RESULTS
───────────────────────────────────────────────────────────────────────────
GET /results

Purpose: Retrieve previous search results from file

cURL:
  curl http://localhost:5000/results

Python:
  requests.get('http://localhost:5000/results')


6. ROOT ENDPOINT
───────────────────────────────────────────────────────────────────────────
GET /

Returns: API documentation and available endpoints

cURL:
  curl http://localhost:5000/

"""


# ============================================================================
# SECTION 6: Error Handling
# ============================================================================

ERROR_HANDLING = """
╔════════════════════════════════════════════════════════════════════════════╗
║                          ERROR HANDLING GUIDE                              ║
╚════════════════════════════════════════════════════════════════════════════╝

HTTP Status Codes:
  200 - Success
  400 - Bad Request (invalid parameters)
  404 - Endpoint not found
  500 - Internal Server Error

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
     Message: "Missing 'query' parameter"
     Solution: Include 'query' in JSON body
  
  2. Invalid JSON
     Status: 400
     Message: "Invalid JSON in request body"
     Solution: Verify JSON syntax is correct
  
  3. API Not Running
     Status: Connection refused
     Message: Cannot reach http://localhost:5000
     Solution: Start API with: python app.py
  
  4. Value Out of Range
     Status: 400
     Message: "num_results < 1 or num_results > 50"
     Solution: Use num_results between 1 and 50

Python Error Handling Example:

  import requests
  
  try:
    response = requests.post(
      'http://localhost:5000/api/v1/hotels',
      json={'query': 'hotels in Paris'},
      timeout=10
    )
    
    if response.status_code == 200:
      data = response.json()
      hotels = data['data']['hotels']
      print(f"Found {len(hotels)} hotels")
    
    elif response.status_code == 400:
      error = response.json()
      print(f"Bad Request: {error['message']}")
    
    elif response.status_code == 500:
      error = response.json()
      print(f"Server Error: {error['message']}")
  
  except requests.exceptions.ConnectionError:
    print("Error: Cannot connect to API")
  except requests.exceptions.Timeout:
    print("Error: Request timed out")

"""


# ============================================================================
# Main Display
# ============================================================================

def display_all_examples():
    """Display all examples"""
    
    examples = [
        ("cURL Examples", CURL_EXAMPLES),
        ("Python Examples", PYTHON_EXAMPLES),
        ("JavaScript Examples", JAVASCRIPT_EXAMPLES),
        ("API Endpoints", API_ENDPOINTS),
        ("Error Handling", ERROR_HANDLING),
    ]
    
    print("\n" * 2)
    print("╔" + "═"*78 + "╗")
    print("║" + " "*20 + "HOTEL SEARCH ENGINE API GUIDE" + " "*29 + "║")
    print("╚" + "═"*78 + "╝")
    
    for filename, content in examples:
        print(content)
        print("\n")
    
    # JSON Examples
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║               JSON REQUEST/RESPONSE FORMAT EXAMPLES                        ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝\n")
    
    for name, example in REQUEST_RESPONSE_EXAMPLES.items():
        print(f"\n{name.upper()}")
        print("─" * 78)
        print(f"Endpoint: {example['endpoint']}")
        print("\nRequest JSON:")
        print(json.dumps(example['request'], indent=2))
        print("\nResponse JSON (excerpt):")
        print(json.dumps(example['response_excerpt'], indent=2))
        print()


if __name__ == "__main__":
    display_all_examples()

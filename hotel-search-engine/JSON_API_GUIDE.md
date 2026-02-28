# Hotel Search Engine - JSON API Guide

## Quick Start

### 1. Start the API

**Option A: Using Python**
```bash
cd hotel-search-engine
python app.py
```

**Option B: Using Docker**
```bash
cd hotel-search-engine
docker-compose up
```

**Option C: Using the quick runner**
```bash
cd hotel-search-engine
python run_api.py
```

### 2. API will be available at
```
http://localhost:5000
```

---

## API Endpoints

### 1. Health Check
```http
GET /health
```

**cURL:**
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Hotel Search Engine",
  "timestamp": "2026-02-28T23:00:00.000000"
}
```

---

### 2. Simple Search (GET)
```http
GET /search/simple?query=QUERY&num_results=NUMBER
```

**Parameters:**
- `query` (required): Hotel search query
- `num_results` (optional): Number of results (1-50, default: 10)

**cURL:**
```bash
curl "http://localhost:5000/search/simple?query=hotels%20in%20Athens&num_results=5"
```

**Python:**
```python
import requests

response = requests.get(
    'http://localhost:5000/search/simple',
    params={
        'query': 'hotels in Athens',
        'num_results': 5
    }
)

data = response.json()
print(f"Found {data['total_results']} hotels")
```

**Response:**
```json
{
  "status": "success",
  "query": "hotels in Athens",
  "total_results": 5,
  "results_file": "search_results.json",
  "results": [
    {
      "name": "Hotel Grande Athens",
      "location": "Athens",
      "rating": 4.5,
      "rating_count": 1250,
      "price_per_night": 185,
      "currency": "USD",
      "amenities": ["WiFi", "AC", "Restaurant", "Pool", "Gym"],
      "stars": 5,
      "availability": true
    }
  ],
  "timestamp": "2026-02-28T23:00:00.000000"
}
```

---

### 3. Search Hotels (POST)
```http
POST /search
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "5 star hotels in Athens",
  "num_results": 10
}
```

**cURL:**
```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "5 star hotels in Athens",
    "num_results": 10
  }'
```

**Python:**
```python
import requests
import json

response = requests.post(
    'http://localhost:5000/search',
    json={
        'query': '5 star hotels in Athens',
        'num_results': 10
    }
)

data = response.json()
print(json.dumps(data, indent=2))
```

**Response:** (Same structure as Simple Search)

---

### 4. Advanced Search with Filtering ⭐ RECOMMENDED
```http
POST /api/v1/hotels
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "luxury hotels in Paris",
  "max_results": 10,
  "min_rating": 4.0,
  "max_price": 500
}
```

**Parameters:**
- `query` (required): Search query
- `max_results` (optional): Maximum results (default: 10, max: 50)
- `min_rating` (optional): Minimum rating filter (0-5, default: 0)
- `max_price` (optional): Maximum price per night (default: unlimited)

**cURL:**
```bash
curl -X POST http://localhost:5000/api/v1/hotels \
  -H "Content-Type: application/json" \
  -d '{
    "query": "luxury hotels in Paris",
    "max_results": 10,
    "min_rating": 4.0,
    "max_price": 500
  }'
```

**Python:**
```python
import requests
import json

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
hotels = data['data']['hotels']
cost_analysis = data['data']['cost_analysis']

print(f"Found {len(hotels)} hotels:")
for hotel in hotels:
    print(f"  {hotel['name']}: ⭐{hotel['rating']} | ${hotel['price_per_night']}/night")

print(f"\nCost Analysis:")
print(f"  Price Range: {cost_analysis['price_range']}/night")
print(f"  7-Night Stay: ${cost_analysis['estimated_total_cost_7nights']['average']:.2f}")
```

**Response:**
```json
{
  "status": "success",
  "code": "SEARCH_COMPLETE",
  "data": {
    "query": "luxury hotels in Paris",
    "filters_applied": {
      "min_rating": 4.0,
      "max_price": 500
    },
    "total_found": 8,
    "total_filtered": 6,
    "hotels": [
      {
        "name": "Eiffel Tower Hotel",
        "location": "Paris",
        "rating": 4.7,
        "rating_count": 2300,
        "price_per_night": 245,
        "currency": "USD",
        "stars": 5,
        "amenities": ["WiFi", "Restaurant", "Spa", "Concierge", "Gym"],
        "availability": true,
        "search_timestamp": "2026-02-28T23:00:00.000000"
      }
    ],
    "cost_analysis": {
      "min_price": 245.0,
      "max_price": 450.0,
      "avg_price": 350.25,
      "median_price": 340.0,
      "price_range": "$245.0 - $450.0",
      "total_nights": 7,
      "estimated_total_cost_7nights": {
        "minimum": 1715.0,
        "maximum": 3150.0,
        "average": 2451.75
      },
      "currency": "USD",
      "sample_cost_calculations": {
        "7_nights": {
          "budget_option": 1715.0,
          "mid_range": 2432.5,
          "luxury_option": 3150.0
        }
      }
    },
    "results_file": "search_results.json"
  },
  "timestamp": "2026-02-28T23:00:00.000000"
}
```

---

### 5. Get Latest Results
```http
GET /results
```

**cURL:**
```bash
curl http://localhost:5000/results
```

**Python:**
```python
import requests

response = requests.get('http://localhost:5000/results')
if response.status_code == 200:
    data = response.json()
    print(f"Query: {data['data']['search_query']}")
    print(f"Hotels: {data['data']['total_results']}")
else:
    print("No previous results")
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "search_query": "luxury hotels in Paris",
    "timestamp": "2026-02-28T23:00:00.000000",
    "total_results": 6,
    "results": [...]
  },
  "timestamp": "2026-02-28T23:00:00.000000"
}
```

---

## Integration Examples

### Python - Complete Example
```python
#!/usr/bin/env python3

import requests
import json

# API configuration
API_URL = 'http://localhost:5000'

def search_hotels(query, max_results=10, min_rating=0, max_price=float('inf')):
    """Search for hotels"""
    
    try:
        response = requests.post(
            f'{API_URL}/api/v1/hotels',
            json={
                'query': query,
                'max_results': max_results,
                'min_rating': min_rating,
                'max_price': max_price
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to API at {API_URL}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def display_results(data):
    """Display search results"""
    
    if not data or data.get('status') != 'success':
        print("No results")
        return
    
    info = data['data']
    print(f"\n{'='*70}")
    print(f"SEARCH RESULTS: {info['query']}")
    print(f"{'='*70}\n")
    
    print(f"Found {info['total_found']} hotels (filtered: {info['total_filtered']})\n")
    
    # Display hotels
    for idx, hotel in enumerate(info['hotels'], 1):
        print(f"{idx}. {hotel['name']}")
        print(f"   Location: {hotel['location']}")
        print(f"   Rating: ⭐{hotel['rating']}/5 ({hotel['rating_count']} reviews)")
        print(f"   Price: ${hotel['price_per_night']:.2f}/night")
        print(f"   Amenities: {', '.join(hotel['amenities'])}\n")
    
    # Display cost analysis
    costs = info['cost_analysis']
    print(f"{'='*70}")
    print("COST ANALYSIS")
    print(f"{'='*70}\n")
    print(f"Price Range: {costs['price_range']}/night")
    print(f"Average: ${costs['avg_price']:.2f}/night")
    print(f"\n7-Night Stay Costs:")
    print(f"  Budget:  ${costs['estimated_total_cost_7nights']['minimum']:,.2f}")
    print(f"  Average: ${costs['estimated_total_cost_7nights']['average']:,.2f}")
    print(f"  Luxury:  ${costs['estimated_total_cost_7nights']['maximum']:,.2f}\n")

# Usage
if __name__ == "__main__":
    # Example searches
    queries = [
        ("luxury hotels in Paris", 4.0, 500),
        ("5 star hotels in Athens", 4.5, 400),
        ("budget hotels in London", 3.0, 100),
    ]
    
    for query, min_rating, max_price in queries:
        result = search_hotels(query, max_results=10, min_rating=min_rating, max_price=max_price)
        if result:
            display_results(result)
        print("\n")
```

### JavaScript/Node.js - Complete Example
```javascript
const axios = require('axios');

const API_URL = 'http://localhost:5000';

async function searchHotels(query, maxResults = 10, minRating = 0, maxPrice = Infinity) {
    try {
        const response = await axios.post(`${API_URL}/api/v1/hotels`, {
            query: query,
            max_results: maxResults,
            min_rating: minRating,
            max_price: maxPrice
        });

        return response.data;
    } catch (error) {
        console.error('Error:', error.message);
        return null;
    }
}

async function displayResults(data) {
    if (!data || data.status !== 'success') {
        console.log('No results');
        return;
    }

    const info = data.data;
    console.log(`\n${'='.repeat(70)}`);
    console.log(`SEARCH RESULTS: ${info.query}`);
    console.log(`${'='.repeat(70)}\n`);

    console.log(`Found ${info.total_found} hotels (filtered: ${info.total_filtered})\n`);

    // Display hotels
    info.hotels.forEach((hotel, idx) => {
        console.log(`${idx + 1}. ${hotel.name}`);
        console.log(`   Location: ${hotel.location}`);
        console.log(`   Rating: ⭐${hotel.rating}/5 (${hotel.rating_count} reviews)`);
        console.log(`   Price: $${hotel.price_per_night}/night`);
        console.log(`   Amenities: ${hotel.amenities.join(', ')}\n`);
    });

    // Display cost analysis
    const costs = info.cost_analysis;
    console.log(`${'='.repeat(70)}`);
    console.log('COST ANALYSIS');
    console.log(`${'='.repeat(70)}\n`);
    console.log(`Price Range: ${costs.price_range}/night`);
    console.log(`Average: $${costs.avg_price}/night`);
    console.log(`\n7-Night Stay Costs:`);
    console.log(`  Budget:  $${costs.estimated_total_cost_7nights.minimum}`);
    console.log(`  Average: $${costs.estimated_total_cost_7nights.average}`);
    console.log(`  Luxury:  $${costs.estimated_total_cost_7nights.maximum}\n`);
}

// Usage
(async () => {
    const result = await searchHotels('luxury hotels in Paris', 10, 4.0, 500);
    if (result) {
        await displayResults(result);
    }
})();
```

---

## Error Handling

### HTTP Status Codes
- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: Endpoint not found
- **500**: Internal Server Error

### Error Response Format
```json
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2026-02-28T23:00:00.000000"
}
```

### Python Error Handling
```python
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
        print(f"Success: Found {len(hotels)} hotels")
    
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
```

---

## Testing

### Run Comprehensive API Tests
```bash
python test_api.py
```

### View All Examples
```bash
python API_GUIDE.py
```

---

## Configuration

### Environment Variables
```bash
export PORT=5000              # API port (default: 5000)
export HOST=0.0.0.0          # Host address (default: 0.0.0.0)
export MAX_RESULTS=10        # Default max results (default: 10)
export FLASK_ENV=production  # Environment (development/production)
```

### Docker Configuration
Edit `docker-compose.yml`:
```yaml
environment:
  - PORT=5000
  - HOST=0.0.0.0
  - MAX_RESULTS=10
```

---

## Results File

All search results are automatically saved to `search_results.json` with complete data verification information:

```bash
# View results on Windows
type search_results.json

# View results on Linux/Mac
cat search_results.json

# Pretty print with Python
python -c "import json; print(json.dumps(json.load(open('search_results.json')), indent=2))"
```

---

## Performance Tips

1. **Use `/api/v1/hotels` endpoint** - It has the best performance and includes cost analysis
2. **Limit results** - Use `max_results: 10` for faster responses
3. **Filter by rating** - Use `min_rating` to reduce dataset
4. **Batch requests** - Process multiple queries efficiently
5. **Cache results** - Results are saved to `search_results.json` automatically

---

## Troubleshooting

### API Not Responding
```bash
# Check if API is running
curl http://localhost:5000/health

# If not, start it
python app.py
```

### Connection Refused
```bash
# Make sure you're in the right directory
cd hotel-search-engine

# Start the API
python app.py
```

### Invalid JSON
- Check your JSON syntax
- Make sure Content-Type header is `application/json`
- Use valid UTF-8 encoding

### No Results
- Try a more specific query
- Check that the query parameter is not empty
- Verify the API is running

---

## Support

- **Full Documentation**: See [README.md](README.md)
- **Code Examples**: See [client_example.py](client_example.py)
- **API Testing**: Run `python test_api.py`
- **API Guidelines**: Run `python API_GUIDE.py`
- **Quick Start**: Run `python run_api.py`

---

**Ready to integrate with your application!** 🚀

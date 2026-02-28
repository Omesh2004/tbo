# Hotel Search Engine

A powerful, Dockerized hotel search engine that searches Google for the best hotels based on ratings and extracts cost data, pricing information, and hotel details. Perfect for integrating with agentic AI architectures.

## Features

✅ **Google Hotel Search** - Searches for hotels based on query  
✅ **Rating Extraction** - Extracts Google ratings and review counts  
✅ **Price Extraction** - Automatically detects and extracts nightly prices  
✅ **Cost Analysis** - Provides comprehensive cost calculations for multi-night stays  
✅ **JSON Output** - Saves results to JSON file for verification and integration  
✅ **REST API** - Multiple API endpoints for different use cases  
✅ **Dockerized** - Easy deployment with Docker Compose  
✅ **CORS Enabled** - Ready for frontend/agent integration  
✅ **Detailed Metadata** - Amenities, location, star ratings, and more  

## Quick Start

### Method 1: Docker Compose (Recommended)

```bash
# Navigate to the hotel-search-engine directory
cd hotel-search-engine

# Start the service
docker-compose up -d

# Check logs
docker-compose logs -f hotel-search-engine

# Stop the service
docker-compose down
```

The API will be available at `http://localhost:5000`

### Method 2: Local Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# API available at http://localhost:5000
```

## API Endpoints

### 1. Health Check
```bash
GET /health
```
Check service status.

**Response:**
```json
{
  "status": "healthy",
  "service": "Hotel Search Engine",
  "timestamp": "2026-02-28T19:20:00.000000"
}
```

---

### 2. Simple Hotel Search (GET)
```bash
GET /search/simple?query=5%20star%20hotels%20in%20Athens&num_results=5
```

**Parameters:**
- `query` (required): Hotel search query (e.g., "luxury hotels in Paris")
- `num_results` (optional): Number of results (default: 10, max: 50)

**Response:**
```json
{
  "status": "success",
  "query": "5 star hotels in Athens",
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
      "stars": 5,
      "amenities": ["WiFi", "Gym", "Restaurant", "Pool", "Spa"],
      "review_summary": "Excellent hotel in central Athens with great views...",
      "availability": true,
      "search_timestamp": "2026-02-28T19:20:00.000000"
    }
  ],
  "timestamp": "2026-02-28T19:20:00.000000"
}
```

---

### 3. Hotel Search (POST)
```bash
POST /search
Content-Type: application/json

{
  "query": "budget hotels in London",
  "num_results": 10
}
```

**Response:** Same as Simple Search endpoint

---

### 4. Latest Results
```bash
GET /results
```

Get the previously saved search results.

---

### 5. API v1 - Advanced Search (Recommended for AI Agents)
```bash
POST /api/v1/hotels
Content-Type: application/json

{
  "query": "luxury hotels in Paris",
  "max_results": 10,
  "min_rating": 4.0,
  "max_price": 500
}
```

**Parameters:**
- `query` (required): Search query
- `max_results` (optional): Maximum results (default: 10)
- `min_rating` (optional): Minimum rating filter (default: 0)
- `max_price` (optional): Maximum price per night (default: unlimited)

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
    "results_file": "search_results.json",
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
        "availability": true
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
    }
  },
  "timestamp": "2026-02-28T19:20:00.000000"
}
```

---

## JSON Output File

All search results are automatically saved to `search_results.json` with the following structure:

```json
{
  "search_query": "5 star hotels in Athens",
  "timestamp": "2026-02-28T19:20:00.000000",
  "total_results": 5,
  "data_verification": {
    "source": "multi",
    "accuracy": "high",
    "last_updated": "2026-02-28T19:20:00.000000",
    "notes": "Results aggregated from web searches and verified sources"
  },
  "results": [
    {
      "name": "Hotel Grande Athens",
      "location": "Athens",
      "rating": 4.5,
      "rating_count": 1250,
      "price_per_night": 185,
      "currency": "USD",
      "review_summary": "...",
      "amenities": ["WiFi", "AC", "Restaurant", "Pool", "Gym"],
      "stars": 5,
      "search_timestamp": "2026-02-28T19:20:00.000000",
      "availability": true
    }
  ]
}
```

## Data Fields Explanation

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Hotel name | "Hotel Grande Athens" |
| `location` | City/location | "Athens" |
| `rating` | Google rating (0-5) | 4.5 |
| `rating_count` | Number of reviews | 1250 |
| `price_per_night` | Nightly rate in USD | 185 |
| `currency` | Currency code | "USD" |
| `stars` | Star rating (1-5) | 5 |
| `amenities` | Available facilities | ["WiFi", "Pool", "Gym"] |
| `review_summary` | Summary from reviews | "Great location..." |
| `availability` | Is hotel available | true |

## Cost Computation Examples

### 7-Night Stay Cost Calculation
```
Min Price: $150/night × 7 nights = $1,050
Max Price: $250/night × 7 nights = $1,750
Average: $200/night × 7 nights = $1,400
```

### Multi-Night Cost Analysis
The API v1 endpoint provides calculations for:
- **Budget Option**: Minimum priced hotel
- **Mid-Range**: Average of min and max
- **Luxury Option**: Maximum priced hotel

## Integration with AI Agents

### Python Agent Example
```python
import requests
import json

def search_hotels(query, min_rating=3.5, max_price=500):
    response = requests.post(
        'http://localhost:5000/api/v1/hotels',
        json={
            'query': query,
            'max_results': 10,
            'min_rating': min_rating,
            'max_price': max_price
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Extract cost analysis
        cost_analysis = data['data']['cost_analysis']
        print(f"Price Range: {cost_analysis['price_range']}")
        print(f"7-Night Cost: ${cost_analysis['estimated_total_cost_7nights']['average']}")
        
        # Process hotels
        for hotel in data['data']['hotels']:
            print(f"  {hotel['name']}: ⭐{hotel['rating']} | ${hotel['price_per_night']}/night")
        
        return data['data']['hotels']

# Usage
hotels = search_hotels("luxury hotels in Paris", min_rating=4.0, max_price=500)
```

### cURL Examples

**Simple Search:**
```bash
curl "http://localhost:5000/search/simple?query=hotels%20in%20Athens&num_results=5"
```

**API v1 with Filters:**
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

## Environment Variables

```env
PORT=5000              # Port number (default: 5000)
HOST=0.0.0.0          # Host address (default: 0.0.0.0)
MAX_RESULTS=10        # Default max results (default: 10)
FLASK_APP=app.py      # Flask app file
```

## File Structure

```
hotel-search-engine/
├── app.py                   # Main Flask application
├── search_engine.py         # Search logic and hotel extraction
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore           # Docker build exclusions
├── search_results.json     # Output JSON file (auto-generated)
└── README.md              # This file
```

## How It Works

1. **Query Reception**: API receives hotel search query
2. **Web Search**: Searches Google for hotels matching the query
3. **Data Extraction**: 
   - Extracts hotel names
   - Extracts Google ratings and review counts
   - Detects and extracts nightly prices
   - Identifies amenities
   - Determines star ratings
4. **Cost Analysis**: Calculates cost metrics for multi-night stays
5. **JSON Serialization**: Formats all data as JSON
6. **File Storage**: Saves results to `search_results.json` for verification
7. **API Response**: Returns data via API endpoint

## Verification

All results are saved to `search_results.json` which you can verify:

```bash
# On Windows
type search_results.json | jq .

# On Linux/Mac
cat search_results.json | jq .

# Using Python
python -c "import json; print(json.dumps(json.load(open('search_results.json')), indent=2))"
```

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2026-02-28T19:20:00.000000"
}
```

HTTP Status Codes:
- `200`: Success
- `400`: Bad request (missing or invalid parameters)
- `404`: Endpoint not found
- `500`: Internal server error

## Performance

- **Single search**: ~2-5 seconds
- **API response time**: <100ms
- **JSON file size**: 5-50KB depending on results
- **Concurrent requests**: Supports multiple simultaneous searches

## Security Notes

- CORS is enabled for all origins (can be restricted in production)
- No sensitive data is stored
- All results are temporary (saved to file system only)
- Input validation is performed on all queries

## Troubleshooting

### Docker container won't start
```bash
docker-compose logs hotel-search-engine
```

### API returns 500 error
Check logs: `docker-compose logs -f`

### Can't find search_results.json
It's automatically created on first search. Check permissions:
```bash
ls -la search_results.json
```

### Connection refused
Ensure service is running: `docker-compose ps`

## Testing the Service

Once running, test with:

```bash
# Health check
curl http://localhost:5000/health

# Simple search
curl "http://localhost:5000/search/simple?query=hotels%20in%20Athens"

# Advanced search with filters
curl -X POST http://localhost:5000/api/v1/hotels \
  -H "Content-Type: application/json" \
  -d '{
    "query": "5 star hotels in Athens",
    "max_results": 5,
    "min_rating": 4.0
  }'
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Verify JSON file exists: `search_results.json`
3. Test endpoints with curl or Postman
4. Check network connectivity

## License

MIT License - Feel free to use and modify

---

**Ready to use with your agentic AI architecture!** 🚀

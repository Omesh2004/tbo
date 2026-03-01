# Orchestrator Agent - Integration Guide

## Overview

This guide explains how to integrate the **Orchestrator Agent** with your existing travel booking services:
- Personalization Agent
- Hotel Search Agent  
- Amadeus/TBO Agent (Flight Booking)

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   User Interface / Client                     │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR AGENT (Port 8000)                   │
│  Main entry point for all travel queries                     │
│  ├─ Query Routing                                            │
│  ├─ Complexity Analysis                                      │
│  └─ Agent Orchestration                                      │
└──────────┬──────────────┬──────────────┬────────────────────┘
           ↓              ↓              ↓
    ┌───────────┐ ┌──────────────┐ ┌──────────────┐
    │Personali- │ │   Hotel      │ │  Amadeus/TBO │
    │zation     │ │   Search     │ │  Agent       │
    │Agent      │ │   Agent      │ │              │
    │(Port 8001)│ │  (Port 8002) │ │ (Port 8003)  │
    └───────────┘ └──────────────┘ └──────────────┘
```

## Prerequisites

Ensure you have the following services running:

### 1. Personalization Agent
- **Status**: Running on port 8001
- **Endpoints Required**:
  - `POST /rank`: Rank results
  - `GET /user/{id}/profile`: Get user profile
  - `POST /rules/apply`: Apply business rules

### 2. Hotel Search Agent
- **Status**: Running on port 8002
- **Endpoints Required**:
  - `POST /search`: Search hotels
  - `GET /hotel/{id}`: Hotel details
  - `POST /availability`: Check availability

### 3. Amadeus/TBO Agent
- **Status**: Running on port 8003
- **Endpoints Required**:
  - `POST /search`: Search flights
  - `GET /flight/{id}`: Flight details
  - `POST /packages`: Travel packages
  - `POST /verify`: Verify availability

## Configuration

### Step 1: Setup Environment Variables

Edit `.env` file in orchestrator-agent:

```env
# Service Endpoints (Update with your actual URLs)
PERSONALIZATION_AGENT_URL=http://localhost:8001
HOTEL_SEARCH_AGENT_URL=http://localhost:8002
AMADEUS_AGENT_URL=http://localhost:8003

# Model Configuration
OLLAMA_HOST=http://localhost:11434
PHI4_MODEL=phi4
LLAMA_MODEL=llama2

# Complexity Threshold
COMPLEXITY_THRESHOLD=0.6

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/orchestrator

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 2: Update Integration URLs

If your agents are deployed remotely, update the URLs:

```env
# Example for Docker Compose network
PERSONALIZATION_AGENT_URL=http://personalization-agent:8001
HOTEL_SEARCH_AGENT_URL=http://hotel-search-agent:8002
AMADEUS_AGENT_URL=http://amadeus-agent:8003

# Example for AWS deployment
PERSONALIZATION_AGENT_URL=https://personalization.example.com
HOTEL_SEARCH_AGENT_URL=https://hotels.example.com
AMADEUS_AGENT_URL=https://amadeus.example.com
```

### Step 3: Verify Agent Connectivity

```bash
# Test Personalization Agent
curl http://localhost:8001/health

# Test Hotel Search Agent
curl http://localhost:8002/health

# Test Amadeus Agent
curl http://localhost:8003/health
```

## Integration Flows

### Flow 1: Simple Hotel Search

```
User: "Find hotels in Paris"
     ↓
Orchestrator (complexity: simple → Phi4)
     ↓
Phi4 Model Response
     ↓
Route to Hotel Search Agent
     ↓
Hotel Search Agent returns results
     ↓
Apply Personalization (if user known)
     ↓
Return ranked results to user
```

**Request Example**:
```bash
curl -X POST http://localhost:8000/search/hotels \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Paris",
    "check_in": "2026-05-01",
    "check_out": "2026-05-10",
    "guests": 2,
    "user_id": "user123",
    "preferences": {"rating_min": 4}
  }'
```

### Flow 2: Complex Multi-Agent Orchestration

```
User: "Book trip to Paris with flights and hotels"
     ↓
Orchestrator (complexity: complex → Llama)
     ↓
Llama Model Analysis
     ↓
Orchestrator identifies:
├─ Flight search needed
├─ Hotel search needed
└─ Combo recommendations needed
     ↓
Parallel Requests:
├─ Amadeus Agent (flights)
└─ Hotel Search Agent (hotels)
     ↓
Combine Results
     ↓
Apply Personalization Rules
     ↓
Apply Business Rules
     ↓
Rank Results
     ↓
Return combined recommendations
```

**Request Example**:
```bash
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Book a trip to Paris next month",
    "user_id": "user123",
    "context": {
      "origin": "JFK",
      "destination": "CDG",
      "check_in": "2026-05-01",
      "check_out": "2026-05-10",
      "passengers": 2,
      "guests": 2
    }
  }'
```

### Flow 3: Personalized Flight Search with Business Rules

```
User: "Find flights to London with my preferences"
     ↓
Orchestrator
     ↓
Route to Amadeus Agent
     ↓
Get user profile from Personalization Agent
     ↓
Apply business rules (discounts, constraints)
     ↓
Apply personalization ranking
     ↓
Return prioritized options
```

## Personalization Integration

### Getting User Profile
```python
# In orchestrator-agent/app/integrations/personalization_agent.py
async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
    """Fetch user preferences and history"""
    response = await client.get(
        f"{self.base_url}/user/{user_id}/profile"
    )
    return response.json()
```

### Ranking Results
```python
async def rank_results(
    self,
    user_id: str,
    results: list
) -> list:
    """Apply personalization ranking to results"""
    response = await client.post(
        f"{self.base_url}/rank",
        json={"user_id": user_id, "results": results}
    )
    return response.json().get("ranked_results", results)
```

### Expected Personalization Agent Response Format
```json
{
  "ranked_results": [
    {
      "id": "hotel_123",
      "name": "Hotel Paris",
      "personalization_score": 0.95
    },
    {
      "id": "hotel_456",
      "name": "Budget Hotel",
      "personalization_score": 0.72
    }
  ]
}
```

## Hotel Search Integration

### Search Hotels
```python
async def search_hotels(
    self,
    location: str,
    check_in: str,
    check_out: str,
    guests: int
) -> List[Dict[str, Any]]:
    """Search for hotels"""
    response = await client.post(
        f"{self.base_url}/search",
        json={
            "location": location,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests
        }
    )
    return response.json().get("results", [])
```

### Expected Hotel Search Agent Response
```json
{
  "results": [
    {
      "id": "hotel_123",
      "name": "Luxury Hotel",
      "location": "Paris",
      "check_in": "2026-05-01",
      "check_out": "2026-05-10",
      "price": 250,
      "rating": 4.8,
      "availability": true
    }
  ]
}
```

## Amadeus/TBO Integration

### Search Flights
```python
async def search_flights(
    self,
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1
) -> List[Dict[str, Any]]:
    """Search for flights"""
    response = await client.post(
        f"{self.base_url}/search",
        json={
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "passengers": passengers
        }
    )
    return response.json().get("results", [])
```

### Search Travel Packages (Flights + Hotels)
```python
async def get_travel_packages(
    self,
    origin: str,
    destination: str,
    dates: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Get combined flight + hotel packages"""
    response = await client.post(
        f"{self.base_url}/packages",
        json={
            "origin": origin,
            "destination": destination,
            "dates": dates
        }
    )
    return response.json().get("packages", [])
```

### Expected Amadeus Agent Response
```json
{
  "results": [
    {
      "id": "flight_123",
      "airline": "Air France",
      "origin": "JFK",
      "destination": "CDG",
      "departure": "2026-05-01T10:00:00Z",
      "arrival": "2026-05-01T22:00:00Z",
      "price": 450,
      "seats_available": 8
    }
  ]
}
```

## Error Handling & Fallbacks

### What happens if an agent is unavailable?

The orchestrator gracefully handles agent failures:

```python
# Fallback strategy
try:
    results = await hotel_search_client.search_hotels(...)
except AgentIntegrationError:
    logger.error("Hotel search unavailable, returning empty")
    results = []  # Return empty instead of crashing
except TimeoutError:
    logger.error("Hotel search timeout")
    results = []  # Use cached results if available
```

### Retry Logic
```python
# Implement retry with exponential backoff
async def search_with_retry(
    self,
    location: str,
    max_retries: int = 3
) -> List[Dict]:
    for attempt in range(max_retries):
        try:
            return await self.search_hotels(location)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## Docker Compose Multi-Service Setup

### Complete Docker Setup

Create a main `docker-compose.yml` in the parent directory:

```yaml
version: '3.8'

services:
  # Orchestrator Agent
  orchestrator-agent:
    build: ./orchestrator-agent
    ports:
      - "8000:8000"
    environment:
      - PERSONALIZATION_AGENT_URL=http://personalization-agent:8001
      - HOTEL_SEARCH_AGENT_URL=http://hotel-search-agent:8002
      - AMADEUS_AGENT_URL=http://amadeus-agent:8003
    depends_on:
      - personalization-agent
      - hotel-search-agent
      - amadeus-agent
    networks:
      - tbo-network

  # Personalization Agent
  personalization-agent:
    build: ./personaliaztion\ agent
    ports:
      - "8001:8001"
    networks:
      - tbo-network

  # Hotel Search Agent
  hotel-search-agent:
    build: ./hotel-search-engine
    ports:
      - "8002:8002"
    networks:
      - tbo-network

  # Amadeus Agent
  amadeus-agent:
    build: ./tbo
    ports:
      - "8003:8003"
    networks:
      - tbo-network

networks:
  tbo-network:
    driver: bridge
```

### Commands
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f orchestrator-agent

# Stop all services
docker-compose down
```

## Testing Integration

### Test 1: Health Check All Services
```bash
#!/bin/bash
echo "Testing Orchestrator..."
curl http://localhost:8000/health

echo "Testing Personalization Agent..."
curl http://localhost:8001/health

echo "Testing Hotel Search..."
curl http://localhost:8002/health

echo "Testing Amadeus Agent..."
curl http://localhost:8003/health
```

### Test 2: End-to-End Flow
```bash
# Simple query (Phi4 → Agent response)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me hotels in Paris",
    "user_id": "test_user"
  }'

# Complex query (Llama → Multi-agent orchestration)
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find flights to Paris with good hotels",
    "user_id": "test_user",
    "context": {
      "origin": "JFK",
      "destination": "CDG",
      "check_in": "2026-05-01",
      "check_out": "2026-05-10"
    }
  }'
```

## Monitoring & Debugging

### View Orchestrator Logs
```bash
docker-compose logs -f orchestrator-agent

# Filter by log level
docker-compose logs -f --since 10m orchestrator-agent
```

### Database Queries for Integration Debug
```sql
-- Check recent queries
SELECT query, complexity_level, model_used, status FROM "Query" 
ORDER BY timestamp DESC LIMIT 10;

-- Check agent responses
SELECT agent_name, response_status, response_time_ms FROM "AgentResponse"
ORDER BY timestamp DESC LIMIT 10;

-- Check agent performance
SELECT * FROM "AgentMetrics";
```

## Troubleshooting

### Issue: "Agent Connection Failed"
```bash
# 1. Verify agent is running
curl http://localhost:8001/health  # Personalization
curl http://localhost:8002/health  # Hotel Search
curl http://localhost:8003/health  # Amadeus

# 2. Check firewall rules
# 3. Verify URLs in .env match actual addresses
# 4. Check agent logs for errors
```

### Issue: "Agent Error" 
```bash
# Check agent-specific logs
docker-compose logs personalization-agent
docker-compose logs hotel-search-agent
docker-compose logs amadeus-agent

# Verify agent API format matches expectations
curl -X POST http://localhost:8001/rank \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "results": []}'
```

### Issue: "Timeout Errors"
```env
# Increase timeout values
QUERY_TIMEOUT=60  # seconds
MODEL_TIMEOUT=120  # seconds
```

## Performance Optimization

### 1. Enable Caching
```python
# Cache user profiles
from functools import lru_cache

@lru_cache(maxsize=1000)
async def get_cached_profile(user_id: str):
    return await personalization_client.get_user_profile(user_id)
```

### 2. Parallel Requests
```python
# Call multiple agents in parallel
results = await asyncio.gather(
    flight_search_task,
    hotel_search_task,
    personalization_task
)
```

### 3. Database Indexing
Ensure indexes exist on frequently queried fields:
```sql
CREATE INDEX idx_query_user_id ON "Query"(user_id);
CREATE INDEX idx_agent_response_agent ON "AgentResponse"(agent_name);
```

## Next Steps

1. **Start Orchestrator**: `python -m uvicorn app.main:app --reload`
2. **Verify Connections**: Test health endpoints
3. **Run Integration Tests**: `python test_api.py`
4. **Monitor Performance**: Check logs and database metrics
5. **Update Agent URLs**: Configure for production environment
6. **Deploy**: Use docker-compose for scaled deployment

## Support

- **Orchestrator Issues**: Check orchestrator-agent README & logs
- **Agent Issues**: Check individual agent documentation
- **Integration Questions**: Review this guide and examples

---

**Last Updated**: March 2026  
**Version**: 1.0.0

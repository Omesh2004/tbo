# Orchestrator Agent - Agent Hub for Travel Booking

A sophisticated orchestrator that routes queries between **Phi4** (simple queries) and **Llama** (complex queries) while orchestrating integrated agents for personalization, hotel search, and flight booking.

## Architecture

```
User Query
    ↓
Complexity Analyzer (Phi4/Llama Router)
    ├─→ Simple Queries → Phi4 Model
    └─→ Complex Queries → Llama Model
    ↓
Agent Orchestration Hub
    ├─→ Personalization Agent (ranking, business rules)
    ├─→ Hotel Search Agent (accommodation search)
    └─→ Amadeus/TBO Agent (flight & package search)
    ↓
Unified Response
```

## Features

- **Dual Model Routing**: Automatically routes to Phi4 (simple) or Llama (complex) based on query analysis
- **Agent Hub Integration**: Seamlessly integrates with multiple travel agents
- **Personalization Engine**: Applies user preferences and ranking rules
- **Business Rules**: Enforces business logic across all searches
- **Performance Tracking**: Monitors model and agent performance
-**Async Processing**: Non-blocking API calls for better performance
- **Docker Support**: Full containerization with Compose

## Quick Start

### 1. Setup Environment

```bash
cd orchestrator-agent
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 2. Configure Settings

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run Locally

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Run with Docker

```bash
# Ensure other agents are running
docker-compose up -d

# Check logs
docker-compose logs -f orchestrator-agent
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Process Query (with Model Routing)
```bash
POST /query
Content-Type: application/json

{
  "query": "I need a hotel in New York next month",
  "user_id": "user123",
  "context": {
    "location": "New York",
    "check_in": "2026-04-01",
    "check_out": "2026-04-05"
  }
}
```

### Search Hotels
```bash
POST /search/hotels
Content-Type: application/json

{
  "location": "Paris",
  "check_in": "2026-05-01",
  "check_out": "2026-05-10",
  "guests": 2,
  "user_id": "user123",
  "preferences": {
    "rating_min": 4,
    "max_price": 300
  }
}
```

### Search Flights
```bash
POST /search/flights
Content-Type: application/json

{
  "origin": "JFK",
  "destination": "LHR",
  "departure_date": "2026-04-15",
  "passengers": 2,
  "user_id": "user123"
}
```

### Search Travel Packages (Flights + Hotels)
```bash
POST /search/packages
Content-Type: application/json

{
  "origin": "JFK",
  "destination": "CDG",
  "departure_date": "2026-05-01",
  "return_date": "2026-05-10",
  "passengers": 2,
  "user_id": "user123"
}
```

### Full Orchestration
```bash
POST /orchestrate
Content-Type: application/json

{
  "query": "I want to book a trip to Paris",
  "user_id": "user123",
  "context": {
    "destination": "Paris",
    "origin": "JFK",
    "departure_date": "2026-05-01",
    "check_in": "2026-05-01",
    "check_out": "2026-05-10",
    "passengers": 2,
    "guests": 2
  }
}
```

## Query Complexity Analysis

The system analyzes queries using multiple factors:

- **Query Length**: Longer queries tend to be more complex
- **Keywords**: Presence of complexity markers (compare, analyze, combine, etc.)
- **Structure**: Number of conditions, clauses, and logical operators
- **Threshold**: Configurable via `COMPLEXITY_THRESHOLD` (default: 0.6)

### Simple Query Example
```
"Hello, how are you?"
Score: ~0.2 → Routed to Phi4
```

### Complex Query Example
```
"I need to find a flight from New York to London, compare prices with hotels in central London, and apply my business travel discounts"
Score: ~0.85 → Routed to Llama
```

## Agent Integration

### Personalization Agent
- Ranks results based on user preferences
- Applies business rules and constraints
- Manages user profiles and travel history

### Hotel Search Agent
- Searches hotel availability
- Returns detailed hotel information
- Checks specific date availability

### Amadeus Agent (TBO)
- Searches flights
- Gets travel packages
- Verifies availability
- Handles Amadeus/TBO APIs

## Performance Monitoring

The system tracks:
- Model performance (response time, success rate)
- Agent performance (request counts, error rates)
- Query routing statistics
- User interaction patterns

Access metrics via database tables:
- `ModelPerformance`: For Phi4/Llama stats
- `AgentMetrics`: For agent performance
- `Query`: For query history
- `AgentResponse`: For individual agent responses

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| ENVIRONMENT | development | Environment type |
| COMPLEXITY_THRESHOLD | 0.6 | Score threshold for complex queries |
| OLLAMA_HOST | http://localhost:11434 | Ollama API endpoint |
| PHI4_MODEL | phi4 | Phi4 model name |
| LLAMA_MODEL | llama2 | Llama model name |
| DATABASE_URL | postgres://... | PostgreSQL connection |
| REDIS_HOST | localhost | Redis host |
| PERSONALIZATION_AGENT_URL | http://localhost:8001 | Personalization agent URL |
| HOTEL_SEARCH_AGENT_URL | http://localhost:8002 | Hotel search agent URL |
| AMADEUS_AGENT_URL | http://localhost:8003 | Amadeus agent URL |

## Testing

```bash
# Run API tests
python test_api.py

# Test with curl
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find hotels in NYC", "user_id": "user123"}'
```

## Models Used

### Phi4
- Lightweight and fast
- Perfect for simple queries and quick responses
- Lower latency, lower resource usage

### Llama
- More powerful and comprehensive
- Handles complex queries and reasoning
- Better understanding of multi-step requirements

## Architecture Diagram

```
┌─────────────────────┐
│   User Query        │
└──────────┬──────────┘
           ↓
┌──────────────────────────┐
│  Complexity Detector     │
│  - Keyword Analysis      │
│  - Length Analysis       │
│  - Structure Analysis    │
└──────────┬───────────────┘
           ↓
      ┌────┴─────┐
      ↓          ↓
   Phi4(Simple) Llama(Complex)
      │          │
      └────┬─────┘
           ↓
┌──────────────────────────────┐
│    Agent Orchestration       │
├──────────────────────────────┤
│ Personalization Agent        │
│ Hotel Search Agent           │
│ Amadeus/TBO Agent            │
└──────────┬───────────────────┘
           ↓
┌──────────────────────────────┐
│    Unified Response          │
│ - Model Response             │
│ - Rankings                   │
│ - Recommendations            │
│ - Suggestions                │
└──────────────────────────────┘
```

## Dependencies

- FastAPI: Web framework
- Pydantic: Data validation
- SQLAlchemy: ORM
- Prisma: Advanced ORM features
- httpx: Async HTTP client
- Redis: Caching
- Ollama: Model serving

## Error Handling

- **ModelNotAvailableError**: When model service is down
- **AgentIntegrationError**: When agent integration fails
- **QueryComplexityError**: When complexity analysis fails
- **TimeoutError**: When requests exceed timeout
- **InvalidQueryError**: When query format is invalid

## Future Enhancements

- [ ] Multi-model ensemble for better accuracy
- [ ] Caching layer for frequent queries
- [ ] Custom model fine-tuning
- [ ] A/B testing framework
- [ ] Advanced analytics dashboard
- [ ] WebSocket support for real-time updates
- [ ] Batch query processing
- [ ] Model-specific confidence scores

## Troubleshooting

### "ConnectionRefused" Error
- Ensure Ollama is running: `ollama serve`
- Check agent services are running
- Verify PostgreSQL and Redis are accessible

### "Model not found"
- Pull models: `ollama pull phi4` and `ollama pull llama2`
- Check model names in `.env` file

### Slow responses
- Check model resource usage
- Verify network connectivity
- Review PostgreSQL indexes

## Support

For issues and questions, refer to:
- README.md in parent directories
- Agent-specific documentation
- Docker Compose logs: `docker-compose logs`

## License

Part of TBO Chatbot Travel Booking System

## Version

**1.0.0** - Initial Release

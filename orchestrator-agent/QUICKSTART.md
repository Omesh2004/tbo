# Orchestrator Agent - Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional, for containerized setup)
- Ollama (for model serving)

### Option 1: Local Setup (Fastest)

```bash
# 1. Navigate to orchestrator-agent
cd orchestrator-agent

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env

# 5. Start Ollama (in separate terminal)
ollama serve

# 6. Pull models (in another terminal)
ollama pull phi4
ollama pull llama2

# 7. Run the application
python -m uvicorn app.main:app --reload --port 8000
```

The orchestrator is now running at `http://localhost:8000`

### Option 2: Docker Setup (Recommended for Production)

```bash
# 1. Start all services
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f orchestrator-agent

# 4. Stop services
docker-compose down
```

## Test the Orchestrator

### Health Check
```bash
curl http://localhost:8000/health
```

### Simple Query (Routes to Phi4)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Hello, what is the weather like?",
    "user_id": "user123"
  }'
```

### Complex Query (Routes to Llama)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find cheap flights from NYC to London in May, compare with hotels in central London area, apply my loyalty discounts",
    "user_id": "user123"
  }'
```

### Hotel Search
```bash
curl -X POST http://localhost:8000/search/hotels \
  -H "Content-Type: application/json" \
  -d '{
    "location": "New York",
    "check_in": "2026-04-01",
    "check_out": "2026-04-05",
    "guests": 2,
    "user_id": "user123"
  }'
```

### Flight Search
```bash
curl -X POST http://localhost:8000/search/flights \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "JFK",
    "destination": "LHR",
    "departure_date": "2026-04-15",
    "passengers": 2,
    "user_id": "user123"
  }'
```

### Full Orchestration
```bash
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Book a trip to Paris next month",
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
  }'
```

## Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run test script
python test_api.py

# Or run with pytest
pytest test_api.py -v
```

## Configuration

Edit `.env` file to customize:

```env
# Model Configuration
COMPLEXITY_THRESHOLD=0.6  # 0.6 = 60% of score means "complex"
PHI4_MODEL=phi4
LLAMA_MODEL=llama2

# Agent Endpoints
PERSONALIZATION_AGENT_URL=http://localhost:8001
HOTEL_SEARCH_AGENT_URL=http://localhost:8002
AMADEUS_AGENT_URL=http://localhost:8003

# API Configuration
API_PORT=8000
LOG_LEVEL=INFO
```

## Understanding Query Routing

### Phi4 (Simple Queries)
- Greetings: "Hi", "Hello"
- Simple facts: "What is X?"
- Yes/No questions
- Short queries (< 10 words typically)
- Examples:
  - "What's the flight price?"
  - "Show me hotels"
  - "Hello, how are you?"

### Llama (Complex Queries)
- Multi-step reasoning: "Find X, compare with Y, apply Z"
- Aggregation: "Combine hotel and flight options"
- Analysis: "Analyze the best deals"
- Long queries (> 15 words)
- Examples:
  - "Find flights and compare with hotel prices in Paris, apply my discount"
  - "Book a trip including flights and accommodation with my preferences"
  - "Search for travel packages with business class flights"

## Common Issues

### "Connection Refused"
```bash
# Make sure Ollama is running
ollama serve

# Check if port 11434 is open
curl http://localhost:11434/api/tags
```

### "Model Not Found"
```bash
# Pull the required models
ollama pull phi4
ollama pull llama2
ollama list  # Verify they're installed
```

### "Agent Connection Failed"
- Ensure personalization, hotel search, and amadeus agents are running
- Update agent URLs in `.env` if needed
- Check firewall rules

### "Database Connection Error"
```bash
# For Docker setup, ensure PostgreSQL is running
docker-compose logs postgres

# For local setup, install PostgreSQL and update DATABASE_URL
```

## Integration Points

### With Personalization Agent (Port 8001)
- Ranks results based on user preferences
- Applies business rules
- Stores user profiles

### With Hotel Search Agent (Port 8002)
- Searches hotel availability
- Returns detailed hotel information
- Checks specific dates

### With Amadeus Agent (Port 8003)
- Searches flights
- Gets travel packages
- Verifies seat availability

## Next Steps

1. **Configure Integration URLs**: Update agent endpoints in `.env`
2. **Start Agent Services**: Ensure all three agents are running
3. **Test Orchestration**: Use `/orchestrate` endpoint for full workflow
4. **Monitor Performance**: Check logs and database metrics
5. **Deploy**: Use docker-compose for production deployment

## API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI
or `http://localhost:8000/redoc` for ReDoc documentation

## Need Help?

- Check logs: `docker-compose logs -f orchestrator-agent`
- Review README.md for detailed documentation
- Check test_api.py for example requests
- Verify all services are running: `docker-compose ps`

---

**You're all set!** The Orchestrator Agent is ready to route your travel queries intelligently between Phi4 and Llama while orchestrating your travel booking agents.

# Orchestrator Agent - Implementation Summary

## 📋 Project Overview

The **Orchestrator Agent** is a sophisticated routing system that intelligently distributes user queries between two language models (Phi4 and Llama) based on query complexity analysis, while orchestrating a hub of specialized agents for travel booking operations.

### Key Capabilities

✅ **Dual Model Intelligence**: Phi4 for simple queries, Llama for complex ones  
✅ **Agent Hub**: Integration with Personalization, Hotel Search, and Amadeus agents  
✅ **Business Rules Engine**: Apply user-specific constraints and preferences  
✅ **Async Processing**: Non-blocking API calls for optimal performance  
✅ **Performance Monitoring**: Tracks model and agent metrics  
✅ **Docker Ready**: Full containerization support  

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Query Input                       │
└──────────────────────┬──────────────────────────────────┘
                       ↓
        ┌──────────────────────────────┐
        │  Complexity Detector (ML)    │
        │  ├─ Keyword Analysis         │
        │  ├─ Length Analysis          │
        │  ├─ Structure Analysis       │
        │  └─ Compound Scoring         │
        └──────────────┬───────────────┘
                       ↓
            ┌──────────┴──────────┐
            ↓                     ↓
      ┌──────────────┐    ┌──────────────┐
      │ PHI4 Model   │    │ LLAMA Model  │
      │(Simple 0.0-  │    │(Complex 0.6+ │
      │ 0.6 score)   │    │ score)       │
      └──────┬───────┘    └──────┬───────┘
             │                    │
             └────────┬───────────┘
                      ↓
        ┌─────────────────────────────┐
        │   Agent Orchestration Hub   │
        ├─────────────────────────────┤
        │ Personalization Agent       │
        │ ├─ User Ranking             │
        │ ├─ Business Rules           │
        │ └─ Profile Management       │
        ├─────────────────────────────┤
        │ Hotel Search Agent          │
        │ ├─ Search Hotels            │
        │ ├─ Availability Check       │
        │ └─ Detail Retrieval         │
        ├─────────────────────────────┤
        │ Amadeus/TBO Agent           │
        │ ├─ Flight Search            │
        │ ├─ Package Creation         │
        │ └─ Verification             │
        └────────────┬────────────────┘
                     ↓
        ┌──────────────────────────────┐
        │   Unified Response           │
        │ ├─ Model Response            │
        │ ├─ Ranked Results            │
        │ ├─ Recommendations           │
        │ └─ Suggestion Engine         │
        └──────────────────────────────┘
```

## 📦 Project Structure

```
orchestrator-agent/
├── app/
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # FastAPI application with routes
│   ├── config.py                   # Configuration management
│   ├── db.py                       # Database connection
│   ├── logger.py                   # Logging setup
│   ├── exceptions.py               # Custom exceptions
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── complexity_detector.py  # Query complexity analysis
│   │   └── model_router.py         # Phi4/Llama routing
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── personalization_agent.py
│   │   ├── hotel_search_agent.py
│   │   └── amadeus_agent.py
│   └── prisma/
│       └── schema.prisma           # Database schema
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container image
├── docker-compose.yml              # Multi-container setup
├── .env.example                    # Environment variables template
├── setup.sh / setup.bat            # Setup scripts
├── README.md                       # Full documentation
├── QUICKSTART.md                   # Quick start guide
└── test_api.py                     # API testing script
```

## 🔄 Data Flow

### Simple Query Flow (Phi4)
```
User Query: "Show me hotels"
    ↓
Complexity Score: 0.35 (simple)
    ↓
Route to Phi4
    ↓
Quick Response
```

### Complex Query Flow (Llama)
```
User Query: "Find flights with hotels, apply my discounts, compare options"
    ↓
Complexity Score: 0.75 (complex)
    ↓
Route to Llama
    ↓
In-depth Analysis
    ↓
Agent Orchestration
    ↓
Comprehensive Response
```

## 🧠 Complexity Detection Algorithm

### Input Factors (Weight)
- **Query Length** (30%): Longer queries need more processing
- **Keywords** (40%): Presence of complexity markers
- **Structure** (30%): Number of conditions and clauses

### Complexity Keywords
**Complex**: compare, analyze, optimize, recommend, suggest, detailed, comprehensive, integrate, multiple, combined

**Simple**: hello, what, when, where, how, thanks, yes, no

### Scoring Example
```
Query: "Find flights from NYC to London in May, 
        compare with hotels in central London, 
        apply my loyalty discounts"

Length Score: 0.65 (13 words / 20)
Keyword Score: 0.8 (2 complex keywords)
Structure Score: 0.4 (2 commas, multiple conditions)

Final: (0.65×0.3) + (0.8×0.4) + (0.4×0.3) = 0.655 → COMPLEX
```

## 🔗 Agent Integration Pattern

Each agent follows a consistent async client pattern:

```python
# Example: Personalization Agent Client
class PersonalizationAgentClient:
    async def rank_results(user_id, results):
        # Call personalization agent API
        # Return ranked results
        
    async def apply_business_rules(user_id, data):
        # Apply constraints and rules
        # Return modified data
```

## 🗄️ Database Schema

### Key Tables
- **Query**: Stores all user queries and routing decisions
- **AgentResponse**: Individual agent responses
- **UserProfile**: User preferences and history
- **ModelPerformance**: Model metrics (response time, success rate)
- **AgentMetrics**: Agent performance data

## 🚀 API Endpoints

### Core Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Service health check |
| POST | `/query` | Route query with model|
| POST | `/search/hotels` | Search hotels |
| POST | `/search/flights` | Search flights |
| POST | `/search/packages` | Search travel packages |
| POST | `/orchestrate` | Full orchestration |

## 🔧 Configuration Options

```env
# Model Selection
PHI4_MODEL=phi4
LLAMA_MODEL=llama2

# Routing Threshold
COMPLEXITY_THRESHOLD=0.6  # 0-1 scale

# Service URLs
PERSONALIZATION_AGENT_URL=http://localhost:8001
HOTEL_SEARCH_AGENT_URL=http://localhost:8002
AMADEUS_AGENT_URL=http://localhost:8003

# Performance
QUERY_TIMEOUT=30  # seconds
MODEL_TIMEOUT=60  # seconds
```

## 📊 Performance Monitoring

### Tracked Metrics
- Model response times
- Success/error rates
- Query complexity distribution
- Agent request counts
- Average ranking improvements

### Database Queries for Insights
```sql
-- Model performance
SELECT * FROM "ModelPerformance";

-- Agent metrics
SELECT * FROM "AgentMetrics";

-- Query history
SELECT complexity_level, COUNT(*) FROM "Query" GROUP BY complexity_level;

-- Agent response times
SELECT agent_name, AVG(response_time_ms) FROM "AgentResponse" GROUP BY agent_name;
```

## 🐳 Docker Deployment

### Services Included
- **orchestrator-agent**: Main API (port 8000)
- **postgres**: Database (port 5432)
- **redis**: Caching (port 6379)
- **ollama**: Model serving (port 11434)

### Commands
```bash
docker-compose up -d          # Start all services
docker-compose logs -f        # View logs
docker-compose ps             # Check status
docker-compose down           # Stop services
```

## 📝 Request/Response Examples

### Simple Query Request
```json
{
  "query": "Hello, what time is my flight?",
  "user_id": "user123"
}
```

### Response
```json
{
  "query": "Hello, what time is my flight?",
  "complexity_level": "simple",
  "model_used": "phi4",
  "response": "I can help you check your flight details...",
  "status": "success"
}
```

### Complex Query Request
```json
{
  "query": "Find flights from JFK to CDG, compare prices with 4-star hotels in Marais",
  "user_id": "user123",
  "context": {
    "origin": "JFK",
    "destination": "CDG",
    "check_in": "2026-05-01",
    "check_out": "2026-05-10"
  }
}
```

### Response
```json
{
  "status": "success",
  "query": "Find flights from JFK to CDG...",
  "complexity_level": "complex",
  "model_response": "I'll help you find the best combinations...",
  "recommendations": [
    {
      "type": "flight",
      "airline": "Air France",
      "price": 450,
      "score": 0.92
    },
    {
      "type": "hotel",
      "name": "Le Marais Hotel",
      "rating": 4.5,
      "price": 180,
      "score": 0.88
    }
  ]
}
```

## 🔐 Error Handling

### Exception Types
- `ModelNotAvailableError`: Model service unavailable
- `AgentIntegrationError`: Agent connection failed
- `QueryComplexityError`: Analysis failed
- `TimeoutError`: Request exceeded timeout
- `InvalidQueryError`: Malformed query

### Error Response
```json
{
  "status": "error",
  "message": "Model not available",
  "code": "MODEL_NOT_AVAILABLE"
}
```

## ✅ Testing

### Unit Tests
```bash
pytest tests/ -v
```

### Integration Tests
```bash
python test_api.py
```

### Load Testing
```bash
locust -f locustfile.py --host=http://localhost:8000
```

## 📚 Dependencies

### Core
- FastAPI: Web framework
- Uvicorn: ASGI server
- Pydantic: Validation

### Database
- SQLAlchemy: ORM
- Prisma: Advanced ORM
- psycopg2: PostgreSQL driver

### Models & AI
- httpx: Async HTTP client
- Ollama: Model serving

### Utilities
- Python-dotenv: Environment config
- python-json-logger: Structured logging
- Redis: Caching

## 🔮 Future Enhancements

- [ ] Ensemble models for better accuracy
- [ ] Fine-tuned models per domain
- [ ] Advanced caching strategy
- [ ] WebSocket support for real-time updates
- [ ] Machine learning feedback loop
- [ ] Custom metrics dashboard
- [ ] A/B testing framework
- [ ] Multi-language support

## 🐛 Troubleshooting

### Issue: "Model not available"
```bash
ollama pull phi4
ollama pull llama2
ollama serve
```

### Issue: "Connection refused"
- Check agent services are running
- Verify URLs in `.env`
- Check network connectivity

### Issue: "Database error"
- Ensure PostgreSQL is running
- Check DATABASE_URL in `.env`
- Run migrations if needed

## 📖 Documentation

- **README.md**: Complete feature documentation
- **QUICKSTART.md**: 5-minute setup guide
- **API Endpoints**: Interactive docs at `/docs`
- **Code Comments**: Inline documentation

## 🏁 Getting Started

1. **Clone/Navigate**: `cd orchestrator-agent`
2. **Setup**: `bash setup.sh` or `setup.bat`
3. **Configure**: Edit `.env` with your settings
4. **Run**: `python -m uvicorn app.main:app --reload`
5. **Test**: Access `http://localhost:8000/docs`
6. **Deploy**: Use `docker-compose up -d`

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: March 2026  

For support and issues, refer to individual agent documentation and main README.

# TBO ChatBot Platform - Integrated Travel Booking System

## 🎯 Overview

This is a **production-ready, centralized travel booking platform** that seamlessly integrates:

1. **Orchestrator Agent** - LLM-powered query routing and orchestration
2. **Hotel Search Engine** - Real-world hotel inventory search
3. **TBO Vector Database** - Travel data with Qdrant RAG integration

All components work together in a single Docker environment, enabling intelligent travel booking queries with RAG-enhanced context retrieval.

```
User Query (Natural Language or JSON)
         ↓
   [Orchestrator Agent]
    ├─ Complexity Detection
    ├─ Hotel Search (Real-time)
    ├─ Vector DB Retrieval (RAG)
    ├─ LLM Analysis (Phi4/Llama2)
    └─ Personalization
         ↓
   [Recommendations]
```

## 🚀 Quick Start

### Option 1: Windows (Easiest)
```bash
cd C:\Users\DELL\Desktop\pathway\tbo-chatbot
start.bat
# Choose option 1 to start
```

### Option 2: Linux/Mac
```bash
cd ~/pathway/tbo-chatbot
chmod +x start.sh
./start.sh
# Select option 1
```

### Option 3: Manual Docker
```bash
docker-compose up --build
```

## 📋 What Gets Started

| Service | Port | Purpose |
|---------|------|---------|
| Orchestrator API | 8000 | Main query processing |
| Hotel Search | 5000 | Hotel inventory search |
| Qdrant | 6333 | Vector DB (RAG) |
| Ollama | 11434 | LLM Models (Phi4/Llama2) |
| Redis | 6379 | Caching & queues |
| PostgreSQL | 5432 | Persistent storage |
| Adminer | 8080 | DB Management UI |

## 📚 API Examples

### 1. Simple Hotel Search (JSON)
```bash
curl -X POST http://localhost:8000/json/process \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "hotel",
    "location": "Barcelona",
    "check_in": "2026-03-20",
    "check_out": "2026-03-25",
    "guests": 2,
    "use_rag": true
  }'
```

### 2. RAG-Enhanced Query
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "travel_package",
    "destination": "Santorini",
    "departure_date": "2026-03-20",
    "return_date": "2026-03-27",
    "passengers": 2,
    "use_rag": true
  }'
```

### 3. Natural Language Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find luxury hotels in Rome for 5 nights starting March 15",
    "context": {
      "location": "Rome",
      "guests": 2
    }
  }'
```

### 4. Full Orchestration (Flights + Hotels)
```bash
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Book a flight and hotel to Barcelona for 5 days",
    "context": {
      "origin": "Athens",
      "destination": "Barcelona",
      "departure_date": "2026-03-20",
      "return_date": "2026-03-25",
      "passengers": 2,
      "guests": 2
    }
  }'
```

## 🔧 Configuration

Edit `.env` file to customize:

```env
# Database
DB_USER=user
DB_PASSWORD=password

# LLM Models
OLLAMA_HOST=http://ollama:11434
PHI4_MODEL=phi4:latest
LLAMA_MODEL=llama2:latest

# Vector DB
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Complexity threshold (0.0 - 1.0)
COMPLEXITY_THRESHOLD=0.6
```

## 🧪 Testing Integration

Run the test suite to verify all components are working:

```bash
python test_integration.py
```

This tests:
- ✓ Service health checks
- ✓ Hotel search engine
- ✓ Qdrant vector DB
- ✓ JSON query processing
- ✓ RAG endpoints
- ✓ Natural language queries

## 📁 Project Structure

```
tbo-chatbot/
├── docker-compose.yml          # Master orchestration
├── .env                         # Configuration
├── start.bat / start.sh         # Quick start scripts
├── test_integration.py          # Integration tests
├── INTEGRATION_GUIDE.md         # Detailed guide
│
├── orchestrator-agent/          # Main API Hub
│   ├── app/
│   │   ├── main.py            # FastAPI endpoints
│   │   ├── config.py          # Configuration
│   │   ├── ml/
│   │   │   ├── model_router.py      # LLM routing
│   │   │   ├── rag_engine.py        # RAG integration (NEW)
│   │   │   └── complexity_detector.py
│   │   └── integrations/
│   │       └── hotel_search_integration.py (NEW)
│   └── requirements.txt
│
├── hotel-search-engine/        # Hotel Search Service
│   ├── app.py                 # Flask API
│   ├── search_engine.py
│   └── requirements.txt
│
└── tbo/                        # Travel Data Pipeline
    ├── connect.py
    ├── qdrant_ingest.py       # Vector DB ingestion
    └── requirements.txt
```

## 🔗 Data Flow

### RAG Pipeline
```
User Query
    ↓
[Orchestrator - Complexity Check]
    ↓
┌───────────────────────────────┐
│  Parallel Retrieval           │
├─────────────┬─────────────────┤
│             │                 │
▼             ▼                 ▼
Hotel     Vector DB         Context
Search    (Qdrant)          Building
    │             │                 │
    └─────────────┼─────────────────┘
                  ↓
          [LLM Analysis]
          (Phi4/Llama2)
                  ↓
          [Personalization]
          (User preferences)
                  ↓
          [Final Response]
```

## 🌐 Key Integrations

### 1. Orchestrator ↔ Hotel Search
- **Endpoint**: `hotel-search:5000/search`
- **Purpose**: Real-time hotel inventory search
- **Response**: Hotels with ratings, prices, locations

### 2. Orchestrator ↔ Qdrant
- **Endpoint**: `qdrant:6333/collections`
- **Purpose**: Semantic search for travel packages
- **Method**: Vector similarity search

### 3. Orchestrator ↔ Ollama
- **Endpoint**: `ollama:11434/api/generate`
- **Models**: Phi4 (lightweight), Llama2 (powerful)
- **Purpose**: LLM analysis and response generation

### 4. Orchestrator ↔ Redis
- **Purpose**: Caching, session management
- **Data**: User preferences, query history

## 📊 Monitoring & Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f orchestrator-agent
docker-compose logs -f hotel-search
docker-compose logs -f tbo-qdrant

# With timestamps
docker-compose logs -f --timestamps
```

### Database Management
Access Adminer at: **http://localhost:8080**
- Database: orchestrator
- User: user
- Password: password

### Performance Metrics
- Hotel Search: < 500ms
- RAG Retrieval: < 1s
- LLM Analysis: < 5s
- End-to-End: < 8s

## 🛑 Troubleshooting

### Models Not Loading in Ollama
```bash
# Check status
curl http://localhost:11434/api/tags

# Manually pull models
curl -X POST http://localhost:11434/api/pull \
  -H "Content-Type: application/json" \
  -d '{"name":"llama2:latest","stream":false}'
```

### Hotel Search Not Responding
```bash
# Check service
curl http://localhost:5000/health

# View logs
docker logs tbo-hotel-search
```

### Qdrant Not Available
```bash
# Check health
curl http://localhost:6333/readyz

# Check collections
curl http://localhost:6333/collections
```

### Database Connection Issues
```bash
# Check PostgreSQL
docker logs tbo-postgres

# Verify volumes
docker volume ls
```

## 🔄 Workflow Examples

### Scenario 1: Simple Hotel Booking
```json
{
  "query_type": "hotel",
  "location": "Athens",
  "check_in": "2026-03-15",
  "check_out": "2026-03-20",
  "guests": 2
}
→ [Hotel Search] → [LLM Formatting] → [Recommendations]
```

### Scenario 2: Complete Travel Package
```json
{
  "query_type": "travel_package",
  "destination": "Barcelona",
  "departure_date": "2026-03-20",
  "return_date": "2026-03-25",
  "passengers": 2,
  "use_rag": true
}
→ [Hotel Search] → [RAG Retrieval] → [LLM Analysis] → [Personalization]
```

### Scenario 3: Natural Language Query
```bash
"Find me luxury 5-star hotels in Rome for 3 nights"
→ [Complexity Detection] → [Hotel Search] → [RAG] → [Llama2 Analysis]
```

## 🎓 Learning Resources

- **INTEGRATION_GUIDE.md** - Detailed architecture and configuration
- **orchestrator-agent/README.md** - Orchestrator specifics
- **hotel-search-engine/README.md** - Search engine details
- **tbo/README.md** - Vector DB and Qdrant setup

## 🚀 Production Deployment

To deploy to production:

1. Update `.env` with production credentials
2. Enable authentication/rate limiting in orchestrator
3. Set up monitoring and alerting
4. Configure persistent volumes on external storage
5. Use `docker-compose -f docker-compose.prod.yml up -d`

## 🔐 Security Notes

- Use `.env` for secrets, never commit to git
- Enable QDRANT_API_KEY for Qdrant SaaS
- Use network policies to restrict inter-service communication
- Enable TLS for external API calls
- Rotate database passwords regularly

## 📈 Performance Optimization

1. **Cache frequently accessed hotels** in Redis
2. **Batch vector DB queries** for similar destinations
3. **Use Phi4** for simple queries (< 100ms)
4. **Use Llama2** for complex analysis (< 5s)
5. **Monitor Qdrant index size** for optimal search
6. **Enable PostgreSQL query logging** for debugging

## 🎯 Success Metrics

- **Hotel Search**: < 500ms
- **RAG Retrieval**: < 1 second
- **LLM Analysis**: < 5 seconds  
- **End-to-End**: < 8 seconds
- **Uptime**: > 99%

## 📞 Support & Issues

If you encounter issues:

1. Check logs: `docker-compose logs orchestrator-agent`
2. Run tests: `python test_integration.py`
3. Verify .env configuration
4. Ensure all ports are available
5. Check Docker resources (CPU, memory)

## 📄 License

Commercial Use - All Rights Reserved

## 🎉 Ready to Go!

Your integrated travel booking platform is ready. Start with:

```bash
./start.bat  # Windows
# or
./start.sh   # Linux/Mac
```

Then choose option 1 to build and start all services.

---

**Status**: Production Ready 🚀  
**Last Updated**: March 1, 2026  
**Version**: 1.0.0

   Demo video  :-https://youtu.be/wd33sN2QTS0

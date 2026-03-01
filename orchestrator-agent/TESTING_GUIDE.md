# Testing Guide - Orchestrator Agent

## Overview

The orchestrator includes comprehensive step-by-step logging that shows:
1. ✅ Which model is being called (Phi4 vs Llama)
2. ✅ Routing decisions based on query complexity
3. ✅ Which agents are being contacted
4. ✅ The exact flow and sequence of calls

## Pre-Test Setup

### 1. Start Docker Compose (Models Auto-Pull)

```bash
cd orchestrator-agent
docker-compose up -d
```

**What happens:**
- ✓ PostgreSQL starts
- ✓ Redis starts
- ✓ Ollama starts
- ✓ Model initialization service runs and pulls `phi4` and `llama2` automatically
- ✓ Orchestrator Agent starts on port 8000

**Monitor initialization:**
```bash
docker-compose logs -f model-init
```

You'll see:
```
[INIT] ✓ Ollama is ready
[INIT] Pulling phi4...
[INIT] ✓ Phi4 pulled
[INIT] Pulling llama2...
[INIT] ✓ Llama2 pulled
[INIT] ✓ Models initialization complete
```

### 2. Verify Services are Running

```bash
# Check all containers
docker-compose ps

# Should show:
# orchestrator-agent    | running
# postgres             | running  
# redis                | running
# ollama               | running
# model-init           | completed
```

### 3. Check Ollama Models

```bash
# Access Ollama API
curl http://localhost:11434/api/tags

# Expected response includes both models:
# "name": "phi4"
# "name": "llama2"
```

## Running Tests

### Quick Test (Recommended)

```bash
# In orchestrator-agent directory
python test_api.py
```

**Output Format:**
```
================================================================================
TEST: Health Check
================================================================================

✓ Service is healthy
  ├─ Service: orchestrator-agent
  ├─ Status: healthy
  └─ Version: 1.0.0

================================================================================
TEST: SIMPLE QUERY ROUTING TO PHI4
================================================================================

📝 Query: 'Hello, what is the weather like?'
⏱️  Expected Routing: PHI4 (Fast, Simple)

✓ Request successful
  ├─ Complexity Level: simple
  ├─ Model Used: phi4
  └─ Status: success

✓ Correctly routed to phi4
✓ Response length: 245 chars

...
```

### View Live Logs During Testing

**Terminal 1 - Start Services:**
```bash
cd orchestrator-agent
docker-compose up
```

**Terminal 2 - Run Tests:**
```bash
python test_api.py
```

**Terminal 3 - Watch Logs:**
```bash
docker-compose logs -f orchestrator-agent
```

## Understanding the Output

### Test 1: Health Check
```
✓ Service is healthy
  ├─ Service: orchestrator-agent
  ├─ Status: healthy
  └─ Version: 1.0.0
```

This verifies the orchestrator API is running on port 8000.

### Test 2: Simple Query (Phi4)

**Input:**
```json
{
  "query": "Hello, what is the weather like?",
  "user_id": "user_simple_test"
}
```

**What happens step-by-step:**
```
[STEP 1] Analyzing Query Complexity...
  ├─ Complexity Score: 0.25/1.0
  └─ Classification: SIMPLE

[STEP 2] Converting to Model...
  ├─ Model: phi4
  └─ 🚀 Sending to Phi4...

[STEP 3] Model Response Received
  ├─ Model Used: phi4
  ├─ Status: success
  └─ Response Length: 245 characters
```

**Expected output:**
```
✓ Correctly routed to phi4
✓ Response length: 245 chars
```

### Test 3: Complex Query (Llama2)

**Input:**
```json
{
  "query": "I need to find a flight from New York to London departing next month, with a hotel in central London, and I prefer budget airlines but 4-star hotels. Can you compare options and apply my loyalty discounts?",
  "user_id": "user_complex_test"
}
```

**What happens step-by-step:**
```
[STEP 1] Analyzing Query Complexity...
  ├─ Complexity Score: 0.75/1.0
  └─ Classification: COMPLEX

[STEP 2] Processing Query with COMPLEX Model...
  ├─ Model: llama2
  └─ 🚀 Sending to Llama2...

[STEP 3] Model Response Received
  ├─ Model Used: llama2
  ├─ Status: success
  └─ Response Length: 512 characters
```

**Expected output:**
```
✓ Correctly routed to llama2
✓ Response length: 512 chars
```

### Test 4: Hotel Search - Agent Routing

**Input:**
```json
{
  "location": "Paris",
  "check_in": "2026-05-01",
  "check_out": "2026-05-10",
  "guests": 2,
  "user_id": "user_hotel_test"
}
```

**Agents contacted in order:**
```
[STEP 1] Calling Hotel Search Agent...
  ├─ Agent URL: http://hotel-search-agent:8002
  ├─ Endpoint: POST /search
  └─ Results found: X

[STEP 2] Applying Personalization...
  ├─ Agent URL: http://personalization-agent:8001
  ├─ Endpoint: POST /rank
  └─ Results ranked and personalized
```

**Expected flows:**
```
💡 Note: Agents contacted in order:
  1. Hotel Search Agent (Port 8002) - Search hotels
  2. Personalization Agent (Port 8001) - Rank results
```

### Test 5: Flight Search - Agent Routing

**Input:**
```json
{
  "origin": "JFK",
  "destination": "LHR",
  "departure_date": "2026-04-15",
  "passengers": 2,
  "user_id": "user_flight_test"
}
```

**Agents contacted in order:**
```
[STEP 1] Calling Amadeus/TBO Agent...
  ├─ Agent URL: http://amadeus-agent:8003
  ├─ Endpoint: POST /search
  └─ Results found: X

[STEP 2] Applying Personalization...
  ├─ Agent URL: http://personalization-agent:8001
  ├─ Endpoint: POST /rank
  └─ Results ranked and personalized
```

**Expected flows:**
```
💡 Note: Agents contacted in order:
  1. Amadeus/TBO Agent (Port 8003) - Search flights
  2. Personalization Agent (Port 8001) - Rank results
```

### Test 6: Full Orchestration - Multi-Agent

**Input:**
```json
{
  "query": "Book a trip to Paris next month",
  "user_id": "user_orchestrate_test",
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

**Complete flow:**
```
[STEP 1] Analyzing Query Complexity...
  ├─ Complexity Score: 0.55/1.0
  └─ Classification: SIMPLE

[STEP 2] Processing Query with SIMPLE Model...
  ├─ Model: phi4
  └─ Model processing complete

[STEP 3] Identifying Required Agents...
  └─ Agents needed: Hotel Search Agent, Amadeus/TBO Agent

[STEP 4.1] Calling Hotel Search Agent...
  ├─ Endpoint: POST /search
  └─ Retrieved X hotel results

[STEP 4.2] Calling Amadeus/TBO Agent...
  ├─ Endpoint: POST /search
  └─ Retrieved X flight results

[STEP 5] Applying Personalization & Business Rules...
  ├─ User ID: user_orchestrate_test
  ├─ Results to rank: X
  └─ Personalization applied
```

**Agent Call Sequence:**
```
💡 Agent Call Sequence:
  1. Query Complexity Analyzer
  2. Phi4/Llama Model (based on complexity)
  3. Hotel Search Agent (Port 8002)
  4. Amadeus/TBO Agent (Port 8003)
  5. Personalization Agent (Port 8001) - Final ranking
```

## Live Testing with curl

### Test Simple Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Hello, how are you?",
    "user_id": "test_user"
  }'
```

**Console output will show:**
```
[STEP 1] Analyzing Query Complexity...
[STEP 2] Routing Query to Model...
Model Used: phi4
...
```

### Test Complex Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find flights from NYC to London, compare with hotels in Marais district, and apply my business travel discounts",
    "user_id": "test_user"
  }'
```

**Console output will show:**
```
[STEP 1] Analyzing Query Complexity...
[STEP 2] Routing Query to Model...
Model Used: llama2
...
```

## Complexity Scoring Reference

### Simple Queries (Score < 0.6)
- "Hello" → ~0.15
- "What time is my flight?" → ~0.25
- "Show me hotels" → ~0.35

### Complex Queries (Score >= 0.6)
- "Find flights and compare with hotels" → ~0.70
- "Book trip with multiple options and discounts" → ~0.80
- "Analyze all options, apply rules, optimize for budget" → ~0.90

## Troubleshooting Tests

### Issue: "Connection refused"
```bash
# Make sure services are running
docker-compose ps

# If not running, start them
docker-compose up -d

# Check logs
docker-compose logs
```

### Issue: "Model not found"
```bash
# Check if models were pulled
curl http://localhost:11434/api/tags

# If not there, manually pull
docker exec orchestrator-ollama ollama pull phi4
docker exec orchestrator-ollama ollama pull llama2
```

### Issue: "Agent connection failed"
The test will still pass because it gracefully handles agent availability. The orchestrator includes fallback logic for agent failures.

```bash
# Check agent services are running separately
curl http://localhost:8001/health  # Personalization
curl http://localhost:8002/health  # Hotel Search
curl http://localhost:8003/health  # Amadeus

# If not running, start them separately
```

## Test Output Legend

### Symbols
- ✓ = Success
- ✗ = Failure  
- ✅ = Complete
- 📝 = Input/Query
- 🚀 = Sending/Processing
- 🔷 = Orchestrator
- 🏨 = Hotel
- ✈️ = Flight
- 🎯 = Orchestration
- 👤 = User
- 📍 = Location
- 📅 = Dates
- 👥 = Guests/Passengers

### Color Meanings
- 🟢 Green = Success/OK
- 🔴 Red = Failure/Error
- 🟡 Yellow = Warning
- 🔵 Blue = Info/Debug

## Expected Test Results

```
TEST SUMMARY
================================================================================
Health Check: ✓ PASS
Simple Query Routing To Phi4: ✓ PASS
Complex Query Routing To Llama: ✓ PASS
Hotel Search: ✓ PASS (or graceful degradation if agents not running)
Flight Search: ✓ PASS (or graceful degradation if agents not running)
Full Orchestration: ✓ PASS (or graceful degradation if agents not running)

Result: 6/6 tests passed
================================================================================
```

## Next Steps

1. **Run in Docker:** `docker-compose up -d`
2. **Execute tests:** `python test_api.py`
3. **Monitor logs:** `docker-compose logs -f orchestrator-agent`
4. **Test with curl:** Use examples above
5. **Integrate agents:** Update agent URLs in `.env`

---

**Happy Testing!** 🎉

The logs show exactly which agent is being called at each step, making it easy to understand the routing and orchestration flow.

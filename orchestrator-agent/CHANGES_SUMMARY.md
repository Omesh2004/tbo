# Orchestrator Agent - Testing & Auto-Model-Pull Implementation

## Summary of Changes

### ✅ Auto-Model-Pull Implementation

#### 1. Docker Compose Enhancement
**File:** `docker-compose.yml`

**Changes:**
- Added `model-init` service that runs BEFORE orchestrator-agent starts
- Service automatically pulls `phi4` and `llama2` models from Ollama registry
- Orchestrator depends on model-init completion before starting
- No manual model pulling needed!

**How it works:**
```yaml
model-init:
  image: curlimages/curl:latest
  depends_on:
    - ollama
  command: sh -c "
    # Wait for Ollama to be ready
    # Pull phi4 model (5-7GB)
    # Pull llama2 model (5-7GB)
    # Verify both are loaded
  "
```

#### 2. Initialization Scripts (Optional Local Use)
**Files:** 
- `scripts/init-ollama.sh` (Linux/Mac)
- `scripts/init-ollama.bat` (Windows)

**Purpose:** If you want to init models locally without Docker

---

### ✅ Advanced Testing & Logging Implementation

#### 1. Enhanced Logger
**File:** `app/logger.py`

**Features:**
- 🎨 Color-coded console output (Green=Info, Red=Error, Yellow=Warning)
- 📊 Structured JSON logging for production
- 📍 Function name and line number tracking
- 🎯 Separate handlers for console and JSON
- ⏰ Timestamp formatting

**Example output:**
```
[INFO] | orchestrator.main | process_query:115 | [STEP 1] Received query...
[DEBUG] | orchestrator.ml | analyze:42 | Complexity Score: 0.75
```

#### 2. Detailed Step-by-Step Logging in API Routes
**File:** `app/main.py`

All endpoints now show detailed routing information:

**Query Processing:**
```
================================================================================
🔷 ORCHESTRATOR AGENT - QUERY PROCESSING
================================================================================
📝 USER QUERY: I need flights from NYC to London
👤 USER ID: user123
================================================================================

[STEP 1] Analyzing Query Complexity...
  ├─ Complexity Score: 0.75/1.0
  ├─ Threshold: 0.6
  └─ Classification: COMPLEX

[STEP 2] Preparing Context...
  ├─ Fetching user profile...
  └─ ✓ User profile loaded

[STEP 3] Routing Query to Model...
  ├─ Query is COMPLEX (score 0.75 >= 0.6)
  ├─ MODEL: Llama2 (Powerful, In-depth)
  └─ 🚀 Sending to Llama2...

[STEP 4] Model Response Received
  ├─ Model Used: llama2
  ├─ Status: success
  └─ Response Length: 512 characters
```

**Hotel Search Flow:**
```
================================================================================
🏨 HOTEL SEARCH - AGENT ROUTING
================================================================================
📍 Location: Paris
📅 Check-in: 2026-05-01 | Check-out: 2026-05-10
👥 Guests: 2
👤 User ID: user123
================================================================================

[STEP 1] Calling Hotel Search Agent...
  ├─ Agent URL: http://hotel-search-agent:8002
  ├─ Endpoint: POST /search
  └─ Results found: 12

[STEP 2] Applying Personalization...
  ├─ Agent URL: http://personalization-agent:8001
  ├─ Endpoint: POST /rank
  └─ ✓ Results ranked and personalized
```

**Flight Search Flow:**
```
================================================================================
✈️ FLIGHT SEARCH - AGENT ROUTING
================================================================================
🛫 Origin: JFK → Destination: LHR
📅 Departure: 2026-04-15
👥 Passengers: 2
👤 User ID: user123
================================================================================

[STEP 1] Calling Amadeus/TBO Agent...
  ├─ Agent URL: http://amadeus-agent:8003
  ├─ Endpoint: POST /search
  └─ Results found: 24

[STEP 2] Applying Personalization...
  ├─ Agent URL: http://personalization-agent:8001
  ├─ Endpoint: POST /rank
  └─ ✓ Results ranked and personalized
```

**Full Orchestration Flow:**
```
================================================================================
🎯 ORCHESTRATOR - FULL ORCHESTRATION FLOW
================================================================================

[STEP 1] Analyzing Query Complexity...
[STEP 2] Processing Query with MODEL...
[STEP 3] Identifying Required Agents...
  └─ Agents needed: Hotel Search Agent, Amadeus/TBO Agent
[STEP 4.1] Calling Hotel Search Agent...
[STEP 4.2] Calling Amadeus/TBO Agent...
[STEP 5] Applying Personalization & Business Rules...

Agent Call Sequence:
  1. Query Complexity Analyzer
  2. Phi4/Llama Model (based on complexity)
  3. Hotel Search Agent (Port 8002)
  4. Amadeus/TBO Agent (Port 8003)
  5. Personalization Agent (Port 8001) - Final ranking
```

#### 3. Comprehensive Test Script
**File:** `test_api.py`

**Features:**
- 6 comprehensive tests covering all flows
- Color-coded output (Green=Pass, Red=Fail)
- Step-by-step logging for each test
- Detailed agent call sequence information
- Connection error handling
- Test summary report

**Tests Included:**
1. ✅ Health Check
2. ✅ Simple Query (Routes to Phi4)
3. ✅ Complex Query (Routes to Llama)
4. ✅ Hotel Search (Shows agent routing)
5. ✅ Flight Search (Shows agent routing)
6. ✅ Full Orchestration (Multi-agent flow)

**Run Tests:**
```bash
python test_api.py
```

**Expected Output:**
```
TEST SUMMARY
================================================================================
Health Check: ✓ PASS
Simple Query Routing To Phi4: ✓ PASS
Complex Query Routing To Llama: ✓ PASS
Hotel Search: ✓ PASS
Flight Search: ✓ PASS
Full Orchestration: ✓ PASS

Result: 6/6 tests passed
================================================================================
```

---

## Complete Workflow

### 1. Start Everything (Auto-Pull Models)
```bash
cd orchestrator-agent
docker-compose up -d
```

**What happens automatically:**
```
✓ PostgreSQL starts (port 5432)
✓ Redis starts (port 6379)
✓ Ollama starts (port 11434)
✓ Model-Init service runs
  ├─ Waits for Ollama to be ready
  ├─ Pulls phi4 model (5-7GB, takes ~10-15 min)
  ├─ Pulls llama2 model (5-7GB, takes ~10-15 min)
  └─ Marks completion
✓ Orchestrator-Agent starts (port 8000)
```

### 2. Monitor Model Download
```bash
docker-compose logs -f model-init
```

Output:
```
[INIT] ✓ Ollama is ready
[INIT] Pulling phi4...
[INIT] ✓ Phi4 pulled
[INIT] Pulling llama2...
[INIT] ✓ Llama2 pulled
[INIT] ✓ Models initialization complete
```

### 3. Run Tests
```bash
python test_api.py
```

Output shows step-by-step:
```
[STEP 1] Analyzing Query Complexity...
  ├─ Complexity Score: 0.75/1.0
[STEP 2] Processing Query with COMPLEX Model...
[STEP 3] Identifying Required Agents...
[STEP 4.1] Calling Hotel Search Agent...
[STEP 4.2] Calling Amadeus/TBO Agent...
[STEP 5] Applying Personalization...
```

### 4. View Agent Routing in Logs
```bash
docker-compose logs -f orchestrator-agent | grep -E "\[STEP|Agent|Model"
```

Output:
```
[STEP 1] Analyzing Query Complexity...
[STEP 2] Routing Query to Model...
[STEP 3] Calling Hotel Search Agent...
[STEP 4] Calling Amadeus/TBO Agent...
[STEP 5] Calling Personalization Agent...
```

---

## Files Changed

### Modified Files
1. **docker-compose.yml** - Added model-init service
2. **app/main.py** - Added detailed step-by-step logging to all routes
3. **app/logger.py** - Enhanced with colored output and better formatting
4. **test_api.py** - Replaced with comprehensive test suite

### New Files
1. **TESTING_GUIDE.md** - Complete testing documentation
2. **scripts/init-ollama.sh** - Model initialization script (Linux/Mac)
3. **scripts/init-ollama.bat** - Model initialization script (Windows)
4. **.dockerignore** - Docker build optimization

---

## Key Features

### 🤖 Automatic Model Management
- Models auto-pull on `docker-compose up`
- No manual `ollama pull` commands needed
- Models cached in Docker volume for reuse

### 📊 Clear Progress Tracking
- Shows which model is being used (Phi4 vs Llama)
- Displays complexity scores and thresholds
- Lists agents being contacted in order

### 🎯 Agent Routing Visibility
- Prints agent URLs being called
- Shows response counts from each agent
- Displays personalization rankings applied

### ✅ Comprehensive Testing
- 6 different test scenarios
- Color-coded pass/fail results
- Shows exact agent sequencing for each test

### 📝 Detailed Logging
- Console output with emojis and formatting
- JSON logging for production systems
- Function-level tracking with line numbers

---

## Quick Start Commands

```bash
# Start with auto-model-pull
docker-compose up -d

# Monitor model download
docker-compose logs -f model-init

# Run comprehensive tests
python test_api.py

# View live orchestrator logs
docker-compose logs -f orchestrator-agent

# Test a specific query with curl
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find hotels in Paris", "user_id": "test"}'

# Stop everything
docker-compose down
```

---

## Expected Behavior

### Simple Query → Phi4
```bash
Query: "Hello, how are you?"
↓
Complexity: 0.25 (SIMPLE)
↓
Model: Phi4 (Fast)
↓
Response: Immediate
```

### Complex Query → Llama
```bash
Query: "Find flights and hotels with discounts"
↓
Complexity: 0.75 (COMPLEX)
↓
Model: Llama2 (Comprehensive)
↓
Agents: Hotel Search → Amadeus → Personalization
↓
Response: Detailed with recommendations
```

---

## Troubleshooting

### Models Taking Too Long to Pull
```bash
# This is normal - models are 5-7GB each
# First run takes 10-15 minutes
# Subsequent runs use cached images (instant)

# Monitor progress
docker-compose logs -f model-init
```

### Tests Failing with "Connection Refused"
```bash
# Services still starting
# Wait a minute and retry
docker-compose ps  # Check all running

# If stuck, restart
docker-compose down
docker-compose up -d
```

### Want to See All Logs
```bash
# Everything
docker-compose logs

# Just orchestrator
docker-compose logs orchestrator-agent

# Follow in real-time with colors
docker-compose logs -f --timestamps orchestrator-agent
```

---

## Architecture Diagram

```
docker-compose up
  ↓
1. Start Database, Cache, Models
  ├─ PostgreSQL (5432)
  ├─ Redis (6379)
  └─ Ollama (11434)
      ↓
2. Model-Init Service (runs once)
   ├─ Wait for Ollama
   ├─ Pull phi4 (5-7GB)
   ├─ Pull llama2 (5-7GB)
   └─ Complete ✓
      ↓
3. Orchestrator-Agent starts
   └─ Ready on port 8000 ✓

User Query
  ↓
[STEP 1] Complexity Analysis
  ├─ Score < 0.6 → Phi4
  └─ Score >= 0.6 → Llama
      ↓
[STEP 2] Model Processing
      ↓
[STEP 3] Agent Identification
      ├─ Hotel keywords? → Hotel Agent
      ├─ Flight keywords? → Amadeus Agent
      └─ Both? → Multi-agent
          ↓
[STEP 4] Agent Calls
  ├─ Hotel Search (Port 8002)
  ├─ Flight Search (Port 8003)
  └─ Personalization (Port 8001)
      ↓
[STEP 5] Response with Rankings
  └─ Return to User ✓
```

---

## Summary

You now have:
1. ✅ **Auto-pulling models** - No manual `ollama pull` needed
2. ✅ **Step-by-step logging** - See exactly which agent is called
3. ✅ **Comprehensive tests** - Verify routing and segregation
4. ✅ **Clear visibility** - Color-coded output showing the flow
5. ✅ **Production ready** - Docker Compose with all services

**Everything is ready to go!** Just run `docker-compose up -d` and `python test_api.py` to see it in action.

---

Last Updated: March 2026  
Version: 1.0.0

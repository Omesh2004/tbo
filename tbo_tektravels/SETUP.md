# Quick Start Guide - TBO/TekTravels Travel Pipeline

## Quick Choice: Docker or Manual?

| Method | Time | Recommended | Effort |
|--------|------|-------------|--------|
| **Docker Compose** | 2-3 min | ✅ Yes | Minimal |
| **Manual Setup** | 5-10 min | For advanced users | More |

---

## Setup Option 1: Docker (Recommended) ⭐

### Prerequisites
- Docker installed
- Docker Compose installed
- 4GB RAM available

### Installation (2-3 minutes)

```bash
# Navigate to folder
cd tbo_tektravels

# Copy environment file
cp .env.example .env

# Start all services (Redis, Kafka, Zookeeper, Qdrant, Pipeline)
docker-compose up
```

**That's it!** The pipeline will:
- Start automatically
- Run every 15 minutes
- Save output to `travel_package_data_tbo.json`
- Stream to Kafka & Redis
- Ingest to Qdrant

### Check Status
```bash
# In another terminal
docker-compose ps

# View logs
docker-compose logs -f tbo-pipeline

# Stop when done
docker-compose down
```

### Data Access (Docker)
```bash
# View JSON output
docker exec tbo-pipeline cat travel_package_data_tbo.json

# Access Redis
docker exec -it tbo-redis redis-cli

# Check Kafka topics
docker-compose exec tbo-kafka kafka-topics.sh \
  --bootstrap-server localhost:9092 --list

# Query Qdrant
curl http://localhost:6333/collections
```

### Production Deployment (Docker)
```bash
# Start with production settings (resource limits, healthier logs)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Monitor
docker-compose ps
docker-compose logs -f tbo-pipeline

# Stop safely
docker-compose down
```

**For detailed Docker documentation, see: `DOCKER.md`**

---

## Setup Option 2: Manual Installation

### Prerequisites
- Python 3.8+
- Redis running on `redis:6379` (or configured host)
- Kafka running on `kafka:9092` (or configured broker)
- Qdrant running on `http://qdrant:6333` (or configured URL)

### Step 1: Install Python Dependencies
```bash
cd tbo_tektravels
pip install -r requirements.txt
```

### Step 2: Set Environment Variables
Create a `.env` file or export these variables:

```bash
export REDIS_HOST=redis
export REDIS_PORT=6379
export KAFKA_BROKER=kafka:9092
export KAFKA_TOPIC=travel-data-raw
export QDRANT_URL=http://qdrant:6333
export QDRANT_COLLECTION=travel_data
export TBO_HOTEL_USERNAME=Hackathon
export TBO_HOTEL_PASSWORD=Hackathon@1234
export TEKTRAVELS_FLIGHT_USER_ID=Hackathon
export TEKTRAVELS_FLIGHT_PASSWORD=Hackathon@123
```

### Step 3: Run the Pipeline
```bash
python testamad_tbo.py
```

Expected output:
```
2026-02-28 10:30:00 - INFO - Starting Travel Data Pipeline Service (TBO/TekTravels)...
2026-02-28 10:30:00 - INFO - Redis Host: redis:6379
2026-02-28 10:30:00 - INFO - Kafka Broker: kafka:9092
2026-02-28 10:30:00 - INFO - Kafka Topic: travel-data-raw
2026-02-28 10:30:00 - INFO - Scheduled to run every 15 minutes

2026-02-28 10:30:00 - INFO - Running initial job on startup...
2026-02-28 10:30:01 - INFO - 🔄 Starting scheduled data fetch...
2026-02-28 10:30:02 - INFO - Fetching travel data from TBO and TekTravels APIs...
...
2026-02-28 10:30:05 - INFO - ✅ Data published to Kafka topic 'travel-data-raw'
2026-02-28 10:30:05 - INFO - Stored in Redis Stream with ID: 1709022605123-0
2026-02-28 10:30:05 - INFO - Data saved to travel_package_data_tbo.json
2026-02-28 10:30:06 - INFO - Qdrant upsert: {'upserted': 16, 'embedded': 16, ...}
2026-02-28 10:30:07 - INFO - 🎉 Scheduled job completed successfully!
```

### Verify Qdrant Connection
```bash
python connect.py
```

Should output your Qdrant collections.

## Data Files Created

After first run, check these outputs:

**JSON Output:**
```bash
cat travel_package_data_tbo.json
```

**Redis Stream (access via redis-cli):**
```bash
redis-cli XLEN travel_data_stream
redis-cli XREAD COUNT 1 STREAMS travel_data_stream 0
```

**Kafka (if you have kafka-console-consumer):**
```bash
kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic travel-data-raw --from-beginning
```

## Architecture

```
┌─────────────────┐
│ TBO Hotel API   │
└────────┬────────┘
         │
         ├─────────────────────────────────────────┐
         │                                         │
         v                                         v
┌─────────────────────────────────────────────────────────┐
│         fetch_travel_data()                             │
│  (Combines hotel, flight, and activity data)            │
└────┬────────────────┬──────────────────┬────────────────┘
     │                │                  │
     v                v                  v
  Kafka           Redis Stream        Qdrant Vector DB
                                           │
                                           v
                                    travel_package_data_tbo.json
```

## Scheduling

- **Interval**: Every 15 minutes
- **Start**: Immediate on script start
- **No manual intervention needed** while running

## Stopping the Service

Press `Ctrl+C` to stop. It will gracefully close Kafka connection.

## Troubleshooting

### Docker Issues
| Issue | Solution |
|-------|----------|
| `docker-compose: command not found` | Install Docker Compose: https://docs.docker.com/compose/install |
| `Cannot connect to Docker daemon` | Start Docker Desktop or Docker service |
| `Ports already in use` | Change ports in docker-compose.yml or stop existing containers |
| `Out of memory` | Increase Docker memory allocation |
| `Service not healthy` | Check `docker-compose logs <service-name>` |

### Manual Setup Issues

| Issue | Solution |
|-------|----------|
| `ConnectionRefusedError: Redis` | Ensure Redis is running on specified host:port |
| `NoBrokersAvailable: Kafka` | Ensure Kafka is running on specified broker |
| `Unable to connect to Qdrant` | Ensure Qdrant is running on specified URL |
| `No flights/hotels returned` | Check API credentials and destination codes |
| `Module not found` | Verify all `.py` files are in same directory |

## Configuration Reference

See `README.md` for detailed configuration options and environment variables.

## What's Different from Original?

✅ **Same Architecture** (Kafka, Redis, Qdrant, scheduled jobs)
✅ **Same Functionality** (fetch, publish, store, embed)
❌ **Different APIs** (TBO Hotel + TekTravels Flight instead of Amadeus)
❌ **Different Output File** (`travel_package_data_tbo.json` vs `travel_package_data.json`)

## Original Amadeus Version

Still available unchanged in `../tbo/` directory for comparison.

---

**Need help?** Check the full `README.md` in this folder.

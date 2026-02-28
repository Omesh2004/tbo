# Docker Setup Guide - TBO/TekTravels Travel Pipeline

## Overview

This folder contains a complete Docker-based deployment of the TBO/TekTravels Travel Data Pipeline. The Docker setup includes:

- **Application Container**: Python service running the travel data pipeline
- **Redis Container**: Stream data store and caching layer
- **Kafka Container**: Event streaming message broker
- **Zookeeper Container**: Kafka coordination service
- **Qdrant Container**: Vector database for semantic search

All services are orchestrated using Docker Compose and communicate over an isolated network.

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────┐
│                  Docker Compose Network                     │
│              (travel-tbo-network - Bridge)                  │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐  ┌─────────────────────┐             │
│  │  tbo-redis      │  │  tbo-zookeeper      │             │
│  │  redis:7-alpine │  │  cp-zookeeper:7.5.0 │             │
│  │  Port: 6379     │  │  Port: 2181         │             │
│  │  - Persistent   │  │  - Kafka Coord      │             │
│  │  - Stream DB    │  │  - Health Check ✓   │             │
│  └────────┬────────┘  └──────────┬──────────┘             │
│           │                       │                         │
│           │                       └──────────────┐          │
│           │                                      │          │
│           │            ┌──────────────────────────┴──────┐  │
│           │            │                                  │  │
│           │            v                                  v  │
│           │      ┌──────────────────────────────┐         │  │
│           │      │   tbo-kafka                  │         │  │
│           │      │   cp-kafka:7.5.0             │         │  │
│           │      │   Port: 9092                 │         │  │
│           │      │   - Event Streaming          │         │  │
│           │      │   - Health Check ✓           │         │  │
│           │      └──────────────────────────────┘         │  │
│           │                 ▲                              │  │
│           │                 │                              │  │
│           │                 │                    ┌─────────┘  │
│           │                 │                    │            │
│           │                 │                    │            │
│  ┌────────┴────────┬────────┴───┐               │            │
│  │                 │             │               │            │
│  v                 v             v               v            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │      tbo-pipeline (Python Application)                 │  │
│  │      - testamad_tbo.py                                 │  │
│  │      - Depends on: Redis, Kafka, Qdrant (healthy)      │  │
│  │      - Fetches from TBO Hotel API                      │  │
│  │      - Fetches from TekTravels Flight API              │  │
│  │      - Publishes to Kafka & Redis                      │  │
│  │      - Ingests into Qdrant                             │  │
│  │      - Saves to travel_package_data_tbo.json           │  │
│  │      - Health Check: Redis connectivity ✓              │  │
│  └────────────────────────────────────────────────────────┘  │
│                             ▲                                  │
│                             │                                  │
│  ┌──────────────────────────┘                                │
│  │                                                            │
│  v                                                            │
│  ┌──────────────────────────────────┐                        │
│  │   tbo-qdrant                      │                        │
│  │   qdrant/qdrant:latest            │                        │
│  │   Ports: 6333 (REST), 6334 (gRPC)│                        │
│  │   - Vector Database               │                        │
│  │   - Semantic Search               │                        │
│  │   - Health Check ✓                │                        │
│  └──────────────────────────────────┘                        │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

## Services

### 1. tbo-redis (Redis 7 Alpine)
- **Purpose**: Stream data storage and caching
- **Image**: `redis:7-alpine` (lightweight)
- **Port**: 6379
- **Features**:
  - Persistence enabled (`appendonly yes`)
  - Health checks (redis-cli PING)
  - Named volume for data persistence
  - Automatically restarts on failure
- **Health Status**: Required before other services start

### 2. tbo-zookeeper (Confluent Zookeeper)
- **Purpose**: Kafka coordination and consensus
- **Image**: `confluentinc/cp-zookeeper:7.5.0`
- **Port**: 2181
- **Features**:
  - Handles Kafka broker coordination
  - Health checks via TCP port
  - Named configuration (ZOOKEEPER_TICK_TIME = 2000ms)

### 3. tbo-kafka (Confluent Kafka)
- **Purpose**: Event streaming and message broker
- **Image**: `confluentinc/cp-kafka:7.5.0`
- **Port**: 9092
- **Features**:
  - Depends on Zookeeper
  - Auto-creates topics if enabled
  - Health checks via broker API
  - 24-hour log retention for development
- **Health Status**: Required before pipeline starts

### 4. tbo-qdrant (Qdrant Vector DB)
- **Purpose**: Vector database for semantic search
- **Image**: `qdrant/qdrant:latest`
- **Ports**: 6333 (REST API), 6334 (gRPC API)
- **Features**:
  - Health checks via HTTP GET /collections
  - Named volume for persistent storage
  - Optional API key support
- **Health Status**: Required before pipeline starts

### 5. tbo-pipeline (Custom Python Application)
- **Purpose**: Main travel data pipeline service
- **Image**: Built from local `Dockerfile`
- **Features**:
  - Fetches from TBO Hotel API & TekTravels Flight API
  - Publishes to Kafka topic
  - Stores in Redis Streams
  - Ingests to Qdrant vector database
  - Saves to JSON file
  - Runs every 15 minutes
  - Health checks verify Redis connectivity
- **Dependencies**: All 4 infrastructure services (healthy)
- **Restart Policy**: unless-stopped (restarts on failure)

## Quick Start

### Prerequisites
- Docker & Docker Compose installed
- 4GB RAM minimum available
- Ports 6379, 2181, 9092, 6333, 6334 available

### 1. Basic Startup (Development)
```bash
# Navigate to folder
cd tbo_tektravels

# Copy environment template
cp .env.example .env

# Start all services
docker-compose up

# In another terminal, check status
docker-compose ps

# View pipeline logs
docker-compose logs -f tbo-pipeline
```

**Expected Output** (after ~30-45 seconds):
```
tbo-redis is healthy ✓
tbo-zookeeper is healthy ✓
tbo-kafka is healthy ✓
tbo-qdrant is healthy ✓
tbo-pipeline: Starting scheduled data fetch...
tbo-pipeline: ✅ Retrieved 3 flights
tbo-pipeline: ✅ Retrieved 10 hotels
tbo-pipeline: ✅ Data published to Kafka
...
tbo-pipeline: 🎉 Scheduled job completed successfully!
```

### 2. Production Startup
```bash
# Start with production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify services
docker-compose ps

# View logs
docker-compose logs tbo-pipeline
```

### 3. Detached Mode (Background)
```bash
# Start in background
docker-compose up -d

# Check status
docker-compose ps

# View logs anytime
docker-compose logs tbo-pipeline

# Stop when ready
docker-compose down
```

## Configuration

### Environment Variables

#### API Credentials
```bash
TBO_HOTEL_USERNAME=Hackathon
TBO_HOTEL_PASSWORD=Hackathon@1234
TEKTRAVELS_FLIGHT_USER_ID=Hackathon
TEKTRAVELS_FLIGHT_PASSWORD=Hackathon@123
```

#### Service Endpoints (Pre-configured for Docker)
```bash
REDIS_HOST=tbo-redis
REDIS_PORT=6379
KAFKA_BROKER=tbo-kafka:9092
QDRANT_URL=http://tbo-qdrant:6333
```

#### Qdrant Configuration
```bash
QDRANT_COLLECTION=travel_data
QDRANT_VECTOR_DIM=384
QDRANT_DISTANCE=Cosine
```

#### Custom Settings
```bash
KAFKA_TOPIC=travel-data-raw-tbo  # Change topic name if needed
LOG_LEVEL=INFO                    # INFO, DEBUG, WARNING
DEBUG=false                       # Enable debug mode
```

### Using .env File

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env  (or use your editor)

# Docker Compose will automatically load .env file
docker-compose up
```

## Data Access

### JSON Output File
```bash
# View generated JSON output
docker exec tbo-pipeline cat travel_package_data_tbo.json

# Or from host (if volume mounted)
cat tbo_tektravels/travel_package_data_tbo.json
```

### Redis Streams
```bash
# Access Redis CLI
docker exec -it tbo-redis redis-cli

# Check stream length
> XLEN travel_data_stream

# Read latest messages (last 3)
> XREVRANGE travel_data_stream + COUNT 3

# Exit
> EXIT
```

### Kafka Topics
```bash
# List topics
docker-compose exec tbo-kafka kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list

# Read messages
docker-compose exec tbo-kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic travel-data-raw-tbo \
  --from-beginning
```

### Qdrant Collections
```bash
# List collections
curl http://localhost:6333/collections

# Get collection info
curl http://localhost:6333/collections/travel_data

# Search vectors (example)
curl -X POST http://localhost:6333/collections/travel_data/points/search \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, 0.3, ...],
    "limit": 10
  }'
```

## Service Health Status

Each service has health checks configured to verify it's running correctly:

### View Health Status
```bash
# Check all services
docker-compose ps

# Output should show:
# NAME              STATUS              PORTS
# tbo-redis         healthy             0.0.0.0:6379->6379/tcp
# tbo-zookeeper     healthy             0.0.0.0:2181->2181/tcp
# tbo-kafka         healthy             0.0.0.0:9092->9092/tcp
# tbo-qdrant        healthy             0.0.0.0:6333->6333/tcp, 0.0.0.0:6334->6334/tcp
# tbo-pipeline      healthy             (no ports exposed)
```

### Health Check Details

| Service | Health Check | Interval | Timeout | Retries |
|---------|-------------|----------|---------|---------|
| redis | `redis-cli ping` | 10s | 5s | 5 |
| zookeeper | TCP port 2181 + ruok | 10s | 5s | 5 |
| kafka | Binary protocol port | 10s | 5s | 5 |
| qdrant | HTTP GET /collections | 10s | 5s | 5 |
| pipeline | Redis connectivity | 30s | 10s | 3 |

## Logs & Monitoring

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs tbo-pipeline

# Last 50 lines
docker-compose logs --tail 50

# Follow in real-time
docker-compose logs -f

# Follow specific service
docker-compose logs -f tbo-pipeline

# With timestamps
docker-compose logs --timestamps
```

### Monitor Performance
```bash
# CPU & Memory usage
docker stats

# Specific container
docker stats tbo-pipeline

# Network I/O
docker exec tbo-pipeline netstat -an

# Disk usage
docker system df
```

## Volumes & Data Persistence

### Named Volumes
```yaml
redis_data:      # Redis persistent storage
qdrant_storage:  # Qdrant vector database storage
```

### Inspect Volumes
```bash
# List all volumes
docker volume ls

# Inspect specific volume
docker volume inspect tbo_redis_data

# See volume location on host
docker volume inspect tbo_qdrant_storage
```

### Backup Data
```bash
# Backup Redis data
docker exec tbo-redis redis-cli BGSAVE
docker cp tbo-redis:/data/dump.rdb ./redis-backup.rdb

# Backup Qdrant data
docker cp tbo-qdrant:/qdrant/storage ./qdrant-backup/
```

### Restore Data
```bash
# Restore Redis data
docker cp redis-backup.rdb tbo-redis:/data/
docker exec tbo-redis redis-cli SHUTDOWN NOSAVE
docker-compose up tbo-redis

# Restore Qdrant data
docker cp qdrant-backup/ tbo-qdrant:/qdrant/storage
docker-compose restart tbo-qdrant
```

## Networking

### Network Configuration
```yaml
networks:
  travel-tbo-network:
    driver: bridge
```

### Service Communication
Services communicate using service names as hostnames within the network:
- `tbo-redis:6379` - Redis connection
- `tbo-kafka:9092` - Kafka broker
- `tbo-qdrant:6333` - Qdrant REST API
- `tbo-zookeeper:2181` - Zookeeper cluster

### External Port Access
| Service | Port | Access |
|---------|------|--------|
| redis | 6379 | localhost:6379 |
| kafka | 9092 | localhost:9092 |
| qdrant | 6333 | localhost:6333 |
| qdrant | 6334 | localhost:6334 |
| zookeeper | 2181 | localhost:2181 |

## Resource Management

### Development Resources (Default)
- No explicit limits
- Suitable for 4GB+ RAM machines
- Uses ~2-3GB total with all services

### Production Resources (docker-compose.prod.yml)
```yaml
tbo-redis:      1 CPU, 512MB RAM (limit), 256MB (reserved)
tbo-kafka:      2 CPU, 1GB RAM (limit), 512MB (reserved)
tbo-qdrant:     2 CPU, 2GB RAM (limit), 1GB (reserved)
tbo-pipeline:   1 CPU, 512MB RAM (limit), 256MB (reserved)
```

### Set Custom Resource Limits
```yaml
# In docker-compose.yml
services:
  tbo-pipeline:
    deploy:
      resources:
        limits:
          cpus: '2'           # 2 CPU cores max
          memory: 1G          # 1GB RAM max
        reservations:
          cpus: '1'           # Reserve 1 CPU
          memory: 512M        # Reserve 512MB
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs tbo-pipeline

# Check if dependencies are healthy
docker-compose ps

# Restart service
docker-compose restart tbo-pipeline
```

### Redis Connection Failed
```bash
# Check Redis status
docker-compose logs tbo-redis

# Test connection
docker exec tbo-redis redis-cli PING

# Restart Redis
docker-compose restart tbo-redis
```

### Kafka Issues
```bash
# Check Kafka logs
docker-compose logs tbo-kafka

# List topics
docker-compose exec tbo-kafka kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list

# Create topic manually
docker-compose exec tbo-kafka kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic travel-data-raw-tbo \
  --partitions 1 \
  --replication-factor 1
```

### Out of Memory
```bash
# Check resource usage
docker stats

# Free up space
docker system prune -a

# Or reduce retention
# Edit docker-compose.yml: KAFKA_LOG_RETENTION_HOURS: 24
```

### Ports Already in Use
```bash
# Find process using port 6379 (Redis)
lsof -i :6379

# Or use different port mapping
# Edit docker-compose.yml: "6380:6379"
```

## Cleanup & Shutdown

### Stop Services
```bash
# Stop running services
docker-compose down

# Stop and remove volumes (clear data)
docker-compose down -v

# Stop and remove everything (images too)
docker-compose down -v --rmi all
```

### Prune Docker System
```bash
# Remove unused containers, networks, volumes
docker system prune

# Also remove unused images
docker system prune -a

# But keep volume data
docker system prune --volumes
```

## Production Deployment

### Using Production Configuration
```bash
# Start with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Monitor services
docker-compose ps
docker-compose logs -f tbo-pipeline
```

### Docker Registry (Push Image)
```bash
# Build with tag
docker build -t your-registry/tbo-tektravels:v1.0 .

# Push to registry
docker push your-registry/tbo-tektravels:v1.0

# In docker-compose.yml, change image
# image: your-registry/tbo-tektravels:v1.0
```

### Kubernetes (Optional)
If deploying to Kubernetes:
1. Create ConfigMap from .env file
2. Create StatefulSets for Redis, Kafka, Qdrant
3. Create Deployment for tbo-pipeline
4. Create Services for network access
5. Configure PersistentVolumeClaims for storage

## Common Commands

```bash
# See all running containers
docker-compose ps

# View logs (all services)
docker-compose logs

# Follow logs (real-time)
docker-compose logs -f

# Restart a service
docker-compose restart tbo-pipeline

# Rebuild image
docker-compose build --no-cache

# Remove all containers and volumes
docker-compose down -v

# Access service shell
docker exec -it tbo-pipeline bash

# Run one-off command
docker exec tbo-pipeline python connect.py

# View environment variables
docker exec tbo-pipeline env | grep KAFKA
```

## Support & Documentation

- **Main Documentation**: See `README.md` in this folder
- **Setup Guide**: See `SETUP.md` in this folder
- **Implementation Details**: See `IMPLEMENTATION_COMPLETE.md`
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/

---

**Last Updated**: 2026-02-28
**Docker Compose Version**: 3.8
**Base Python Image**: 3.11-slim

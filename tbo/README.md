# Travel Data Pipeline Service

A dockerized travel data ingestion pipeline that fetches travel data every 15 minutes using Redis Streams and publishes to Kafka.

## Architecture

- **Redis Streams**: Manages data scheduling and stores stream records
- **Kafka**: Topic-based message broker for raw data ingestion
- **Amadeus API**: Fetches real-time flight, hotel, and activity data
- **Docker Compose**: Orchestrates all services

## Features

✅ Fetches travel data from Amadeus API every 15 minutes
✅ Stores data in Redis Streams for stream processing
✅ Publishes raw data to Kafka topic (`travel-data-raw`)
✅ Prints formatted JSON results to logs
✅ Saves data to `travel.json` file
✅ Full Docker containerization with health checks
✅ Environment variable configuration

## Prerequisites

- Docker
- Docker Compose
- Valid Amadeus API credentials (included in .env)

## Quick Start

### 1. Start All Services

```bash
docker-compose up -d
```

This will start:
- Redis (port 6379)
- Zookeeper (port 2181)
- Kafka (port 9092)
- Travel Pipeline Service (runs automatically)

### 2. View Logs

```bash
# View all services logs
docker-compose logs -f

# View only travel pipeline logs
docker-compose logs -f travel-pipeline

# View Redis logs
docker-compose logs -f redis

# View Kafka logs
docker-compose logs -f kafka
```

### 3. Verify Services

```bash
# Check service status
docker-compose ps

# Test Redis connection
docker-compose exec redis redis-cli ping

# Test Kafka connection
docker-compose exec kafka kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

## Consuming Kafka Messages

To view messages published to the Kafka topic:

```bash
docker-compose exec kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic travel-data-raw \
  --from-beginning
```

## Redis Streams

To view data in Redis Streams:

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# View stream entries
> XRANGE travel_data_stream - +

# Get stream length
> XLEN travel_data_stream

# Read latest entries
> XREAD COUNT 5 STREAMS travel_data_stream $
```

## Configuration

All configuration is in `.env` file:

```env
AMADEUS_CLIENT_ID=your_client_id
AMADEUS_CLIENT_SECRET=your_secret
REDIS_HOST=redis
REDIS_PORT=6379
KAFKA_BROKER=kafka:9092
KAFKA_TOPIC=travel-data-raw
```

## File Structure

```
.
├── testamad.py          # Main application
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Service orchestration
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
├── travel.json          # Output data file
└── README.md            # This file
```

## What Happens Every 15 Minutes

1. **Fetch**: Retrieves flights, hotels, and activities from Amadeus API
2. **Store**: Adds data to Redis Stream (`travel_data_stream`)
3. **Publish**: Sends JSON data to Kafka topic (`travel-data-raw`)
4. **Save**: Writes JSON to `travel.json` file
5. **Log**: Prints formatted result to console/logs

## Monitoring

- **Health Checks**: Services have built-in health checks
- **Logging**: All actions are logged with timestamps
- **File Output**: Results saved to `travel.json`
- **Stream Persistence**: Redis maintains stream history

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Troubleshooting

### Services not starting
```bash
docker-compose logs -f
```

### Connection refused errors
- Wait for health checks to pass
- Verify firewall settings
- Check port availability

### Redis connection failed
```bash
docker-compose exec redis redis-cli ping
```

### Kafka not receiving messages
```bash
docker-compose logs travel-pipeline
docker-compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092
```

## API Response Data

Each fetch retrieves:
- **Flights**: Top 3 available flight offers (MAD → ATH)
- **Hotels**: Top 10 hotels in Athens with offers
- **Hotels Price Range**: Min, Max, Average prices
- **Activities**: Top 3 activities in Athens
- **Timestamp**: When data was fetched

## Performance Notes

- Initial data fetch runs on startup
- Subsequent fetches run every 15 minutes
- All API calls timeout after 30 seconds
- Kafka batches messages for efficiency
- Redis persists data to disk

## Next Steps

1. Monitor the logs to see data being fetched
2. Consume Kafka topic to process raw data
3. Query Redis Streams for historical data
4. Extend pipeline with additional processing steps

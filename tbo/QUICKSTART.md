# Quick Start Guide - Travel Data Pipeline

## 🚀 Start Services

```bash
cd c:\Users\DELL\Desktop\pathway\tbo
docker-compose up -d
```

This will start:
- Redis (stream storage)
- Zookeeper (Kafka coordinator)
- Kafka (message broker)
- Travel Pipeline (app service)

**Wait 30-60 seconds for all services to be healthy**

## 📊 Monitor in Real-Time

### Windows Users:
```bash
monitor.bat
```

### Mac/Linux Users:
```bash
./monitor.sh
```

Or view logs directly:
```bash
docker-compose logs -f travel-pipeline
```

## 📈 What You'll See

Every 15 minutes:
1. Data fetched from Amadeus API
2. Stored in Redis Stream
3. Published to Kafka topic
4. Saved to travel.json
5. Logged to console with full JSON

Example output:
```
2026-02-17 10:30:45 - INFO - Starting scheduled data fetch...
2026-02-17 10:30:47 - INFO - ✅ Data published to Kafka topic 'travel-data-raw'
2026-02-17 10:30:48 - INFO - Stored in Redis Stream with ID: 1739790647000-0
2026-02-17 10:30:49 - INFO - ✅ SUCCESS - Travel Data Fetched
[Full JSON data printed here]
```

## 🔍 View Data in Real-Time

### Option 1: Consume Kafka Messages
```bash
# In another terminal
docker-compose exec kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic travel-data-raw \
  --from-beginning
```

### Option 2: Query Redis Stream
```bash
# In another terminal
docker-compose exec redis redis-cli
> XRANGE travel_data_stream - +
> XLEN travel_data_stream
```

### Option 3: Use Python Consumer
```bash
# In another terminal
pip install kafka-python redis
python kafka_consumer.py
```

### Option 4: Inspect Redis with Python
```bash
# In another terminal
pip install redis
python redis_inspector.py
```

## 🛑 Stop Services

```bash
docker-compose down
```

Remove data volumes:
```bash
docker-compose down -v
```

## 📁 Output Files

- **travel.json** - Latest fetched data (updated every 15 mins)
- **Docker logs** - All operations logged

## 🔧 Troubleshooting

### Services won't start
```bash
docker-compose logs
```

### Kafka not receiving data
```bash
docker-compose logs travel-pipeline
```

### Redis connection error
```bash
docker-compose exec redis redis-cli ping
```

### Check if services are healthy
```bash
docker-compose ps
```

## 📊 Data Flow

```
┌─────────────────────┐
│  Amadeus API        │
│  (every 15 mins)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Travel Pipeline    │
│  (testamad.py)      │
└──────────┬──────────┘
           │
       ┌───┴───┐
       │       │
       ▼       ▼
    REDIS    KAFKA
   STREAM    TOPIC
   
   └────┬────┘
        │
        ▼
   travel.json
   + Console/Logs
```

## 🎯 Next Steps

1. Monitor the first data fetch (happens immediately on startup)
2. Wait for 15 minutes to see the scheduled fetch
3. Consume Kafka messages for downstream processing
4. Query Redis Stream for historical data
5. Extend pipeline with additional processing

## ⚙️ Configuration

Edit `.env` file to change:
- Amadeus credentials
- Redis host/port
- Kafka broker address
- Kafka topic name

Then restart:
```bash
docker-compose down
docker-compose up -d
```

## 📞 Support

View detailed README.md for comprehensive documentation

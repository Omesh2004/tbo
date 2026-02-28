# TBO/TekTravels Travel Data Pipeline

This folder contains a complete travel data pipeline implementation using TBO Hotel API (v2.1) and TekTravels Flight API, maintaining all the original functionality from the Amadeus-based implementation.

## Overview

This pipeline replicates the entire architecture from the original `../tbo/testamad.py` but replaces the Amadeus SDK with direct API integrations for TBO Hotel and TekTravels Flight APIs.

**Original folder (`../tbo/`) remains completely untouched.**

## Architecture & Components

### 1. **API Clients**

#### `tbo_hotel_client.py`
- **Purpose**: TBO Hotel API v2.1 client
- **Authentication**: Basic Auth (credentials via environment variables)
- **Key Methods**:
  - `search_hotels()` - Search hotels in a city
  - `get_hotel_details()` - Get hotel information
  - `prebook_hotel()` - Pre-book a hotel
  - `book_hotel()` - Complete hotel booking
  - `get_countries()` - List all countries
  - `get_cities()` - Cities in a country
  - `get_hotel_codes_by_city()` / `get_tbo_hotel_codes()` - Get hotel lists
  - `cancel_booking()` - Cancel a hotel booking
  - `get_booking_details()` - Get booking information

#### `tektravels_flight_client.py`
- **Purpose**: TekTravels Flight API client for B2B flight operations
- **Authentication**: B2B credentials (UserId/Password via environment variables)
- **Key Methods**:
  - `search_flights()` - Search available flights
  - `get_flight_fare_rules()` - Get fare restrictions
  - `prebook_flight()` - Reserve a flight
  - `book_flight()` - Complete flight booking
  - `get_booking_details()` - Get flight booking info
  - `cancel_booking()` - Cancel flight booking
  - `get_seat_map()` - Get available seats
  - `get_baggage_details()` - Get baggage allowances
  - `add_ancillary_services()` - Add extras (seats, baggage, etc.)

### 2. **Main Pipeline**

#### `testamad_tbo.py`
- **Purpose**: Main scheduling and orchestration engine
- **Functions**:
  - `fetch_travel_data()` - Fetch data from both TBO and TekTravels APIs
  - `publish_to_kafka()` - Publish data to Kafka topic
  - `store_in_redis_stream()` - Store in Redis Stream for real-time access
  - `save_to_file()` - Save to JSON file (`travel_package_data_tbo.json`)
  - `build_qdrant_records()` - Prepare data for vector database
  - `scheduled_job()` - Main orchestration (runs every 15 minutes)
  - `main()` - Initialize and schedule jobs

**Execution Flow**:
```
TBO Hotel API ──┐
TekTravels Flight API ┤──> fetch_travel_data() ──> Kafka
Static Activities    ──┤                         ──> Redis Stream
                       └──> Qdrant Vector DB
                              ├──> File (JSON)
                              └──> Logging
```

### 3. **Infrastructure Modules**

#### `qdrant_ingest.py`
- Qdrant vector database integration
- Functions:
  - `get_qdrant_client()` - Initialize Qdrant client
  - `ensure_collection()` - Create collection if needed
  - `embed_texts()` - Generate embeddings using hash-based method
  - `prepare_points()` - Convert records to Qdrant format
  - `upsert_records()` - Insert/update records in Qdrant

#### `connect.py`
- Simple Qdrant connectivity verification
- Run: `python connect.py` to test connection

## Data Sources

### Hotels
- **Source**: TBO Hotel API v2.1
- **Base URL**: `http://api.tbotechnology.in/TBOHolidays_HotelAPI`
- **Sample Query**: Athens (ATH), March 15-17, 2026
- **Response Contains**: Hotel names, codes, prices, facilities, ratings

### Flights
- **Source**: TekTravels Flight API
- **Base URL**: `https://api.tektravels.com`
- **Sample Query**: Madrid (MAD) → Athens (ATH), March 15, 2026
- **Response Contains**: Flight details, prices, airlines, times

### Activities
- **Source**: Static data (TBO API doesn't include activities)
- **Locations**: Athens tourist attractions with pricing and ratings

## Environment Configuration

### Required Environment Variables

```bash
# Redis
REDIS_HOST=redis              # Default: redis
REDIS_PORT=6379              # Default: 6379

# Kafka
KAFKA_BROKER=kafka:9092       # Default: kafka:9092
KAFKA_TOPIC=travel-data-raw   # Default: travel-data-raw

# Qdrant
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=<optional>
QDRANT_COLLECTION=travel_data
QDRANT_VECTOR_DIM=384
QDRANT_DISTANCE=Cosine

# TBO Hotel API
TBO_HOTEL_USERNAME=Hackathon
TBO_HOTEL_PASSWORD=Hackathon@1234

# TekTravels Flight API
TEKTRAVELS_FLIGHT_USER_ID=Hackathon
TEKTRAVELS_FLIGHT_PASSWORD=Hackathon@123
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Docker Setup (if using containers)
```bash
# From parent directory
docker-compose up -d
```

### 3. Run Pipeline
```bash
# Standalone (runs immediately + every 15 minutes)
python testamad_tbo.py

# Test Qdrant connection only
python connect.py
```

## Output Files

- **`travel_package_data_tbo.json`** - Main data output (flights, hotels, activities)
- **Redis Stream** - Real-time data at key `travel_data_stream`
- **Kafka Topic** - `travel-data-raw` (configurable)
- **Qdrant Vector DB** - Collection `travel_data` with embeddings

## Sample Data Structure

```json
{
  "flights": [
    {
      "id": "...",
      "airline": "...",
      "departureTime": "...",
      "arrivalTime": "...",
      "price": 150.00,
      "stops": 0
    }
  ],
  "hotels": [
    {
      "hotelId": "...",
      "hotelName": "...",
      "city": "ATH",
      "price": 85.00,
      "rating": 4.5,
      "amenities": [...]
    }
  ],
  "hotel_price_range": {
    "min": 45.00,
    "max": 250.00,
    "avg": 95.50,
    "currency": "USD"
  },
  "activities": [
    {
      "id": "act-001",
      "name": "Acropolis Guided Tour",
      "price": 45.00,
      "duration": "3 hours",
      "rating": 4.8
    }
  ],
  "source": "TBO_TEKTRAVELS",
  "timestamp": "2026-02-28T10:30:00"
}
```

## Scheduling

Jobs run on a **15-minute interval**:
- Fetches latest flight and hotel data
- Publishes to Kafka & Redis
- Saves to JSON file
- Ingests to Qdrant vector database
- Logs all activity

## Error Handling

- **Non-fatal errors** (Qdrant, File I/O) don't stop pipeline
- **Fatal errors** (API fetch, Kafka) logged and re-attempted next cycle
- All errors logged with timestamps and details

## Files Summary

| File | Purpose | Type |
|------|---------|------|
| `testamad_tbo.py` | Main orchestration engine | Script |
| `tbo_hotel_client.py` | TBO Hotel API integration | Module |
| `tektravels_flight_client.py` | TekTravels Flight API integration | Module |
| `qdrant_ingest.py` | Vector database utility | Module |
| `connect.py` | Qdrant connectivity test | Script |
| `requirements.txt` | Python dependencies | Config |
| `README.md` | This documentation | Doc |

## Dependencies

- **redis** (5.0.1) - In-memory data store & streams
- **kafka-python** (2.0.2) - Event streaming
- **schedule** (1.2.0) - Job scheduling
- **requests** (2.31.0) - HTTP API calls
- **qdrant-client** (1.8.2) - Vector database

## Key Differences from Original (Amadeus)

| Aspect | Amadeus (Original) | TBO/TekTravels (New) |
|--------|-------------------|---------------------|
| Hotel API | Amadeus Hotel API | TBO Holiday Hotel API v2.1 |
| Flight API | Amadeus Flight API | TekTravels Flight API |
| Activities | Amadeus API | Static Dataset |
| Authentication | API Key/Secret | Basic Auth (Hotels), B2B (Flights) |
| Response Format | Amadeus schema | TBO/TekTravels schemas |
| Data Output | `travel_package_data.json` | `travel_package_data_tbo.json` |

## Logging Format

```
2026-02-28 10:30:00 - INFO - Fetching travel data from TBO and TekTravels APIs...
2026-02-28 10:30:01 - INFO - Fetching flight data from TekTravels...
2026-02-28 10:30:02 - INFO - ✅ Retrieved 3 flights
...
2026-02-28 10:30:05 - INFO - 🎉 Scheduled job completed successfully!
```

## Troubleshooting

**No data returned?**
- Verify API credentials in environment variables
- Check API endpoint connectivity
- Review logs for specific error messages

**Redis connection failed?**
- Ensure Redis is running on specified host:port
- Check `REDIS_HOST` and `REDIS_PORT` env vars

**Qdrant ingestion errors?**
- Non-fatal - pipeline continues running
- Test with `python connect.py`
- Check `QDRANT_URL` configuration

## Next Steps

1. Configure environment variables for your deployment
2. Test API connectivity: `python connect.py`
3. Run pipeline: `python testamad_tbo.py`
4. Monitor logs for data flow
5. Verify output in `travel_package_data_tbo.json`
6. Check Redis/Kafka/Qdrant for data

---

**Original Amadeus-based code**: `../tbo/testamad.py` (unchanged)

**TBO/TekTravels implementation**: `./testamad_tbo.py` (this folder)

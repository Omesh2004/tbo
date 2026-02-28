import json
import os
import time
import logging
import hashlib
import sys
from datetime import datetime

from tbo_hotel_client import TBOHotelClient
from tektravels_flight_client import TekTravelsFlightClient
from qdrant_ingest import upsert_records

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'travel-data-raw')

# Qdrant config
QDRANT_COLLECTION = os.getenv('QDRANT_COLLECTION', 'travel_data')
QDRANT_VECTOR_DIM = int(os.getenv('QDRANT_VECTOR_DIM', '384'))
QDRANT_DISTANCE = os.getenv('QDRANT_DISTANCE', 'Cosine')

# Initialize API Clients
hotel_client = TBOHotelClient()
flight_client = TekTravelsFlightClient()

# Initialize Redis (optional)
redis_client = None
try:
    import redis
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=2)
    redis_client.ping()  # Test connection
    logger.info("✓ Redis connection established")
except Exception as e:
    logger.warning(f"⚠ Redis not available (optional): {e}")

# Initialize Kafka Producer (optional - skip on Windows for stability)
kafka_producer = None
if sys.platform != 'win32':  # Skip Kafka on Windows due to platform detection issues
    try:
        from kafka import KafkaProducer
        kafka_producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            request_timeout_ms=3000
        )
        logger.info("✓ Kafka connection established")
    except Exception as e:
        logger.warning(f"⚠ Kafka not available (optional): {e}")
else:
    logger.warning("⚠ Kafka skipped on Windows for stability")

STREAM_KEY = "travel_data_stream"
CONSUMER_GROUP = "travel_data_consumer_group"


def fetch_travel_data():
    """Fetch travel data from TBO Hotel API and TekTravels Flight API"""
    logger.info("Fetching travel data from TBO and TekTravels APIs...")
    data = {
        "flights": [],
        "hotels": [],
        "hotel_price_range": {},
        "activities": [],
        "source": "TBO_TEKTRAVELS",
        "fetch_mode": "live",  # Track if data is from live APIs or mock
        "api_status": {
            "flights": "pending",
            "flights_error": None,
            "hotels": "pending",
            "hotels_error": None
        }
    }

    try:
        # -------- FLIGHTS --------
        logger.info("Fetching flight data from TekTravels...")
        try:
            flights_resp = flight_client.search_flights(
                origin="MAD",
                destination="ATH",
                departure_date="2026-03-15",
                adults=1,
                trip_type="OneWay"
            )

            # DEBUG: Print actual response structure
            logger.info(f"Flight API Response Type: {type(flights_resp)}")
            if isinstance(flights_resp, dict):
                logger.info(f"Flight API Response Keys: {list(flights_resp.keys())}")

            # Extract flight data from response
            if flights_resp and isinstance(flights_resp, dict):
                # Check for error status
                if 'Status' in flights_resp:
                    status = flights_resp.get('Status', {})
                    code = status.get('Code', 'unknown')
                    desc = status.get('Description', 'Unknown error')
                    if code != 200 and code != '200':
                        raise Exception(f"API Error {code}: {desc}")
                
                flights_data = flights_resp.get('data', []) or flights_resp.get('FlightOffers', [])
                data["flights"] = flights_data[:3] if flights_data else []
                data["api_status"]["flights"] = "success"
                logger.info(f"Retrieved {len(data['flights'])} flights from live API")
            else:
                data["api_status"]["flights"] = "empty_response"
                logger.warning(f"No flight data in response: {flights_resp}")
                raise Exception("Empty response from Flight API")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Flight fetch error: {error_msg}")
            
            # Provide helpful error messages
            if "Invalid Resource Requested" in error_msg:
                helpful_msg = "TekTravels Flight API endpoint 'Invalid Resource Requested' - API format may have changed or credentials invalid. This may indicate the test credentials are expired or the API endpoint format changed."
                logger.error(f"[HINT] {helpful_msg}")
                error_msg = helpful_msg
            elif "JSONDecodeError" in error_msg and "Expecting value" in error_msg:
                helpful_msg = "TekTravels Flight API returned non-JSON response. Check API credentials and ensure endpoint is correct. May also indicate API is down or credentials expired."
                logger.error(f"[HINT] {helpful_msg}")
                error_msg = helpful_msg
            elif "401" in error_msg or "Unauthorized" in error_msg:
                helpful_msg = "TekTravels Flight API authentication failed (HTTP 401). Please check TEKTRAVELS_USERNAME and TEKTRAVELS_PASSWORD"
                logger.error(f"[HINT] {helpful_msg}")
                error_msg = helpful_msg
            
            error_msg = f"{type(e).__name__}: {error_msg}"
            data["api_status"]["flights"] = "error"
            data["api_status"]["flights_error"] = error_msg
            data["flights"] = []
            # Note: We continue without throwing, using fallback

        # -------- HOTELS --------
        logger.info("Fetching hotel data from TBO...")
        try:
            # Get hotel list for Athens
            hotels_resp = hotel_client.search_hotels(
                city_code="ATH",
                check_in="2026-03-15",
                check_out="2026-03-17",
                adults=1,
                rooms=1
            )

            # DEBUG: Print actual response structure
            logger.info(f"Hotel API Response Type: {type(hotels_resp)}")
            if isinstance(hotels_resp, dict):
                logger.info(f"Hotel API Response Keys: {list(hotels_resp.keys())}")

            # Extract hotel offer data
            if hotels_resp and isinstance(hotels_resp, dict):
                # Check for error status
                if 'Status' in hotels_resp:
                    status = hotels_resp.get('Status', {})
                    code = status.get('Code', 'unknown')
                    desc = status.get('Description', 'Unknown error')
                    if code != 200 and code != '200':
                        raise Exception(f"API Error {code}: {desc}")
                
                hotel_offers = hotels_resp.get('Hotels', []) or hotels_resp.get('data', [])
                data["hotels"] = hotel_offers[:10] if hotel_offers else []
                data["api_status"]["hotels"] = "success"
                logger.info(f"Retrieved {len(data['hotels'])} hotels from live API")
            else:
                data["api_status"]["hotels"] = "empty_response"
                logger.warning(f"No hotel data in response: {hotels_resp}")
                raise Exception("Empty response from Hotel API")

            # -------- PRICE RANGE --------
            prices = []
            for h in data["hotels"]:
                # Extract price from various possible response formats
                price = None
                if isinstance(h, dict):
                    if "Price" in h:
                        price = float(h["Price"])
                    elif "TotalPrice" in h:
                        price = float(h["TotalPrice"])
                    elif "Tariff" in h and isinstance(h["Tariff"], dict):
                        if "BaseFare" in h["Tariff"]:
                            price = float(h["Tariff"]["BaseFare"])

                if price:
                    prices.append(price)

            if prices:
                data["hotel_price_range"] = {
                    "min": min(prices),
                    "max": max(prices),
                    "avg": sum(prices) / len(prices),
                    "currency": "USD"
                }
                logger.info(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
            else:
                data["hotel_price_range"] = "No pricing available"

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Hotel fetch error: {error_msg}")
            
            # Provide helpful error messages
            if "401" in error_msg or "Login Failed" in error_msg:
                helpful_msg = "TBO Hotel API credentials are invalid (HTTP 401). Please check TBO_HOTEL_USERNAME and TBO_HOTEL_PASSWORD"
                logger.error(f"[HINT] {helpful_msg}")
                error_msg = helpful_msg
            elif "Invalid Resource Requested" in error_msg:
                helpful_msg = "TBO Hotel API endpoint error - API format may have changed or credentials invalid"
                logger.error(f"[HINT] {helpful_msg}")
                error_msg = helpful_msg
            
            error_msg = f"{type(e).__name__}: {error_msg}"
            data["api_status"]["hotels"] = "error"
            data["api_status"]["hotels_error"] = error_msg
            data["hotels"] = []
            data["hotel_price_range"] = "No pricing available"
            # Note: We continue without throwing, using fallback

        # -------- FALLBACK DATA --------
        # If both APIs failed, use mock data and indicate source
        if not data["flights"] and not data["hotels"]:
            logger.warning("⚠ Both APIs returned no data. Using mock data for demonstration...")
            data["fetch_mode"] = "mock"
            data["flights"] = [
                {
                    "id": "FL-MAD-ATH-001",
                    "origin": "MAD",
                    "destination": "ATH",
                    "departure": "2026-03-15T08:00:00",
                    "arrival": "2026-03-15T11:30:00",
                    "airline": "Iberia Express",
                    "price": 120,
                    "currency": "USD",
                    "seats_available": 5
                },
                {
                    "id": "FL-MAD-ATH-002",
                    "origin": "MAD",
                    "destination": "ATH",
                    "departure": "2026-03-15T14:30:00",
                    "arrival": "2026-03-15T18:00:00",
                    "airline": "Lufthansa",
                    "price": 150,
                    "currency": "USD",
                    "seats_available": 8
                }
            ]
            data["hotels"] = [
                {
                    "id": "HTL-ATH-001",
                    "name": "Hotel Grande Athens",
                    "city": "Athens",
                    "stars": 4,
                    "price_per_night": 85,
                    "currency": "USD",
                    "check_in": "2026-03-15",
                    "check_out": "2026-03-17",
                    "rooms_available": 12
                },
                {
                    "id": "HTL-ATH-002",
                    "name": "Acropolis View Hotel",
                    "city": "Athens",
                    "stars": 5,
                    "price_per_night": 180,
                    "currency": "USD",
                    "check_in": "2026-03-15",
                    "check_out": "2026-03-17",
                    "rooms_available": 5
                }
            ]
            data["hotel_price_range"] = {
                "min": 85,
                "max": 180,
                "avg": 132.5,
                "currency": "USD"
            }

        # -------- ACTIVITIES --------
        # Note: TBO API doesn't have activities endpoint, using static data
        logger.info("Loading activity data...")
        data["activities"] = [
            {
                "id": "act-001",
                "name": "Acropolis Guided Tour",
                "location": "Athens",
                "price": 45.00,
                "currency": "USD",
                "duration": "3 hours",
                "rating": 4.8
            },
            {
                "id": "act-002",
                "name": "Parthenon & Ancient Agora",
                "location": "Athens",
                "price": 55.00,
                "currency": "USD",
                "duration": "4 hours",
                "rating": 4.9
            },
            {
                "id": "act-003",
                "name": "Mount Lycabettus Sunset Tour",
                "location": "Athens",
                "price": 35.00,
                "currency": "USD",
                "duration": "2 hours",
                "rating": 4.7
            }
        ]

        return data

    except Exception as e:
        logger.error(f"Fatal error in fetch_travel_data: {e}")
        raise


def publish_to_kafka(data):
    """Publish data to Kafka topic (optional)"""
    if not kafka_producer:
        logger.warning("⚠ Kafka producer not available, skipping publish")
        return
    
    try:
        # Add timestamp
        data["timestamp"] = datetime.now().isoformat()

        # Send to Kafka
        kafka_producer.send(KAFKA_TOPIC, value=data)
        kafka_producer.flush()

        logger.info(f"✅ Data published to Kafka topic '{KAFKA_TOPIC}'")
    except Exception as e:
        logger.error(f"❌ Kafka Error: {e}")



def store_in_redis_stream(data):
    """Store data in Redis Stream (optional)"""
    if not redis_client:
        logger.warning("⚠ Redis client not available, skipping Redis storage")
        return
    
    try:
        # Add timestamp field
        stream_data = {
            "data": json.dumps(data),
            "timestamp": datetime.now().isoformat()
        }

        # Add to Redis Stream
        message_id = redis_client.xadd(STREAM_KEY, stream_data)
        logger.info(f"✅ Stored in Redis Stream with ID: {message_id}")

        return message_id
    except Exception as e:
        logger.error(f"❌ Redis Error: {e}")


def save_to_file(data):
    """Save data to travel_package_data_tbo.json file"""
    try:
        output_file = "travel_package_data_tbo.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"✅ Data saved to {output_file}")
        
        # Also log the status
        if data.get('api_status'):
            logger.info(f"API Status: {data['api_status']}")
    except Exception as e:
        logger.error(f"File save error: {e}")
        raise


def print_result(data):
    """Print the result JSON with status"""
    logger.info("=" * 70)
    logger.info("✅ PIPELINE COMPLETED - Travel Data Summary")
    logger.info("=" * 70)
    
    # Show fetch mode
    fetch_mode = data.get('fetch_mode', 'live')
    if fetch_mode == 'mock':
        logger.warning("📊 DATA SOURCE: Mock Data (APIs unavailable)")
    else:
        logger.info("📊 DATA SOURCE: Live TBO APIs")
    
    # Show API Status
    api_status = data.get('api_status', {})
    logger.info(f"🔍 API Status:")
    logger.info(f"   - Hotels: {api_status.get('hotels', 'unknown')}")
    if api_status.get('hotels_error'):
        logger.error(f"     Error: {api_status.get('hotels_error')}")
    logger.info(f"   - Flights: {api_status.get('flights', 'unknown')}")
    if api_status.get('flights_error'):
        logger.error(f"     Error: {api_status.get('flights_error')}")
    
    # Show data counts
    logger.info(f"📈 Data Collected:")
    logger.info(f"   - Hotels: {len(data.get('hotels', []))} properties")
    logger.info(f"   - Flights: {len(data.get('flights', []))} options")
    logger.info(f"   - Activities: {len(data.get('activities', []))} options")
    
    # Show price range
    price_range = data.get('hotel_price_range', {})
    if isinstance(price_range, dict) and 'min' in price_range:
        logger.info(f"💰 Hotel Price Range: ${price_range['min']:.2f} - ${price_range['max']:.2f}")
    
    logger.info("=" * 70)
    logger.info("📁 Full data saved to: travel_package_data_tbo.json")
    logger.info("=" * 70)
    print("\n" + "=" * 70)
    print(json.dumps(data, indent=2))
    print("=" * 70)


def _hash_id(prefix: str, obj: dict) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return f"{prefix}-" + hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]


def _summarize_json(obj: dict) -> str:
    # Minimal textual summary; for better quality, map specific fields as needed
    return json.dumps(obj, ensure_ascii=False)


def build_qdrant_records(data: dict):
    records = []
    # Flights
    for f in data.get('flights', []) or []:
        rid = _hash_id('flight', f)
        text = _summarize_json(f)
        records.append({
            'id': rid,
            'text': text,
            'type': 'flight',
            'timestamp': data.get('timestamp') or datetime.now().isoformat(),
        })
    # Hotels
    for h in data.get('hotels', []) or []:
        rid = _hash_id('hotel', h)
        text = _summarize_json(h)
        records.append({
            'id': rid,
            'text': text,
            'type': 'hotel',
            'timestamp': data.get('timestamp') or datetime.now().isoformat(),
        })
    # Activities
    for a in data.get('activities', []) or []:
        rid = _hash_id('activity', a)
        text = _summarize_json(a)
        records.append({
            'id': rid,
            'text': text,
            'type': 'activity',
            'timestamp': data.get('timestamp') or datetime.now().isoformat(),
        })
    return records


def scheduled_job():
    """Main job to run every time it's called"""
    logger.info("🔄 Starting travel data fetch...")
    try:
        # Fetch data from TBO and TekTravels APIs
        data = fetch_travel_data()

        # Publish to Kafka (optional)
        publish_to_kafka(data)

        # Store in Redis Stream (optional)
        store_in_redis_stream(data)

        # Save to file
        save_to_file(data)

        # Ingest into Qdrant
        try:
            records = build_qdrant_records(data)
            if records:
                result = upsert_records(
                    collection=QDRANT_COLLECTION,
                    records=records,
                    vector_dim=QDRANT_VECTOR_DIM,
                    distance=QDRANT_DISTANCE,
                    batch_size=256,
                )
                logger.info(f"✅ Qdrant upsert successful: {result['upserted']} records ingested")
            else:
                logger.info("⚠ No records to ingest into Qdrant this cycle")
        except Exception as qe:
            logger.error(f"❌ Qdrant ingestion error (non-fatal): {qe}")

        # Print result
        print_result(data)

        logger.info("🎉 Job completed successfully!\n")
        return True

    except Exception as e:
        logger.error(f"❌ Job failed: {e}\n")
        return False


def main():
    """Main function with flexible execution modes"""
    logger.info("="*70)
    logger.info("TBO Travel Data Pipeline - Fetching from TBO APIs and Qdrant Ingestion")
    logger.info("="*70)
    logger.info(f"Qdrant Collection: {QDRANT_COLLECTION}")
    logger.info(f"Qdrant Vector Dim: {QDRANT_VECTOR_DIM}")
    
    if redis_client:
        logger.info(f"Redis: {REDIS_HOST}:{REDIS_PORT} ✓")
    if kafka_producer:
        logger.info(f"Kafka Broker: {KAFKA_BROKER} ✓")
    logger.info("="*70)
    
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--schedule':
        # Scheduled mode with interval
        try:
            import schedule
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 15
            logger.info(f"Running in SCHEDULED mode - Every {interval} minutes\n")
            logger.info("Press Ctrl+C to stop\n")
            
            # Schedule the job
            schedule.every(interval).minutes.do(scheduled_job)
            
            # Run the job immediately on startup
            logger.info("Running initial job on startup...")
            scheduled_job()
            
            # Keep the scheduler running
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n⏹ Shutting down scheduler...")
        except ImportError:
            logger.error("Schedule library not installed. Run: pip install schedule")
        except Exception as e:
            logger.error(f"Fatal error in scheduled mode: {e}")
    else:
        # Single run mode (default)
        logger.info("Running in SINGLE RUN mode (use --schedule argument for scheduled mode)\n")
        success = scheduled_job()
        
        if success:
            logger.info("✅ Pipeline execution completed successfully")
            sys.exit(0)
        else:
            logger.error("❌ Pipeline execution failed")
            sys.exit(1)


if __name__ == "__main__":
    main()

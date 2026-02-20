import json
import os
import time
import logging
import hashlib
from datetime import datetime
from amadeus import Client, ResponseError
import redis
from kafka import KafkaProducer
import schedule

from qdrant_ingest import upsert_records

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
AMADEUS_CLIENT_ID = os.getenv('AMADEUS_CLIENT_ID', '3U0F7vgHIN9Xvq31WiQnVVPB6ohfYpT9')
AMADEUS_CLIENT_SECRET = os.getenv('AMADEUS_CLIENT_SECRET', 'g83BzbXv4GzafOCT')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'travel-data-raw')

# Qdrant config
QDRANT_COLLECTION = os.getenv('QDRANT_COLLECTION', 'travel_data')
QDRANT_VECTOR_DIM = int(os.getenv('QDRANT_VECTOR_DIM', '384'))
QDRANT_DISTANCE = os.getenv('QDRANT_DISTANCE', 'Cosine')

# Initialize Amadeus Client
amadeus = Client(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

# Initialize Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Initialize Kafka Producer
kafka_producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

STREAM_KEY = "travel_data_stream"
CONSUMER_GROUP = "travel_data_consumer_group"


def fetch_travel_data():
    """Fetch travel data from Amadeus API"""
    logger.info("Fetching travel data from Amadeus API...")
    data = {}

    try:
        # -------- FLIGHTS --------
        flights_resp = amadeus.shopping.flight_offers_search.get(
            originLocationCode="MAD",
            destinationLocationCode="ATH",
            departureDate="2026-03-15",
            adults=1
        )

        data["flights"] = flights_resp.data[:3] if flights_resp.data else []


        # -------- HOTEL IDS --------
        hotels_city = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode="ATH"
        ).data

        hotel_ids = ",".join(
            [h["hotelId"] for h in hotels_city[:10]]
        )


        # -------- HOTEL OFFERS --------
        offers_resp = amadeus.shopping.hotel_offers_search.get(
            hotelIds=hotel_ids,
            checkInDate="2026-03-15",
            checkOutDate="2026-03-17",
            adults=1
        )

        hotel_offers = offers_resp.data or []

        data["hotels"] = hotel_offers


        # -------- PRICE RANGE SAFE --------
        prices = []

        for h in hotel_offers:
            if h.get("offers"):
                prices.append(
                    float(h["offers"][0]["price"]["total"])
                )

        if prices:
            data["hotel_price_range"] = {
                "min": min(prices),
                "max": max(prices),
                "avg": sum(prices)/len(prices)
            }
        else:
            data["hotel_price_range"] = "No pricing available"


        # -------- ACTIVITIES --------
        act_resp = amadeus.shopping.activities.get(
            latitude=37.9838,
            longitude=23.7275
        )

        data["activities"] = act_resp.data[:3] if act_resp.data else []

        return data

    except ResponseError as e:
        logger.error(f"API ERROR: {e.response.body}")
        raise


def publish_to_kafka(data):
    """Publish data to Kafka topic"""
    try:
        # Add timestamp
        data["timestamp"] = datetime.now().isoformat()
        
        # Send to Kafka
        kafka_producer.send(KAFKA_TOPIC, value=data)
        kafka_producer.flush()
        
        logger.info(f"✅ Data published to Kafka topic '{KAFKA_TOPIC}'")
    except Exception as e:
        logger.error(f"❌ Kafka Error: {e}")
        raise


def store_in_redis_stream(data):
    """Store data in Redis Stream"""
    try:
        # Add timestamp field
        stream_data = {
            "data": json.dumps(data),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to Redis Stream
        message_id = redis_client.xadd(STREAM_KEY, stream_data)
        logger.info(f"Stored in Redis Stream with ID: {message_id}")
        
        return message_id
    except Exception as e:
        logger.error(f"Redis Error: {e}")
        raise


def save_to_file(data):
    """Save data to travel_package_data.json file"""
    try:
        with open("travel_package_data.json", "w") as f:
            json.dump(data, f, indent=2)
        logger.info("Data saved to travel_package_data.json")
    except Exception as e:
        logger.error(f"File save error: {e}")
        raise


def print_result(data):
    """Print the result JSON"""
    logger.info("=" * 60)
    logger.info("✅ SUCCESS - Travel Data Fetched")
    logger.info("=" * 60)
    print(json.dumps(data, indent=2))
    logger.info("=" * 60)


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
    """Main job to run every 15 minutes"""
    logger.info("🔄 Starting scheduled data fetch...")
    try:
        # Fetch data from Amadeus API
        data = fetch_travel_data()
        
        # Publish to Kafka
        publish_to_kafka(data)
        
        # Store in Redis Stream
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
                logger.info(f"Qdrant upsert: {result}")
            else:
                logger.info("No records to ingest into Qdrant this cycle")
        except Exception as qe:
            logger.error(f"Qdrant ingestion error (non-fatal): {qe}")
        
        # Print result
        print_result(data)
        
        logger.info("🎉 Scheduled job completed successfully!\n")
        
    except Exception as e:
        logger.error(f"❌ Scheduled job failed: {e}\n")


def main():
    """Main function to schedule jobs"""
    logger.info("Starting Travel Data Pipeline Service...")
    logger.info(f"Redis Host: {REDIS_HOST}:{REDIS_PORT}")
    logger.info(f"Kafka Broker: {KAFKA_BROKER}")
    logger.info(f"Kafka Topic: {KAFKA_TOPIC}")
    logger.info("Scheduled to run every 15 minutes\n")
    
    # Schedule the job to run every 15 minutes
    schedule.every(15).minutes.do(scheduled_job)
    
    # Run the job immediately on startup
    try:
        logger.info("Running initial job on startup...")
        scheduled_job()
    except Exception as e:
        logger.error(f"Initial job failed: {e}")
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        kafka_producer.close()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        kafka_producer.close()


if __name__ == "__main__":
    main()
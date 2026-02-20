#!/usr/bin/env python3
"""
Kafka Consumer for Travel Data Pipeline
Consumes messages from the travel-data-raw topic and processes them
"""

import json
import logging
from kafka import KafkaConsumer
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BROKER = "localhost:9092"  # Change to kafka:9092 when running in Docker
KAFKA_TOPIC = "travel-data-raw"
CONSUMER_GROUP = "travel-data-consumer"


def consume_travel_data():
    """Consume and process travel data from Kafka"""
    
    logger.info(f"Connecting to Kafka broker: {KAFKA_BROKER}")
    logger.info(f"Consuming from topic: {KAFKA_TOPIC}")
    logger.info(f"Consumer group: {CONSUMER_GROUP}\n")
    
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        group_id=CONSUMER_GROUP,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    
    try:
        message_count = 0
        for message in consumer:
            message_count += 1
            data = message.value
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Message #{message_count} - Offset: {message.offset}")
            logger.info(f"{'='*60}")
            
            # Process the data
            if 'timestamp' in data:
                logger.info(f"Timestamp: {data['timestamp']}")
            
            if 'flights' in data:
                logger.info(f"Flights: {len(data.get('flights', []))} offers")
            
            if 'hotels' in data:
                logger.info(f"Hotels: {len(data.get('hotels', []))} offers")
                
            if 'hotel_price_range' in data:
                price_range = data['hotel_price_range']
                if isinstance(price_range, dict):
                    logger.info(f"Hotel Price Range: ${price_range.get('min', 'N/A')} - ${price_range.get('max', 'N/A')}")
            
            if 'activities' in data:
                logger.info(f"Activities: {len(data.get('activities', []))} found")
            
            # Print full JSON for detailed inspection
            logger.info("\nFull Data:")
            print(json.dumps(data, indent=2))
            logger.info(f"{'='*60}\n")
            
    except KeyboardInterrupt:
        logger.info("\nShutting down consumer...")
    except Exception as e:
        logger.error(f"Error consuming messages: {e}")
    finally:
        consumer.close()
        logger.info("Consumer closed")


if __name__ == "__main__":
    consume_travel_data()

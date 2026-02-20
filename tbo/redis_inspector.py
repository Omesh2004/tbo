#!/usr/bin/env python3
"""
Redis Stream Inspector for Travel Data Pipeline
Inspects and displays data from Redis Streams
"""

import json
import redis
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = "localhost"  # Change to 'redis' when running in Docker
REDIS_PORT = 6379
STREAM_KEY = "travel_data_stream"


def inspect_redis_stream():
    """Inspect and display Redis Stream data"""
    
    try:
        logger.info(f"Connecting to Redis: {REDIS_HOST}:{REDIS_PORT}")
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )
        
        # Test connection
        redis_client.ping()
        logger.info("✅ Connected to Redis\n")
        
        # Get stream info
        logger.info(f"{'='*60}")
        logger.info(f"Stream Key: {STREAM_KEY}")
        logger.info(f"{'='*60}")
        
        stream_info = redis_client.xinfo_stream(STREAM_KEY)
        logger.info(f"First Entry ID: {stream_info['first-entry'][0]}")
        logger.info(f"Last Entry ID: {stream_info['last-entry'][0]}")
        logger.info(f"Length: {stream_info['length']}")
        logger.info(f"Consumers: {stream_info['ngroups']}")
        logger.info(f"Radix Tree Nodes: {stream_info['radix-tree-nodes']}")
        logger.info(f"Radix Tree Keys: {stream_info['radix-tree-keys']}\n")
        
        # Get latest entries
        logger.info(f"{'='*60}")
        logger.info("Latest 5 Entries:")
        logger.info(f"{'='*60}\n")
        
        entries = redis_client.xrevrange(STREAM_KEY, count=5)
        
        if not entries:
            logger.warning("No entries found in stream")
            return
        
        for idx, (entry_id, data) in enumerate(entries, 1):
            logger.info(f"Entry #{idx}")
            logger.info(f"ID: {entry_id}")
            logger.info(f"Timestamp: {data.get('timestamp', 'N/A')}")
            
            # Parse and display JSON data
            if 'data' in data:
                try:
                    travel_data = json.loads(data['data'])
                    logger.info(f"Flights: {len(travel_data.get('flights', []))} offers")
                    logger.info(f"Hotels: {len(travel_data.get('hotels', []))} offers")
                    logger.info(f"Activities: {len(travel_data.get('activities', []))} found")
                    
                    if 'hotel_price_range' in travel_data:
                        price_range = travel_data['hotel_price_range']
                        if isinstance(price_range, dict):
                            logger.info(f"Hotel Prices: ${price_range.get('min')} - ${price_range.get('max')}")
                    
                    logger.info("\nFull Data:")
                    print(json.dumps(travel_data, indent=2))
                except json.JSONDecodeError:
                    logger.warning("Could not parse JSON data")
            
            logger.info(f"\n{'-'*60}\n")
        
        # Consumer group info
        logger.info(f"{'='*60}")
        logger.info("Consumer Groups:")
        logger.info(f"{'='*60}")
        
        try:
            groups = redis_client.xinfo_groups(STREAM_KEY)
            if groups:
                for group in groups:
                    logger.info(f"Group: {group['name']}")
                    logger.info(f"  Consumers: {group['consumers']}")
                    logger.info(f"  Pending: {group['pending']}")
                    logger.info(f"  Last Delivered ID: {group.get('last-delivered-id', 'N/A')}\n")
            else:
                logger.info("No consumer groups found")
        except redis.ResponseError as e:
            logger.info(f"No consumer groups: {e}")
        
    except redis.ConnectionError:
        logger.error("❌ Could not connect to Redis")
        logger.error("Make sure Redis is running: docker-compose exec redis redis-cli")
    except redis.ResponseError as e:
        logger.error(f"Redis error: {e}")
        logger.info("Stream may not exist yet. Wait for first data fetch.")
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    inspect_redis_stream()

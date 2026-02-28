#!/usr/bin/env python3
"""
Quick test to verify JSON generation with api_status
"""

import json
import logging
from datetime import datetime
from tbo_hotel_client import TBOHotelClient
from tektravels_flight_client import TekTravelsFlightClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize API Clients
hotel_client = TBOHotelClient()
flight_client = TekTravelsFlightClient()

def fetch_and_save():
    """Fetch travel data and save to JSON"""
    logger.info("Starting data fetch...")
    data = {
        "flights": [],
        "hotels": [],
        "hotel_price_range": {},
        "activities": [],
        "source": "TBO_TEKTRAVELS",
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

            # Extract flight data from response
            if flights_resp and isinstance(flights_resp, dict):
                flights_data = flights_resp.get('data', []) or flights_resp.get('FlightOffers', [])
                data["flights"] = flights_data[:3] if flights_data else []
                data["api_status"]["flights"] = "success"
                logger.info(f"✓ Retrieved {len(data['flights'])} flights")
            else:
                data["api_status"]["flights"] = "empty_response"
                logger.warning("No flight data in response")
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Flight fetch error: {error_msg}")
            data["api_status"]["flights"] = "error"
            data["api_status"]["flights_error"] = error_msg
            data["flights"] = []

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

            # Extract hotel offer data
            if hotels_resp and isinstance(hotels_resp, dict):
                hotel_offers = hotels_resp.get('Hotels', []) or hotels_resp.get('data', [])
                data["hotels"] = hotel_offers[:10] if hotel_offers else []
                data["api_status"]["hotels"] = "success"
                logger.info(f"✓ Retrieved {len(data['hotels'])} hotels")
            else:
                data["api_status"]["hotels"] = "empty_response"
                logger.warning("No hotel data in response")

            # Price range
            prices = []
            for h in data["hotels"]:
                price = None
                if isinstance(h, dict):
                    if "Price" in h:
                        price = float(h["Price"])
                    elif "TotalPrice" in h:
                        price = float(h["TotalPrice"])
                if price:
                    prices.append(price)

            if prices:
                data["hotel_price_range"] = {
                    "min": min(prices),
                    "max": max(prices),
                    "avg": sum(prices) / len(prices),
                    "currency": "USD"
                }
            else:
                data["hotel_price_range"] = "No pricing available"

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Hotel fetch error: {error_msg}")
            data["api_status"]["hotels"] = "error"
            data["api_status"]["hotels_error"] = error_msg
            data["hotels"] = []
            data["hotel_price_range"] = "No pricing available"

        # -------- ACTIVITIES --------
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

        # Add timestamp
        data["timestamp"] = datetime.now().isoformat()

        # Save to file
        output_file = "travel_package_data_tbo.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Data saved to {output_file}")

        # Print result
        logger.info("="*60)
        logger.info("SUCCESS - Travel Data Fetched and Saved")
        logger.info("="*60)
        print(json.dumps(data, indent=2))

        return True

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return False

if __name__ == "__main__":
    success = fetch_and_save()
    exit(0 if success else 1)

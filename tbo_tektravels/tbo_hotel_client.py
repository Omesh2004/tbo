import os
import json
import logging
import requests
from datetime import datetime
from base64 import b64encode

logger = logging.getLogger(__name__)

class TBOHotelClient:
    """TBO Hotel API Client using Basic Authentication"""

    def __init__(self, username: str = None, password: str = None, base_url: str = None):
        self.username = username or os.getenv('TBO_HOTEL_USERNAME', 'Hackathon')
        self.password = password or os.getenv('TBO_HOTEL_PASSWORD', 'Hackathon@1234')
        self.base_url = base_url or os.getenv('TBO_HOTEL_BASE_URL', 'http://api.tbotechnology.in/TBOHolidays_HotelAPI')

        # Prepare Basic Auth header
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = b64encode(credentials.encode()).decode()
        self.headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, endpoint: str, method: str = 'GET', data: dict = None):
        """Make HTTP request to TBO Hotel API"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"TBO Hotel API Error ({endpoint}): {str(e)}")
            raise

    def search_hotels(self, city_code: str, check_in: str, check_out: str,
                     adults: int = 1, children: int = 0, rooms: int = 1) -> dict:
        """
        Search hotels in a city

        Args:
            city_code: City code (e.g., 'ATH' for Athens)
            check_in: Check-in date (YYYY-MM-DD format)
            check_out: Check-out date (YYYY-MM-DD format)
            adults: Number of adults
            children: Number of children
            rooms: Number of rooms

        Returns:
            Hotel search results
        """
        logger.info(f"Searching hotels in {city_code} from {check_in} to {check_out}")

        search_payload = {
            "CityCode": city_code,
            "CheckInDate": check_in,
            "CheckOutDate": check_out,
            "AdultCount": adults,
            "ChildCount": children,
            "RoomCount": rooms
        }

        return self._make_request('/Search', method='POST', data=search_payload)

    def get_hotel_details(self, hotel_code: str) -> dict:
        """Get details for a specific hotel"""
        logger.info(f"Fetching details for hotel: {hotel_code}")

        payload = {
            "HotelCode": hotel_code
        }

        return self._make_request('/HotelDetails', method='POST', data=payload)

    def prebook_hotel(self, hotel_code: str, check_in: str, check_out: str,
                     rooms: int = 1, guest_name: str = "Guest") -> dict:
        """Pre-book a hotel"""
        logger.info(f"Pre-booking hotel: {hotel_code}")

        prebook_payload = {
            "HotelCode": hotel_code,
            "CheckInDate": check_in,
            "CheckOutDate": check_out,
            "RoomCount": rooms,
            "GuestName": guest_name
        }

        return self._make_request('/PreBook', method='POST', data=prebook_payload)

    def book_hotel(self, prebook_ref_id: str, guest_email: str = None,
                  guest_phone: str = None) -> dict:
        """Complete hotel booking"""
        logger.info(f"Completing booking for ref: {prebook_ref_id}")

        book_payload = {
            "PrebookRefId": prebook_ref_id,
            "GuestEmail": guest_email or "guest@example.com",
            "GuestPhone": guest_phone or "+1234567890"
        }

        return self._make_request('/Book', method='POST', data=book_payload)

    def get_countries(self) -> dict:
        """Get list of countries"""
        logger.info("Fetching countries list")
        return self._make_request('/CountryList', method='GET')

    def get_cities(self, country_code: str) -> dict:
        """Get cities in a country"""
        logger.info(f"Fetching cities in {country_code}")

        payload = {
            "CountryCode": country_code
        }

        return self._make_request('/CityList', method='POST', data=payload)

    def get_hotel_codes_by_city(self, city_code: str) -> dict:
        """Get hotel codes in a city"""
        logger.info(f"Fetching hotel codes for city: {city_code}")

        payload = {
            "CityCode": city_code
        }

        return self._make_request('/HotelCodeList', method='GET')

    def get_tbo_hotel_codes(self, city_code: str = None) -> dict:
        """Get TBO hotel codes"""
        logger.info(f"Fetching TBO hotel codes for city: {city_code}")

        payload = {
            "CityCode": city_code
        } if city_code else {}

        return self._make_request('/TBOHotelCodeList', method='POST', data=payload)

    def cancel_booking(self, booking_id: str, reason: str = None) -> dict:
        """Cancel a booking"""
        logger.info(f"Cancelling booking: {booking_id}")

        cancel_payload = {
            "BookingId": booking_id,
            "CancellationReason": reason or "Customer Request"
        }

        return self._make_request('/Cancel', method='POST', data=cancel_payload)

    def get_booking_details(self, booking_id: str) -> dict:
        """Get details of a booking"""
        logger.info(f"Fetching booking details for: {booking_id}")

        payload = {
            "BookingId": booking_id
        }

        return self._make_request('/BookingDetail', method='POST', data=payload)

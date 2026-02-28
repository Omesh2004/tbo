import os
import json
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class TekTravelsFlightClient:
    """TekTravels Flight API Client for B2B Flight Search and Booking"""

    def __init__(self, user_id: str = None, password: str = None, base_url: str = None):
        self.user_id = user_id or os.getenv('TEKTRAVELS_FLIGHT_USER_ID', 'Hackathon')
        self.password = password or os.getenv('TEKTRAVELS_FLIGHT_PASSWORD', 'Hackathon@123')
        self.base_url = base_url or os.getenv('TEKTRAVELS_FLIGHT_BASE_URL', 'https://api.tektravels.com')

        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Session credentials to be sent with each request
        self.session_data = {
            'UserId': self.user_id,
            'Password': self.password
        }

    def _make_request(self, endpoint: str, method: str = 'POST', data: dict = None):
        """Make HTTP request to TekTravels Flight API with enhanced error handling"""
        url = f"{self.base_url}{endpoint}"

        # Add session credentials to the request
        request_data = {**self.session_data}
        if data:
            request_data.update(data)

        try:
            if method == 'POST':
                response = requests.post(url, headers=self.headers, json=request_data, timeout=30)
            elif method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            
            # Check if response is actually JSON
            if response.text.strip() == '':
                raise ValueError("Empty response from API")
            
            # Check for error messages in plain text
            if 'Invalid Resource Requested' in response.text:
                raise ValueError(f"API Error: Invalid Resource Requested. Endpoint: {endpoint}")
            
            if 'Unauthorized' in response.text or 'Authentication' in response.text:
                raise ValueError(f"API Error: Authentication failed. Please check credentials.")
            
            # Try to parse JSON
            try:
                return response.json()
            except json.JSONDecodeError as e:
                # If not valid JSON, return the raw text as error
                logger.error(f"Response is not valid JSON: {response.text[:200]}")
                raise ValueError(f"API returned non-JSON response: {response.text[:100]}")

        except requests.exceptions.RequestException as e:
            logger.error(f"TekTravels Flight API Error ({endpoint}): {str(e)}")
            raise

    def search_flights(self, origin: str, destination: str, departure_date: str,
                      return_date: str = None, adults: int = 1, children: int = 0,
                      infants: int = 0, trip_type: str = 'OneWay') -> dict:
        """
        Search flights

        Args:
            origin: Origin airport code (e.g., 'MAD')
            destination: Destination airport code (e.g., 'ATH')
            departure_date: Departure date (YYYY-MM-DD format)
            return_date: Return date for round trips (YYYY-MM-DD format)
            adults: Number of adult passengers
            children: Number of child passengers
            infants: Number of infant passengers
            trip_type: 'OneWay', 'Return', or 'MultiCity'

        Returns:
            Flight search results
        """
        logger.info(f"Searching flights from {origin} to {destination} on {departure_date}")

        search_payload = {
            "Origin": origin,
            "Destination": destination,
            "DepartureDate": departure_date,
            "ReturnDate": return_date or departure_date,
            "AdultCount": adults,
            "ChildCount": children,
            "InfantCount": infants,
            "TripType": trip_type,
            "IsDirectFlight": False,
            "PreferredAirlines": []
        }

        return self._make_request('/FlightSearch', method='POST', data=search_payload)

    def get_flight_fare_rules(self, flight_key: str) -> dict:
        """Get fare rules for a flight"""
        logger.info(f"Fetching fare rules for flight key: {flight_key}")

        payload = {
            "FlightKey": flight_key
        }

        return self._make_request('/GetFareRules', method='POST', data=payload)

    def prebook_flight(self, flight_key: str, passengers: list) -> dict:
        """
        Pre-book a flight

        Args:
            flight_key: Flight identifier from search results
            passengers: List of passenger information dicts

        Returns:
            Pre-booking reference
        """
        logger.info(f"Pre-booking flight: {flight_key}")

        prebook_payload = {
            "FlightKey": flight_key,
            "Passengers": passengers or [{
                "Title": "Mr",
                "FirstName": "Guest",
                "LastName": "Traveler",
                "DOB": "1990-01-01",
                "Gender": "M",
                "Nationality": "US",
                "PassportNumber": "AB123456"
            }]
        }

        return self._make_request('/PreBook', method='POST', data=prebook_payload)

    def book_flight(self, prebook_id: str, contact_email: str = None,
                   contact_phone: str = None) -> dict:
        """
        Complete flight booking

        Args:
            prebook_id: Pre-booking reference ID
            contact_email: Passenger contact email
            contact_phone: Passenger contact phone

        Returns:
            Booking confirmation
        """
        logger.info(f"Booking flight with prebook ID: {prebook_id}")

        book_payload = {
            "PreBookingId": prebook_id,
            "ContactEmail": contact_email or "passenger@example.com",
            "ContactPhone": contact_phone or "+1234567890"
        }

        return self._make_request('/Book', method='POST', data=book_payload)

    def get_booking_details(self, booking_id: str) -> dict:
        """Get booking details"""
        logger.info(f"Fetching booking details for: {booking_id}")

        payload = {
            "BookingId": booking_id
        }

        return self._make_request('/GetBookingDetails', method='POST', data=payload)

    def cancel_booking(self, booking_id: str, remarks: str = None) -> dict:
        """Cancel a flight booking"""
        logger.info(f"Cancelling flight booking: {booking_id}")

        cancel_payload = {
            "BookingId": booking_id,
            "Remarks": remarks or "Customer Request"
        }

        return self._make_request('/CancelBooking', method='POST', data=cancel_payload)

    def get_seat_map(self, flight_key: str) -> dict:
        """Get seat map for a flight"""
        logger.info(f"Fetching seat map for flight: {flight_key}")

        payload = {
            "FlightKey": flight_key
        }

        return self._make_request('/GetSeatMap', method='POST', data=payload)

    def get_baggage_details(self, flight_key: str) -> dict:
        """Get baggage information for a flight"""
        logger.info(f"Fetching baggage details for flight: {flight_key}")

        payload = {
            "FlightKey": flight_key
        }

        return self._make_request('/GetBaggageDetails', method='POST', data=payload)

    def add_ancillary_services(self, booking_id: str, services: list) -> dict:
        """Add ancillary services (seat selection, baggage, etc.) to booking"""
        logger.info(f"Adding ancillary services to booking: {booking_id}")

        payload = {
            "BookingId": booking_id,
            "AncillaryServices": services
        }

        return self._make_request('/AddAncillaryServices', method='POST', data=payload)

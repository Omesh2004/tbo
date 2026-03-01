"""Integration with Amadeus Agent (TBO)"""
import httpx
from typing import Dict, Any, List, Optional
from app.config import settings
from app.logger import logger
from app.exceptions import AgentIntegrationError


class AmadeusAgentClient:
    """Client for Amadeus/TBO Agent integration"""

    def __init__(self):
        """Initialize Amadeus agent client"""
        self.base_url = settings.amadeus_agent_url
        self.timeout = settings.query_timeout

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        passengers: int = 1,
        preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for flights
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            departure_date: Departure date
            return_date: Return date (optional for round trips)
            passengers: Number of passengers
            preferences: Search preferences
            
        Returns:
            List of flight results
        """
        logger.info(f"Searching flights from {origin} to {destination}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json={
                        "origin": origin,
                        "destination": destination,
                        "departure_date": departure_date,
                        "return_date": return_date,
                        "passengers": passengers,
                        "preferences": preferences or {}
                    }
                )
                
                if response.status_code != 200:
                    raise AgentIntegrationError(
                        f"Amadeus agent returned {response.status_code}"
                    )
                
                return response.json().get("results", [])
                
        except Exception as e:
            logger.error(f"Flight search failed: {str(e)}")
            return []

    async def get_flight_details(self, flight_id: str) -> Dict[str, Any]:
        """Get detailed information for a flight"""
        logger.info(f"Fetching details for flight {flight_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/flight/{flight_id}"
                )
                
                if response.status_code == 200:
                    return response.json()
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching flight details: {str(e)}")
            return {}

    async def get_travel_packages(
        self,
        origin: str,
        destination: str,
        dates: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Get travel packages (flight + hotel combinations)"""
        logger.info(f"Fetching packages from {origin} to {destination}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/packages",
                    json={
                        "origin": origin,
                        "destination": destination,
                        "dates": dates
                    }
                )
                
                if response.status_code == 200:
                    return response.json().get("packages", [])
                return []
                
        except Exception as e:
            logger.error(f"Error fetching travel packages: {str(e)}")
            return []

    async def verify_availability(
        self,
        flight_id: str,
        passengers: int
    ) -> Dict[str, Any]:
        """Verify flight availability"""
        logger.info(f"Verifying availability for flight {flight_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/verify",
                    json={"flight_id": flight_id, "passengers": passengers}
                )
                
                if response.status_code == 200:
                    return response.json()
                return {"available": False}
                
        except Exception as e:
            logger.error(f"Error verifying availability: {str(e)}")
            return {"available": False}

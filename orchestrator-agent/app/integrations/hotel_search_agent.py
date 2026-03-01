"""Integration with Hotel Search Agent"""
import httpx
from typing import Dict, Any, List, Optional
from app.config import settings
from app.logger import logger
from app.exceptions import AgentIntegrationError


class HotelSearchAgentClient:
    """Client for Hotel Search Agent integration"""

    def __init__(self):
        """Initialize hotel search agent client"""
        self.base_url = settings.hotel_search_agent_url
        self.timeout = settings.query_timeout

    async def search_hotels(
        self,
        location: str,
        check_in: str,
        check_out: str,
        guests: int,
        preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for hotels
        
        Args:
            location: Hotel location
            check_in: Check-in date
            check_out: Check-out date
            guests: Number of guests
            preferences: Search preferences
            
        Returns:
            List of hotel results
        """
        logger.info(f"Searching hotels in {location}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json={
                        "location": location,
                        "check_in": check_in,
                        "check_out": check_out,
                        "guests": guests,
                        "preferences": preferences or {}
                    }
                )
                
                if response.status_code != 200:
                    raise AgentIntegrationError(
                        f"Hotel search agent returned {response.status_code}"
                    )
                
                return response.json().get("results", [])
                
        except Exception as e:
            logger.error(f"Hotel search failed: {str(e)}")
            return []

    async def get_hotel_details(self, hotel_id: str) -> Dict[str, Any]:
        """Get detailed information for a hotel"""
        logger.info(f"Fetching details for hotel {hotel_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/hotel/{hotel_id}"
                )
                
                if response.status_code == 200:
                    return response.json()
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching hotel details: {str(e)}")
            return {}

    async def get_availability(
        self,
        hotel_id: str,
        check_in: str,
        check_out: str
    ) -> Dict[str, Any]:
        """Check hotel availability"""
        logger.info(f"Checking availability for hotel {hotel_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/availability",
                    json={
                        "hotel_id": hotel_id,
                        "check_in": check_in,
                        "check_out": check_out
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                return {"available": False}
                
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            return {"available": False}

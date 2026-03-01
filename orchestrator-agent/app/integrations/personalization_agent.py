"""Integration with Personalization Agent"""
import httpx
from typing import Dict, Any, Optional
from app.config import settings
from app.logger import logger
from app.exceptions import AgentIntegrationError


class PersonalizationAgentClient:
    """Client for Personalization Agent integration"""

    def __init__(self):
        """Initialize personalization agent client"""
        self.base_url = settings.personalization_agent_url
        self.timeout = settings.query_timeout

    async def rank_results(
        self,
        user_id: str,
        results: list,
        context: Optional[Dict[str, Any]] = None
    ) -> list:
        """
        Rank results based on user personalization
        
        Args:
            user_id: User identifier
            results: Results to rank
            context: Additional context
            
        Returns:
            Ranked results
        """
        logger.info(f"Ranking results for user {user_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/rank",
                    json={
                        "user_id": user_id,
                        "results": results,
                        "context": context or {}
                    }
                )
                
                if response.status_code != 200:
                    raise AgentIntegrationError(
                        f"Personalization agent returned {response.status_code}"
                    )
                
                return response.json().get("ranked_results", results)
                
        except Exception as e:
            logger.error(f"Personalization ranking failed: {str(e)}")
            return results  # Return original results on error

    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user personalization profile"""
        logger.info(f"Fetching profile for user {user_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/user/{user_id}/profile"
                )
                
                if response.status_code == 200:
                    return response.json()
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            return {}

    async def apply_business_rules(
        self,
        user_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply business rules for user"""
        logger.info(f"Applying business rules for user {user_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/rules/apply",
                    json={"user_id": user_id, "data": data}
                )
                
                if response.status_code == 200:
                    return response.json().get("result", data)
                return data
                
        except Exception as e:
            logger.error(f"Error applying business rules: {str(e)}")
            return data

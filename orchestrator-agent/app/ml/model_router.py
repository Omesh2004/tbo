"""Model Router - Routes queries between Phi4 and Llama"""
import httpx
import asyncio
from typing import Dict, Any, Optional
from app.config import settings
from app.logger import logger
from app.exceptions import ModelNotAvailableError, TimeoutError


class ModelRouter:
    """Route queries to appropriate model based on complexity"""

    def __init__(self):
        """Initialize model router"""
        self.ollama_host = settings.ollama_host
        self.phi4_model = settings.phi4_model
        self.llama_model = settings.llama_model
        # Increase timeout to 300 seconds (5 minutes) for large models
        self.timeout = 300
        self.max_retries = 2

    async def route_query(
        self,
        query: str,
        complexity_level: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route query to appropriate model
        
        Args:
            query: User query
            complexity_level: 'simple' or 'complex'
            context: Additional context data
            
        Returns:
            Model response with routing info
        """
        model = self.llama_model if complexity_level == "complex" else self.phi4_model
        
        logger.info(f"Routing query to {model} (complexity: {complexity_level})")
        logger.info(f"Ollama Host: {self.ollama_host}")
        
        try:
            response = await self._call_model(model, query, context)
            return {
                "model": model,
                "complexity_level": complexity_level,
                "response": response,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Model call failed: {str(e)}", exc_info=True)
            raise

    async def _call_model(
        self,
        model: str,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> str:
        """Call Ollama model with retry logic"""
        prompt = self._build_prompt(query, context)
        
        logger.debug(f"[Attempt {retry_count + 1}/{self.max_retries}] Calling {model}")
        logger.debug(f"Ollama endpoint: {self.ollama_host}/api/generate")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # First verify Ollama is reachable
                try:
                    health_response = await client.get(
                        f"{self.ollama_host}/api/tags",
                        timeout=10
                    )
                    logger.debug(f"Ollama health check: {health_response.status_code}")
                except Exception as health_e:
                    logger.error(f"Ollama health check failed: {str(health_e)}")
                    raise ModelNotAvailableError(
                        f"Cannot reach Ollama at {self.ollama_host}: {str(health_e)}"
                    )
                
                # Call the model
                logger.info(f"Sending query to {model} model...")
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7
                }
                logger.debug(f"Request payload: {payload}")
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json=payload,
                    timeout=self.timeout
                )
                
                logger.debug(f"Ollama response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f"Model response length: {len(result.get('response', ''))}")
                    return result.get("response", "")
                elif response.status_code == 404:
                    raise ModelNotAvailableError(
                        f"Model '{model}' not found in Ollama. Available models may need to be pulled."
                    )
                else:
                    error_detail = response.text if response.text else f"Status {response.status_code}"
                    logger.error(f"Ollama error response: {error_detail}")
                    raise ModelNotAvailableError(
                        f"Model {model} returned status {response.status_code}: {error_detail}"
                    )
                
        except asyncio.TimeoutError:
            logger.error(f"Model {model} request timed out after {self.timeout}s")
            if retry_count < self.max_retries:
                logger.info(f"Retrying ({retry_count + 1}/{self.max_retries})...")
                await asyncio.sleep(5)
                return await self._call_model(model, query, context, retry_count + 1)
            raise TimeoutError(
                f"Model {model} request timed out after {self.timeout}s (tried {self.max_retries} times)"
            )
        except ModelNotAvailableError:
            raise
        except Exception as e:
            logger.error(f"Error calling model {model}: {str(e)}", exc_info=True)
            if retry_count < self.max_retries:
                logger.info(f"Retrying ({retry_count + 1}/{self.max_retries})...")
                await asyncio.sleep(5)
                return await self._call_model(model, query, context, retry_count + 1)
            raise ModelNotAvailableError(f"Error calling model {model}: {str(e)}")

    @staticmethod
    def _build_prompt(query: str, context: Optional[Dict[str, Any]]) -> str:
        """Build prompt with context"""
        import json
        prompt = f"Query: {query}\n"
        
        if context:
            if "user_profile" in context:
                profile = context['user_profile']
                if isinstance(profile, dict):
                    profile = json.dumps(profile)
                prompt += f"\nUser Profile: {profile}\n"
            if "business_rules" in context:
                rules = context['business_rules']
                if isinstance(rules, (dict, list)):
                    rules = json.dumps(rules)
                prompt += f"Business Rules: {rules}\n"
            if "previous_context" in context:
                prev = context['previous_context']
                if isinstance(prev, (dict, list)):
                    prev = json.dumps(prev)
                prompt += f"Previous Context: {prev}\n"
        
        prompt += "\nResponse:"
        return prompt

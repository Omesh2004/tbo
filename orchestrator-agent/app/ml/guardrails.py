"""Input Guardrails for Chatbot Security"""
import re
from typing import Tuple
from app.logger import logger
from app.exceptions import GuardrailException


class InputGuardrail:
    """Pre-filter user queries for prompt injection and inappropriate content"""

    # Obvious injection patterns
    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?(previous\s+)?instructions",
        r"(?i)system\s+prompt",
        r"(?i)disregard\s+(all\s+)?(previous\s+)?instructions",
        r"(?i)you\s+are\s+now",
        r"(?i)forget\s+(all\s+)?(previous\s+)?instructions",
        r"(?i)override\s+instructions",
        r"(?i)bypass\s+restrictions",
    ]

    # Forbidden or highly inappropriate keywords/topics
    FORBIDDEN_KEYWORDS = [
        "hack", "exploit", "bypass", "malware", "virus", "phishing",
        "nsfw", "porn", "suicide", "murder", "bomb", "terrorist"
    ]

    def __init__(self):
        """Initialize InputGuardrail"""
        self.compiled_patterns = [re.compile(p) for p in self.INJECTION_PATTERNS]
        self.forbidden_patterns = [re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE) for kw in self.FORBIDDEN_KEYWORDS]

    def validate_query(self, query: str) -> None:
        """
        Validate the user query against guardrail rules.
        
        Args:
            query: The user query string
            
        Raises:
            GuardrailException: If the query violates a rule
        """
        if not query or not query.strip():
            logger.warning("Guardrail triggered: Empty query")
            raise GuardrailException("Please provide a valid query.")

        # Check for injection patterns
        for pattern in self.compiled_patterns:
            if pattern.search(query):
                logger.warning(f"Guardrail triggered (Injection): {query}")
                raise GuardrailException(
                    "I am a travel assistant and cannot process instructions that attempt to alter my programming."
                )

        # Check for forbidden keywords using word boundaries to prevent Scunthorpe problem (e.g., 'Bombay' matching 'bomb')
        for pattern in self.forbidden_patterns:
            if pattern.search(query):
                logger.warning(f"Guardrail triggered (Forbidden Topic): Pattern '{pattern.pattern}' found in query.")
                raise GuardrailException(
                    "I am a professional travel assistant and cannot assist with that topic. Please ask me about travel, flights, or hotels."
                )
        
        logger.debug("Guardrail passed for query.")


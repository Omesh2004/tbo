"""Query Complexity Detector - Determines if query is simple or complex"""
import re
from typing import Tuple
from app.logger import logger


class ComplexityDetector:
    """Analyze query complexity to route to appropriate model"""

    # Simple query keywords
    SIMPLE_KEYWORDS = {
        "hello", "hi", "thanks", "thank you", "bye", "goodbye",
        "what is", "how much", "when is", "where is", "who is",
        "yes", "no", "ok", "okay", "sure"
    }

    # Complex query keywords
    COMPLEX_KEYWORDS = {
        "compare", "analyze", "optimize", "recommend", "suggest",
        "detailed", "comprehensive", "complex", "integrate", "orchestrate",
        "multiple", "combined", "cross", "requirements", "constraints"
    }

    def __init__(self, complexity_threshold: float = 0.6):
        """
        Initialize complexity detector
        
        Args:
            complexity_threshold: Score threshold for complex queries (0-1)
        """
        self.complexity_threshold = complexity_threshold

    def analyze(self, query: str) -> Tuple[str, float]:
        """
        Analyze query complexity
        
        Args:
            query: User query string
            
        Returns:
            Tuple of (complexity_level: 'simple'/'complex', score: 0-1)
        """
        try:
            score = self._calculate_score(query)
            level = "complex" if score >= self.complexity_threshold else "simple"
            
            logger.info(f"Query complexity analysis: {level} (score: {score:.2f})")
            return level, score
            
        except Exception as e:
            logger.error(f"Error analyzing query complexity: {str(e)}")
            return "complex", 0.5  # Default to complex on error

    def _calculate_score(self, query: str) -> float:
        """Calculate complexity score (0-1)"""
        query_lower = query.lower()
        length = len(query.split())
        
        # Base score from query length
        length_score = min(length / 20, 1.0)  # Normalize by 20 words
        
        # Keyword-based scoring
        keyword_score = self._keyword_score(query_lower)
        
        # Structural scoring
        structure_score = self._structure_score(query)
        
        # Combined score
        final_score = (length_score * 0.3 + keyword_score * 0.4 + structure_score * 0.3)
        
        return min(max(final_score, 0.0), 1.0)

    def _keyword_score(self, query_lower: str) -> float:
        """Score based on keywords"""
        complex_count = sum(1 for kw in self.COMPLEX_KEYWORDS if kw in query_lower)
        simple_count = sum(1 for kw in self.SIMPLE_KEYWORDS if kw in query_lower)
        
        if complex_count + simple_count == 0:
            return 0.5  # Neutral
        
        return complex_count / (complex_count + simple_count)

    def _structure_score(self, query: str) -> float:
        """Score based on query structure"""
        score = 0.0
        
        # Multiple conditions
        if " and " in query.lower() or " or " in query.lower():
            score += 0.3
        
        # Questions with multiple clauses
        if query.count(",") > 1 or query.count(";") > 0:
            score += 0.2
        
        # Parentheses or brackets
        if "(" in query and ")" in query:
            score += 0.2
        
        # Multiple question marks
        if query.count("?") > 1:
            score += 0.15
        
        # Specific patterns for complex queries
        if re.search(r"(aggregate|combine|reconcile|compare|analyze)", query.lower()):
            score += 0.2
        
        return min(score, 1.0)

"""Custom exceptions"""


class OrchestratorException(Exception):
    """Base exception for orchestrator"""
    pass


class ModelNotAvailableError(OrchestratorException):
    """Model not available"""
    pass


class QueryComplexityError(OrchestratorException):
    """Error analyzing query complexity"""
    pass


class AgentIntegrationError(OrchestratorException):
    """Error integrating with agent"""
    pass


class TimeoutError(OrchestratorException):
    """Operation timeout"""
    pass


class InvalidQueryError(OrchestratorException):
    """Invalid query format"""
    pass

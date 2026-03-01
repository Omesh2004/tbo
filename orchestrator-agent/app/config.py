"""Configuration management for Orchestrator Agent"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application Settings"""

    # Environment
    environment: str = "development"
    debug: bool = True

    # Model Configuration
    ollama_host: str = "http://localhost:11434"
    phi4_model: str = "phi4:latest"
    llama_model: str = "llama2:latest"
    complexity_threshold: float = 0.6

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/orchestrator"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Agent Endpoints
    personalization_agent_url: str = "http://localhost:8001"
    hotel_search_agent_url: str = "http://localhost:8002"
    amadeus_agent_url: str = "http://localhost:8003"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # Timeouts
    query_timeout: int = 300
    model_timeout: int = 300

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

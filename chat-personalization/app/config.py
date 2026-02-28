"""Configuration for Chat Personalization Service"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/chat_personalization"
    
    # Application
    app_name: str = "Chat Personalization Service"
    debug: bool = False
    environment: str = "development"
    
    # API
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # LLM Context
    max_context_length: int = 2000
    enable_context_caching: bool = True
    
    # Analysis
    min_prompts_for_analysis: int = 3
    max_prompts_to_analyze: int = 100
    analysis_batch_size: int = 20
    
    # Features
    enable_real_time_update: bool = True
    enable_sentiment_analysis: bool = True
    enable_topic_modeling: bool = False
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

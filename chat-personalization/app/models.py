"""Pydantic models for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class UserProfile(BaseModel):
    """User profile model"""
    user_id: str
    google_email: str
    google_id: str
    name: str
    picture_url: Optional[str] = None
    locale: str = "en"
    
    class Config:
        from_attributes = True


class PromptInput(BaseModel):
    """Input for saving a prompt"""
    user_id: str
    prompt_text: str
    response_text: Optional[str] = None
    category: Optional[str] = "general"
    tags: Optional[List[str]] = []
    
    class Config:
        from_attributes = True


class PromptHistoryResponse(BaseModel):
    """Response with prompt history"""
    id: str
    user_id: str
    prompt_text: str
    response_text: Optional[str]
    category: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class UserCharacteristics(BaseModel):
    """User characteristics model"""
    user_id: str
    travel_preferences: Dict[str, Any]
    budget_profile: Dict[str, Any]
    booking_patterns: Dict[str, Any]
    interests: List[str]
    personality_traits: List[str]
    pain_points: List[str]
    motivation_drivers: List[str]
    decision_style: str
    tone_preference: str
    communication_style: str
    detailed_summary: str
    risk_tolerance: str = "moderate"
    
    class Config:
        from_attributes = True


class LLMContextRequest(BaseModel):
    """Request to get LLM context for a user"""
    user_id: str
    include_full_history: Optional[bool] = False
    max_context_tokens: Optional[int] = 2000


class LLMContextResponse(BaseModel):
    """Response with LLM context for a user"""
    user_id: str
    user_name: str
    system_context: str
    detailed_summary: str
    key_characteristics: Dict[str, Any]
    user_interests: List[str]
    tone_preference: str
    communication_style: str
    confidence_score: float
    last_analyzed_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    """Request to trigger analysis of user prompts"""
    user_id: str
    force_reanalyze: Optional[bool] = False


class AnalysisResponse(BaseModel):
    """Response from analysis"""
    status: str
    user_id: str
    prompts_analyzed: int
    characteristics: UserCharacteristics
    confidence_score: float
    analysis_timestamp: datetime


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: datetime

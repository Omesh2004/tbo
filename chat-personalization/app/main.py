"""Main FastAPI application for Chat Personalization Service"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from app.config import settings
from app.db import connect_db, disconnect_db, db
from app.models import (
    PromptInput, PromptHistoryResponse, LLMContextRequest, 
    LLMContextResponse, AnalysisRequest, AnalysisResponse,
    UserCharacteristics, HealthCheckResponse
)
from app.ml.analyzer import PromptAnalyzer

# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize analyzer
analyzer = PromptAnalyzer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info("Starting Chat Personalization Service...")
    try:
        await connect_db()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to start service: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Chat Personalization Service...")
    try:
        await disconnect_db()
        logger.info("Database disconnected")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.api_version,
        "timestamp": datetime.utcnow(),
    }


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.post(f"{settings.api_prefix}/users/create", response_model=dict)
async def create_user(user_data: dict):
    """
    Create a new user profile (from Google OAuth)
    
    Call this endpoint after Google OAuth login to create user profile.
    """
    try:
        user_id = user_data.get("user_id")
        google_email = user_data.get("google_email")
        google_id = user_data.get("google_id")
        name = user_data.get("name")
        picture_url = user_data.get("picture_url")
        
        # Validate required fields
        if not all([user_id, google_email, google_id, name]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: user_id, google_email, google_id, name"
            )
        
        logger.info(f"Creating user profile for {google_email}")
        
        # Check if user already exists
        existing_user = await db.user_profile.find_unique(where={"user_id": user_id})
        if existing_user:
            logger.info(f"User {user_id} already exists")
            return {
                "status": "already_exists",
                "user_id": user_id,
                "message": "User profile already exists"
            }
        
        # Create user
        new_user = await db.user_profile.create(
            data={
                "user_id": user_id,
                "google_email": google_email,
                "google_id": google_id,
                "name": name,
                "picture_url": picture_url or None,
                "locale": user_data.get("locale", "en"),
            }
        )
        
        logger.info(f"User profile created: {user_id}")
        
        return {
            "status": "success",
            "message": "User profile created successfully",
            "user_id": new_user.user_id,
            "name": new_user.name,
            "email": new_user.google_email,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


# ============================================================================
# PROMPT MANAGEMENT ENDPOINTS
# ============================================================================

@app.post(f"{settings.api_prefix}/prompts/save", response_model=dict)
async def save_prompt(prompt_input: PromptInput):
    """
    Save a user prompt to the database
    
    This endpoint stores user chat prompts for later analysis.
    Each prompt can have tags and categories for better organization.
    """
    try:
        logger.info(f"Saving prompt for user {prompt_input.user_id}")
        
        # Check if user exists
        user = await db.user_profile.find_unique(where={"user_id": prompt_input.user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {prompt_input.user_id} not found"
            )
        
        # Save prompt to database
        saved_prompt = await db.prompt_history.create(
            data={
                "user_id": prompt_input.user_id,
                "prompt_text": prompt_input.prompt_text,
                "response_text": prompt_input.response_text,
                "category": prompt_input.category,
                "tags": prompt_input.tags,
            }
        )
        
        logger.info(f"Prompt saved successfully: {saved_prompt.id}")
        
        return {
            "status": "success",
            "message": "Prompt saved successfully",
            "prompt_id": saved_prompt.id,
            "user_id": prompt_input.user_id,
            "timestamp": saved_prompt.timestamp,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving prompt: {str(e)}"
        )


@app.get(f"{settings.api_prefix}/prompts/{{user_id}}")
async def get_user_prompts(user_id: str, limit: int = 50, offset: int = 0):
    """
    Get prompt history for a user
    
    Returns recent prompts with pagination support.
    """
    try:
        # Get prompts with pagination
        prompts = await db.prompt_history.find_many(
            where={"user_id": user_id},
            order={"timestamp": "desc"},
            take=limit,
            skip=offset,
        )
        
        return {
            "status": "success",
            "user_id": user_id,
            "total_returned": len(prompts),
            "prompts": prompts,
        }
    
    except Exception as e:
        logger.error(f"Error fetching prompts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching prompts: {str(e)}"
        )


# ============================================================================
# USER CHARACTERISTICS ENDPOINTS
# ============================================================================

@app.post(f"{settings.api_prefix}/analyze", response_model=AnalysisResponse)
async def analyze_user_prompts(analysis_request: AnalysisRequest):
    """
    Analyze user prompts and generate characteristics
    
    This endpoint processes all user prompts, extracts patterns,
    and generates a detailed user profile with characteristics.
    """
    try:
        logger.info(f"Analyzing prompts for user {analysis_request.user_id}")
        
        user_id = analysis_request.user_id
        
        # Check if user exists
        user = await db.user_profile.find_unique(where={"user_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        # Fetch all prompts for the user
        prompts = await db.prompt_history.find_many(
            where={"user_id": user_id},
            order={"timestamp": "desc"},
            take=settings.max_prompts_to_analyze,
        )
        
        if not prompts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No prompts found for user {user_id}"
            )
        
        # Extract prompt texts
        prompt_texts = [p.prompt_text for p in prompts]
        logger.info(f"Found {len(prompt_texts)} prompts for analysis")
        
        # Analyze prompts
        analysis = analyzer.analyze_prompts(prompt_texts)
        
        # Get or create user characteristics
        characteristics = await db.user_characteristics.find_unique(
            where={"user_id": user_id}
        )
        
        if characteristics and not analysis_request.force_reanalyze:
            logger.info(f"Using cached characteristics for user {user_id}")
            return {
                "status": "success",
                "user_id": user_id,
                "prompts_analyzed": len(prompts),
                "characteristics": characteristics,
                "confidence_score": characteristics.confidence_score,
                "analysis_timestamp": characteristics.updated_at,
            }
        
        # Update or create characteristics
        characteristics_data = {
            "user_id": user_id,
            "travel_preferences": analysis.get('travel_preferences', {}),
            "budget_profile": analysis.get('budget_profile', {}),
            "booking_patterns": analysis.get('booking_patterns', {}),
            "interests": analysis.get('interests', []),
            "personality_traits": analysis.get('personality_traits', []),
            "pain_points": analysis.get('pain_points', []),
            "motivation_drivers": analysis.get('motivation_drivers', []),
            "decision_style": analysis.get('decision_style', 'balanced'),
            "tone_preference": analysis.get('tone_preference', 'helpful'),
            "communication_style": analysis.get('communication_style', 'balanced'),
            "detailed_summary": analysis.get('detailed_summary', ''),
            "total_prompts": len(prompts),
            "avg_sentiment": analysis.get('avg_sentiment', 0.0),
            "confidence_score": analysis.get('confidence_score', 0.0),
        }
        
        if characteristics:
            # Update existing
            updated = await db.user_characteristics.update(
                where={"user_id": user_id},
                data=characteristics_data,
            )
            logger.info(f"Updated characteristics for user {user_id}")
        else:
            # Create new
            updated = await db.user_characteristics.create(data=characteristics_data)
            logger.info(f"Created new characteristics for user {user_id}")
        
        # Log analysis
        await db.analysis_logs.create(
            data={
                "user_id": user_id,
                "analysis_type": "prompt_analysis",
                "prompts_analyzed": len(prompts),
                "confidence": analysis.get('confidence_score', 0.0),
                "key_insights": {
                    "interests": analysis.get('interests', []),
                    "traits": analysis.get('personality_traits', []),
                    "pain_points": analysis.get('pain_points', []),
                },
            }
        )
        
        return {
            "status": "success",
            "user_id": user_id,
            "prompts_analyzed": len(prompts),
            "characteristics": updated,
            "confidence_score": updated.confidence_score,
            "analysis_timestamp": updated.updated_at,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing prompts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing prompts: {str(e)}"
        )


# ============================================================================
# LLM CONTEXT ENDPOINTS
# ============================================================================

@app.post(f"{settings.api_prefix}/context", response_model=LLMContextResponse)
async def get_llm_context(context_request: LLMContextRequest):
    """
    Get complete LLM context for a user
    
    This endpoint returns the user's characteristics and summary
    formatted for use as system context in LLM prompts.
    """
    try:
        logger.info(f"Fetching LLM context for user {context_request.user_id}")
        
        user_id = context_request.user_id
        
        # Check if user exists
        user = await db.user_profile.find_unique(where={"user_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        # Get user characteristics
        characteristics = await db.user_characteristics.find_unique(
            where={"user_id": user_id}
        )
        
        if not characteristics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No characteristics found for user {user_id}. Run analysis first."
            )
        
        # Build system context
        system_context = f"""
You are assisting a user with the following profile:

Name: {user.name}

## User Characteristics
{characteristics.detailed_summary}

## Key Preferences
- Travel Style: {', '.join(characteristics.interests) if characteristics.interests else 'Not specified'}
- Budget Tier: {characteristics.budget_profile.get('budget_tier', 'moderate') if characteristics.budget_profile else 'moderate'}
- Decision Style: {characteristics.decision_style}
- Communication Preference: {characteristics.tone_preference}

## Personality Traits
{', '.join(characteristics.personality_traits) if characteristics.personality_traits else 'Not specified'}

## Pain Points
{', '.join(characteristics.pain_points) if characteristics.pain_points else 'Not specified'}

## What Motivates Them
{', '.join(characteristics.motivation_drivers) if characteristics.motivation_drivers else 'Not specified'}

Use this context to provide personalized responses that align with their preferences and communication style.
        """.strip()
        
        response = LLMContextResponse(
            user_id=user.user_id,
            user_name=user.name,
            system_context=system_context,
            detailed_summary=characteristics.detailed_summary,
            key_characteristics={
                "travel_preferences": characteristics.travel_preferences,
                "budget_profile": characteristics.budget_profile,
                "booking_patterns": characteristics.booking_patterns,
                "decision_style": characteristics.decision_style,
            },
            user_interests=characteristics.interests,
            tone_preference=characteristics.tone_preference,
            communication_style=characteristics.communication_style,
            confidence_score=characteristics.confidence_score,
            last_analyzed_at=characteristics.updated_at,
        )
        
        logger.info(f"LLM context generated for user {user_id}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating LLM context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating LLM context: {str(e)}"
        )


@app.get(f"{settings.api_prefix}/characteristics/{{user_id}}")
async def get_user_characteristics(user_id: str):
    """
    Get user characteristics without full LLM context
    
    Returns structured characteristics data suitable for filtering or API calls.
    """
    try:
        characteristics = await db.user_characteristics.find_unique(
            where={"user_id": user_id}
        )
        
        if not characteristics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No characteristics found for user {user_id}"
            )
        
        return {
            "status": "success",
            "user_id": user_id,
            "characteristics": {
                "travel_preferences": characteristics.travel_preferences,
                "budget_profile": characteristics.budget_profile,
                "booking_patterns": characteristics.booking_patterns,
                "interests": characteristics.interests,
                "personality_traits": characteristics.personality_traits,
                "pain_points": characteristics.pain_points,
                "motivation_drivers": characteristics.motivation_drivers,
                "decision_style": characteristics.decision_style,
                "tone_preference": characteristics.tone_preference,
                "communication_style": characteristics.communication_style,
                "detailed_summary": characteristics.detailed_summary,
                "confidence_score": characteristics.confidence_score,
                "last_analyzed_at": characteristics.updated_at,
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching characteristics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching characteristics: {str(e)}"
        )


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level=settings.log_level.lower(),
    )

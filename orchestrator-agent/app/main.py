"""Main Orchestrator Agent Application"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.config import settings
from app.logger import logger
from app.ml.complexity_detector import ComplexityDetector
from app.ml.model_router import ModelRouter
from app.integrations import (
    PersonalizationAgentClient,
    HotelSearchAgentClient,
    AmadeusAgentClient
)
from app.exceptions import OrchestratorException

# Initialize app
app = FastAPI(
    title="Orchestrator Agent",
    description="Agent Hub for Travel Booking - Routes queries and orchestrates agent responses",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
complexity_detector = ComplexityDetector(
    complexity_threshold=settings.complexity_threshold
)
model_router = ModelRouter()
personalization_client = PersonalizationAgentClient()
hotel_search_client = HotelSearchAgentClient()
amadeus_client = AmadeusAgentClient()


# Request/Response Models
class QueryRequest(BaseModel):
    """User query request"""
    query: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Orchestrator response"""
    query: str
    complexity_level: str
    model_used: str
    response: str
    recommendations: Optional[List[Dict[str, Any]]] = None
    status: str


class HotelSearchRequest(BaseModel):
    """Hotel search request"""
    location: str
    check_in: str
    check_out: str
    guests: int
    user_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class FlightSearchRequest(BaseModel):
    """Flight search request"""
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    user_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "orchestrator-agent",
        "version": "1.0.0"
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process user query through orchestrator
    
    Routes to Phi4 for simple queries, Llama for complex ones
    """
    try:
        print("\n" + "="*80)
        print("🔷 ORCHESTRATOR AGENT - QUERY PROCESSING")
        print("="*80)
        print(f"📝 USER QUERY: {request.query}")
        if request.user_id:
            print(f"👤 USER ID: {request.user_id}")
        print("="*80)
        
        logger.info(f"[STEP 1] Received query: {request.query[:50]}...")
        
        # Step 2: Analyze complexity
        print("\n[STEP 2] Analyzing Query Complexity...")
        complexity_level, score = complexity_detector.analyze(request.query)
        print(f"  ├─ Complexity Score: {score:.2f}/1.0")
        print(f"  ├─ Threshold: {settings.complexity_threshold}")
        print(f"  └─ Classification: {complexity_level.upper()}")
        logger.info(f"Complexity: {complexity_level} (score: {score:.2f})")
        
        # Step 3: Prepare context
        print("\n[STEP 3] Preparing Context...")
        context = request.context or {}
        if request.user_id:
            print(f"  ├─ Fetching user profile...")
            user_profile = await personalization_client.get_user_profile(
                request.user_id
            )
            context["user_profile"] = user_profile
            print(f"  └─ ✓ User profile loaded")
            logger.info(f"Loaded user profile for {request.user_id}")
        
        # Step 4: Route to appropriate model
        print(f"\n[STEP 4] Routing Query to Model...")
        if complexity_level == "simple":
            print(f"  ├─ Query is SIMPLE (score {score:.2f} < {settings.complexity_threshold})")
            print(f"  ├─ MODEL: Phi4 (Fast, Lightweight)")
            print(f"  └─ 🚀 Sending to Phi4...")
        else:
            print(f"  ├─ Query is COMPLEX (score {score:.2f} >= {settings.complexity_threshold})")
            print(f"  ├─ MODEL: Llama2 (Powerful, In-depth)")
            print(f"  └─ 🚀 Sending to Llama2...")
        
        logger.info(f"Routing to {complexity_level} model")
        
        # Call the model
        model_response = await model_router.route_query(
            request.query,
            complexity_level,
            context
        )
        
        print(f"\n[STEP 5] Model Response Received")
        print(f"  ├─ Model Used: {model_response['model']}")
        print(f"  ├─ Status: {model_response['status']}")
        print(f"  └─ Response Length: {len(model_response['response'])} characters")
        
        print("\n" + "="*80)
        print("✅ QUERY PROCESSING COMPLETE")
        print("="*80 + "\n")
        
        return QueryResponse(
            query=request.query,
            complexity_level=complexity_level,
            model_used=model_response["model"],
            response=model_response["response"],
            status="success"
        )
        
    except OrchestratorException as e:
        logger.error(f"Orchestrator error: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/search/hotels")
async def search_hotels(request: HotelSearchRequest):
    """
    Search for hotels with personalization
    """
    try:
        print("\n" + "="*80)
        print("🏨 HOTEL SEARCH - AGENT ROUTING")
        print("="*80)
        print(f"📍 Location: {request.location}")
        print(f"📅 Check-in: {request.check_in} | Check-out: {request.check_out}")
        print(f"👥 Guests: {request.guests}")
        if request.user_id:
            print(f"👤 User ID: {request.user_id}")
        print("="*80)
        
        logger.info(f"Hotel search request: {request.location}")
        
        # Step 1: Call Hotel Search Agent
        print("\n[STEP 1] Calling Hotel Search Agent...")
        print(f"  ├─ Agent URL: {settings.hotel_search_agent_url}")
        print(f"  ├─ Endpoint: POST /search")
        
        results = await hotel_search_client.search_hotels(
            location=request.location,
            check_in=request.check_in,
            check_out=request.check_out,
            guests=request.guests,
            preferences=request.preferences
        )
        
        print(f"  ├─ ✓ Response received")
        print(f"  └─ Results found: {len(results)}")
        logger.info(f"Hotel search returned {len(results)} results")
        
        # Step 2: Apply personalization if user provided
        if request.user_id and results:
            print(f"\n[STEP 2] Applying Personalization...")
            print(f"  ├─ Agent URL: {settings.personalization_agent_url}")
            print(f"  ├─ Endpoint: POST /rank")
            print(f"  ├─ User ID: {request.user_id}")
            print(f"  ├─ Results to rank: {len(results)}")
            
            results = await personalization_client.rank_results(
                user_id=request.user_id,
                results=results
            )
            
            print(f"  └─ ✓ Results ranked and personalized")
            logger.info(f"Applied personalization ranking for {request.user_id}")
        
        print("\n" + "="*80)
        print(f"✅ HOTEL SEARCH COMPLETE - {len(results)} results")
        print("="*80 + "\n")
        
        return {
            "status": "success",
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Hotel search error: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/flights")
async def search_flights(request: FlightSearchRequest):
    """
    Search for flights with personalization
    """
    try:
        print("\n" + "="*80)
        print("✈️  FLIGHT SEARCH - AGENT ROUTING")
        print("="*80)
        print(f"🛫 Origin: {request.origin} → Destination: {request.destination}")
        print(f"📅 Departure: {request.departure_date}")
        if request.return_date:
            print(f"📅 Return: {request.return_date}")
        print(f"👥 Passengers: {request.passengers}")
        if request.user_id:
            print(f"👤 User ID: {request.user_id}")
        print("="*80)
        
        logger.info(f"Flight search request: {request.origin} to {request.destination}")
        
        # Step 1: Call Amadeus/TBO Agent
        print("\n[STEP 1] Calling Amadeus/TBO Agent...")
        print(f"  ├─ Agent URL: {settings.amadeus_agent_url}")
        print(f"  ├─ Endpoint: POST /search")
        print(f"  ├─ Route: {request.origin} → {request.destination}")
        
        results = await amadeus_client.search_flights(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            passengers=request.passengers,
            preferences=request.preferences
        )
        
        print(f"  ├─ ✓ Response received")
        print(f"  └─ Results found: {len(results)}")
        logger.info(f"Flight search returned {len(results)} results")
        
        # Step 2: Apply personalization if user provided
        if request.user_id and results:
            print(f"\n[STEP 2] Applying Personalization...")
            print(f"  ├─ Agent URL: {settings.personalization_agent_url}")
            print(f"  ├─ Endpoint: POST /rank")
            print(f"  ├─ User ID: {request.user_id}")
            print(f"  ├─ Results to rank: {len(results)}")
            
            results = await personalization_client.rank_results(
                user_id=request.user_id,
                results=results
            )
            
            print(f"  └─ ✓ Results ranked and personalized")
            logger.info(f"Applied personalization ranking for {request.user_id}")
        
        print("\n" + "="*80)
        print(f"✅ FLIGHT SEARCH COMPLETE - {len(results)} results")
        print("="*80 + "\n")
        
        return {
            "status": "success",
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Flight search error: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/packages")
async def search_packages(request: FlightSearchRequest):
    """
    Search for complete travel packages (flights + hotels)
    """
    try:
        logger.info(f"Package search: {request.origin} to {request.destination}")
        
        # Get travel packages
        packages = await amadeus_client.get_travel_packages(
            origin=request.origin,
            destination=request.destination,
            dates={
                "departure": request.departure_date,
                "return": request.return_date,
                "check_in": request.departure_date,
                "check_out": request.return_date
            }
        )
        
        # Personalize if user_id provided
        if request.user_id and packages:
            packages = await personalization_client.rank_results(
                user_id=request.user_id,
                results=packages
            )
        
        return {
            "status": "success",
            "count": len(packages),
            "packages": packages
        }
        
    except Exception as e:
        logger.error(f"Package search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orchestrate")
async def orchestrate(request: QueryRequest):
    """
    Main orchestration endpoint - intelligently routes to agents
    """
    try:
        print("\n" + "="*80)
        print("🎯 ORCHESTRATOR - FULL ORCHESTRATION FLOW")
        print("="*80)
        print(f"📝 USER QUERY: {request.query}")
        if request.user_id:
            print(f"👤 USER ID: {request.user_id}")
        print("="*80)
        
        logger.info("Starting full orchestration...")
        
        # Step 1: Analyze query complexity
        print("\n[STEP 1] Analyzing Query Complexity...")
        complexity_level, score = complexity_detector.analyze(request.query)
        print(f"  ├─ Complexity Score: {score:.2f}/1.0")
        print(f"  └─ Classification: {complexity_level.upper()}")
        logger.info(f"Query complexity: {complexity_level} (score: {score:.2f})")
        
        # Step 2: Route to LLM for initial processing
        print(f"\n[STEP 2] Processing Query with {complexity_level.upper()} Model...")
        model = settings.llama_model if complexity_level == "complex" else settings.phi4_model
        print(f"  ├─ Model: {model}")
        print(f"  ├─ Ollama Host: {settings.ollama_host}")
        
        model_response = await model_router.route_query(
            request.query,
            complexity_level,
            request.context
        )
        print(f"  └─ ✓ Model processing complete")
        
        # Step 3: Identify which agents to call
        recommendations = []
        print(f"\n[STEP 3] Identifying Required Agents...")
        
        agents_needed = []
        if any(kw in request.query.lower() for kw in ["hotel", "accommodation", "stay"]):
            agents_needed.append("Hotel Search Agent")
        if any(kw in request.query.lower() for kw in ["flight", "fly", "travel", "ticket"]):
            agents_needed.append("Amadeus/TBO Agent")
        
        if agents_needed:
            print(f"  ├─ Agents needed: {', '.join(agents_needed)}")
        else:
            print(f"  └─ Using model response only")
        
        # Step 4: Call identified agents
        if "Hotel Search Agent" in agents_needed:
            if "location" in request.context or "destination" in request.context:
                location = request.context.get("location") or request.context.get("destination")
                print(f"\n[STEP 4.1] Calling Hotel Search Agent...")
                print(f"  ├─ Agent URL: {settings.hotel_search_agent_url}")
                print(f"  ├─ Endpoint: POST /search")
                print(f"  ├─ Location: {location}")
                
                hotel_results = await hotel_search_client.search_hotels(
                    location=location,
                    check_in=request.context.get("check_in", ""),
                    check_out=request.context.get("check_out", ""),
                    guests=request.context.get("guests", 1)
                )
                recommendations.extend(hotel_results[:3])
                print(f"  └─ ✓ Retrieved {len(hotel_results)} hotel results")
                logger.info(f"Hotel search returned {len(hotel_results)} results")
        
        if "Amadeus/TBO Agent" in agents_needed:
            if "origin" in request.context and "destination" in request.context:
                print(f"\n[STEP 4.2] Calling Amadeus/TBO Agent...")
                print(f"  ├─ Agent URL: {settings.amadeus_agent_url}")
                print(f"  ├─ Endpoint: POST /search")
                print(f"  ├─ Route: {request.context['origin']} → {request.context['destination']}")
                
                flight_results = await amadeus_client.search_flights(
                    origin=request.context["origin"],
                    destination=request.context["destination"],
                    departure_date=request.context.get("departure_date", ""),
                    passengers=request.context.get("passengers", 1)
                )
                recommendations.extend(flight_results[:3])
                print(f"  └─ ✓ Retrieved {len(flight_results)} flight results")
                logger.info(f"Flight search returned {len(flight_results)} results")
        
        # Step 5: Apply personalization and business rules
        if request.user_id:
            print(f"\n[STEP 5] Applying Personalization & Business Rules...")
            print(f"  ├─ Agent URL: {settings.personalization_agent_url}")
            print(f"  ├─ Endpoint: POST /rank")
            print(f"  ├─ User ID: {request.user_id}")
            print(f"  ├─ Results to rank: {len(recommendations)}")
            
            recommendations = await personalization_client.rank_results(
                user_id=request.user_id,
                results=recommendations
            )
            print(f"  └─ ✓ Personalization applied")
            logger.info(f"Applied personalization for {request.user_id}")
        
        print("\n" + "="*80)
        print(f"✅ ORCHESTRATION COMPLETE")
        print(f"  ├─ Total Recommendations: {len(recommendations[:5])}")
        print(f"  ├─ Agents Contacted: {len(agents_needed)}")
        print("="*80 + "\n")
        
        return {
            "status": "success",
            "query": request.query,
            "complexity_level": complexity_level,
            "model_used": model,
            "model_response": model_response["response"],
            "recommendations": recommendations[:5],
            "agents_contacted": agents_needed,
            "suggestion": "Use hotel search for bookings or flight search for travel"
        }
        
    except Exception as e:
        logger.error(f"Orchestration error: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )
